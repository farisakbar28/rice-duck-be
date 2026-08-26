"""R2 simulation service -- pure orchestration over the Phase-2 engines.

The service sequences the canonical R2 engines (``app.engines.r2``) and maps
their Decimal results onto the nested API DTOs at the boundary. It contains
NO scientific formulas: every number comes from an engine fed by the
immutable ``R2EngineConfig`` built from the canonical seed registry.

Flow (docs/02 migration plan M4/M5, docs/03 contract):

    request -> reference resolution -> config -> normalization -> support
    flags -> calendar -> survival -> yield -> fertilizer -> infrastructure
    -> feed/weeding/pest -> economic ledger -> nested DTO -> warnings/trace
    -> optional authenticated v4 persistence -> exact same response back

Boundary rules:
  * Only ``app.engines.r2`` engines are imported; the invalidated legacy
    engines are never reachable from this module (statically enforced).
  * Unknown scientific values stay ``None`` with explicit availability /
    reason metadata; nothing is coerced to zero and nothing is rounded
    inside the pipeline.
  * Authentication affects persistence only -- never numeric results.
  * Persistence writes exactly one v4 row (docs/05) whose snapshots are the
    canonical semantic record returned to the caller.
"""

from __future__ import annotations

from datetime import date, datetime, timezone

from app.core.config import settings
from app.core.exceptions import AppError, InvalidReferenceError, ResourceNotFoundError
from app.data.seed import (
    FREEZE_ID,
    MODEL_FROZEN,
    MODEL_VERSION,
    PARAMETER_REGISTRY,
    PARAMETER_REGISTRY_VERSION,
)
from app.domain.models import (
    AvailabilityStatus,
    ExtrapolationFlag,
    PlantingSystem,
    RiceVariety,
    R2HistorySnapshot,
)
from app.engines.r2 import (
    FORMULA_IDS,
    compute_calendar_windows,
    compute_economic_ledger,
    compute_feed_cost,
    compute_fertilizer_baseline,
    compute_infrastructure,
    compute_pest_effect,
    compute_survival,
    compute_weeding_baseline,
    compute_yield,
    classify_age,
    classify_density,
    load_default_config,
    normalize_inputs,
    operational_extrapolation,
)
from app.repositories.history_repository import history_repository
from app.repositories.lookup_repository import lookup_repository
from app.schemas.dss import (
    AgeSupportFlag,
    AvailabilityStatus as AvailabilityStatusSchema,
    CalendarWindow,
    CageCost,
    ComponentAvailability,
    CostCompletenessFlag,
    CostLedger,
    DeleteHistoryResponse,
    DefaultedInputRecord,
    DSSOptionsResponse,
    DSSSimulationRequest,
    DSSSimulationResponse,
    DensitySupportFlag,
    DuckOutputs,
    DuckPurchaseCost,
    EconomicsOutputs,
    FeedCost,
    FertilizerBaseline,
    HistoryListItem,
    HistoryListResponse,
    ModelMeta,
    NetInfrastructureCost,
    OperationalProfile,
    PesticideCost,
    PlantingSystemOption,
    PurchasePriceOption,
    R2HistorySummary,
    ReliabilitySummary,
    RiceVarietyOption,
    SimulationInputEcho,
    TraceMeta,
    WeedingCost,
    YieldOutputs,
)

# Registry groups whose rules are executed on every successful simulation.
# Branch-specific formula IDs are appended by ``_build_trace`` only when that
# branch actually produced a value.
_ALWAYS_ACTIVE_TRACE_GROUPS = (
    "normalization",
    "age_support",
    "density_support",
    "fertilizer",
    "infrastructure_net",
    "infrastructure_cage",
    "weeding",
    "pest",
)

