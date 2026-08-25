"""Phase 2: static anti-regression + import boundary for app/engines/r2.

docs/07_R2_LEGACY_INVALIDATION_REGISTER.md section 5-6:
  * banned scientific identifiers/constants must not live in production paths;
  * R2 engine modules must not import the invalidated legacy engines.

Numeric tokens use digit/decimal boundaries so legitimate values that merely
contain the digits (e.g. cage range 200000 vs banned feed shortcut 20000) do
not false-positive -- the context-aware approach recommended by docs/07.
"""

import ast
import re
from pathlib import Path

import pytest

APP_DIR = Path(__file__).resolve().parents[1] / "app"
R2_DIR = APP_DIR / "engines" / "r2"

# Banned identifiers / aggregates (plain substring match, case-sensitive).
BANNED_IDENTIFIERS = [
    "R_age",
    "P_over",
    "P_under",
    "F_age",
    "F_density_bio",
    "alpha_bio",
    "beta_tramp",
    "Revenue_duck_potential",
    "Total_Revenue_DSS",
    "Net_Cash_Contribution_DSS",
    "Profit_net_cash",
    "Core_Cash_Cost",
    "Cost_feed_isolated",
    "Yield_are_pred",
    "Yield_total_pred",
    # Point-calendar legacy names.
    "HST_IN",
    "HST_OUT",
    "T_ACTIVE",
]

# Banned numeric constants (boundary-aware so embedded substrings do not fire).
BANNED_NUMBERS = [
    "47.8767507",  # recap-derived yield baseline
    "0.78125",     # recap-derived survival ceiling
    "289260",      # infrastructure regression coefficient
    "1.211",       # system multiplier from clean recap
    "52500",       # duck potential sale price
    "20000",       # fixed feed shortcut
    "4500",        # legacy feed base formula constant
    "9500",        # KCl regulatory assumption
    "21000",       # weeding sandbox base
    "4830",        # weeding residual split
    "16170",       # weeding avoided split
    "109",         # invalidated harvest window edge
    "116",         # invalidated harvest window edge
    "134",         # invalidated harvest HST variant
]


def r2_sources() -> dict[Path, str]:
    files = sorted(R2_DIR.rglob("*.py"))
    return {path: path.read_text(encoding="utf-8") for path in files}


def test_r2_package_modules_exist() -> None:
    """Guard against silent scan shrinkage if modules are removed."""
    files = sorted(R2_DIR.rglob("*.py"))
    assert len(files) >= 10, f"expected >=10 R2 engine modules, found {len(files)}"
    expected = {
        "__init__.py",
        "common.py",
        "config.py",
        "normalization.py",
        "support.py",
        "calendar.py",
        "survival.py",
        "yield_engine.py",
        "fertilizer.py",
        "infrastructure.py",
        "availability.py",
        "economics.py",
    }
    assert {p.name for p in files} == expected


@pytest.mark.parametrize("path", sorted(R2_DIR.rglob("*.py")), ids=lambda p: p.name)
class TestNoBannedLegacySemantics:
    def test_no_banned_identifiers(self, path: Path) -> None:
        src = path.read_text(encoding="utf-8")
        for token in BANNED_IDENTIFIERS:
            assert token not in src, (
                f"{path.name}: banned legacy identifier '{token}' found in R2 engine"
            )

    def test_no_banned_numeric_constants(self, path: Path) -> None:
        src = path.read_text(encoding="utf-8")
        for number in BANNED_NUMBERS:
            pattern = re.compile(rf"(?<![\d.]){re.escape(number)}(?![\d.])")
            match = pattern.search(src)
            assert match is None, (
                f"{path.name}: banned legacy constant '{number}' found in R2 engine"
            )


# ---------------------------------------------------------------------------
# Import boundary
# ---------------------------------------------------------------------------

FORBIDDEN_IMPORT_ROOTS = (
    "app.engines.formula_engine",
    "app.engines.impact_engine",
    "app.services",
    "app.api",
    "app.repositories",
)

ALLOWED_APP_MODULES_EXACT = {
    "app.domain.models",
    "app.data.seed",
}
R2_PACKAGE_PREFIX = "app.engines.r2"
SCHEMAS_ALLOWED_NAMES = {"ReasonCode"}
SCHEMAS_MODULE = "app.schemas.dss"


def _iter_app_imports(tree: ast.AST):
    """Yield (module_name, alias_names, node) for absolute imports."""
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            if node.level:  # relative import: intra-package by construction
                continue
            yield node.module, [alias.name for alias in node.names], node
        elif isinstance(node, ast.Import):
            for alias in node.names:
                yield alias.name, None, node


@pytest.mark.parametrize("path", sorted(R2_DIR.rglob("*.py")), ids=lambda p: p.name)
def test_import_boundary(path: Path) -> None:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    for module, names, node in _iter_app_imports(tree):
        if not module.startswith("app"):
            continue  # stdlib / third-party allowed
        for forbidden in FORBIDDEN_IMPORT_ROOTS:
            assert not module.startswith(forbidden), (
                f"{path.name}: forbidden import '{module}' "
                f"(line {node.lineno}); R2 engines must not depend on legacy "
                "engines, services, API layer, or repositories"
            )
        if module.startswith(R2_PACKAGE_PREFIX):
            continue  # intra-package
        if module in ALLOWED_APP_MODULES_EXACT:
            continue
        if module == SCHEMAS_MODULE:
            assert names is not None and set(names) <= SCHEMAS_ALLOWED_NAMES, (
                f"{path.name}: only ReasonCode may be imported from the schema "
                f"contract module; got {names}"
            )
            continue
        pytest.fail(
            f"{path.name}: unexpected app import '{module}' (line {node.lineno})"
        )


# ---------------------------------------------------------------------------
# Reason-code vocabulary consistency with the canonical contract enum
# ---------------------------------------------------------------------------


def test_engine_reason_codes_subset_of_contract_enum() -> None:
    from app.schemas.dss import ReasonCode

    contract_values = {member.value for member in ReasonCode}
    referenced: set[str] = set()
    pattern = re.compile(r"ReasonCode\.([A-Z_]+)")
    for path, _src in r2_sources().items():
        for match in pattern.finditer(path.read_text(encoding="utf-8")):
            referenced.add(ReasonCode[match.group(1)].value)
    assert referenced and referenced <= contract_values


def test_production_tree_defines_no_other_yield_store_implementation() -> None:
    """Only EmptyYieldLookupStore may implement the store protocol in app/."""
    offenders: list[str] = []
    for py_file in sorted(APP_DIR.rglob("*.py")):
        rel = py_file.relative_to(APP_DIR).as_posix()
        if rel.startswith("engines/r2/yield_engine.py"):
            continue
        try:
            tree = ast.parse(py_file.read_text(encoding="utf-8"))
        except SyntaxError:
            continue  # intentionally broken pre-R2 service modules stay broken
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                base_names = {
                    getattr(base, "id", getattr(base, "attr", ""))
                    for base in node.bases
                }
                if "YieldLookupStore" in base_names and node.name != "EmptyYieldLookupStore":
                    offenders.append(f"{rel}:{node.name}")
    assert offenders == [], f"unexpected populated lookup stores in production: {offenders}"
