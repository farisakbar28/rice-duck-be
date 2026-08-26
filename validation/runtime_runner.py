"""Canonical-runtime execution for validation evidence (task §20–§23).

Every prediction comes from the REAL FastAPI application through TestClient.
The harness contains no formula reimplementation; the only independent
arithmetic here is the docs-prescribed INVARIANT VERIFICATION for fertilizer
(B16) and net infrastructure (B17), which recomputes expected values to
CHECK engine output -- it never feeds values into production.

Raw response JSON is preserved verbatim for every executed case.
"""

from __future__ import annotations

import math
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

from validation._bootstrap import REPO_ROOT, configure_runtime_env

configure_runtime_env()

from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402

API = "/api/v1"
BASE_PAYLOAD = {
    "land_area_are": 10,
    "duck_count": 30,
    "planting_date": "2026-01-01",
    "planting_system": "jajar_legowo",
    "rice_variety": "sertani",
    "duck_age_days": 30,
    # p_duck_buy omitted -> registry default (B01 semantics).
}


def make_client() -> TestClient:
    return TestClient(app)


def _g(obj: Any, *path: str) -> Any:
    for key in path:
        obj = obj[key]
    return obj


def _close(a: float, b: float) -> bool:
    return math.isclose(float(a), float(b), rel_tol=1e-9, abs_tol=1e-6)


# ---------------------------------------------------------------------------
# Synthetic contract cases B01-B18 (docs/tes_skenario_R2.md section 3)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class SyntheticCase:
    case_id: str
    title: str
    payload: dict
    expected_status: int
    checks: tuple[tuple[str, Callable[[dict], bool]], ...] = field(default_factory=tuple)


def _case(case_id: str, title: str, overrides: dict, checks_spec: list[tuple]) -> SyntheticCase:
    payload = dict(BASE_PAYLOAD)
    payload.update(overrides)
    payload = {k: v for k, v in payload.items() if v is not ...}
    checks = []
    for desc, fn in checks_spec:
        checks.append((desc, fn))
    return SyntheticCase(case_id, title, payload, 200 if case_id != "B14" else 400,
                         tuple(checks))


def _supported_survival_checks(duck_count: int) -> list[tuple]:
    return [
        ("survival_availability == AVAILABLE",
         lambda b: _g(b, "duck", "survival_availability") == "AVAILABLE"),
        ("lambda_eff == 0.90", lambda b: _close(_g(b, "duck", "lambda_eff"), 0.90)),
        (f"N_survive == floor({duck_count}*0.90)",
         lambda b: _g(b, "duck", "surviving_ducks")
         == math.floor(duck_count * 0.90)),
    ]


def _yield_unavailable_checks() -> list[tuple]:
    def _reasons(b):
        return set(_g(b, "yield", "reason_codes"))

    return [
        ("yield_availability == UNAVAILABLE",
         lambda b: _g(b, "yield", "availability") == "UNAVAILABLE"),
        ("yield_kg_per_are is null",
         lambda b: _g(b, "yield", "yield_kg_per_are") is None),
        ("yield_total_kg is null",
         lambda b: _g(b, "yield", "yield_total_kg") is None),
        ("reason codes group baseline + exact F_RD node missing",
         lambda b: _reasons(b) == {
             "Y_BASE_GROUP_LOOKUP_MISSING", "F_RD_NODE_MISSING"
         }),
        ("paddy_revenue_rp is null",
         lambda b: _g(b, "economics", "paddy_revenue_rp") is None),
        ("margin_core_rp is null",
         lambda b: _g(b, "economics", "margin_core_rp") is None),
    ]


