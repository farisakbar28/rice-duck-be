"""Phase 3: GET /api/v1/dss/options -- canonical R2 seed/registry contract."""

from tests.r2_api_utils import API, make_client


def test_options_shape_matches_r2_registry() -> None:
    client = make_client()
    response = client.get(f"{API}/dss/options")
    assert response.status_code == 200
    body = response.json()

    assert body["model_version"] == "R2"

    varieties = {item["code"]: item for item in body["rice_varieties"]}
    assert set(varieties) == {"sertani", "inpari"}
    assert varieties["sertani"]["label"] == "Sertani / Seratih"
    assert (varieties["sertani"]["harvest_hst_min"], varieties["sertani"]["harvest_hst_max"]) == (100, 110)
    assert (varieties["inpari"]["harvest_hst_min"], varieties["inpari"]["harvest_hst_max"]) == (90, 100)
    for item in varieties.values():
        assert item["calendar_status"] == "local-estimate"
        assert item["yield_lookup_status"] == "ACTIVE_RANGE"

    systems = {item["code"]: item for item in body["planting_systems"]}
    assert set(systems) == {"jajar_legowo", "tegel"}
    assert (systems["jajar_legowo"]["supported_density_min_are"], systems["jajar_legowo"]["supported_density_max_are"]) == (2.0, 4.0)
    assert (systems["tegel"]["supported_density_min_are"], systems["tegel"]["supported_density_max_are"]) == (2.0, 3.0)

    price = body["purchase_price"]
    assert price["optional"] is True
    assert price["default_rp_per_duck"] == 26500
    assert price["local_range_rp_per_duck"] == [25000, 28000]
    assert price["status"] == "mixed"


def test_options_exposes_no_legacy_or_yield_multiplier_fields() -> None:
    client = make_client()
    raw = client.get(f"{API}/dss/options").text

    banned_fragments = [
        "F_sys",
        "Y_base",
        "47.8767507",
        "52500",
        '"p_duck_sell',
        "feed_price",
        "9500",
        "HST_in",
        "HST_out",
        "t_active",
        "Net_Cash_Contribution_DSS",
    ]
    for fragment in banned_fragments:
        assert fragment not in raw, f"banned field/constant leaked into options: {fragment}"

    variety_keys = set(client.get(f"{API}/dss/options").json()["rice_varieties"][0])
    assert "yield_multiplier" not in variety_keys
    assert "f_yield" not in variety_keys
