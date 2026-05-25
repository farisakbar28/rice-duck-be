from app.domain.models import ParameterSet
from app.repositories.parameter_repository import parameter_repository
from app.schemas.parameters import (
    BiologicalConstantsResponse,
    EmissionConstantsResponse,
    MarketPricesResponse,
    OptimizationParametersResponse,
    ParameterSetResponse,
)


class ParameterService:
    def get_active_parameter_set(self) -> ParameterSetResponse:
        parameter_set = parameter_repository.get_active()
        return self._to_response(parameter_set)

    def _to_response(self, parameter_set: ParameterSet) -> ParameterSetResponse:
        return ParameterSetResponse(
            id=parameter_set.id,
            name=parameter_set.name,
            version=parameter_set.version,
            calibration_status=parameter_set.calibration_status.value,
            market_prices=MarketPricesResponse(**parameter_set.market_prices.__dict__),
            biological_constants=BiologicalConstantsResponse(
                **parameter_set.biological_constants.__dict__
            ),
            emission_constants=EmissionConstantsResponse(
                **parameter_set.emission_constants.__dict__
            ),
            optimization=OptimizationParametersResponse(**parameter_set.optimization.__dict__),
        )


parameter_service = ParameterService()

