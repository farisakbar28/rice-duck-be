from enum import Enum


class LandAreaUnit(str, Enum):
    ARE = "are"
    HECTARE = "hectare"


class DuckEconomicModel(str, Enum):
    LOCAL_GROSS = "local_gross"


class RiskLevel(str, Enum):
    NORMAL = "normal"
    WASPADA = "waspada"
    BAHAYA = "bahaya"


class CalibrationStatus(str, Enum):
    INITIAL_ASSUMPTION = "initial_assumption"
    LITERATURE_BASED = "literature_based"
    FIELD_VALIDATED = "field_validated"
    REQUIRES_LOCAL_VALIDATION = "requires_local_validation"


class EmissionStatus(str, Enum):
    NOT_CALCULATED = "not_calculated"
    LIMITED = "limited"

