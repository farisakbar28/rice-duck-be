"""Active lookup/default metadata for frozen Model C only."""

from app.domain.models import ParameterMetadata, PlantingSystem, RiceVariety


RICE_VARIETIES = [
    RiceVariety(
        code="sertani",
        label="Sertani / Seratih",
        risk_note="Variety is a reference gate only; it does not modify C0 yield.",
        status="reference-only",
    ),
    RiceVariety(
        code="inpari",
        label="Inpari (Generic)",
        risk_note="Variety is a reference gate only; it does not modify C0 yield.",
        status="reference-only",
    ),
]
PLANTING_SYSTEMS = [
    PlantingSystem(
        code="jajar_legowo",
        label="Jajar Legowo",
        recommended_density_min_are=2.0,
        recommended_density_max_are=4.0,
        note="Recommended density 2–4 ducks/are; yield remains C0.",
    ),
    PlantingSystem(
        code="tegel",
        label="Tegel",
        recommended_density_min_are=2.0,
        recommended_density_max_are=3.0,
        note="Recommended density 2–3 ducks/are; yield remains C0.",
    ),
]
PARAMETER_METADATA = {
    "Y0_C": ParameterMetadata(
        value=50.0,
        unit="kg/are",
        source="farmer-grouped calibration",
        status="local-calibrated",
        note="25 calibration cycles, 13 farmers; C0 selected by one-standard-error rule.",
        minimum=42.81,
        maximum=55.78,
    ),
    "p_gabah": ParameterMetadata(
        value=6000,
        unit="Rp/kg",
        source="calibration records",
        status="local-calibrated",
        note="Median of 25 calibration price records.",
    ),
    "p_duck_buy": ParameterMetadata(
        value=25000,
        unit="Rp/ekor",
        source="calibration records",
        status="local-calibrated",
        note="Median of 21 positive calibration records.",
    ),
    "p_duck_sell": ParameterMetadata(
        value=45000,
        unit="Rp/ekor",
        source="expert scenario",
        status="local-estimate",
        note="All-sold scenario ceiling, not realized-sale prediction.",
    ),
}
