"""Phase 1: static anti-regression scan over active R2 foundation code.

docs/07_R2_LEGACY_INVALIDATION_REGISTER.md section 5: banned scientific
identifiers must not live in production paths. This scan covers the Phase-1
foundation files only; engines/services are later-phase rewrites and are
deliberately out of scope here.

Numeric tokens are matched with digit/decimal boundaries so legitimate
values that merely contain the digits (e.g. cage range 200000 vs banned
feed 20000) do not false-positive -- the context-aware approach recommended
by docs/07 section 5.
"""

import re
from pathlib import Path

import pytest

APP_DIR = Path(__file__).resolve().parents[1] / "app"
SCAN_FILES = [
    APP_DIR / "schemas" / "dss.py",
    APP_DIR / "domain" / "models.py",
    APP_DIR / "data" / "seed.py",
    APP_DIR / "repositories" / "lookup_repository.py",
]

# Banned identifiers / aggregates (plain substring match).
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
    "Cost_feed_isolated",
    "Core_Cash_Cost",
    "Yield_are_pred",
    "Yield_total_pred",
    # Banned provenance/status labels (exact token, hyphen-prefixed forms of
    # *locked are handled separately below).
    "local-validated",
    "local-calculated",
    "local-empirical-reference",
    "hardware-locked",
    "system-neutral-SoT",
]

# Banned numeric constants (boundary-aware so embedded substrings don't fire).
BANNED_NUMBERS = [
    "47.8767507",  # recap-derived yield baseline (LEG-Y0-478767507)
    "0.78125",     # recap-derived survival ceiling (LEG-LAMBDA-078125)
    "289260",      # infrastructure regression coefficient (LEG-INFRA-289260)
    "1.211",       # F_sys Tegel multiplier (LEG-FSYS-1211)
    "52500",       # duck potential sale price (LEG-DUCKSELL-52500)
    "20000",       # fixed feed cost shortcut (LEG-FEED-20000)
    "4500",        # legacy feed base formula constant (LEG-FEED-4500)
    "9500",        # KCl regulatory assumption (LEG-KCL-9500)
]

# Standalone word 'locked' is a banned status label; 'regulatory-locked' is canonical.
BANNED_LOCKED_LABEL = re.compile(r"(?<![-\w])locked(?![\w])")


def _sources() -> dict[Path, str]:
    return {path: path.read_text(encoding="utf-8") for path in SCAN_FILES}


@pytest.mark.parametrize("path", SCAN_FILES, ids=[p.name for p in SCAN_FILES])
class TestNoBannedLegacySemantics:
    def test_no_banned_identifiers(self, path: Path) -> None:
        src = _sources()[path]
        for token in BANNED_IDENTIFIERS:
            assert token not in src, (
                f"{path.name}: banned legacy identifier '{token}' found in active R2 code"
            )

    def test_no_banned_numeric_constants(self, path: Path) -> None:
        src = _sources()[path]
        for number in BANNED_NUMBERS:
            pattern = re.compile(rf"(?<![\d.]){re.escape(number)}(?![\d.])")
            match = pattern.search(src)
            assert match is None, (
                f"{path.name}: banned legacy constant '{number}' found in active R2 code"
            )

    def test_standalone_locked_label_absent(self, path: Path) -> None:
        src = _sources()[path]
        match = BANNED_LOCKED_LABEL.search(src)
        assert match is None, (
            f"{path.name}: standalone 'locked' status label found "
            "(only 'regulatory-locked' provenance is canonical)"
        )


def test_scan_targets_exist() -> None:
    """Guard against silent scan shrinkage if files move."""
    for path in SCAN_FILES:
        assert path.exists(), f"missing scan target: {path}"