SYNTHETIC_CASES: list[SyntheticCase] = [
    _case("B01", "Supported Jarwo + default purchase price", {},
          [
              ("p_duck_buy_effective == 26500",
               lambda b: _g(b, "input", "p_duck_buy_effective") == 26500.0),
              ("purchase source LOCAL_DEFAULT_MIDPOINT",
               lambda b: _g(b, "input", "p_duck_buy_source")
               == "LOCAL_DEFAULT_MIDPOINT"),
              ("age SUPPORTED", lambda b: _g(b, "operational", "age_support")
               == "SUPPORTED"),
              ("density_are == 3", lambda b: _close(_g(b, "operational", "density_are"), 3)),
              ("density SUPPORTED",
               lambda b: _g(b, "operational", "density_support") == "SUPPORTED"),
              ("release HST 21..30",
               lambda b: (_g(b, "calendar", "release_hst_min"),
                          _g(b, "calendar", "release_hst_max")) == (21, 30)),
              ("pull HST 56..60",
               lambda b: (_g(b, "calendar", "pull_hst_min"),
                          _g(b, "calendar", "pull_hst_max")) == (56, 60)),
              ("harvest HST 100..110",
               lambda b: (_g(b, "calendar", "harvest_hst_min"),
                          _g(b, "calendar", "harvest_hst_max")) == (100, 110)),
              ("feed UNAVAILABLE",
               lambda b: _g(b, "costs", "feed", "availability") == "UNAVAILABLE"),
              ("cost_completeness INCOMPLETE",
               lambda b: _g(b, "costs", "cost_completeness") == "INCOMPLETE"),
              ("profit_full_est_rp is null",
               lambda b: _g(b, "economics", "profit_full_est_rp") is None),
          ] + _supported_survival_checks(30) + _yield_unavailable_checks()),
    _case("B02", "Supported Tegel d=3",
          {"planting_system": "tegel"},
          [
              ("density_are == 3", lambda b: _close(_g(b, "operational", "density_are"), 3)),
              ("density SUPPORTED",
               lambda b: _g(b, "operational", "density_support") == "SUPPORTED"),
          ] + _supported_survival_checks(30)),
    _case("B03", "Jarwo upper supported boundary d=4",
          {"duck_count": 40},
          [
              ("density_are == 4", lambda b: _close(_g(b, "operational", "density_are"), 4)),
              ("density SUPPORTED",
               lambda b: _g(b, "operational", "density_support") == "SUPPORTED"),
          ] + _supported_survival_checks(40)),
    _case("B04", "Tegel above supported below limited band d=4 EXTRAPOLATION",
          {"duck_count": 40, "planting_system": "tegel"},
          [
              ("density EXTRAPOLATION (no penalty coefficient)",
               lambda b: _g(b, "operational", "density_support") == "EXTRAPOLATION"),
              ("survival UNAVAILABLE",
               lambda b: _g(b, "duck", "survival_availability") == "UNAVAILABLE"),
              ("N_survive null", lambda b: _g(b, "duck", "surviving_ducks") is None),
          ]),
    _case("B05", "Limited test d=5.5",
          {"duck_count": 55},
          [
              ("density LIMITED_TEST",
               lambda b: _g(b, "operational", "density_support") == "LIMITED_TEST"),
              ("survival UNAVAILABLE",
               lambda b: _g(b, "duck", "survival_availability") == "UNAVAILABLE"),
              ("N_survive null", lambda b: _g(b, "duck", "surviving_ducks") is None),
          ]),
    _case("B06", "High risk d=8 no 60% fallback",
          {"duck_count": 80},
          [
              ("density HIGH_RISK",
               lambda b: _g(b, "operational", "density_support") == "HIGH_RISK"),
              ("survival UNAVAILABLE",
               lambda b: _g(b, "duck", "survival_availability") == "UNAVAILABLE"),
              ("N_survive null", lambda b: _g(b, "duck", "surviving_ducks") is None),
              ("no 60% survival anywhere",
               lambda b: _g(b, "duck", "lambda_eff") is None),
          ]),
    _case("B07", "Age 20 CAUTION", {"duck_age_days": 20},
          [
              ("age CAUTION", lambda b: _g(b, "operational", "age_support") == "CAUTION"),
              ("survival UNAVAILABLE",
               lambda b: _g(b, "duck", "survival_availability") == "UNAVAILABLE"),
          ]),
    _case("B08", "Age 21 SUPPORTED boundary", {"duck_age_days": 21},
          [("age SUPPORTED",
            lambda b: _g(b, "operational", "age_support") == "SUPPORTED")]
          + _supported_survival_checks(30)),
    _case("B09", "Age 30 SUPPORTED boundary", {"duck_age_days": 30},
          [("age SUPPORTED",
            lambda b: _g(b, "operational", "age_support") == "SUPPORTED")]
          + _supported_survival_checks(30)),
    _case("B10", "Age 31 OUTSIDE_LOCAL_RANGE", {"duck_age_days": 31},
          [
              ("age OUTSIDE_LOCAL_RANGE",
               lambda b: _g(b, "operational", "age_support") == "OUTSIDE_LOCAL_RANGE"),
              ("survival UNAVAILABLE",
               lambda b: _g(b, "duck", "survival_availability") == "UNAVAILABLE"),
          ]),
    _case("B11", "Inpari calendar 90..100 not 109..116/134",
          {"rice_variety": "inpari"},
          [
              ("harvest HST 90..100",
               lambda b: (_g(b, "calendar", "harvest_hst_min"),
                          _g(b, "calendar", "harvest_hst_max")) == (90, 100)),
              ("not legacy 109..116/134",
               lambda b: (_g(b, "calendar", "harvest_hst_min"),
                          _g(b, "calendar", "harvest_hst_max"))
               not in ((109, 116), (134, 134))),
          ]),
    _case("B12", "Manual purchase price 30000 passthrough",
          {"duck_count": 30, "p_duck_buy": 30000},
          [
              ("effective == 30000",
               lambda b: _g(b, "input", "p_duck_buy_effective") == 30000.0),
              ("source USER_INPUT",
               lambda b: _g(b, "input", "p_duck_buy_source") == "USER_INPUT"),
              ("C_duck_buy == J*30000",
               lambda b: _close(_g(b, "costs", "duck_purchase", "amount_rp"),
                                30 * 30000)),
          ]),
    _case("B13", "Null purchase price default 26500",
          {"p_duck_buy": None},
          [
              ("effective == 26500",
               lambda b: _g(b, "input", "p_duck_buy_effective") == 26500.0),
              ("manual echo null",
               lambda b: _g(b, "input", "p_duck_buy_manual") is None),
          ]),
    _case("B14", "Invalid zero purchase price rejected",
          {"p_duck_buy": 0},
          []),  # zero is not R2 missing-value semantics -> HTTP 400
    _case("B15", "Missing yield lookup chain null", {},
          _yield_unavailable_checks()),
    _case("B16", "Fertilizer baseline identities (A=10)",
          {},
          [
              ("manure_credit_applied is False",
               lambda b: _g(b, "fertilizer_baseline", "manure_credit_applied")
               is False),
              ("nutrient basis N-P2O5-K2O",
               lambda b: _g(b, "fertilizer_baseline", "nutrient_basis")
               == "N-P2O5-K2O"),
              ("N_need == 1.1761*A",
               lambda b: _close(_g(b, "fertilizer_baseline", "n_need_kg"),
                                1.1761 * 10)),
              ("P2O5_need == 0.2745*A",
               lambda b: _close(_g(b, "fertilizer_baseline", "p2o5_need_kg"),
                                0.2745 * 10)),
              ("K2O_need == 0.2745*A",
               lambda b: _close(_g(b, "fertilizer_baseline", "k2o_need_kg"),
                                0.2745 * 10)),
              ("Q_npk == max(P2O5/.10, K2O/.12)",
               lambda b: _close(_g(b, "fertilizer_baseline", "q_npk_kg"),
                                max(2.745 / 0.10, 2.745 / 0.12))),
              ("Q_urea == max(0,(N-.15Qn)/.46)",
               lambda b: _close(
                   _g(b, "fertilizer_baseline", "q_urea_kg"),
                   max(0.0, (11.761 - 0.15 * 27.45) / 0.46))),
              ("C_fert == 1800*Qu + 1840*Qn",
               lambda b: _close(
                   _g(b, "fertilizer_baseline", "cost_total_rp"),
                   1800 * max(0.0, (11.761 - 0.15 * 27.45) / 0.46)
                   + 1840 * 27.45)),
          ]),
    _case("B17", "Net infrastructure range monotonic (A=10)", {},
          [
              ("L == 4*sqrt(100*A)",
               lambda b: _close(_g(b, "costs", "net_infrastructure",
                                   "equivalent_perimeter_m"),
                                4 * math.sqrt(1000))),
              ("min == L*6000/3",
               lambda b: _close(_g(b, "costs", "net_infrastructure",
                                   "cost_min_rp_per_cycle"),
                                4 * math.sqrt(1000) * 6000 / 3)),
              ("ref == L*6750/2.5",
               lambda b: _close(_g(b, "costs", "net_infrastructure",
                                   "cost_ref_rp_per_cycle"),
                                4 * math.sqrt(1000) * 6750 / 2.5)),
              ("max == L*6750/2",
               lambda b: _close(_g(b, "costs", "net_infrastructure",
                                   "cost_max_rp_per_cycle"),
                                4 * math.sqrt(1000) * 6750 / 2)),
              ("min <= ref <= max",
               lambda b: (
                   _g(b, "costs", "net_infrastructure", "cost_min_rp_per_cycle")
                   <= _g(b, "costs", "net_infrastructure", "cost_ref_rp_per_cycle")
                   <= _g(b, "costs", "net_infrastructure", "cost_max_rp_per_cycle")
               )),
          ]),
    _case("B18", "Terminal value is asset value, never cash revenue", {},
          [
              ("V_end_ref == N_survive*45000",
               lambda b: _close(_g(b, "duck", "terminal_value_ref_rp"),
                                math.floor(30 * 0.90) * 45000)),
              ("terminal_value_is_cash_revenue is False",
               lambda b: _g(b, "duck", "terminal_value_is_cash_revenue") is False),
              ("cash_revenue null while yield unavailable",
               lambda b: _g(b, "economics", "cash_revenue_rp") is None),
              ("sale_quantity_status UNAVAILABLE",
               lambda b: _g(b, "duck", "sale_quantity_status") == "UNAVAILABLE"),
          ]),
]


