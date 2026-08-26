"""Phase 5: freeze governance semantics (docs/11_R2_FREEZE_MANIFEST.md).

Proves:
  * response model metadata sources ``frozen``/``freeze_id`` from the freeze
    configuration instead of a hardcoded literal;
  * simulation and visualization expose identical freeze identity;
  * FREEZE_ID stays a distinct provenance dimension (not model version, not
    registry version, not app version, not history schema version, not a Git
    SHA);
  * the scientific parameter surface is unchanged from the approved Phase-4
    candidate 39fd69fbfa207862ce4da5be5d4f75e06eed6bdb;
  * frozen does NOT change availability semantics: yield/feed stay
    unavailable, full profit stays null.

The Phase-4 expected values below come from the canonical R2 documentation
(docs/01 SSOT, docs/04 registry, docs/10 provenance), NOT from historical
recap data. Recap is comparator-only and is never an oracle here.
"""

import re

from fastapi.testclient import TestClient

import app.data.seed as seed
from app.core.config import settings
from app.main import app
from tests.r2_api_utils import API, DEFAULT_SIMULATION_PAYLOAD, make_client

PHASE5C_REGISTRY_VERSION = "R2-2026-08-26.3"
PHASE6CC_FREEZE_ID = "R2-FREEZE-2026-08-26.4"

# Approved Phase-4 scientific snapshot (docs/01/docs/04/docs/10). Any drift
# here means a scientific change happened outside a formally approved
# pre-freeze review -- a release blocker for the frozen candidate.
PHASE4_PARAMETER_SNAPSHOT: dict[str, object] = {
    "p_duck_buy_default": 26_500,
    "lambda_safe_ref": 0.90,
    "n_need_kg_per_are": 1.1761,
    "p2o5_need_kg_per_are": 0.2745,
    "k2o_need_kg_per_are": 0.2745,
    "het_urea_rp_per_kg": 1_800,
    "het_npk_rp_per_kg": 1_840,
    "urea_n_fraction": 0.46,
    "npk_n_fraction": 0.15,
    "npk_p2o5_fraction": 0.10,
    "npk_k2o_fraction": 0.12,
    "p_gabah_ref_rp_per_kg": 6_500,
    "duck_terminal_value_rp_per_duck": 45_000,
    "active_duration_ref_days": 32,
}
PHASE4_PARAMETER_RANGES: dict[str, tuple[object, object]] = {
    "p_duck_buy_local_range": (25_000, 28_000),
    "release_hst_window": (21, 30),
    "pull_hst_window": (56, 60),
    "active_duration_ref_days": (28, 40),
    "supported_age_window_days": (21, 30),
    "density_limited_test_are": (5, 6),
    "net_price_rp_per_m": (6_000, 6_750),
    "net_lifetime_cycles": (2, 3),
    "cage_cost_per_unit_cycle_rp": (150_000, 200_000),
    "weeding_baseline_rp_per_are": (6_000, 38_000),
    "duck_terminal_value_rp_per_duck": (30_000, 60_000),
}
PHASE4_VARIETY_WINDOWS = {"sertani": (100, 110), "inpari": (90, 100)}
PHASE4_SYSTEM_DENSITIES = {
    "jajar_legowo": (2.0, 4.0),
    "tegel": (2.0, 3.0),
}


def _simulate(client: TestClient, **overrides):
    payload = dict(DEFAULT_SIMULATION_PAYLOAD)
    payload.update(overrides)
    return client.post(f"{API}/dss/simulate", json=payload)


class TestFreezeMetadataSource:
    def test_response_frozen_sourced_from_freeze_config(self) -> None:
        client = make_client()
        body = _simulate(client).json()
        assert body["model"]["frozen"] is seed.MODEL_FROZEN
        assert body["model"]["freeze_id"] == seed.FREEZE_ID

    def test_frozen_flag_is_true_for_phase6cc_candidate(self) -> None:
        assert seed.MODEL_FROZEN is True
        assert seed.FREEZE_ID == PHASE6CC_FREEZE_ID

    def test_visualization_model_matches_simulation_freeze_identity(self) -> None:
        client = make_client()
        sim = _simulate(client).json()["model"]
        viz = client.post(
            f"{API}/dss/visualize", json=DEFAULT_SIMULATION_PAYLOAD
        ).json()["model"]
        assert viz["frozen"] == sim["frozen"] is True
        assert viz["freeze_id"] == sim["freeze_id"]

    def test_persisted_v4_snapshot_keeps_freeze_identity(self) -> None:
        from tests.r2_api_utils import register_and_login

        client = make_client()
        headers = register_and_login(client)
        payload = dict(DEFAULT_SIMULATION_PAYLOAD)
        body = client.post(
            f"{API}/dss/simulate", json=payload, headers=headers
        ).json()
        history_id = client.get(
            f"{API}/dss/histories", headers=headers
        ).json()["data"][0]["id"]
        stored = client.get(
            f"{API}/dss/histories/{history_id}", headers=headers
        ).json()
        assert stored["model"]["freeze_id"] == body["model"]["freeze_id"]
        assert stored["model"]["frozen"] is True


