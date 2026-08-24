"""Optimizer routes — STAND-ALONE feature, OUT OF SoT scope.

See ``app.schemas.optimizer`` for the scope notice. The optimizer uses a
archived, separate formula set. It MUST NOT import or call
``app.engines.formula_engine`` or ``app.engines.impact_engine`` directly;
The current endpoint is a self-contained stub: it does not call the DSS core
endpoint or claim a Model C recommendation.

The route below is intentionally minimal: it returns a structured response
saying the optimizer is currently a stub. Real product work would re-implement
the legacy grid-search here without touching DSS core.
"""

from fastapi import APIRouter
from pydantic import BaseModel

from app.schemas.optimizer import (
    OptimizerRecommendRequest,
    OptimizerRecommendResponse,
    ActualScenario,
    ComparisonSummary,
    DataReadinessSummary,
    EconomicsSummary,
    EcologySummary,
    EnvironmentSummary,
    InfrastructureOutput,
    OptimalityAssessment,
    PredictedYield,
    RecommendedScenario,
    RiskSummary,
    ScenarioEcology,
    ScenarioEconomics,
    ScenarioEnvironment,
    SoilNutrients,
    ValidationSummary,
)


router = APIRouter(prefix="/optimizer")


def _stub_predicted_yield() -> PredictedYield:
    return PredictedYield(
        kg_per_ha=0.0,
        kg_per_are=0.0,
        ton_per_ha=0.0,
        estimated_total_kg=0.0,
    )


def _stub_infrastructure() -> InfrastructureOutput:
    return InfrastructureOutput(
        status="optimizer-stub",
        net_cost_per_cycle_rp=0.0,
        shelter_cost_per_cycle_rp=0.0,
        maintenance_cost_rp=0.0,
        total_infrastructure_cost_rp=0.0,
        note="Optimizer stub",
    )


def _stub_soil_nutrients() -> SoilNutrients:
    return SoilNutrients(
        status="optimizer-stub",
        missing_parameters=[],
    )


def _stub_economics() -> ScenarioEconomics:
    return ScenarioEconomics(
        status="optimizer-stub",
        perspective="optimizer-stub",
        rice_revenue_rp=None,
        conventional_rice_revenue_rp=None,
        delta_rice_value_rp=None,
        duck_revenue_rp=0.0,
        duck_purchase_cost_rp=None,
        feed_cost_rp=None,
        feed_cost_status="optimizer-stub",
        duck_net_value_rp=None,
        infrastructure=_stub_infrastructure(),
        penalty_yield_rp=None,
        penalty_feed_rp=None,
        net_profit_rp=None,
        net_profit_rp_per_are=None,
        missing_parameters=[],
        sumber_data="optimizer-stub",
        additional_cost=0.0,
    )


def _stub_ecology() -> ScenarioEcology:
    return ScenarioEcology(
        status="optimizer-stub",
        fertilizer_saving_rp=0.0,
        fertilizer_saving_raw_rp=0.0,
        fertilizer_saving_status="optimizer-stub",
        pesticide_herbicide_saving_rp=None,
        pesticide_herbicide_saving_status="optimizer-stub",
        weed_reduction_rate=0.0,
        weeding_saving_rp=0.0,
        weeding_saving_status="optimizer-stub",
        partial_ecological_value_rp=0.0,
        total_ecological_value_rp=None,
        included_components=[],
        missing_parameters=[],
        soil_nutrients=_stub_soil_nutrients(),
    )


def _stub_environment() -> ScenarioEnvironment:
    return ScenarioEnvironment(
        status="optimizer-stub",
        calibration_note="Optimizer stub",
        missing_parameters=[],
        sumber_data="optimizer-stub",
    )


