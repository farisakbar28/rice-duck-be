"""Frozen A+C lookup metadata. No legacy numerical model constants are seeded."""
from app.domain.models import ParameterMetadata, PlantingSystem, RiceVariety

RICE_VARIETIES = [
    RiceVariety("sertani", "Sertani / Seratih", "Reference code only; does not modify C0 production yield.", "local-reference"),
    RiceVariety("inpari", "Inpari", "Reference code only; does not modify C0 production yield.", "local-reference"),
]
PLANTING_SYSTEMS = [
    PlantingSystem("jajar_legowo", "Jajar Legowo", 2.0, 4.0, "Recommended density 2–4 ducks/are; no production-yield multiplier."),
    PlantingSystem("tegel", "Tegel", 2.0, 3.0, "Recommended density 2–3 ducks/are; no production-yield multiplier."),
]
PARAMETER_METADATA = {
    "Y0_C": ParameterMetadata(50.0, "kg/are", "25 calibration cycles / 13 farmers", "local-calibrated", "Frozen primary C0 baseline selected by farmer-grouped LOFO one-standard-error rule."),
    "density_recommended_jarwo": ParameterMetadata(4.0, "ducks/are", "current lookup", "system-design", "Jajar Legowo recommended upper boundary.", 2.0, 4.0),
    "density_recommended_tegel": ParameterMetadata(3.0, "ducks/are", "current lookup", "system-design", "Tegel recommended upper boundary.", 2.0, 3.0),
    "release_hst": ParameterMetadata([21, 30], "HST", "local evidence", "local-estimate", "Recommendation release window."),
    "withdraw_hst": ParameterMetadata([56, 60], "HST", "local evidence", "local-estimate", "Recommendation withdrawal window."),
    "p_gabah": ParameterMetadata(6000.0, "Rp/kg", "calibration partition", "local-calibrated", "Runtime value overrides fallback."),
    "p_duck_buy": ParameterMetadata(25000.0, "Rp/duck", "calibration partition", "local-calibrated", "Runtime zero is valid and never falls back."),
    "p_duck_sell": ParameterMetadata(45000.0, "Rp/duck", "expert scenario", "local-estimate", "All-sold scenario fallback."),
    "xiong_density_ha": ParameterMetadata([0, 600], "ducks/ha", "Xiong et al. (2014)", "literature-uncalibrated", "Practical/general validity guard; lower bound is exclusive."),
    "xiong_duration_days": ParameterMetadata([50, 80], "days", "Xiong et al. (2014)", "literature-uncalibrated", "Explicit literature duration validity guard."),
}
