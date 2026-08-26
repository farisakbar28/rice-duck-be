"""Phase 1: R2 response schema can represent unavailable/partial outputs.

docs/03_R2_API_CONTRACT.md section 4: unknown scientific values serialize as
JSON null plus explicit availability/reason metadata. Nothing here computes
numbers -- this only proves the contract shape.
"""

import json
from datetime import date

import pytest
from pydantic import ValidationError

from app.domain.models import (
    AvailabilityStatus,
    CostCompletenessFlag,
    ProvenanceStatus,
    PurchasePriceSource,
)
from app.schemas.dss import (
    CageCost,
    CostLedger,
    DSSOptionsResponse,
    DSSSimulationResponse,
    DuckPurchaseCost,
    FeedCost,
    ModelMeta,
    PlantingSystemOption,
    PurchasePriceOption,
    ReasonCode,
    RiceVarietyOption,
    SimulationInputEcho,
    TraceMeta,
    YieldOutputs,
)

BANNED_RESPONSE_KEYS = (
    "Revenue_duck_potential",
    "Revenue_duck",
    "Total_Revenue_DSS",
    "Net_Cash_Contribution_DSS",
    "Profit_net_cash",
    "Yield_are_pred",
    "Yield_total_pred",
    "HST_in",
    "HST_out",
    "D_in",
    "D_out",
    "Cost_feed",
    "Core_Cash_Cost",
)


def minimal_response() -> DSSSimulationResponse:
    return DSSSimulationResponse(
        model=ModelMeta(),
        input=SimulationInputEcho(
            land_area_are=7.0,
            duck_count=28,
            planting_date=date(2026, 6, 1),
            planting_system="jajar_legowo",
            rice_variety="sertani",
            duck_age_days=30,
            p_duck_buy_manual=None,
            p_duck_buy_effective=26500.0,
            p_duck_buy_source=PurchasePriceSource.LOCAL_DEFAULT_MIDPOINT,
        ),
    )


class TestUnavailableRepresentation:
    def test_yield_group_defaults_to_null_numerics(self) -> None:
        resp = minimal_response()
        g = resp.crop_yield
        assert g.availability is None
        assert g.baseline_kg_per_are is None
        assert g.rice_duck_response_factor is None
        assert g.yield_kg_per_are is None
        assert g.yield_total_kg is None

    def test_explicit_unavailable_yield_with_reasons(self) -> None:
        resp = minimal_response()
        resp.crop_yield = YieldOutputs(
            availability=AvailabilityStatus.UNAVAILABLE,
            reason_codes=[
                ReasonCode.Y_BASE_LOOKUP_MISSING,
                ReasonCode.F_RD_LOOKUP_MISSING,
            ],
        )
        dumped = resp.model_dump(mode="json", by_alias=True)
        y = dumped["yield"]
        assert y["availability"] == "UNAVAILABLE"
        assert y["baseline_kg_per_are"] is None
        assert y["yield_total_kg"] is None
        assert y["reason_codes"] == ["Y_BASE_LOOKUP_MISSING", "F_RD_LOOKUP_MISSING"]

    def test_feed_null_with_reason_codes(self) -> None:
        resp = minimal_response()
        resp.costs.feed = FeedCost(
            availability=AvailabilityStatus.UNAVAILABLE,
            amount_rp=None,
            reason_codes=[
                ReasonCode.FEED_QUANTITY_LOOKUP_MISSING,
                ReasonCode.FEED_PRICE_LOOKUP_MISSING,
            ],
        )
        feed = resp.model_dump(mode="json", by_alias=True)["costs"]["feed"]
        assert feed["amount_rp"] is None
        assert feed["availability"] == "UNAVAILABLE"
        assert len(feed["reason_codes"]) == 2

    def test_cage_total_null_with_reason(self) -> None:
        ledger = CostLedger(
            cage=CageCost(
                total_amount_rp=None,
                reason_codes=[ReasonCode.CAGE_CAPACITY_RULE_MISSING],
            )
        )
        assert ledger.cage.total_amount_rp is None

    def test_full_profit_null_while_incomplete(self) -> None:
        resp = minimal_response()
        resp.economics.profit_full_est_rp = None  # must never be required numeric
        resp.economics.paddy_revenue_rp = None
        resp.reliability.cost_completeness = CostCompletenessFlag.INCOMPLETE
        dumped = resp.model_dump(mode="json", by_alias=True)
        assert dumped["economics"]["profit_full_est_rp"] is None
        assert dumped["reliability"]["cost_completeness"] == "INCOMPLETE"

    def test_sale_quantity_is_distinct_and_nullable(self) -> None:
        resp = minimal_response()
        assert resp.duck.surviving_ducks is None
        assert resp.duck.sale_quantity is None
        assert resp.duck.terminal_value_is_cash_revenue is False

    def test_unknown_never_requires_zero_anywhere(self) -> None:
        """Full default-constructed response must serialize with nulls, not zeros."""
        resp = minimal_response()
        raw = json.dumps(resp.model_dump(mode="json", by_alias=True))
        # Scientific/economic numerics default to None; scan the JSON for the
        # canonical unavailable slots being 0.
        dumped = json.loads(raw)
        assert dumped["yield"]["baseline_kg_per_are"] is None
        assert dumped["costs"]["feed"]["amount_rp"] is None
        assert dumped["costs"]["cage"]["total_amount_rp"] is None
        assert dumped["economics"]["profit_full_est_rp"] is None
        assert dumped["duck"]["sale_quantity"] is None


