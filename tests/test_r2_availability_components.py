"""Phase 2: feed / weeding / pest availability semantics -- missing is not zero."""

from decimal import Decimal

import pytest

from app.domain.models import AvailabilityStatus, ComponentAvailability
from app.engines.r2.availability import FEED_REASON_CODES, compute_feed_cost, compute_pest_effect, compute_weeding_baseline
from app.engines.r2.config import load_default_config
from app.schemas.dss import ReasonCode


@pytest.fixture(scope="module")
def config():
    return load_default_config()


class TestFeed:
    def test_unavailable_with_both_reason_codes(self, config) -> None:
        result = compute_feed_cost(config)
        assert result.availability is AvailabilityStatus.UNAVAILABLE
        assert result.reason_codes == (
            ReasonCode.FEED_QUANTITY_LOOKUP_MISSING,
            ReasonCode.FEED_PRICE_LOOKUP_MISSING,
        )

    def test_amount_is_none_not_zero(self, config) -> None:
        assert compute_feed_cost(config).amount_rp is None

    def test_reason_codes_match_module_constant(self, config) -> None:
        assert compute_feed_cost(config).reason_codes == FEED_REASON_CODES


class TestWeeding:
    def test_area_seven_baseline_range(self, config) -> None:
        result = compute_weeding_baseline(7, config)
        assert result.baseline_min_rp == Decimal("42000")
        assert result.baseline_max_rp == Decimal("266000")

    def test_area_one_and_half(self, config) -> None:
        result = compute_weeding_baseline(Decimal("1.5"), config)
        assert result.baseline_min_rp == Decimal("9000")
        assert result.baseline_max_rp == Decimal("57000")

    def test_availability_is_baseline_range_only(self, config) -> None:
        result = compute_weeding_baseline(7, config)
        assert result.availability is ComponentAvailability.BASELINE_RANGE_ONLY

    def test_saving_is_never_monetized(self, config) -> None:
        """No suppression percentage is converted into money."""
        assert compute_weeding_baseline(7, config).saving_rp is None


class TestPest:
    def test_effect_is_context_specific_descriptor(self, config) -> None:
        result = compute_pest_effect(config)
        assert result.effect == "CONTEXT_SPECIFIC"

    def test_saving_is_none(self, config) -> None:
        assert compute_pest_effect(config).saving_rp is None

    def test_no_universal_scalar_field(self, config) -> None:
        import dataclasses

        names = {f.name for f in dataclasses.fields(type(compute_pest_effect(config)))}
        assert names == {"effect", "saving_rp"}