def run_synthetic_cases(client: TestClient | None = None) -> list[dict]:
    client = client or make_client()
    records: list[dict] = []
    for case in SYNTHETIC_CASES:
        response = client.post(f"{API}/dss/simulate", json=case.payload)
        body = response.json()
        status_ok = response.status_code == case.expected_status
        if case.case_id == "B14":
            body_ok = (
                isinstance(body, dict)
                and body.get("error", {}).get("code") == "validation_error"
            )
            observed_invariants = {"http_error_code": body.get("error", {}).get("code")}
            results = []
        else:
            results = []
            for desc, fn in case.checks:
                try:
                    ok = bool(fn(body))
                    results.append({"invariant": desc, "pass": ok})
                except Exception as exc:  # malformed shape counts as failure
                    results.append(
                        {"invariant": desc, "pass": False, "error": repr(exc)}
                    )
            body_ok = all(item["pass"] for item in results)
            observed_invariants = {
                "age_support": _g(body, "operational", "age_support"),
                "density_support": _g(body, "operational", "density_support"),
                "survival_availability": _g(body, "duck", "survival_availability"),
                "yield_availability": _g(body, "yield", "availability"),
                "feed_availability": _g(body, "costs", "feed", "availability"),
                "cost_completeness": _g(body, "costs", "cost_completeness"),
            }
        records.append(
            {
                "case_id": case.case_id,
                "title": case.title,
                "case_type": "SYNTHETIC",
                "request_json": case.payload,
                "expected_http_status": case.expected_status,
                "http_status": response.status_code,
                "raw_response_json": body,
                "observed_invariants": observed_invariants,
                "invariant_results": results,
                "pass": bool(status_ok and body_ok),
            }
        )
    return records