@router.post(
    "/recommend",
    response_model=OptimizerRecommendResponse,
    summary="Optimizer recommendation (OUT OF SoT scope)",
    description=(
        "Stand-alone optimizer feature. NOT aligned with the local-calibrated "
        "Frozen Model C DSS core is separate. This endpoint may use archived "
        "formulas internally."
    ),
)
def optimizer_recommend(payload: OptimizerRecommendRequest) -> OptimizerRecommendResponse:
    # Placeholder: real implementation will re-introduce the legacy grid
    # search here, OUTSIDE the DSS core calculator.
    actual = ActualScenario(
        duck_count=payload.duck_count,
        land_area_are=payload.land_area_are,
        land_area_ha=payload.land_area_are / 100.0,
        density_are=payload.duck_count / payload.land_area_are,
        density_ha=(payload.duck_count / payload.land_area_are) * 100.0,
        duration_days=0,
        release_date=payload.planting_date,
        pull_date=payload.planting_date,
        surviving_ducks=0.0,
        dung_total_per_duck_kg=0.0,
        dung_status="unknown",
        effective_duration_days=0.0,
        x_base_kg_per_ha=0.0,
        penalty_rate=0.0,
        x_penalized_kg_per_ha=0.0,
        predicted_yield=_stub_predicted_yield(),
        risk_status="unknown",
        rey=None,
        rey_status="not-computed",
        rey_notes="Optimizer stub; legacy grid-search not yet re-implemented here.",
    )
    recommended = RecommendedScenario(
        recommended_duck_count=payload.duck_count,
        recommended_density_are=payload.duck_count / payload.land_area_are,
        recommended_density_ha=(payload.duck_count / payload.land_area_are) * 100.0,
        recommended_duration_days=0,
        recommended_release_date=payload.planting_date,
        recommended_pull_date=payload.planting_date,
        surviving_ducks=0.0,
        dung_total_per_duck_kg=0.0,
        dung_status="unknown",
        effective_duration_days=0.0,
        x_base_kg_per_ha=0.0,
        penalty_rate=0.0,
        x_penalized_kg_per_ha=0.0,
        predicted_yield=_stub_predicted_yield(),
        risk_status="unknown",
        reasoning_summary="Optimizer stub",
        rey=None,
        rey_status="not-computed",
        rey_notes="Optimizer stub",
    )
    return OptimizerRecommendResponse(
        actual_scenario=actual,
        recommended_scenario=recommended,
        comparison=ComparisonSummary(
            duck_count_difference=0,
            density_difference_are=0.0,
            yield_difference_kg_per_ha=0.0,
            yield_difference_total_kg=0.0,
            risk_change="no-change",
            profit_difference_rp=None,
        ),
        economics=EconomicsSummary(
            status="optimizer-stub",
            actual=_stub_economics(),
            recommended=_stub_economics(),
            delta_profit_rp=None,
            assumptions=[],
        ),
        ecology=EcologySummary(
            status="optimizer-stub",
            actual=_stub_ecology(),
            recommended=_stub_ecology(),
            assumptions=[],
        ),
        environment=EnvironmentSummary(
            status="optimizer-stub",
            actual=_stub_environment(),
            recommended=_stub_environment(),
            assumptions=[],
        ),
        risk=RiskSummary(
            actual_status="unknown",
            recommended_status="unknown",
            density_risk="",
            phase_risk="",
            feed_warning="",
            survival_data_warning="",
            thresholds={},
            notes=[],
        ),
        optimality=OptimalityAssessment(
            is_optimal=False,
            score_safety=False,
            density_gap_ratio=None,
            density_gap_within_threshold=None,
            delta_yield_pct=None,
            delta_yield_within_threshold=None,
            delta_profit_ratio=None,
            delta_profit_within_threshold=None,
            profit_component_included=False,
            optimality_basis="optimizer-stub",
            catatan_kalibrasi="Optimizer stub; not yet re-implemented.",
            thresholds={},
            threshold_status="optimizer-stub",
            sumber_data="optimizer-stub",
            profit_data_purity="literature-uncalibrated",
        ),
        validation=ValidationSummary(
            input_valid=True,
            constraint_violations=[],
            warnings=["optimizer-stub"],
            missing_parameters=[],
        ),
        data_readiness=DataReadinessSummary(
            agronomy_ready="stub",
            yield_ready="stub",
            economics_ready="stub",
            ecology_ready="stub",
            environment_ready="stub",
            overall_status="optimizer-stub",
        ),
        assumptions=["Optimizer is a stand-alone stub in this build."],
    )
