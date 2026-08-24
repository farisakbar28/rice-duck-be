"""Active A+C lookup and frozen metadata; legacy coefficients are not seeded."""
from app.domain.models import DSSConstants, ParameterMetadata, PlantingSystem, RiceVariety

RICE_VARIETIES=[
    RiceVariety(code="sertani",label="Sertani / Seratih",hst_panen_min=0,hst_panen_max=0,risk_note="Variety is a reference code only; it does not modify C0 production yield.",status="local-reference"),
    RiceVariety(code="inpari",label="Inpari",hst_panen_min=0,hst_panen_max=0,risk_note="Variety is a reference code only; it does not modify C0 production yield.",status="local-reference"),
]
PLANTING_SYSTEMS=[
    PlantingSystem(code="jajar_legowo",label="Jajar Legowo",recommended_density_max_are=4.0,recommended_density_min_are=2.0,note="Recommended density 2–4 ducks/are; no production-yield multiplier."),
    PlantingSystem(code="tegel",label="Tegel",recommended_density_max_are=3.0,recommended_density_min_are=2.0,note="Recommended density 2–3 ducks/are; no production-yield multiplier."),
]
DSS_CONSTANTS=DSSConstants(duck_sale_price_rp_per_duck=45000.0,duck_buy_price_rp_per_duck=25000.0,rice_duck_price_rp_per_kg=6000.0,duck_target_out_max_days=60,calibration_note="A+C: frozen C0=50 kg/are; Xiong is optional literature reference only.")
PARAMETER_METADATA={
    "Y0_C":ParameterMetadata(value=50.0,unit="kg/are",source="25 calibration cycles / 13 farmers",status="local-calibrated",note="Frozen C0 primary baseline selected by farmer-grouped LOFO one-standard-error rule."),
    "p_gabah":ParameterMetadata(value=6000.0,unit="Rp/kg",source="calibration partition",status="local-calibrated",note="Runtime value overrides fallback."),
    "p_duck_buy":ParameterMetadata(value=25000.0,unit="Rp/duck",source="calibration partition",status="local-calibrated",note="Runtime zero is valid and never falls back."),
    "p_duck_sell":ParameterMetadata(value=45000.0,unit="Rp/duck",source="expert scenario",status="local-estimate",note="All-sold scenario fallback."),
}
