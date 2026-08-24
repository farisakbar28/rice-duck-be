"""Run Model A acceptance cases over real HTTP and save auditable raw evidence."""
from __future__ import annotations

import json
import os
import re
import socket
import subprocess
import sys
import time
from hashlib import sha256
from secrets import token_urlsafe
from decimal import Decimal
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

OUTPUT = Path("docs/runtime_evidence_model_a.json")
SCENARIO_DOC = Path("docs/tes_skenario.md")
MAIN_DATABASE_PATH = Path("data/rice_duck.db")
BASE_URL = ""
REQUIRED_BRANCH = "focus-model-a"


def approximately_equal(actual: object, expected: Decimal, tolerance: Decimal = Decimal("0.000000001")) -> bool:
    return actual is not None and abs(Decimal(str(actual)) - expected) <= tolerance


def acceptance_passes(summary: dict, metadata: dict) -> bool:
    """Single source of truth for evidence documentation and process exit."""
    return all((
        metadata["branch"] == REQUIRED_BRANCH,
        summary["health_pass"],
        summary["historical_pass"] == summary["historical_total"],
        summary["synthetic_pass"] == summary["synthetic_total"],
        summary["calendar_pass"],
        summary["history_pass"],
        metadata["runtime_database_changed"],
        metadata["main_database_unchanged"],
    ))


def require_model_a_branch(branch: str) -> None:
    if branch != REQUIRED_BRANCH:
        raise RuntimeError(
            f"Model A runtime evidence requires branch '{REQUIRED_BRANCH}', got '{branch}'."
        )


def file_snapshot(path: Path) -> dict:
    """Return auditable metadata plus a content hash for a database file."""
    if not path.exists():
        return {"exists": False, "size_bytes": 0, "modified_at_utc": None, "sha256": None}
    stat = path.stat()
    return {
        "exists": True,
        "size_bytes": stat.st_size,
        "modified_at_utc": datetime.fromtimestamp(stat.st_mtime, timezone.utc).isoformat(),
        "sha256": sha256(path.read_bytes()).hexdigest(),
    }


