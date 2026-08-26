"""R2 production-path anti-regression + import boundary.

Scope (docs/07 section 5-6): the reachable R2 core path must have NO
import/call dependency on the invalidated legacy engines and must not carry
banned legacy identifiers/constants. Legacy v3 column names inside the
isolated legacy handling of ``history_repository`` / the marked legacy region
of ``database.py`` are allowed; everything else in the scanned set is clean.
"""

import ast
import re
from pathlib import Path

APP_DIR = Path(__file__).resolve().parents[1] / "app"

# Reachable R2 core production path (task section 37).
SCANNED_FILES = [
    APP_DIR / "api" / "routes" / "dss.py",
    APP_DIR / "services" / "simulation_service.py",
    APP_DIR / "services" / "visualization_service.py",
    APP_DIR / "repositories" / "history_repository.py",
    APP_DIR / "core" / "database.py",
    APP_DIR / "schemas" / "dss.py",
    APP_DIR / "domain" / "models.py",
    APP_DIR / "data" / "seed.py",
]

FORBIDDEN_IMPORT_MODULES = (
    "app.engines.formula_engine",
    "app.engines.impact_engine",
)

# CamelCase invalidated aggregates/fields -- never legitimate anywhere in the
# scanned production set (legacy storage uses snake_case names, which stay
# confined to the isolated legacy mapper).
BANNED_IDENTIFIERS = [
    "Revenue_duck_potential",
    "Total_Revenue_DSS",
    "Net_Cash_Contribution_DSS",
    "Profit_net_cash",
    "Core_Cash_Cost",
    "Cost_feed_isolated",
    "Yield_are_pred",
    "Yield_total_pred",
    "HST_IN",
    "HST_OUT",
    "T_ACTIVE",
    "F_age",
    "F_density_bio",
    "alpha_bio",
    "beta_tramp",
]

# Banned only in the R2 service module (the orchestrator must not call or
# reimplement these legacy entry points).
BANNED_IN_SERVICE = [
    "compute_core_economics",
    "compute_sandbox_",
    "compute_surviving_ducks",
    "get_constants",
    "create_v3",
    "formula_engine",
    "impact_engine",
    "Y_BASE",
]

BANNED_NUMBERS = [
    "47.8767507",  # recap-derived fixed yield
    "0.78125",     # recap-derived survival ceiling
    "289260",      # infrastructure regression coefficient
    "1.211",       # system multiplier from clean recap
    "52500",       # duck potential sale price
    "9500",        # KCl regulatory assumption
]

LEGACY_REGION_MARKERS = (
    "# legacy-compat-region: v3 columns (do not scan numerics) -- START",
    "# legacy-compat-region: v3 columns -- END",
)