# ---------------------------------------------------------------------------
# Supported-age scenario invariance (task §16)
# ---------------------------------------------------------------------------

AGE_INVARIANCE_EXCLUDED_PATHS = {
    ("model", "generated_at"),   # wall-clock metadata
    ("input", "duck_age_days"),  # legitimate echo difference
}


def _prune(node: Any, prefix: tuple[str, ...] = ()) -> Any:
    if isinstance(node, dict):
        return {
            key: _prune(value, prefix + (key,))
            for key, value in node.items()
            if (prefix + (key,)) not in AGE_INVARIANCE_EXCLUDED_PATHS
        }
    if isinstance(node, list):
        return [_prune(item, prefix) for item in node]
    return node


def _diff_paths(a: Any, b: Any, prefix: tuple[str, ...] = ()) -> list[str]:
    diffs: list[str] = []
    if isinstance(a, dict) and isinstance(b, dict):
        for key in sorted(set(a) | set(b)):
            diffs.extend(_diff_paths(a.get(key), b.get(key), prefix + (key,)))
    elif a != b:
        diffs.append(".".join(prefix) or "<root>")
    return diffs


def run_age_invariance(client: TestClient | None = None) -> dict:
    """Numeric outputs must be identical for supported ages 21 vs 30."""
    client = client or make_client()
    payloads = {}
    raw_bodies = {}
    for age in (21, 30):
        payload = dict(BASE_PAYLOAD)
        payload["duck_age_days"] = age
        response = client.post(f"{API}/dss/simulate", json=payload)
        assert response.status_code == 200, response.text
        payloads[age] = payload
        raw_bodies[age] = response.json()
    pruned = {age: _prune(body) for age, body in raw_bodies.items()}
    differing = _diff_paths(pruned[21], pruned[30])
    return {
        "assumptions_days": [21, 30],
        "provenance": "VALIDATION_ASSUMPTION",
        "excluded_paths": [".".join(p) for p in sorted(AGE_INVARIANCE_EXCLUDED_PATHS)],
        "numeric_payloads_invariant": not differing,
        "differing_paths": differing,
        "requests": payloads,
        "raw_response_21": raw_bodies[21],
        "raw_response_30": raw_bodies[30],
        "pass": not differing,
    }


