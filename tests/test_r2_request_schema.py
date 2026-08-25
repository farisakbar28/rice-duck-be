"""Phase 1: R2 request schema contract (docs/03_R2_API_CONTRACT.md section 3)."""

import math

import pytest
from pydantic import ValidationError

from app.schemas.dss import DSSSimulationRequest


def valid_payload(**overrides: object) -> dict:
    value = {
        "land_area_are": 7,
        "duck_count": 28,
        "planting_date": "2026-06-01",
        "planting_system": "jajar_legowo",
        "rice_variety": "sertani",
        "duck_age_days": 30,
    }
    value.update(overrides)
    return value


class TestPurchasePriceOptionality:
    def test_missing_p_duck_buy_is_accepted(self) -> None:
        req = DSSSimulationRequest(**valid_payload())
        assert req.p_duck_buy is None

    def test_explicit_null_p_duck_buy_is_accepted(self) -> None:
        req = DSSSimulationRequest(**valid_payload(p_duck_buy=None))
        assert req.p_duck_buy is None

    @pytest.mark.parametrize("price", [0.01, 15000, 26500, 30000])
    def test_positive_price_passes_through(self, price: float) -> None:
        req = DSSSimulationRequest(**valid_payload(p_duck_buy=price))
        assert req.p_duck_buy == pytest.approx(price)

    def test_zero_is_rejected(self) -> None:
        with pytest.raises(ValidationError):
            DSSSimulationRequest(**valid_payload(p_duck_buy=0))

    def test_zero_float_is_rejected(self) -> None:
        with pytest.raises(ValidationError):
            DSSSimulationRequest(**valid_payload(p_duck_buy=0.0))

    @pytest.mark.parametrize("price", [-1, -0.01, -26500])
    def test_negative_is_rejected(self, price: float) -> None:
        with pytest.raises(ValidationError):
            DSSSimulationRequest(**valid_payload(p_duck_buy=price))

    def test_nan_is_rejected(self) -> None:
        with pytest.raises(ValidationError):
            DSSSimulationRequest(**valid_payload(p_duck_buy=float("nan")))

    @pytest.mark.parametrize("value", [float("inf"), float("-inf")])
    def test_infinity_is_rejected(self, value: float) -> None:
        with pytest.raises(ValidationError):
            DSSSimulationRequest(**valid_payload(p_duck_buy=value))

    def test_non_finite_json_token_is_rejected(self) -> None:
        # Some JSON parsers accept NaN/Infinity tokens; they must not validate.
        raw = (
            '{"land_area_are": 7, "duck_count": 28, "planting_date": "2026-06-01", '
            '"planting_system": "jajar_legowo", "rice_variety": "sertani", '
            '"duck_age_days": 30, "p_duck_buy": NaN}'
        )
        with pytest.raises(ValidationError):
            DSSSimulationRequest.model_validate_json(raw)


class TestRequiredInputs:
    @pytest.mark.parametrize(
        "field",
        [
            "land_area_are",
            "duck_count",
            "planting_date",
            "planting_system",
            "rice_variety",
            "duck_age_days",
        ],
    )
    def test_each_other_input_remains_required(self, field: str) -> None:
        payload = valid_payload()
        del payload[field]
        with pytest.raises(ValidationError) as excinfo:
            DSSSimulationRequest(**payload)
        assert any(err["loc"][0] == field for err in excinfo.value.errors())

    @pytest.mark.parametrize("field", ["land_area_are", "duck_count", "duck_age_days"])
    @pytest.mark.parametrize("bad_value", [0, -1])
    def test_positive_fields_reject_zero_and_negative(
        self, field: str, bad_value: int
    ) -> None:
        with pytest.raises(ValidationError):
            DSSSimulationRequest(**valid_payload(**{field: bad_value}))

    def test_non_finite_area_is_rejected(self) -> None:
        assert math.isnan(float("nan"))
        with pytest.raises(ValidationError):
            DSSSimulationRequest(**valid_payload(land_area_are=float("nan")))
        with pytest.raises(ValidationError):
            DSSSimulationRequest(**valid_payload(land_area_are=float("inf")))

    @pytest.mark.parametrize("bad_date", ["not-a-date", "2026-13-40"])
    def test_invalid_planting_date_is_rejected(self, bad_date: str) -> None:
        with pytest.raises(ValidationError):
            DSSSimulationRequest(**valid_payload(planting_date=bad_date))
