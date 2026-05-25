from datetime import datetime, timezone
from uuid import uuid4

from app.domain.models import SimulationRecord


class SimulationRepository:
    def __init__(self) -> None:
        self._records: list[SimulationRecord] = []

    def create(self, request_payload: dict, response_payload: dict) -> SimulationRecord:
        record = SimulationRecord(
            id=str(uuid4()),
            created_at=datetime.now(timezone.utc),
            request_payload=request_payload,
            response_payload=response_payload,
        )
        self._records.append(record)
        return record

    def update_response_payload(self, simulation_id: str, response_payload: dict) -> SimulationRecord | None:
        record = self.get_by_id(simulation_id)
        if record is None:
            return None
        record.response_payload = response_payload
        return record

    def list_all(self) -> list[SimulationRecord]:
        return sorted(self._records, key=lambda item: item.created_at, reverse=True)

    def get_by_id(self, simulation_id: str) -> SimulationRecord | None:
        return next((item for item in self._records if item.id == simulation_id), None)


simulation_repository = SimulationRepository()