class TestFreezeIdentityDimensions:
    def test_freeze_id_format(self) -> None:
        assert re.fullmatch(r"R2-FREEZE-\d{4}-\d{2}-\d{2}\.\d+", seed.FREEZE_ID)

    def test_freeze_id_is_not_any_other_version_dimension(self) -> None:
        assert seed.FREEZE_ID != seed.MODEL_VERSION
        assert seed.FREEZE_ID != seed.PARAMETER_REGISTRY_VERSION
        assert seed.FREEZE_ID != settings.app_version
        assert seed.FREEZE_ID != str(seed.MODEL_FROZEN)
        # Not a 40/64-hex Git SHA and not derived from one.
        assert not re.fullmatch(r"[0-9a-f]{40}", seed.FREEZE_ID or "")
        assert not re.fullmatch(r"[0-9a-f]{64}", seed.FREEZE_ID or "")

    def test_registry_version_bumped_for_phase5c_semantics(self) -> None:
        assert seed.PARAMETER_REGISTRY_VERSION == PHASE5C_REGISTRY_VERSION

    def test_model_version_and_history_schema_unchanged(self) -> None:
        assert seed.MODEL_VERSION == "R2"
        client = make_client()
        body = _simulate(client).json()
        assert body["model"]["model_version"] == "R2"
        assert body["model"]["history_schema_version"] == 4


class TestNoScientificDriftSincePhase4:
    def test_scalar_parameters_match_phase4_snapshot(self) -> None:
        for key, expected in PHASE4_PARAMETER_SNAPSHOT.items():
            actual = seed.PARAMETER_REGISTRY[key].value
            if isinstance(expected, float):
                assert actual == pytest_approx(expected), key
            else:
                assert actual == expected, key

    def test_range_parameters_match_phase4_snapshot(self) -> None:
        for key, (lo, hi) in PHASE4_PARAMETER_RANGES.items():
            entry = seed.PARAMETER_REGISTRY[key]
            assert (entry.minimum, entry.maximum) == (lo, hi), key

    def test_variety_windows_match_phase4(self) -> None:
        for v in seed.RICE_VARIETIES:
            expected = PHASE4_VARIETY_WINDOWS[v.code]
            assert (v.harvest_hst_min, v.harvest_hst_max) == expected

    def test_system_densities_match_phase4(self) -> None:
        for s in seed.PLANTING_SYSTEMS:
            expected = PHASE4_SYSTEM_DENSITIES[s.code]
            assert (
                s.supported_density_min_are,
                s.supported_density_max_are,
            ) == expected

    def test_pending_and_unavailable_states_unchanged(self) -> None:
        for key in ("yield_base_by_cultivar_group", "f_rd_lookup"):
            p = seed.PARAMETER_REGISTRY[key]
            assert p.execution_state.value in {"ACTIVE", "ACTIVE_RANGE"}
        for key in (
            "feed_quantity_lookup",
            "feed_price_lookup",
            "cage_capacity_rule",
            "kcl_branch",
        ):
            p = seed.PARAMETER_REGISTRY[key]
            assert p.value is None
            assert p.execution_state.value == "UNAVAILABLE"


class TestFrozenDoesNotChangeAvailability:
    def test_yield_stays_unavailable_after_freeze(self) -> None:
        client = make_client()
        yld = _simulate(client).json()["yield"]
        assert yld["availability"] == "AVAILABLE"
        assert yld["yield_kg_per_are"] == yld["yield_ref_kg_per_are"]
        assert yld["yield_total_kg"] == yld["yield_total_ref_kg"]

    def test_feed_cage_profit_stay_unavailable_after_freeze(self) -> None:
        client = make_client()
        body = _simulate(client).json()
        assert body["costs"]["feed"]["availability"] == "UNAVAILABLE"
        assert body["costs"]["feed"]["amount_rp"] is None
        assert body["costs"]["cage"]["total_amount_rp"] is None
        assert body["costs"]["cost_completeness"] == "INCOMPLETE"
        assert body["economics"]["profit_full_est_rp"] is None
        assert body["duck"]["terminal_value_is_cash_revenue"] is False


def pytest_approx(value: float):
    import pytest

    return pytest.approx(value)