class TestContractShape:
    def test_top_level_semantic_groups(self) -> None:
        dumped = minimal_response().model_dump(mode="json", by_alias=True)
        assert set(dumped.keys()) == {
            "model",
            "input",
            "operational",
            "calendar",
            "duck",
            "yield",
            "fertilizer_baseline",
            "costs",
            "economics",
            "reliability",
            "warnings",
            "trace",
        }

    def test_no_legacy_flat_fields_survive(self) -> None:
        raw = json.dumps(minimal_response().model_dump(mode="json", by_alias=True))
        for key in BANNED_RESPONSE_KEYS:
            assert key not in raw

    def test_model_meta_separates_version_concepts(self) -> None:
        meta = ModelMeta(
            model_version="R2",
            history_schema_version=4,
            parameter_registry_version="R2-2026-08-26.1",
            model_commit_sha=None,
        ).model_dump()
        assert meta["model_version"] == "R2"
        assert meta["history_schema_version"] == 4
        assert meta["parameter_registry_version"] == "R2-2026-08-26.1"

    def test_input_echo_keeps_manual_effective_source_distinct(self) -> None:
        echo = SimulationInputEcho(
            land_area_are=7.0,
            duck_count=28,
            planting_date=date(2026, 6, 1),
            planting_system="jajar_legowo",
            rice_variety="sertani",
            duck_age_days=30,
            p_duck_buy_manual=None,
            p_duck_buy_effective=26500.0,
            p_duck_buy_source=PurchasePriceSource.LOCAL_DEFAULT_MIDPOINT,
        )
        dumped = echo.model_dump(mode="json")
        assert dumped["p_duck_buy_manual"] is None
        assert dumped["p_duck_buy_effective"] == 26500.0
        assert dumped["p_duck_buy_source"] == "LOCAL_DEFAULT_MIDPOINT"

    def test_json_round_trip_preserves_nulls(self) -> None:
        resp = minimal_response()
        resp.trace = TraceMeta(
            active_formula_ids=["R2-PRICE-01"],
            defaulted_inputs=[
                {
                    "field": "p_duck_buy",
                    "resolved_value": 26500,
                    "source": "I1",
                    "status_tag": "mixed",
                }
            ],
        )
        revived = DSSSimulationResponse.model_validate(
            json.loads(json.dumps(resp.model_dump(mode="json", by_alias=True)))
        )
        assert revived.crop_yield.baseline_kg_per_are is None
        assert revived.trace.defaulted_inputs[0].resolved_value == 26500

    def test_model_meta_frozen_defaults_false_and_freeze_id_optional(self) -> None:
        # Schema defaults stay conservative; the production service sources
        # frozen/freeze_id from app.data.seed (see tests/test_r2_freeze_semantics.py).
        bare = ModelMeta()
        assert bare.frozen is False
        assert bare.freeze_id is None

    def test_trace_meta_has_availability_reasons_field(self) -> None:
        meta = TraceMeta(
            availability_reasons={"yield": ["Y_BASE_LOOKUP_MISSING"]}
        )
        dumped = meta.model_dump()
        assert dumped["availability_reasons"] == {"yield": ["Y_BASE_LOOKUP_MISSING"]}
        assert TraceMeta().availability_reasons == {}


class TestConstrainedVocabularies:
    def test_invalid_provenance_label_is_rejected(self) -> None:
        with pytest.raises(ValidationError):
            RiceVarietyOption(
                code="x",
                label="X",
                harvest_hst_min=90,
                harvest_hst_max=100,
                calendar_status="local-validated",  # banned current-master label
                yield_lookup_status="PENDING_LOOKUP",
            )

    def test_valid_provenance_labels_accepted(self) -> None:
        opt = RiceVarietyOption(
            code="inpari",
            label="Inpari",
            harvest_hst_min=90,
            harvest_hst_max=100,
            calendar_status=ProvenanceStatus.LOCAL_ESTIMATE,
            yield_lookup_status="PENDING_LOOKUP",
        )
        assert opt.calendar_status is ProvenanceStatus.LOCAL_ESTIMATE

    def test_unknown_reason_code_is_rejected(self) -> None:
        with pytest.raises(ValidationError):
            FeedCost(reason_codes=["MADE_UP_REASON"])

    def test_purchase_cost_group_shape(self) -> None:
        cost = DuckPurchaseCost(
            availability=AvailabilityStatus.AVAILABLE, amount_rp=742000.0
        )
        assert cost.amount_rp == 742000.0


class TestOptionsContract:
    def test_options_response_contract_shape(self) -> None:
        resp = DSSOptionsResponse(
            rice_varieties=[
                RiceVarietyOption(
                    code="inpari",
                    label="Inpari",
                    harvest_hst_min=90,
                    harvest_hst_max=100,
                    calendar_status=ProvenanceStatus.LOCAL_ESTIMATE,
                    yield_lookup_status="PENDING_LOOKUP",
                )
            ],
            planting_systems=[
                PlantingSystemOption(
                    code="tegel",
                    label="Tegel",
                    supported_density_min_are=2.0,
                    supported_density_max_are=3.0,
                    status=ProvenanceStatus.LOCAL_ESTIMATE,
                )
            ],
            purchase_price=PurchasePriceOption(
                optional=True,
                default_rp_per_duck=26500.0,
                local_range_rp_per_duck=[25000.0, 28000.0],
                status=ProvenanceStatus.MIXED,
            ),
        )
        dumped = resp.model_dump(mode="json")
        assert dumped["model_version"] == "R2"
        assert dumped["purchase_price"] == {
            "optional": True,
            "default_rp_per_duck": 26500.0,
            "local_range_rp_per_duck": [25000.0, 28000.0],
            "status": "mixed",
        }
        assert dumped["rice_varieties"][0]["yield_lookup_status"] == "PENDING_LOOKUP"
        raw = json.dumps(dumped)
        for banned in ("F_sys", "47.8767507", "52500", "9500"):
            assert banned not in raw
