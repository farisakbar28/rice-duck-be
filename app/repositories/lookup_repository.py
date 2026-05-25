from app.data.seed import PLANTING_SYSTEMS, RICE_VARIETIES
from app.domain.models import PlantingSystem, RiceVariety


class LookupRepository:
    def list_rice_varieties(self) -> list[RiceVariety]:
        return list(RICE_VARIETIES)

    def list_planting_systems(self) -> list[PlantingSystem]:
        return list(PLANTING_SYSTEMS)

    def get_rice_variety(self, code: str) -> RiceVariety | None:
        normalized = code.strip().lower()
        return next((item for item in RICE_VARIETIES if item.code == normalized), None)

    def get_planting_system(self, code: str) -> PlantingSystem | None:
        normalized = code.strip().lower()
        return next((item for item in PLANTING_SYSTEMS if item.code == normalized), None)


lookup_repository = LookupRepository()

