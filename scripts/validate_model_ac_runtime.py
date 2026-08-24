"""Real-HTTP A+C acceptance against an isolated, nonce-verified Uvicorn runtime."""
import hashlib
import json
import os
import socket
import sqlite3
import subprocess
import sys
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "docs" / "runtime_evidence_model_ac.json"
FIXTURE = ROOT / "tests" / "fixtures" / "historical_replay.json"
MAIN_DB = ROOT / "data" / "rice_duck.db"
RAW_ROWS = {"H01": 8, "H02": 9, "H03": 11, "H04": 14, "H05": 23, "H06": 25, "H07": 38, "H08": 43, "H09": 44, "H10": 47, "H11": 62}


def sha(path: Path) -> str | None:
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() else None


def free_port() -> int:
    sock = socket.socket()
    sock.bind(("127.0.0.1", 0))
    port = sock.getsockname()[1]
    sock.close()
    return port


def expect(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def check_case(name: str, response: httpx.Response, check) -> dict:
    body = response.json() if response.content else None
    expect(response.status_code == 200, f"{name}: HTTP {response.status_code}: {response.text}")
    check(body)
    return {"id": name, "http_status": response.status_code, "response": body, "pass": True}


def main() -> None:
    port, instance = free_port(), uuid.uuid4().hex
    runtime_db = ROOT / "data" / f"runtime_model_ac_{uuid.uuid4().hex}.db"
    before = sha(MAIN_DB)
    clean_head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    dirty_start = bool(subprocess.check_output(["git", "status", "--porcelain"], cwd=ROOT, text=True).strip())
    expect(not dirty_start, "runtime evidence must start from a clean working tree")
    env = os.environ.copy()
    env.update({
        "DATABASE_PATH": str(runtime_db),
        "RUNTIME_INSTANCE_ID": instance,
        "JWT_SECRET_KEY": f"runtime-disposable-{uuid.uuid4().hex}",
        "PYTHONPATH": str(ROOT),
    })
    command = [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", str(port)]
    evidence = {
        "branch": subprocess.check_output(["git", "branch", "--show-current"], cwd=ROOT, text=True).strip(),
        "tested_clean_head": clean_head,
        "working_tree_dirty": dirty_start,
        "captured_at": datetime.now(timezone.utc).isoformat(),
        "server_url": f"http://127.0.0.1:{port}",
        "runtime_instance_id": instance,
        "backend_start_command": " ".join(command),
        "runtime_database_path": str(runtime_db),
        "main_database_before": before,
    }
    process = subprocess.Popen(command, cwd=ROOT, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        with httpx.Client(timeout=10) as client:
            base = evidence["server_url"]
            for _ in range(50):
                try:
                    health = client.get(base + "/health")
                    if health.status_code == 200:
                        break
                except httpx.HTTPError:
                    pass
                time.sleep(0.1)
            else:
                raise RuntimeError("Uvicorn health check timed out")
            evidence["health"] = health.json()
            expect(evidence["health"].get("runtime_instance_id") == instance, "health runtime nonce mismatch")
            evidence["runtime_nonce_verified"] = True

            common = {"rice_variety": "sertani", "planting_system": "jajar_legowo", "duck_age_days": 21}
            def simulate(data):
                return client.post(base + "/api/v1/dss/simulate", json=data)

            synthetic = []
            synthetic.append(check_case("S-C01", simulate({**common, "land_area_are": 10, "duck_count": 20}), lambda x: expect((x["density_status"], x["yield_are_kg"]) == ("RECOMMENDED", 50), "S-C01")))
            synthetic.append(check_case("S-C02", simulate({**common, "land_area_are": 10, "duck_count": 40}), lambda x: expect((x["density_status"], x["yield_are_kg"]) == ("RECOMMENDED", 50), "S-C02")))
            synthetic.append(check_case("S-C03", simulate({**common, "land_area_are": 10, "duck_count": 41}), lambda x: expect((x["density_status"], x["yield_are_kg"]) == ("WARNING_ABOVE_RECOMMENDED", 50), "S-C03")))
            synthetic.append(check_case("S-C04", simulate({**common, "land_area_are": 10, "duck_count": 80}), lambda x: expect(x["survival_risk"] is None and x["yield_are_kg"] == 50, "S-C04")))
            synthetic.append(check_case("S-C05", simulate({**common, "land_area_are": 10, "duck_count": 81}), lambda x: expect(x["survival_risk"] == "HIGH" and x["revenue_duck_all_sold_scenario"] is None, "S-C05")))
            synthetic.append(check_case("S-C06", simulate({**common, "land_area_are": 10, "duck_count": 30, "planting_system": "tegel"}), lambda x: expect(x["density_status"] == "RECOMMENDED", "S-C06")))
            synthetic.append(check_case("S-C07", simulate({**common, "land_area_are": 10, "duck_count": 31, "planting_system": "tegel"}), lambda x: expect(x["density_status"] == "WARNING_ABOVE_RECOMMENDED", "S-C07")))
            age_results = [simulate({**common, "land_area_are": 10, "duck_count": 20, "duck_age_days": age}) for age in (20, 21, 30, 31)]
            expect([x.json()["age_status"] for x in age_results] == ["NOT_RECOMMENDED", "LOCAL_READY", "LOCAL_READY", "OLDER_CONSERVATIVE"], "S-C08")
            synthetic.append({"id": "S-C08", "http_status": [x.status_code for x in age_results], "pass": True})
            synthetic.append(check_case("S-C09", simulate({**common, "land_area_are": 10, "duck_count": 20}), lambda x: expect((x["revenue_gabah"], x["revenue_duck_all_sold_scenario"], x["cost_duck_buy"], x["cash_contribution_before_optional"]) == (3000000, 900000, 500000, 3400000), "S-C09")))
            synthetic.append(check_case("S-C10", simulate({**common, "land_area_are": 10, "duck_count": 20}), lambda x: expect(x["cost_feed_scenario"] is None and x["cost_infra_cycle"] is None and x["cash_contribution_after_optional"] is None, "S-C10")))
            synthetic.append(check_case("S-C11", simulate({**common, "land_area_are": 10, "duck_count": 0}), lambda x: expect(x["yield_are_kg"] == 50 and x["revenue_duck_all_sold_scenario"] == 0 and x["cost_duck_buy"] == 0, "S-C11")))
            invalid = simulate({**common, "land_area_are": 0, "duck_count": 20})
            expect(invalid.status_code == 400, "S-C12")
            synthetic.append({"id": "S-C12", "http_status": invalid.status_code, "response": invalid.json(), "pass": True})
            evidence["shared_c_acceptance"] = synthetic

            references = []
            reference_cases = [("AC-R01", 49, 40, None), ("AC-R02", 50, 40, 65.0044549762), ("AC-R03", 80, 40, 69.7396), ("AC-R04", 81, 40, None), ("AC-R05", 80, 61, None), ("t32_regression", 32, 40, None)]
            for name, duration, ducks, expected in reference_cases:
                response = simulate({**common, "land_area_are": 10, "duck_count": ducks, "literature_duration_days": duration})
                def check_reference(body, expected=expected, name=name):
                    expect(body["yield_are_kg"] == 50, f"{name}: primary changed")
                    if expected is None:
                        expect(body["literature_reference_status"] == "OUTSIDE_LITERATURE_DOMAIN" and body["yield_literature_reference_are_kg"] is None, name)
                    else:
                        expect(body["literature_reference_status"] == "VALID_DOMAIN" and abs(body["yield_literature_reference_are_kg"] - expected) < 1e-8, name)
                references.append(check_case(name, response, check_reference))
            evidence["reference_cases"] = references

            calendar = check_case("calendar_without_literature_duration", simulate({**common, "land_area_are": 10, "duck_count": 40, "planting_date": "2026-01-01"}), lambda x: expect(x["release_date_min"] == "2026-01-22" and x["withdraw_date_max"] == "2026-03-02" and x["literature_reference_status"] == "OUTSIDE_LITERATURE_DOMAIN" and x["yield_literature_reference_are_kg"] is None, "calendar"))
            evidence["calendar_without_literature_duration"] = calendar
            no_ref = simulate({**common, "land_area_are": 10, "duck_count": 40}).json()
            r50, r80 = references[1]["response"], references[2]["response"]
            primary_fields = ["yield_are_kg", "yield_total_kg", "revenue_gabah", "revenue_duck_all_sold_scenario", "cost_duck_buy", "cash_contribution_before_optional", "cash_contribution_after_optional"]
            expect(all(no_ref[field] == r50[field] == r80[field] for field in primary_fields), "primary/reference economic invariance")
            evidence["primary_reference_economic_invariance"] = True

            holdout = json.loads(FIXTURE.read_text(encoding="utf-8"))
            rows, errors = [], []
            for source in holdout:
                request = {key: source[key] for key in ("land_area_are", "duck_count", "rice_variety", "planting_system", "duck_age_days", "p_gabah", "p_duck_buy", "p_duck_sell")}
                if "planting_date" in source:
                    request["planting_date"] = source["planting_date"]
                body = check_case(source["id"], simulate(request), lambda x, source=source: expect(x["literature_reference_status"] == "OUTSIDE_LITERATURE_DOMAIN" and x["yield_literature_reference_are_kg"] is None and abs(x["cost_duck_buy"] - source["duck_count"] * source["p_duck_buy"]) < 0.01, source["id"]))["response"]
                expected_cash = 50 * source["land_area_are"] * source["p_gabah"] + source["duck_count"] * source["p_duck_sell"] - source["duck_count"] * source["p_duck_buy"]
                expect(abs(body["cash_contribution_before_optional"] - expected_cash) < 0.01, source["id"] + " primary cash")
                errors.append(50 - source["actual_yield_are"])
                rows.append({"id": source["id"], "raw_row": source.get("raw_row", RAW_ROWS[source["id"]]), "request": request, "actual_yield_are": source["actual_yield_are"], "actual_gabah_revenue": source["actual_yield_are"] * source["land_area_are"] * source["p_gabah"], "error_backend_minus_actual": 50 - source["actual_yield_are"], "http_status": 200, "response": body, "pass": True})
            absolute = sorted(abs(value) for value in errors)
            metrics = {"MAE": sum(abs(value) for value in errors) / len(errors), "RMSE": (sum(value * value for value in errors) / len(errors)) ** 0.5, "MedAE": absolute[len(absolute) // 2], "Bias": sum(errors) / len(errors)}
            expect(abs(metrics["MAE"] - 11.979) < 0.01 and abs(metrics["RMSE"] - 15.990) < 0.01 and abs(metrics["MedAE"] - 9.583) < 0.01 and abs(metrics["Bias"] - 7.307) < 0.01, "holdout metrics")
            evidence["holdout"] = rows
            evidence["holdout_metrics"] = metrics

            register = client.post(base + "/api/v1/auth/register", json={"name": "Runtime User", "email": "runtime@example.com", "password": "password123"})
            expect(register.status_code == 201, register.text)
            token = client.post(base + "/api/v1/auth/login", json={"email": "runtime@example.com", "password": "password123"}).json()["access_token"]
            headers = {"Authorization": "Bearer " + token}
            saved = client.post(base + "/api/v1/dss/simulate", json={**common, "land_area_are": 10, "duck_count": 40, "literature_duration_days": 50}, headers=headers).json()
            listing = client.get(base + "/api/v1/dss/histories", headers=headers).json()
            history_id = listing["data"][0]["id"]
            expect(listing["data"][0]["schema_version"] == 4 and client.get(base + f"/api/v1/dss/histories/{history_id}", headers=headers).json() == saved, "v4 history")
            expect(client.delete(base + f"/api/v1/dss/histories/{history_id}", headers=headers).status_code == 200 and client.get(base + f"/api/v1/dss/histories/{history_id}", headers=headers).status_code == 404, "v4 delete")
            with sqlite3.connect(runtime_db) as connection:
                user_id = connection.execute("SELECT id FROM users WHERE email='runtime@example.com'").fetchone()[0]
                for version in (1, 2, 3):
                    connection.execute("INSERT INTO dss_simulation_histories (id,user_id,schema_version,created_at) VALUES (?,?,?,?)", (f"legacy-v{version}", user_id, version, "2026-01-01T00:00:00+00:00"))
            expect(client.get(base + "/api/v1/dss/histories", headers=headers).json() == {"data": []}, "legacy rows listed")
            for version in (1, 2, 3):
                identifier = f"legacy-v{version}"
                expect(client.get(base + f"/api/v1/dss/histories/{identifier}", headers=headers).status_code == 404, identifier + " detail")
                expect(client.delete(base + f"/api/v1/dss/histories/{identifier}", headers=headers).status_code == 404, identifier + " delete")
            with sqlite3.connect(runtime_db) as connection:
                physical_legacy_count = connection.execute("SELECT COUNT(*) FROM dss_simulation_histories WHERE schema_version IN (1,2,3)").fetchone()[0]
            expect(physical_legacy_count == 3, "legacy physical preservation")
            evidence["history"] = {"v4_round_trip": True, "v4_delete_then_404": True, "legacy_v1_v3_hidden": True, "legacy_v1_v3_detail_delete_404": True, "legacy_physical_rows_preserved": physical_legacy_count}
            evidence["summary"] = {"S_C01_S_C12": "12/12", "AC_R01_R05": "5/5", "t32_regression": "PASS", "calendar_without_literature_duration": "PASS", "primary_reference_economic_invariance": "PASS", "holdout_source_faithful": "11/11", "holdout_reference_abstention": "11/11", "v4_history": "PASS", "v1_v3_live_preservation": "PASS", "runtime_nonce": "PASS"}
    finally:
        process.terminate()
        process.wait(timeout=10)
        evidence["main_database_after"] = sha(MAIN_DB)
        evidence["main_database_unchanged"] = before == evidence["main_database_after"]
        EVIDENCE.write_text(json.dumps(evidence, ensure_ascii=False, indent=2), encoding="utf-8")
        # Windows can retain SQLite's file handle briefly after Uvicorn exits.
        # Cleanup must not turn a completed acceptance run into a false failure.
        for _ in range(30):
            if not runtime_db.exists():
                break
            try:
                runtime_db.unlink()
                break
            except PermissionError:
                time.sleep(0.1)
    print(json.dumps(evidence.get("summary", {}), indent=2))


if __name__ == "__main__":
    main()