def _source(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _numeric_scan_source(path: Path) -> str:
    """Source with the explicitly marked legacy-compat region removed."""
    src = _source(path)
    start = src.find(LEGACY_REGION_MARKERS[0])
    if start == -1:
        return src
    end = src.find(LEGACY_REGION_MARKERS[1], start)
    assert end != -1, f"{path.name}: legacy region end marker missing"
    return src[:start] + src[end + len(LEGACY_REGION_MARKERS[1]):]


def _module_name(path: Path) -> str:
    rel = path.relative_to(APP_DIR).with_suffix("")
    parts = list(rel.parts)
    if parts[-1] == "__init__":
        parts = parts[:-1]
    return ".".join(["app"] + parts)


def _module_path(module: str) -> Path | None:
    parts = module.split(".")
    if parts and parts[0] == "app":
        parts = parts[1:]
    if not parts:
        return APP_DIR / "__init__.py"
    candidate = APP_DIR.joinpath(*parts).with_suffix(".py")
    if candidate.exists():
        return candidate
    candidate = APP_DIR.joinpath(*parts) / "__init__.py"
    if candidate.exists():
        return candidate
    return None


def _app_imports(tree: ast.AST) -> set[str]:
    modules: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module and node.module.startswith("app"):
            modules.add(node.module)
        elif isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.startswith("app"):
                    modules.add(alias.name)
    return modules


# ---------------------------------------------------------------------------
# Direct bans
# ---------------------------------------------------------------------------


def test_scanned_files_exist() -> None:
    for path in SCANNED_FILES:
        assert path.exists(), f"missing production file: {path}"


def test_no_forbidden_imports_in_production_path() -> None:
    for path in SCANNED_FILES:
        tree = ast.parse(_source(path))
        imported = _app_imports(tree)
        # history_repository legitimately imports nothing forbidden; check all.
        for module in imported:
            for forbidden in FORBIDDEN_IMPORT_MODULES:
                assert not module.startswith(forbidden), (
                    f"{path.name}: forbidden import '{module}'"
                )


def test_reachability_from_route_excludes_legacy_engines() -> None:
    """BFS over app-internal imports starting at the DSS route module."""
    start = "app.api.routes.dss"
    visited: set[str] = set()
    queue = [start]
    while queue:
        module = queue.pop()
        if module in visited:
            continue
        visited.add(module)
        path = _module_path(module)
        assert path is not None, f"unresolvable module on route graph: {module}"
        queue.extend(_app_imports(ast.parse(_source(path))) - visited)

    for banned in FORBIDDEN_IMPORT_MODULES:
        reachable = {m for m in visited if m.startswith(banned)}
        assert not reachable, f"legacy engine reachable from /dss routes: {reachable}"

    # Both R2 services may import only the canonical R2 engine package.
    for service_name in ("simulation_service.py", "visualization_service.py"):
        service_imports = _app_imports(
            ast.parse(_source(APP_DIR / "services" / service_name))
        )
        engine_imports = {m for m in service_imports if m.startswith("app.engines")}
        assert engine_imports <= {"app.engines.r2"}, engine_imports


def test_no_banned_identifiers_anywhere_in_production_path() -> None:
    for path in SCANNED_FILES:
        src = _source(path)
        for token in BANNED_IDENTIFIERS:
            assert token not in src, f"{path.name}: banned identifier '{token}'"


def test_service_has_no_legacy_call_surface() -> None:
    src = _source(APP_DIR / "services" / "simulation_service.py")
    for token in BANNED_IN_SERVICE:
        assert token not in src, f"simulation_service.py: banned token '{token}'"


def test_no_banned_numeric_constants_outside_legacy_region() -> None:
    for path in SCANNED_FILES:
        src = _numeric_scan_source(path)
        for number in BANNED_NUMBERS:
            # The leading '-' exclusion keeps documented legacy formula IDs
            # (e.g. the disabled-LEG register entry containing 289260) from
            # tripping the numeric scan; those strings are invalidation
            # metadata, not scientific constants.
            pattern = re.compile(rf"(?<![\d_.\-]){re.escape(number)}(?![\d.])")
            match = pattern.search(src)
            assert match is None, f"{path.name}: banned constant '{number}'"


def test_no_point_calendar_assignments() -> None:
    """AST-level guard: no HST_OUT=65-style point-calendar constants anywhere."""
    for path in SCANNED_FILES:
        tree = ast.parse(_source(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    name = getattr(target, "id", "")
                    value = getattr(node.value, "value", None)
                    if name in ("HST_OUT", "hst_out_default") and value == 65:
                        pytest_fail(path, node)
                    if name in ("T_ACTIVE", "t_active_default") and value == 44:
                        pytest_fail(path, node)


def pytest_fail(path: Path, node: ast.AST) -> None:  # pragma: no cover
    raise AssertionError(f"{path.name}: legacy point-calendar assignment at line {node.lineno}")


# ---------------------------------------------------------------------------
# Isolation guards
# ---------------------------------------------------------------------------


def test_visualize_endpoint_is_registered() -> None:
    from fastapi.testclient import TestClient

    from app.main import app

    client = TestClient(app)
    openapi = client.get("/openapi.json").json()
    dss_paths = [p for p in openapi["paths"] if p.startswith("/api/v1/dss")]
    assert "/api/v1/dss/visualize" in dss_paths


def test_optimizer_stays_isolated_from_r2_core() -> None:
    optimizer_files = [
        APP_DIR / "api" / "routes" / "optimizer.py",
        APP_DIR / "schemas" / "optimizer.py",
    ]
    for path in optimizer_files:
        imported = _app_imports(ast.parse(_source(path)))
        banned_roots = (
            "app.services",
            "app.engines",
            "app.schemas.dss",
            "app.repositories",
        )
        for module in imported:
            for root in banned_roots:
                assert not module.startswith(root), (
                    f"{path.name}: optimizer must stay isolated; found '{module}'"
                )
