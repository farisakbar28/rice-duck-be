"""Phase 2: calendar windows engine -- both varieties, leap/rollover edges."""

import dataclasses
from datetime import date

import pytest

from app.data.seed import RICE_VARIETIES
from app.domain.models import RiceVariety
from app.engines.r2.calendar import CalendarWindows, compute_calendar_windows
from app.engines.r2.config import load_default_config
from app.repositories.lookup_repository import lookup_repository

SERTANI = next(v for v in RICE_VARIETIES if v.code == "sertani")
INPARI = next(v for v in RICE_VARIETIES if v.code == "inpari")


@pytest.fixture(scope="module")
def config():
    return load_default_config()


class TestSertaniWindows:
    def test_contract_reference_case(self, config) -> None:
        """docs/03 contract example: planting 2026-06-01."""
        windows = compute_calendar_windows(date(2026, 6, 1), SERTANI, config)
        assert (windows.release_hst_min, windows.release_hst_max) == (21, 30)
        assert windows.release_date_min == date(2026, 6, 22)
        assert windows.release_date_max == date(2026, 7, 1)
        assert (windows.pull_hst_min, windows.pull_hst_max) == (56, 60)
        assert windows.pull_date_min == date(2026, 7, 27)
        assert windows.pull_date_max == date(2026, 7, 31)
        assert (windows.harvest_hst_min, windows.harvest_hst_max) == (100, 110)
        assert windows.harvest_date_min == date(2026, 9, 9)
        assert windows.harvest_date_max == date(2026, 9, 19)

    def test_active_duration_independent_values(self, config) -> None:
        windows = compute_calendar_windows(date(2026, 6, 1), SERTANI, config)
        assert windows.active_duration_ref_days == 32
        assert windows.active_duration_support_min_days == 28
        assert windows.active_duration_support_max_days == 40


class TestInpariWindows:
    def test_harvest_window_is_90_100(self, config) -> None:
        windows = compute_calendar_windows(date(2026, 6, 1), INPARI, config)
        assert (windows.harvest_hst_min, windows.harvest_hst_max) == (90, 100)
        # Regression guard: the invalidated window must never appear.
        assert windows.harvest_hst_min < 100
        assert windows.harvest_date_min == date(2026, 8, 30)
        assert windows.harvest_date_max == date(2026, 9, 9)

    def test_release_pull_shared_with_sertani(self, config) -> None:
        windows = compute_calendar_windows(date(2026, 6, 1), INPARI, config)
        assert windows.release_date_min == date(2026, 6, 22)
        assert windows.pull_date_max == date(2026, 7, 31)


class TestDateBoundaries:
    def test_leap_year_planting(self, config) -> None:
        """2024-02-27 + HST offsets across Feb 29."""
        windows = compute_calendar_windows(date(2024, 2, 27), SERTANI, config)
        assert windows.release_date_min == date(2024, 3, 19)
        assert windows.release_date_max == date(2024, 3, 28)
        assert windows.pull_date_min == date(2024, 4, 23)
        assert windows.pull_date_max == date(2024, 4, 27)
        assert windows.harvest_date_min == date(2024, 6, 6)
        assert windows.harvest_date_max == date(2024, 6, 16)

    def test_year_rollover_non_leap_target_year(self, config) -> None:
        """2026-12-01 planting; harvest lands after Feb of non-leap 2027."""
        windows = compute_calendar_windows(date(2026, 12, 1), INPARI, config)
        assert windows.release_date_max == date(2026, 12, 31)
        assert windows.pull_date_min == date(2027, 1, 26)
        assert windows.pull_date_max == date(2027, 1, 30)
        assert windows.harvest_date_min == date(2027, 3, 1)
        assert windows.harvest_date_max == date(2027, 3, 11)


class TestFailExplicit:
    def test_unknown_variety_raises_never_defaults(self, config) -> None:
        with pytest.raises(ValueError):
            compute_calendar_windows(date(2026, 6, 1), None, config)

    def test_repository_returns_none_for_unknown_code(self) -> None:
        """The explicit failure point lives at lookup resolution."""
        assert lookup_repository.get_rice_variety("unknown_variety") is None


class TestWindowShape:
    def test_no_point_calendar_fields_exist(self, config) -> None:
        windows = compute_calendar_windows(date(2026, 6, 1), SERTANI, config)
        names = {f.name for f in dataclasses.fields(CalendarWindows)}
        for banned_point_field in ("hst_in", "hst_out", "t_active", "d_in", "d_out"):
            assert banned_point_field not in names
        # Windows only: release/pull are ranges with two dates each.
        assert isinstance(windows, CalendarWindows)