def free_local_port() -> int:
    """Reserve a currently free loopback port before starting the child server."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
        probe.bind(("127.0.0.1", 0))
        return int(probe.getsockname()[1])


def powershell_start_command(command: list[str], workspace_path: Path, database_path: Path, instance_id: str) -> str:
    """Return a self-contained, Windows-reproducible representation of Popen."""
    def quote(value: str) -> str:
        return "'" + value.replace("'", "''") + "'"

    executable, *arguments = command
    rendered_arguments = " ".join(quote(argument) if " " in argument else argument for argument in arguments)
    return (
        f"Set-Location {quote(str(workspace_path))}; "
        f"$env:DATABASE_PATH={quote(str(database_path))}; "
        f"$env:RUNTIME_INSTANCE_ID={quote(instance_id)}; "
        f"& {quote(executable)} {rendered_arguments}"
    )


def start_isolated_server() -> tuple[subprocess.Popen, dict]:
    """Launch the exact backend process used by this acceptance run.

    A unique, ignored SQLite file and a fresh loopback port prevent an already
    running local server from silently receiving the evidence traffic.
    """
    global BASE_URL
    workspace_path = Path.cwd().resolve()
    run_id = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S%f")
    database_path = (Path("data") / f"model_a_runtime_{run_id}.db").resolve()
    port = free_local_port()
    BASE_URL = f"http://127.0.0.1:{port}"
    # Snapshot before Popen so app startup (which initializes SQLite) is inside
    # the verified isolation window, not silently excluded from it.
    runtime_database_before = file_snapshot(database_path)
    main_database_before = file_snapshot(MAIN_DATABASE_PATH)
    environment = os.environ.copy()
    environment["DATABASE_PATH"] = str(database_path)
    instance_id = token_urlsafe(32)
    environment["RUNTIME_INSTANCE_ID"] = instance_id
    command = [
        sys.executable, "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", str(port),
    ]
    reproducible_command = powershell_start_command(command, workspace_path, database_path, instance_id)
    process = subprocess.Popen(
        command,
        cwd=workspace_path,
        env=environment,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    for _ in range(100):
        if process.poll() is not None:
            raise RuntimeError(f"Isolated backend exited during startup with code {process.returncode}.")
        try:
            health = call("GET", "/health")
            expected_health = {
                "status": "ok",
                "service": "rice-duck-dss-backend",
                "runtime_instance_id": instance_id,
            }
            if health["http_status"] == 200 and health["raw_response_json"] == expected_health:
                return process, {
                    "launcher_pid": process.pid,
                    "runtime_database_path": str(database_path.relative_to(Path.cwd())),
                    "runtime_database_path_absolute": str(database_path),
                    "server_url": BASE_URL,
                    "runtime_instance_id": instance_id,
                    "working_directory": str(workspace_path),
                    "backend_start_command": reproducible_command,
                    "backend_process_arguments": command,
                    "database_before": runtime_database_before,
                    "main_database_before": main_database_before,
                }
        except OSError:
            pass
        time.sleep(0.1)
    process.terminate()
    process.wait(timeout=5)
    raise RuntimeError("Timed out waiting for the isolated backend health endpoint.")


def stop_server(process: subprocess.Popen) -> None:
    if process.poll() is None:
        process.terminate()
        try:
            process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=5)


def call(method: str, path: str, body: dict | None = None, token: str | None = None) -> dict:
    encoded = json.dumps(body, separators=(",", ":")).encode() if body is not None else None
    headers = {"Content-Type": "application/json"} if encoded else {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = Request(f"{BASE_URL}{path}", data=encoded, headers=headers, method=method)
    timestamp = datetime.now(timezone.utc).isoformat()
    try:
        with urlopen(request, timeout=10) as response:
            status, raw = response.status, response.read().decode()
    except HTTPError as error:
        status, raw = error.code, error.read().decode()
    return {
        "timestamp": timestamp,
        "method": method,
        "path": path,
        "request_json": body,
        "http_status": status,
        # Preserve the exact response text received over HTTP.  The parsed form
        # below is only for assertions and convenient evidence inspection.
        "raw_response_body": raw,
        "raw_response_json": json.loads(raw),
    }


def replay_rows() -> list[dict]:
    rows = []
    in_source_table = False
    for line in Path("docs/tes_skenario.md").read_text(encoding="utf-8").splitlines():
        if line.startswith("| ID | Raw row"):
            in_source_table = True
            continue
        if line.startswith("### Expected aggregate result"):
            break
        if not in_source_table or not line.startswith("| A") or len(line.split("|")) < 10:
            continue
        cols = [part.strip() for part in line.split("|")]
        area, ducks = Decimal(cols[4]), int(cols[5])
        payload = {
            "land_area_are": float(area), "duck_count": ducks,
            "rice_variety": cols[7], "planting_system": "tegel" if "Tegel" in cols[8] else "jajar_legowo",
            "duck_age_days": 21,
        }
        entry = call("POST", "/api/v1/dss/simulate", payload)
        response = entry["raw_response_json"]
        expected_density = cols[10]
        expected_density_are = Decimal(ducks) / area
        expected_density_ha = expected_density_are * Decimal("100")
        expected_xiong_density_domain = cols[11] == "VALID"
        expected_survival = "HIGH" if expected_density_are > 8 else None
        passed = (entry["http_status"] == 200 and approximately_equal(response["density_are"], expected_density_are) and approximately_equal(response["density_ha"], expected_density_ha) and response["density_status"] == expected_density and response["survival_risk"] == expected_survival and ((Decimal("0") < expected_density_ha <= Decimal("600")) == expected_xiong_density_domain) and response["yield_status"] == "OUTSIDE_LITERATURE_DOMAIN" and response["yield_are_kg"] is None and response["yield_total_kg"] is None)
        entry.update({"id": cols[1], "expected": {"density_are": float(expected_density_are), "density_ha": float(expected_density_ha), "density_status": expected_density, "xiong_density_domain": expected_xiong_density_domain, "survival_risk": expected_survival, "yield_status": "OUTSIDE_LITERATURE_DOMAIN", "yield_are_kg": None}, "actual": {"density_are": response["density_are"], "density_ha": response["density_ha"], "density_status": response["density_status"], "survival_risk": response["survival_risk"], "yield_status": response["yield_status"], "yield_are_kg": response["yield_are_kg"]}, "numerical_difference_if_applicable": None, "pass": passed})
        rows.append(entry)
    return rows


def synthetic_rows() -> list[dict]:
    base = {"land_area_are": 10, "rice_variety": "sertani", "planting_system": "jajar_legowo", "duck_age_days": 21}
    definitions = [
        ("S-A01", {"duck_count": 19}, "UNDER"), ("S-A02", {"duck_count": 20}, "RECOMMENDED"),
        ("S-A03", {"duck_count": 40}, "RECOMMENDED"), ("S-A04", {"duck_count": 41}, "WARNING_ABOVE_RECOMMENDED"),
        ("S-A05", {"duck_count": 80}, "WARNING_ABOVE_RECOMMENDED"), ("S-A06", {"duck_count": 81}, "HIGH_RISK"),
        ("S-A07", {"duck_count": 30, "planting_system": "tegel"}, "RECOMMENDED"), ("S-A08", {"duck_count": 31, "planting_system": "tegel"}, "WARNING_ABOVE_RECOMMENDED"),
        ("S-A09", {"duck_count": 40, "duck_age_days": 20}, "NOT_RECOMMENDED"), ("S-A10", {"duck_count": 40, "duck_age_days": 21}, "LOCAL_READY"),
        ("S-A11", {"duck_count": 40, "duck_age_days": 30}, "LOCAL_READY"), ("S-A12", {"duck_count": 40, "duck_age_days": 31}, "OLDER_CONSERVATIVE"),
        ("S-A13", {"duck_count": 40, "literature_duration_days": 49}, "OUTSIDE_LITERATURE_DOMAIN"), ("S-A14", {"duck_count": 40, "literature_duration_days": 50, "p_gabah": 6000, "p_duck_buy": 25000, "p_duck_sell": 45000}, "VALID"),
        ("S-A15", {"duck_count": 40, "literature_duration_days": 80}, "VALID"), ("S-A16", {"duck_count": 40, "literature_duration_days": 81}, "OUTSIDE_LITERATURE_DOMAIN"),
        ("S-A17", {"duck_count": 61, "literature_duration_days": 80}, "OUTSIDE_LITERATURE_DOMAIN"), ("S-A18", {"land_area_are": 0, "duck_count": 1}, "HTTP_400"),
        ("S-A19", {"duck_count": 0}, "UNDER"),
    ]
    result = []
    for identifier, overrides, expected in definitions:
        payload = base | overrides
        entry = call("POST", "/api/v1/dss/simulate", payload)
        body = entry["raw_response_json"]
        actual = f"HTTP_{entry['http_status']}" if identifier == "S-A18" else body["age_status"] if identifier in {"S-A09", "S-A10", "S-A11", "S-A12"} else body["yield_status"] if identifier in {"S-A13", "S-A14", "S-A15", "S-A16", "S-A17"} else body["density_status"]
        passed = actual == expected
        if identifier != "S-A18":
            expected_density_are = Decimal(str(payload["duck_count"])) / Decimal(str(payload["land_area_are"]))
            passed = passed and approximately_equal(body["density_are"], expected_density_are) and approximately_equal(body["density_ha"], expected_density_are * Decimal("100"))
        if identifier == "S-A05": passed = passed and body["survival_risk"] is None
        if identifier == "S-A06": passed = passed and body["survival_risk"] == "HIGH" and body["revenue_duck_all_sold_scenario"] is None
        numerical_difference = None
        if identifier == "S-A14":
            passed = passed and approximately_equal(body["yield_are_kg"], Decimal("65.0044549762"), Decimal("0.00000001")) and approximately_equal(body["yield_total_kg"], Decimal("650.0445497616"), Decimal("0.0000001")) and approximately_equal(body["revenue_gabah"], Decimal("3900267.30"), Decimal("0.02")) and body["revenue_duck_all_sold_scenario"] == 1800000 and body["cost_duck_buy"] == 1000000 and approximately_equal(body["cash_contribution_before_optional"], Decimal("4700267.30"), Decimal("0.02"))
            numerical_difference = {"yield_are_kg": float(Decimal(str(body["yield_are_kg"])) - Decimal("65.0044549762")), "yield_total_kg": float(Decimal(str(body["yield_total_kg"])) - Decimal("650.0445497616")), "revenue_gabah": float(Decimal(str(body["revenue_gabah"])) - Decimal("3900267.30")), "cash_contribution_before_optional": float(Decimal(str(body["cash_contribution_before_optional"])) - Decimal("4700267.30"))}
        if identifier == "S-A15":
            passed = passed and approximately_equal(body["yield_are_kg"], Decimal("69.7396")) and approximately_equal(body["yield_total_kg"], Decimal("697.396"))
            numerical_difference = {"yield_are_kg": float(Decimal(str(body["yield_are_kg"])) - Decimal("69.7396")), "yield_total_kg": float(Decimal(str(body["yield_total_kg"])) - Decimal("697.396"))}
        if identifier in {"S-A13", "S-A16", "S-A17"}: passed = passed and body["yield_are_kg"] is None and body["yield_total_kg"] is None
        if identifier == "S-A19": passed = passed and body["density_are"] == 0 and body["yield_are_kg"] is None and body["revenue_duck_all_sold_scenario"] == 0 and body["cost_duck_buy"] == 0
        entry.update({"id": identifier, "expected": expected, "actual": actual, "numerical_difference_if_applicable": numerical_difference, "pass": passed})
        result.append(entry)
    return result


def history_case() -> list[dict]:
    suffix = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S%f")
    email = f"model-a-runtime-{suffix}@example.com"
    register = call("POST", "/api/v1/auth/register", {"name": "Model A Runtime", "email": email, "password": "password123"})
    login = call("POST", "/api/v1/auth/login", {"email": email, "password": "password123"})
    token = login["raw_response_json"]["access_token"]
    register["request_json"]["password"] = "[REDACTED]"
    login["request_json"]["password"] = "[REDACTED]"
    login["raw_response_json"]["access_token"] = "[REDACTED]"
    # Authentication responses contain a credential.  A SHA-256 commitment and
    # byte length prove the precise received body without publishing the token.
    login["raw_response_body_sha256"] = sha256(login["raw_response_body"].encode()).hexdigest()
    login["raw_response_body_bytes"] = len(login["raw_response_body"].encode())
    login["raw_response_body"] = "[REDACTED: response contains access_token]"
    simulation = call("POST", "/api/v1/dss/simulate", {"land_area_are": 10, "duck_count": 40, "rice_variety": "sertani", "planting_system": "jajar_legowo", "duck_age_days": 21, "literature_duration_days": 50}, token)
    listing = call("GET", "/api/v1/dss/histories", token=token)
    history_id = listing["raw_response_json"]["data"][0]["id"]
    detail = call("GET", f"/api/v1/dss/histories/{history_id}", token=token)
    deletion = call("DELETE", f"/api/v1/dss/histories/{history_id}", token=token)
    after_delete = call("GET", f"/api/v1/dss/histories/{history_id}", token=token)
    expected_statuses = [201, 200, 200, 200, 200, 200, 404]
    actual_statuses = [step["http_status"] for step in [register, login, simulation, listing, detail, deletion, after_delete]]
    passed = actual_statuses == expected_statuses and listing["raw_response_json"]["data"][0]["schema_version"] == 4 and simulation["raw_response_json"] == detail["raw_response_json"]
    return [{"id": "HISTORY_V4", "steps": [register, login, simulation, listing, detail, deletion, after_delete], "pass": passed}]


def calendar_case() -> dict:
    entry = call("POST", "/api/v1/dss/simulate", {"land_area_are": 10, "duck_count": 40, "rice_variety": "sertani", "planting_system": "jajar_legowo", "duck_age_days": 21, "planting_date": "2026-01-01"})
    body = entry["raw_response_json"]
    entry.update({"expected": "release 21–30 / withdraw 56–60 with 2026-01-22, 2026-01-31, 2026-02-26, 2026-03-02", "pass": entry["http_status"] == 200 and [body["release_hst_min"], body["release_hst_max"], body["withdraw_hst_min"], body["withdraw_hst_max"], body["release_date_min"], body["release_date_max"], body["withdraw_date_min"], body["withdraw_date_max"]] == [21, 30, 56, 60, "2026-01-22", "2026-01-31", "2026-02-26", "2026-03-02"]})
    return entry


def update_scenario_document(evidence: dict) -> None:
    content = SCENARIO_DOC.read_text(encoding="utf-8")
    captured_at = evidence["metadata"]["captured_at"]
    health = evidence["health"]
    calendar = evidence["calendar"]
    history = evidence["history"][0]
    s14 = next(item for item in evidence["synthetic"] if item["id"] == "S-A14")
    history_statuses = ",".join(str(step["http_status"]) for step in history["steps"])
    historical_pass = evidence["summary"]["historical_pass"] == evidence["summary"]["historical_total"]
    synthetic_pass = evidence["summary"]["synthetic_pass"] == evidence["summary"]["synthetic_total"]
    all_pass = acceptance_passes(evidence["summary"], evidence["metadata"])
    generated_summary = "\n".join([
        "<!-- RUNTIME_GENERATED_SUMMARY_START -->",
        f"- Generated from the latest real HTTP run at `{captured_at}`.",
        f"- Required branch `{REQUIRED_BRANCH}`; captured branch `{evidence['metadata']['branch']}`.",
        f"- Isolated runtime database: `{evidence['metadata']['runtime_database_path']}` (launcher PID `{evidence['metadata']['launcher_pid']}`).",
        f"- Isolation verification: runtime DB changed=`{evidence['metadata']['runtime_database_changed']}`; main DB unchanged by SHA-256 content snapshot=`{evidence['metadata']['main_database_unchanged']}`.",
        f"- Health: HTTP `{health['http_status']}`, instance nonce verified, payload `{json.dumps(health['raw_response_json'], separators=(',', ':'))}`, PASS=`{health['pass']}`.",
        f"- Historical A01-A36: `{evidence['summary']['historical_pass']}/{evidence['summary']['historical_total']}` {'PASS' if historical_pass else 'FAIL'}.",
        f"- Synthetic S-A01-S-A19: `{evidence['summary']['synthetic_pass']}/{evidence['summary']['synthetic_total']}` {'PASS' if synthetic_pass else 'FAIL'}.",
        f"- S-A14 actual: `yield_are_kg={s14['raw_response_json']['yield_are_kg']}`, numerical difference `{s14['numerical_difference_if_applicable']['yield_are_kg']}`.",
        f"- Calendar PASS=`{calendar['pass']}`; v4 history PASS=`{history['pass']}` with HTTP sequence `{history_statuses}`.",
        f"- Discrepancy: `{'none' if all_pass else 'one or more checks failed; inspect the raw evidence entry marked pass=false'}`.",
        "<!-- RUNTIME_GENERATED_SUMMARY_END -->",
    ])
    updated = re.sub(
        r"^- Runtime capture timestamp \(UTC\): `[^`]+`\.$",
        f"- Runtime capture timestamp (UTC): `{captured_at}`.",
        content,
        flags=re.MULTILINE,
    )
    updated = re.sub(
        r"<!-- RUNTIME_GENERATED_SUMMARY_START -->.*?<!-- RUNTIME_GENERATED_SUMMARY_END -->",
        lambda _: generated_summary,
        updated,
        flags=re.DOTALL,
    )
    if updated == content:
        raise RuntimeError("Runtime timestamp marker is missing from docs/tes_skenario.md")
    SCENARIO_DOC.write_text(updated, encoding="utf-8")


def main() -> int:
    branch = subprocess.check_output(["git", "branch", "--show-current"], text=True).strip()
    require_model_a_branch(branch)
    process, launcher = start_isolated_server()
    try:
        health = call("GET", "/health")
        historical, synthetic, history, calendar = replay_rows(), synthetic_rows(), history_case(), calendar_case()
        head = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
        dirty = bool(subprocess.check_output(["git", "status", "--porcelain"], text=True).strip())
        captured_at = datetime.now(timezone.utc).isoformat()
        runtime_after = file_snapshot(Path(launcher["runtime_database_path_absolute"]))
        main_after = file_snapshot(MAIN_DATABASE_PATH)
        launcher.update({
            "runtime_database_after": runtime_after,
            "main_database_after": main_after,
            "runtime_database_changed": runtime_after != launcher["database_before"],
            "main_database_unchanged": main_after == launcher["main_database_before"],
        })
        health["expected"] = {
            "status": "ok",
            "service": "rice-duck-dss-backend",
            "runtime_instance_id": launcher["runtime_instance_id"],
        }
        health["pass"] = health["http_status"] == 200 and health["raw_response_json"] == health["expected"]
        evidence = {"metadata": {"branch": branch, "base_head": head, "working_tree_dirty": dirty, "captured_at": captured_at} | launcher, "health": health, "historical": historical, "synthetic": synthetic, "calendar": calendar, "history": history, "summary": {"health_pass": health["pass"], "historical_pass": sum(x["pass"] for x in historical), "historical_total": len(historical), "synthetic_pass": sum(x["pass"] for x in synthetic), "synthetic_total": len(synthetic), "calendar_pass": calendar["pass"], "history_pass": history[0]["pass"]}}
        update_scenario_document(evidence)
        OUTPUT.write_text(json.dumps(evidence, ensure_ascii=False, indent=2), encoding="utf-8")
        print(json.dumps(evidence["summary"]))
        return 0 if acceptance_passes(evidence["summary"], evidence["metadata"]) else 1
    finally:
        stop_server(process)


if __name__ == "__main__":
    raise SystemExit(main())
