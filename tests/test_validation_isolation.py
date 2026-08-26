"""Phase 5: production/research isolation + anti-calibration static guards.

Enforces (task §7/§41, docs/07 section 6 analog for the validation package):

  * no module under ``app/`` imports the research-only ``validation`` package;
  * no production module pulls in XLSX/research dependencies (openpyxl);
  * the ``validation`` package never imports fitting/optimization stacks and
    never rebinds canonical seed/registry/freeze identifiers -- metrics may
    compute errors, but nothing in the harness writes model parameters.
"""

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP_DIR = ROOT / "app"
VALIDATION_DIR = ROOT / "validation"

# Canonical identifiers the research code must read but never rebind.
PROTECTED_IDENTIFIERS = {
    "MODEL_FROZEN",
    "FREEZE_ID",
    "FREEZE_EFFECTIVE_FROM",
    "MODEL_VERSION",
    "PARAMETER_REGISTRY",
    "PARAMETER_REGISTRY_VERSION",
    "RICE_VARIETIES",
    "PLANTING_SYSTEMS",
    "EFFECTIVE_FROM",
}

FORBIDDEN_VALIDATION_IMPORTS = (
    "sklearn",
    "scipy.optimize",
    "scipy",
    "torch",
    "tensorflow",
    "keras",
    "pandas",
    "numpy",
)

# Method names that would indicate model fitting/tuning inside the harness.
FORBIDDEN_CALL_ATTRS = {
    "fit",
    "fit_transform",
    "fit_predict",
    "minimize",
    "grid_search",
    "calibrate",
    "recalibrate",
    "optimize",
}


def _python_files(base: Path) -> list[Path]:
    return sorted(base.rglob("*.py"))


class TestProductionDoesNotImportResearch:
    def test_app_never_imports_validation_package(self) -> None:
        offenders: list[str] = []
        for path in _python_files(APP_DIR):
            tree = ast.parse(path.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        if alias.name == "validation" or alias.name.startswith(
                            "validation."
                        ):
                            offenders.append(f"{path.name}:{node.lineno}")
                elif isinstance(node, ast.ImportFrom):
                    if node.module == "validation" or (
                        node.module or ""
                    ).startswith("validation."):
                        offenders.append(f"{path.name}:{node.lineno}")
        assert offenders == [], f"app imports research package: {offenders}"

    def test_app_never_imports_xlsx_research_dependencies(self) -> None:
        offenders: list[str] = []
        for path in _python_files(APP_DIR):
            src = path.read_text(encoding="utf-8")
            for dep in ("openpyxl", "pandas", "numpy"):
                if f"import {dep}" in src or f"from {dep}" in src:
                    offenders.append(f"{path.name}: {dep}")
        assert offenders == []

    def test_pytest_never_collects_validation_dir(self) -> None:
        pytest_ini = (ROOT / "pytest.ini").read_text(encoding="utf-8")
        assert "testpaths = tests" in pytest_ini


class TestValidationHarnessStayedResearchOnly:
    def test_no_fitting_or_optimization_imports(self) -> None:
        offenders: list[str] = []
        for path in _python_files(VALIDATION_DIR):
            tree = ast.parse(path.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                modules: list[str] = []
                if isinstance(node, ast.Import):
                    modules = [alias.name for alias in node.names]
                elif isinstance(node, ast.ImportFrom) and node.module:
                    modules = [node.module]
                for module in modules:
                    root = module.split(".")[0]
                    full_prefix = tuple(module.split("."))
                    for banned in FORBIDDEN_VALIDATION_IMPORTS:
                        banned_parts = tuple(banned.split("."))
                        if root == banned_parts[0] and full_prefix[
                            : len(banned_parts)
                        ] == banned_parts:
                            offenders.append(f"{path.name}:{node.lineno} {module}")
        assert offenders == [], f"validation imports fitting stack: {offenders}"

    def test_no_fit_like_method_calls(self) -> None:
        offenders: list[str] = []
        for path in _python_files(VALIDATION_DIR):
            tree = ast.parse(path.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                if (
                    isinstance(node, ast.Call)
                    and isinstance(node.func, ast.Attribute)
                    and node.func.attr in FORBIDDEN_CALL_ATTRS
                ):
                    offenders.append(f"{path.name}:{node.lineno} .{node.func.attr}(")
        assert offenders == []

    def test_never_rebinds_canonical_seed_identifiers(self) -> None:
        offenders: list[str] = []
        for path in _python_files(VALIDATION_DIR):
            tree = ast.parse(path.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                if not isinstance(node, (ast.Assign, ast.AugAssign)):
                    continue
                targets = (
                    node.targets if isinstance(node, ast.Assign) else [node.target]
                )
                for target in targets:
                    if isinstance(target, ast.Name) and target.id in PROTECTED_IDENTIFIERS:
                        offenders.append(f"{path.name}:{node.lineno} {target.id}")
                    elif (
                        isinstance(target, ast.Attribute)
                        and target.attr in PROTECTED_IDENTIFIERS
                    ):
                        offenders.append(
                            f"{path.name}:{node.lineno} .{target.attr}"
                        )
        assert offenders == [], f"harness mutates model identity: {offenders}"

    def test_no_setattr_against_production_modules(self) -> None:
        offenders: list[str] = []
        for path in _python_files(VALIDATION_DIR):
            tree = ast.parse(path.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                if (
                    isinstance(node, ast.Call)
                    and isinstance(node.func, ast.Name)
                    and node.func.id == "setattr"
                ):
                    offenders.append(f"{path.name}:{node.lineno} setattr(")
        assert offenders == []
