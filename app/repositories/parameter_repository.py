from app.data.seed import ACTIVE_PARAMETER_SET
from app.domain.models import ParameterSet


class ParameterRepository:
    def get_active(self) -> ParameterSet:
        return ACTIVE_PARAMETER_SET

    def get_by_id(self, parameter_set_id: str) -> ParameterSet | None:
        if parameter_set_id == ACTIVE_PARAMETER_SET.id:
            return ACTIVE_PARAMETER_SET
        return None


parameter_repository = ParameterRepository()

