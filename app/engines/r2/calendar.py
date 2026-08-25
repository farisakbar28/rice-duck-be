"""R2 calendar engine (registry R2-CAL-01 .. R2-CAL-05).

The calendar returns WINDOWS, never false-precision point estimates:
    release  [D_tanam + 21, D_tanam + 30]
    pull     [D_tanam + 56, D_tanam + 60]
    harvest  [D_tanam + V_min, D_tanam + V_max]   (from the variety lookup)
    active duration reference 32 days, support interval [28, 40]

The reference duration is independently documented; it is NOT derived from
any release/pull pairing. An unresolved variety fails explicitly -- it is
never silently replaced by another variety.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta

from app.domain.models import RiceVariety
from app.engines.r2.config import R2EngineConfig


@dataclass(frozen=True)
class CalendarWindows:
    release_hst_min: int
    release_hst_max: int
    release_date_min: date
    release_date_max: date

    pull_hst_min: int
    pull_hst_max: int
    pull_date_min: date
    pull_date_max: date

    harvest_hst_min: int
    harvest_hst_max: int
    harvest_date_min: date
    harvest_date_max: date

    active_duration_ref_days: int
    active_duration_support_min_days: int
    active_duration_support_max_days: int


def compute_calendar_windows(
    planting_date: date,
    variety: RiceVariety | None,
    config: R2EngineConfig,
) -> CalendarWindows:
    if variety is None:
        raise ValueError(
            "Rice variety lookup unresolved; refusing to fall back to any "
            "default variety (fail-closed calendar)."
        )
    return CalendarWindows(
        release_hst_min=config.release_hst_min,
        release_hst_max=config.release_hst_max,
        release_date_min=planting_date + timedelta(days=config.release_hst_min),
        release_date_max=planting_date + timedelta(days=config.release_hst_max),
        pull_hst_min=config.pull_hst_min,
        pull_hst_max=config.pull_hst_max,
        pull_date_min=planting_date + timedelta(days=config.pull_hst_min),
        pull_date_max=planting_date + timedelta(days=config.pull_hst_max),
        harvest_hst_min=variety.harvest_hst_min,
        harvest_hst_max=variety.harvest_hst_max,
        harvest_date_min=planting_date + timedelta(days=variety.harvest_hst_min),
        harvest_date_max=planting_date + timedelta(days=variety.harvest_hst_max),
        active_duration_ref_days=config.active_duration_ref_days,
        active_duration_support_min_days=config.active_duration_support_min_days,
        active_duration_support_max_days=config.active_duration_support_max_days,
    )
