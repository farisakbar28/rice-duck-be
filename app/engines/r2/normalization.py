"""R2 input normalization engine (registry R2-NORM-01, R2-DEN-01, R2-PRICE-01).

Pure functions only:
    A_m2 = 100 * A_are
    d    = J / A_are
    p_duck_buy_eff = manual if supplied else registry default (26,500)

The default price is read from the injected config (canonical registry), never
hardcoded here. No schema validation is duplicated: the API layer already
guarantees area > 0, count > 0 and a supplied price > 0; zero is not treated
as "missing" anywhere in this engine.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from app.domain.models import LocalCultivarGroup, PurchasePriceSource
from app.engines.r2.common import high_precision, to_decimal
from app.engines.r2.config import R2EngineConfig


@dataclass(frozen=True)
class NormalizedInputs:
    """Effective derived inputs shared by every downstream engine."""

    land_area_are: Decimal
    duck_count: int
    area_m2: Decimal
    density_are: Decimal
    purchase_price_manual: Decimal | None
    purchase_price_effective: Decimal
    purchase_price_source: PurchasePriceSource


# Closed evidence boundary: exact aliases only after harmless whitespace/case
# normalization. Deliberately no substring, edit-distance, prefix, or fuzzy
# matching.
_CULTIVAR_GROUP_ALIASES = {
    "sertani": LocalCultivarGroup.SERTANI_GROUP,
    "sertani 13": LocalCultivarGroup.SERTANI_GROUP,
    "sertani a 13": LocalCultivarGroup.SERTANI_GROUP,
    "seratih": LocalCultivarGroup.SERTANI_GROUP,
    "inpari": LocalCultivarGroup.INPARI_GROUP,
    "inpari 32": LocalCultivarGroup.INPARI_GROUP,
}


def normalize_cultivar_group_label(
    label: str | None,
) -> LocalCultivarGroup | None:
    """Resolve only explicitly approved local cultivar labels.

    Surrounding whitespace and character case are formatting differences, not
    aliases. Internal whitespace is otherwise preserved, so unapproved near
    matches fail closed.
    """

    if not isinstance(label, str):
        return None
    return _CULTIVAR_GROUP_ALIASES.get(label.strip().casefold())


def normalize_inputs(
    *,
    land_area_are: float | int | str | Decimal,
    duck_count: int,
    p_duck_buy_manual: float | int | str | Decimal | None,
    config: R2EngineConfig,
) -> NormalizedInputs:
    area = to_decimal(land_area_are)
    count = int(duck_count)
    manual = None if p_duck_buy_manual is None else to_decimal(p_duck_buy_manual)

    if manual is None:
        effective = config.p_duck_buy_default
        source = PurchasePriceSource.LOCAL_DEFAULT_MIDPOINT
    else:
        effective = manual
        source = PurchasePriceSource.USER_INPUT

    with high_precision():
        area_m2 = config.area_m2_per_are * area
        density = to_decimal(count) / area

    return NormalizedInputs(
        land_area_are=area,
        duck_count=count,
        area_m2=area_m2,
        density_are=density,
        purchase_price_manual=manual,
        purchase_price_effective=effective,
        purchase_price_source=source,
    )