# Non-executable legacy formula register (docs/04 section 2, verbatim).
_DISABLED_LEGACY_FORMULA_IDS = (
    "LEG-RAGE",
    "LEG-POVER",
    "LEG-PUNDER",
    "LEG-LAMBDA-078125",
    "LEG-SURV-FULL60",
    "LEG-Y0-478767507",
    "LEG-FDENSITY",
    "LEG-FAGE",
    "LEG-FSYS-1211",
    "LEG-FVAR-1",
    "LEG-MANURE-T",
    "LEG-WEED-CURVE",
    "LEG-PEST-CURVE",
    "LEG-FEED-4500",
    "LEG-FEED-20000",
    "LEG-INFRA-289260",
    "LEG-CAGE-FLAT175",
    "LEG-KCL-9500",
    "LEG-GABAH-6000",
    "LEG-DUCKSELL-35000",
    "LEG-DUCKSELL-52500",
)

# Parameter-registry keys consumed by R2EngineConfig.from_registry.
_CONSUMED_PARAMETER_KEYS = (
    "p_duck_buy_default",
    "supported_age_window_days",
    "density_high_risk_threshold_are",
    "density_limited_test_are",
    "release_hst_window",
    "pull_hst_window",
    "active_duration_ref_days",
    "lambda_safe_ref",
    "n_need_kg_per_are",
    "p2o5_need_kg_per_are",
    "k2o_need_kg_per_are",
    "urea_n_fraction",
    "npk_n_fraction",
    "npk_p2o5_fraction",
    "npk_k2o_fraction",
    "het_urea_rp_per_kg",
    "het_npk_rp_per_kg",
    "net_price_rp_per_m",
    "net_lifetime_cycles",
    "cage_cost_per_unit_cycle_rp",
    "weeding_baseline_rp_per_are",
    "pesticide_effect",
    "p_gabah_ref_rp_per_kg",
    "duck_terminal_value_rp_per_duck",
)

# Regulatory-locked parameters surfaced as regulation versions in trace.
_REGULATORY_PARAMETER_KEYS = (
    "p_gabah_ref_rp_per_kg",
    "het_urea_rp_per_kg",
    "het_npk_rp_per_kg",
)


def _f(value):
    """Decimal engine value -> float at the DTO boundary (None stays None)."""
    return None if value is None else float(value)