# ---------------------------------------------------------------------------
# Availability probe -- yield metrics derive from THIS state (task §23)
# ---------------------------------------------------------------------------


def probe_production_availability(client: TestClient | None = None) -> dict:
    client = client or make_client()
    body = client.post(f"{API}/dss/simulate", json=BASE_PAYLOAD).json()
    viz = client.post(f"{API}/dss/visualize", json=BASE_PAYLOAD).json()
    return {
        "model_frozen": body["model"]["frozen"],
        "freeze_id": body["model"]["freeze_id"],
        "parameter_registry_version": body["model"]["parameter_registry_version"],
        "yield_availability": body["yield"]["availability"],
        "yield_reason_codes": body["yield"]["reason_codes"],
        "feed_availability": body["costs"]["feed"]["availability"],
        "cage_total_amount_rp": body["costs"]["cage"]["total_amount_rp"],
        "cost_completeness": body["costs"]["cost_completeness"],
        "profit_full_status": body["economics"]["profit_full_status"],
        "terminal_value_is_cash_revenue": body["duck"][
            "terminal_value_is_cash_revenue"
        ],
        "visualization_yield_points_empty": viz["yield_series"]["points"] == [],
        "visualization_model_frozen": viz["model"]["frozen"],
    }


# ---------------------------------------------------------------------------
# Test-suite execution via pytest subprocess (task §3/§21)
# ---------------------------------------------------------------------------