class DSSService:
    # ------------------------------------------------------------------
    # GET /dss/options
    # ------------------------------------------------------------------
    def get_options(self) -> DSSOptionsResponse:
        price_default = PARAMETER_REGISTRY["p_duck_buy_default"]
        price_range = PARAMETER_REGISTRY["p_duck_buy_local_range"]
        return DSSOptionsResponse(
            model_version=MODEL_VERSION,
            rice_varieties=[
                RiceVarietyOption(
                    code=item.code,
                    label=item.label,
                    harvest_hst_min=item.harvest_hst_min,
                    harvest_hst_max=item.harvest_hst_max,
                    calendar_status=item.calendar_status,
                    yield_lookup_status=item.yield_lookup_status,
                )
                for item in lookup_repository.list_rice_varieties()
            ],
            planting_systems=[
                PlantingSystemOption(
                    code=item.code,
                    label=item.label,
                    supported_density_min_are=item.supported_density_min_are,
                    supported_density_max_are=item.supported_density_max_are,
                    status=item.status,
                )
                for item in lookup_repository.list_planting_systems()
            ],
            purchase_price=PurchasePriceOption(
                optional=True,
                default_rp_per_duck=_f(price_default.value),
                local_range_rp_per_duck=[_f(price_range.minimum), _f(price_range.maximum)],
                status=price_default.status_tag,
            ),
        )

    # ------------------------------------------------------------------
    # POST /dss/simulate
    # ------------------------------------------------------------------
    def simulate(
        self,
        payload: DSSSimulationRequest,
        user_id: str | None = None,
    ) -> DSSSimulationResponse:
        # 1-2. Reference resolution (fail-closed, 422 on unknown codes).
        variety = self._find_variety(payload.rice_variety)
        system = self._find_planting_system(payload.planting_system)

        # 3. Immutable R2 configuration from the canonical registry.
        config = load_default_config()

        # 4. Normalization (area_m2 / density / effective purchase price).
        normalized = normalize_inputs(
            land_area_are=payload.land_area_are,
            duck_count=payload.duck_count,
            p_duck_buy_manual=payload.p_duck_buy,
            config=config,
        )

        # 5-7. Support classifiers + operational extrapolation flag.
        age_flag = classify_age(payload.duck_age_days, config)
        density_flag = classify_density(normalized.density_are, system, config)
        extrapolation = operational_extrapolation(age_flag, density_flag)

        # 8. Calendar windows.
        calendar = compute_calendar_windows(payload.planting_date, variety, config)

        # 9. Survival (gated on SUPPORTED age AND density).
        survival = compute_survival(payload.duck_count, age_flag, density_flag, config)

        # 10. Yield -- fail-closed empty production lookup store.
        yld = compute_yield(
            variety=variety,
            system_code=system.code,
            normalized_inputs=normalized,
            config=config,
        )

        # 11-12. Fertilizer baseline + infrastructure ranges.
        fertilizer = compute_fertilizer_baseline(normalized.land_area_are, config)
        infrastructure = compute_infrastructure(normalized.land_area_are, config)

        # 13-15. Feed / weeding / pest availability semantics.
        feed = compute_feed_cost(config)
        weeding = compute_weeding_baseline(normalized.land_area_are, config)
        pest = compute_pest_effect(config)

        # 16. Conditional economic ledger (feed/cage totals absent -> INCOMPLETE).
        ledger = compute_economic_ledger(
            duck_count=payload.duck_count,
            purchase_price_effective=normalized.purchase_price_effective,
            yield_result=yld,
            survival_result=survival,
            infrastructure_result=infrastructure,
            fertilizer_result=fertilizer,
            config=config,
        )

        # One UTC timestamp shared by the response metadata and any snapshot.
        generated_at = datetime.now(timezone.utc)

        warnings = self._build_warnings(
            age_flag=age_flag,
            density_flag=density_flag,
            survival=survival,
            yld=yld,
            feed=feed,
            cage_total=infrastructure.cage.total_amount_rp,
            completeness=ledger.cost_completeness,
        )
        trace = self._build_trace(
            payload=payload,
            variety=variety,
            survival=survival,
            yld=yld,
            feed=feed,
            cage=infrastructure.cage,
            ledger=ledger,
        )

        response = DSSSimulationResponse(
            model=ModelMeta(
                model_version=MODEL_VERSION,
                history_schema_version=4,
                parameter_registry_version=PARAMETER_REGISTRY_VERSION,
                model_commit_sha=settings.model_commit_sha,
                freeze_id=FREEZE_ID,
                frozen=MODEL_FROZEN,  # sourced from the freeze configuration (docs/11)
                generated_at=generated_at,
            ),
            input=SimulationInputEcho(
                land_area_are=payload.land_area_are,
                duck_count=payload.duck_count,
                planting_date=payload.planting_date,
                planting_system=system.code,
                rice_variety=variety.code,
                duck_age_days=payload.duck_age_days,
                p_duck_buy_manual=payload.p_duck_buy,
                p_duck_buy_effective=_f(normalized.purchase_price_effective),
                p_duck_buy_source=normalized.purchase_price_source,
            ),
            operational=OperationalProfile(
                area_m2=_f(normalized.area_m2),
                density_are=_f(normalized.density_are),
                age_support=age_flag,
                density_support=density_flag,
                extrapolation=extrapolation,
            ),
            calendar=self._to_calendar_window(calendar),
            duck=self._to_duck_outputs(survival, ledger),
            crop_yield=self._to_yield_outputs(yld),
            fertilizer_baseline=self._to_fertilizer_baseline(fertilizer),
            costs=self._to_cost_ledger(feed, infrastructure, weeding, pest, ledger),
            economics=EconomicsOutputs(
                paddy_price_benchmark_rp_per_kg=_f(ledger.paddy_price_benchmark_rp_per_kg),
                paddy_price_semantics=ledger.paddy_price_semantics,
                paddy_revenue_rp=_f(ledger.paddy_revenue_rp),
                cash_revenue_rp=_f(ledger.cash_revenue_rp),
                gross_economic_value_rp=_f(ledger.gross_economic_value_rp),
                margin_core_rp=_f(ledger.margin_core_rp),
                profit_full_est_rp=_f(ledger.profit_full_est_rp),
                profit_full_status=ledger.profit_full_status,
            ),
            reliability=ReliabilitySummary(
                yield_availability=yld.availability,
                survival_availability=survival.availability,
                feed_cost_availability=feed.availability,
                cost_completeness=ledger.cost_completeness,
                extrapolation=extrapolation,
            ),
            warnings=warnings,
            trace=trace,
        )

        # 19. Optional authenticated persistence -- one atomic v4 insert.
        if user_id is not None:
            self._persist_r2_snapshot(
                user_id=user_id,
                payload=payload,
                variety=variety,
                system=system,
                normalized=normalized,
                age_flag=age_flag,
                density_flag=density_flag,
                extrapolation=extrapolation,
                yld=yld,
                survival=survival,
                ledger=ledger,
                response=response,
                generated_at=generated_at,
            )

        # 20. The exact semantic response that was persisted.
        return response

    # ------------------------------------------------------------------
    # Histories
    # ------------------------------------------------------------------
    def list_histories(self, user_id: str) -> HistoryListResponse:
        items: list[HistoryListItem] = []
        for snapshot in history_repository.list_r2_by_user(user_id):
            items.append(self._r2_list_item(snapshot))
        for legacy in history_repository.list_legacy_by_user(user_id):
            # Identity/version/timestamp only: no scientific value is
            # synthesized for legacy rows (docs/05 section 7).
            items.append(
                HistoryListItem(
                    id=legacy.id,
                    model_version="LEGACY",
                    schema_version=legacy.schema_version,
                    created_at=legacy.created_at,
                    r2_summary=None,
                )
            )
        items.sort(key=lambda item: item.created_at, reverse=True)
        return HistoryListResponse(data=items)

    def get_history(self, history_id: str, user_id: str) -> DSSSimulationResponse:
        snapshot = history_repository.get_r2_by_id_and_user(history_id, user_id)
        if snapshot is not None:
            # Stored snapshot only -- the R2 engines are never re-run here.
            return DSSSimulationResponse.model_validate_json(snapshot.response_json)

        legacy = history_repository.get_legacy_by_id_and_user(history_id, user_id)
        if legacy is not None:
            raise AppError(
                message=(
                    "Legacy history rows (schema_version <= 3) hold invalidated "
                    "pre-R2 semantics and are never recalculated into R2 "
                    "snapshots."
                ),
                code="legacy_history_semantics",
                status_code=409,
                field="history_id",
            )
        raise ResourceNotFoundError(
            message=f"History '{history_id}' was not found.", field="history_id"
        )

    def delete_history(self, history_id: str, user_id: str) -> DeleteHistoryResponse:
        if history_repository.delete_r2_by_id_and_user(history_id, user_id):
            return DeleteHistoryResponse(message="Simulation history deleted successfully")
        if history_repository.delete_legacy_by_id_and_user(history_id, user_id):
            return DeleteHistoryResponse(message="Simulation history deleted successfully")
        raise ResourceNotFoundError(
            message=f"History '{history_id}' was not found.", field="history_id"
        )

    # ------------------------------------------------------------------
    # Response-group mappers
    # ------------------------------------------------------------------
    @staticmethod
    def _to_calendar_window(calendar):
        return CalendarWindow(
            release_hst_min=calendar.release_hst_min,
            release_hst_max=calendar.release_hst_max,
            release_date_min=calendar.release_date_min,
            release_date_max=calendar.release_date_max,
            pull_hst_min=calendar.pull_hst_min,
            pull_hst_max=calendar.pull_hst_max,
            pull_date_min=calendar.pull_date_min,
            pull_date_max=calendar.pull_date_max,
            active_duration_ref_days=calendar.active_duration_ref_days,
            active_duration_support_min_days=calendar.active_duration_support_min_days,
            active_duration_support_max_days=calendar.active_duration_support_max_days,
            harvest_hst_min=calendar.harvest_hst_min,
            harvest_hst_max=calendar.harvest_hst_max,
            harvest_date_min=calendar.harvest_date_min,
            harvest_date_max=calendar.harvest_date_max,
        )

    @staticmethod
    def _to_duck_outputs(survival, ledger):
        return DuckOutputs(
            survival_availability=survival.availability,
            lambda_eff=_f(survival.lambda_eff),
            surviving_ducks=survival.surviving_ducks,
            sale_quantity=None,
            sale_quantity_status=AvailabilityStatusSchema.UNAVAILABLE,
            terminal_value_ref_rp=_f(ledger.terminal_value_ref_rp),
            terminal_value_min_rp=_f(ledger.terminal_value_min_rp),
            terminal_value_max_rp=_f(ledger.terminal_value_max_rp),
            terminal_value_is_cash_revenue=False,
        )

    @staticmethod
    def _to_yield_outputs(yld):
        return YieldOutputs(
            availability=yld.availability,
            exact_cultivar_resolved=yld.exact_cultivar_resolved,
            baseline_kg_per_are=_f(yld.baseline_kg_per_are),
            rice_duck_response_factor=_f(yld.rice_duck_response_factor),
            yield_kg_per_are=_f(yld.yield_kg_per_are),
            yield_total_kg=_f(yld.yield_total_kg),
            reason_codes=list(yld.reason_codes),
        )

    @staticmethod
    def _to_fertilizer_baseline(fert):
        return FertilizerBaseline(
            availability=fert.availability,
            nutrient_basis=fert.nutrient_basis,
            manure_credit_applied=fert.manure_credit_applied,
            n_need_kg=_f(fert.n_need_kg),
            p2o5_need_kg=_f(fert.p2o5_need_kg),
            k2o_need_kg=_f(fert.k2o_need_kg),
            q_npk_kg=_f(fert.q_npk_kg),
            q_urea_kg=_f(fert.q_urea_kg),
            cost_npk_rp=_f(fert.cost_npk_rp),
            cost_urea_rp=_f(fert.cost_urea_rp),
            cost_total_rp=_f(fert.cost_total_rp),
        )

    @staticmethod
    def _to_cost_ledger(feed, infrastructure, weeding, pest, ledger):
        cage = infrastructure.cage
        return CostLedger(
            duck_purchase=DuckPurchaseCost(
                availability=ledger.duck_purchase_availability,
                amount_rp=_f(ledger.duck_purchase_cost_rp),
            ),
            feed=FeedCost(
                availability=feed.availability,
                amount_rp=_f(feed.amount_rp),
                reason_codes=list(feed.reason_codes),
            ),
            net_infrastructure=NetInfrastructureCost(
                availability=ComponentAvailability.AVAILABLE_RANGE,
                equivalent_perimeter_m=_f(infrastructure.net.equivalent_perimeter_m),
                cost_min_rp_per_cycle=_f(infrastructure.net.cost_min_rp_per_cycle),
                cost_ref_rp_per_cycle=_f(infrastructure.net.cost_ref_rp_per_cycle),
                cost_max_rp_per_cycle=_f(infrastructure.net.cost_max_rp_per_cycle),
                geometry_assumption=infrastructure.net.geometry_assumption,
            ),
            cage=CageCost(
                availability=cage.availability,
                cost_per_unit_min_rp_per_cycle=_f(cage.cost_per_unit_min_rp_per_cycle),
                cost_per_unit_ref_rp_per_cycle=_f(cage.cost_per_unit_ref_rp_per_cycle),
                cost_per_unit_max_rp_per_cycle=_f(cage.cost_per_unit_max_rp_per_cycle),
                total_amount_rp=_f(cage.total_amount_rp),
                reason_codes=list(cage.reason_codes),
            ),
            weeding=WeedingCost(
                availability=weeding.availability,
                baseline_min_rp=_f(weeding.baseline_min_rp),
                baseline_max_rp=_f(weeding.baseline_max_rp),
                saving_rp=_f(weeding.saving_rp),
            ),
            pesticide=PesticideCost(
                effect=pest.effect,
                saving_rp=_f(pest.saving_rp),
            ),
            cost_core_direct_rp=_f(ledger.cost_core_direct_rp),
            cost_total_available_rp=_f(ledger.cost_total_available_rp),
            cost_completeness=ledger.cost_completeness,
        )

    # ------------------------------------------------------------------
    # Warnings / trace builders (metadata only, no science)
    # ------------------------------------------------------------------
    @staticmethod
    def _build_warnings(
        *,
        age_flag: AgeSupportFlag,
        density_flag: DensitySupportFlag,
        survival,
        yld,
        feed,
        cage_total,
        completeness,
    ) -> list[str]:
        warnings: list[str] = []
        if age_flag is AgeSupportFlag.CAUTION:
            warnings.append(
                "AGE_CAUTION: duck age is below the locally supported window "
                "(21-30 days); biological readiness is uncertain."
            )
        if age_flag is AgeSupportFlag.OUTSIDE_LOCAL_RANGE:
            warnings.append(
                "AGE_OUTSIDE_LOCAL_SUPPORT: duck age is above the locally "
                "supported window; affected estimates stay unavailable."
            )
        if density_flag is not DensitySupportFlag.SUPPORTED:
            warnings.append(
                "DENSITY_OUTSIDE_SUPPORTED_DOMAIN: stocking density is outside "
                "the supported range for this planting system."
            )
        if survival.availability is AvailabilityStatus.UNAVAILABLE:
            warnings.append(
                "SURVIVAL_UNAVAILABLE: the surviving-duck count requires "
                "supported age and density; no fallback estimate exists."
            )
        if yld.availability is AvailabilityStatus.UNAVAILABLE:
            warnings.append(
                "YIELD_LOOKUP_UNAVAILABLE: yield numeric output is unavailable "
                "until exact-cultivar baseline and rice-duck response lookups "
                "are configured."
            )
        if feed.availability is AvailabilityStatus.UNAVAILABLE:
            warnings.append(
                "FEED_COST_UNAVAILABLE: feed quantity and price lookups are "
                "not configured."
            )
        if cage_total is None:
            warnings.append(
                "CAGE_TOTAL_UNAVAILABLE: total cage cost requires a sourced "
                "capacity rule."
            )
        if completeness is CostCompletenessFlag.INCOMPLETE:
            warnings.append(
                "FULL_PROFIT_UNAVAILABLE: the full-profit estimate requires a "
                "complete cost ledger."
            )
        return warnings

    def _build_trace(
        self,
        *,
        payload: DSSSimulationRequest,
        variety: RiceVariety,
        survival,
        yld,
        feed,
        cage,
        ledger,
    ) -> TraceMeta:
        active: list[str] = []
        for group in _ALWAYS_ACTIVE_TRACE_GROUPS:
            active.extend(FORMULA_IDS[group])

        # Only the harvest rule for the selected variety executes; the other
        # variety branch must not be advertised in provenance.
        active.extend(
            (
                "R2-CAL-01" if variety.code == "sertani" else "R2-CAL-02",
                "R2-CAL-03",
                "R2-CAL-04",
                "R2-CAL-05",
                "R2-SURV-02",  # availability gate always evaluated
                "R2-COST-01",
                "R2-GRAIN-01",
                "R2-LEDGER-03",
                "R2-LEDGER-04",
            )
        )

        conditional: list[str] = []
        if survival.availability is AvailabilityStatus.AVAILABLE:
            conditional.extend(("R2-SURV-01", "R2-SURV-03", "R2-DUCKVAL-01"))
        if yld.availability is AvailabilityStatus.AVAILABLE:
            conditional.extend(("R2-YLD-01", "R2-YLD-02"))
        if ledger.paddy_revenue_rp is not None:
            conditional.extend(("R2-GRAIN-02", "R2-LEDGER-01"))
        if ledger.gross_economic_value_rp is not None:
            conditional.extend(("R2-LEDGER-02", "R2-LEDGER-05"))
        if ledger.profit_full_est_rp is not None:
            conditional.append("R2-LEDGER-06")

        parameter_sources = {
            key: list(PARAMETER_REGISTRY[key].source_ids)
            for key in _CONSUMED_PARAMETER_KEYS
            if key in PARAMETER_REGISTRY
        }

        lookup_states = {
            "parameter_registry": PARAMETER_REGISTRY_VERSION,
            "yield_base_by_variety": "PENDING_LOOKUP",
            "f_rd_lookup": "PENDING_LOOKUP",
            "feed_quantity_lookup": "UNAVAILABLE",
            "feed_price_lookup": "UNAVAILABLE",
            "cage_capacity_rule": "UNAVAILABLE",
        }
        # Read the states truthfully from the live registry instead of
        # trusting the literals above.
        for key in ("yield_base_by_variety", "f_rd_lookup", "feed_quantity_lookup",
                    "feed_price_lookup", "cage_capacity_rule"):
            entry = PARAMETER_REGISTRY.get(key)
            if entry is not None:
                lookup_states[key] = entry.execution_state.value

        regulation_versions = {
            key: "+".join(PARAMETER_REGISTRY[key].source_ids)
            for key in _REGULATORY_PARAMETER_KEYS
            if key in PARAMETER_REGISTRY and PARAMETER_REGISTRY[key].source_ids
        }

        defaulted_inputs: list[DefaultedInputRecord] = []
        if payload.p_duck_buy is None:
            default_entry = PARAMETER_REGISTRY["p_duck_buy_default"]
            defaulted_inputs.append(
                DefaultedInputRecord(
                    field="p_duck_buy",
                    resolved_value=_f(default_entry.value),
                    source="+".join(default_entry.source_ids) or None,
                    status_tag=default_entry.status_tag,
                )
            )

        availability_reasons: dict[str, list[str]] = {}
        if yld.reason_codes:
            availability_reasons["yield"] = [code.value for code in yld.reason_codes]
        if feed.reason_codes:
            availability_reasons["costs.feed"] = [code.value for code in feed.reason_codes]
        if cage.reason_codes:
            availability_reasons["costs.cage"] = [code.value for code in cage.reason_codes]

        return TraceMeta(
            active_formula_ids=active,
            conditional_formula_ids=conditional,
            disabled_legacy_formula_ids=list(_DISABLED_LEGACY_FORMULA_IDS),
            parameter_sources=parameter_sources,
            lookup_versions=lookup_states,
            regulation_versions=regulation_versions,
            defaulted_inputs=defaulted_inputs,
            availability_reasons=availability_reasons,
        )

    # ------------------------------------------------------------------
    # v4 snapshot persistence (docs/05)
    # ------------------------------------------------------------------
    def _persist_r2_snapshot(
        self,
        *,
        user_id: str,
        payload: DSSSimulationRequest,
        variety: RiceVariety,
        system: PlantingSystem,
        normalized,
        age_flag: AgeSupportFlag,
        density_flag: DensitySupportFlag,
        extrapolation,
        yld,
        survival,
        ledger,
        response: DSSSimulationResponse,
        generated_at: datetime,
    ) -> None:
        snapshot = R2HistorySnapshot(
            id=history_repository.new_id(),
            user_id=user_id,
            schema_version=4,
            model_version=response.model.model_version,
            parameter_registry_version=response.model.parameter_registry_version,
            model_commit_sha=response.model.model_commit_sha,
            created_at=generated_at,
            request_json=response.input.model_dump_json(),
            response_json=response.model_dump_json(by_alias=True),
            trace_json=response.trace.model_dump_json(),
            land_area_are=float(normalized.land_area_are),
            duck_count=payload.duck_count,
            rice_variety=variety.code,
            planting_system=system.code,
            duck_age_days=payload.duck_age_days,
            planting_date=payload.planting_date.isoformat(),
            p_duck_buy_manual=payload.p_duck_buy,
            p_duck_buy_effective=_f(normalized.purchase_price_effective),
            density_are=_f(normalized.density_are),
            age_support=age_flag.value,
            density_support=density_flag.value,
            extrapolation_status=extrapolation.value,
            yield_availability=yld.availability.value,
            survival_availability=survival.availability.value,
            cost_completeness=ledger.cost_completeness.value,
            yield_total_kg=_f(yld.yield_total_kg),
            margin_core_rp=_f(ledger.margin_core_rp),
            profit_full_est_rp=_f(ledger.profit_full_est_rp),
        )
        history_repository.create_r2(snapshot)

    def _r2_list_item(self, snapshot: R2HistorySnapshot) -> HistoryListItem:
        summary = R2HistorySummary(
            land_area_are=snapshot.land_area_are,
            duck_count=snapshot.duck_count,
            rice_variety=snapshot.rice_variety,
            planting_system=snapshot.planting_system,
            duck_age_days=snapshot.duck_age_days,
            planting_date=date.fromisoformat(snapshot.planting_date),
            p_duck_buy_effective=snapshot.p_duck_buy_effective,
            density_are=snapshot.density_are,
            age_support=AgeSupportFlag(snapshot.age_support),
            density_support=DensitySupportFlag(snapshot.density_support),
            extrapolation_status=ExtrapolationFlag(snapshot.extrapolation_status),
            yield_availability=AvailabilityStatus(snapshot.yield_availability),
            survival_availability=AvailabilityStatus(snapshot.survival_availability),
            cost_completeness=CostCompletenessFlag(snapshot.cost_completeness),
            yield_total_kg=snapshot.yield_total_kg,
            margin_core_rp=snapshot.margin_core_rp,
            profit_full_est_rp=snapshot.profit_full_est_rp,
        )
        return HistoryListItem(
            id=snapshot.id,
            model_version=snapshot.model_version,
            schema_version=snapshot.schema_version,
            created_at=snapshot.created_at,
            r2_summary=summary,
        )

    # ------------------------------------------------------------------
    # Reference resolution
    # ------------------------------------------------------------------
    @staticmethod
    def _find_variety(code: str) -> RiceVariety:
        variety = lookup_repository.get_rice_variety(code)
        if variety is None:
            raise InvalidReferenceError(
                message=f"Unknown rice_variety '{code}'. Valid values: 'sertani', 'inpari'.",
                field="rice_variety",
            )
        return variety

    @staticmethod
    def _find_planting_system(code: str) -> PlantingSystem:
        ps = lookup_repository.get_planting_system(code)
        if ps is None:
            raise InvalidReferenceError(
                message=(
                    f"Unknown planting_system '{code}'. "
                    "Valid values: 'jajar_legowo', 'tegel'."
                ),
                field="planting_system",
            )
        return ps


dss_service = DSSService()