def _run_pytest(args: list[str]) -> tuple[int, str]:
    proc = subprocess.run(
        [sys.executable, "-m", "pytest", *args],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    return proc.returncode, proc.stdout + proc.stderr


def parse_pytest_summary(output: str) -> dict:
    summary: dict[str, int] = {
        "collected": None,
        "passed": 0,
        "failed": 0,
        "skipped": 0,
        "xfailed": 0,
        "xpassed": 0,
        "errors": 0,
    }
    for line in output.splitlines():
        stripped = line.strip()
        if stripped.endswith("test(s) collected") or " tests collected" in stripped or (
            " test collected" in stripped
        ):
            try:
                summary["collected"] = int(stripped.split()[0])
            except (ValueError, IndexError):
                pass
        if ", " in stripped and ("passed" in stripped or "failed" in stripped):
            for token in stripped.split(","):
                parts = token.strip().split()
                if len(parts) >= 2 and parts[1] in (
                    "passed",
                    "failed",
                    "skipped",
                    "xfailed",
                    "xpassed",
                    "error",
                ):
                    key = "errors" if parts[1] == "error" else parts[1]
                    try:
                        summary[key] = int(parts[0])
                    except ValueError:
                        pass
    return summary


def run_full_active_suite() -> dict:
    rc_collect, out_collect = _run_pytest(["--collect-only", "-q"])
    rc_run, out_run = _run_pytest(["-q", "--tb=short"])
    summary = parse_pytest_summary(out_collect)
    collected = summary["collected"]
    summary = parse_pytest_summary(out_run)
    if collected is not None:
        summary["collected"] = collected
    summary.update(
        {
            "collect_exit_code": rc_collect,
            "run_exit_code": rc_run,
            "all_passed": rc_run == 0 and rc_collect == 0,
            "legacy_invalid_collected": "tests/legacy_invalid" in out_collect,
            "tail": "\n".join(out_run.strip().splitlines()[-3:]),
        }
    )
    return summary


# docs/06 section 19 V1 computational matrix -> active-test evidence files.
V1_MATRIX: tuple[dict, ...] = (
    {"id": "V1-01", "requirement": "A_m2 = 100*A_are",
     "files": ["tests/test_r2_normalization.py"]},
    {"id": "V1-02", "requirement": "d = J/A_are",
     "files": ["tests/test_r2_normalization.py"]},
    {"id": "V1-03", "requirement": "missing/null purchase price -> 26500",
     "files": ["tests/test_r2_normalization.py", "tests/test_r2_api_simulate.py"]},
    {"id": "V1-04", "requirement": "provided positive purchase price passes through",
     "files": ["tests/test_r2_normalization.py", "tests/test_r2_request_schema.py"]},
    {"id": "V1-05", "requirement": "0/NaN/Infinity purchase price rejected",
     "files": ["tests/test_r2_request_schema.py", "tests/test_r2_api_simulate.py"]},
    {"id": "V1-06", "requirement": "age support boundaries 20/21/30/31",
     "files": ["tests/test_r2_age_support.py"]},
    {"id": "V1-07", "requirement": "Jarwo density boundaries 2/4",
     "files": ["tests/test_r2_density_support.py"]},
    {"id": "V1-08", "requirement": "Tegel density boundaries 2/3",
     "files": ["tests/test_r2_density_support.py"]},
    {"id": "V1-09", "requirement": "limited/high-risk/extrapolation classification",
     "files": ["tests/test_r2_density_support.py"]},
    {"id": "V1-10", "requirement": "survival numeric only when both flags SUPPORTED",
     "files": ["tests/test_r2_survival.py"]},
    {"id": "V1-11", "requirement": "out-of-domain survival null/unavailable, not 60%",
     "files": ["tests/test_r2_survival.py", "tests/test_r2_api_simulate.py"]},
    {"id": "V1-12", "requirement": "calendar windows exact",
     "files": ["tests/test_r2_calendar.py"]},
    {"id": "V1-13", "requirement": "Inpari window 90-100 (not 109-116)",
     "files": ["tests/test_r2_calendar.py", "tests/test_r2_seed_registry.py"]},
    {"id": "V1-14", "requirement": "nutrient basis N-P2O5-K2O",
     "files": ["tests/test_r2_fertilizer.py"]},
    {"id": "V1-15", "requirement": "fertilizer solver constraints satisfied",
     "files": ["tests/test_r2_fertilizer.py"]},
    {"id": "V1-16", "requirement": "KCl branch unused",
     "files": ["tests/test_r2_fertilizer.py", "tests/test_r2_seed_registry.py"]},
    {"id": "V1-17", "requirement": "net min/ref/max monotonic",
     "files": ["tests/test_r2_infrastructure.py"]},
    {"id": "V1-18", "requirement": "feed numeric null while lookup unavailable",
     "files": ["tests/test_r2_availability_components.py"]},
    {"id": "V1-19", "requirement": "yield numeric null while lookup unavailable",
     "files": ["tests/test_r2_yield_engine.py"]},
    {"id": "V1-20", "requirement": "V_duck_end never cash duck sale revenue",
     "files": ["tests/test_r2_economics.py"]},
    {"id": "V1-21", "requirement": "Profit_full_est null while completeness INCOMPLETE",
     "files": ["tests/test_r2_economics.py"]},
    {"id": "V1-22", "requirement": "disabled legacy formulas unreachable from production",
     "files": ["tests/test_r2_production_path_static.py",
               "tests/test_r2_engines_static.py",
               "tests/test_r2_antilegacy_static.py"]},
)


def run_v1_matrix() -> dict:
    """Run every evidence file once; per-item pass derives from the shared run.

    A failing suite fails every item whose evidence could be implicated;
    failures are reported verbatim for investigation.
    """
    union_files: list[str] = []
    for item in V1_MATRIX:
        for f in item["files"]:
            if f not in union_files:
                union_files.append(f)
    rc, output = _run_pytest([*union_files, "-q", "--tb=short"])
    summary = parse_pytest_summary(output)
    suite_passed = rc == 0
    records = []
    for item in V1_MATRIX:
        records.append(
            {
                "id": item["id"],
                "requirement": item["requirement"],
                "expected": "all mapped active unit/API tests pass",
                "observed": {
                    "suite_exit_code": rc,
                    "suite_passed": suite_passed,
                    **summary,
                },
                "pass": suite_passed,
                "evidence_reference": item["files"],
            }
        )
    failed_tail = "\n".join(output.strip().splitlines()[-25:]) if not suite_passed else ""
    return {
        "protocol": "docs/06_R2_TEST_VALIDATION_PROTOCOL.md section 19",
        "items": records,
        "all_pass": suite_passed and all(r["pass"] for r in records),
        "failure_output_tail": failed_tail,
    }
