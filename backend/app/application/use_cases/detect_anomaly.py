"""Use case d'analyse des relevés récents d'une machine."""

from app.application.dto.anomaly_dto import DetectAnomalyCommand, DetectAnomalyResult
from app.application.ports.ml_service import MLService
from app.domain.entities.sensor_reading import SensorReading
from app.domain.repositories.reading_repository import ReadingRepository
from app.domain.value_objects.machine_id import MachineId


class DetectAnomalyUseCase:
    """Charge les mesures et délègue leur analyse au port ML."""

    def __init__(self, reading_repo: ReadingRepository, ml_service: MLService) -> None:
        self.reading_repo = reading_repo
        self.ml_service = ml_service

    async def execute(self, cmd: DetectAnomalyCommand) -> DetectAnomalyResult:
        """Analyse jusqu'à 100 mesures de puissance et renvoie un diagnostic typé."""
        machine_id = MachineId(cmd.machine_id)
        if cmd.start and cmd.end and cmd.start > cmd.end:
            raise ValueError("Le début de période doit précéder sa fin")
        readings: list[SensorReading] = await self.reading_repo.list_for_machine(
            machine_id, start=cmd.start, end=cmd.end
        )
        if not readings:
            raise ValueError("Aucun relevé disponible pour cette machine")
        recent_readings = readings[-100:]
        diagnostic = await self.ml_service.detect_anomaly(recent_readings)
        return DetectAnomalyResult(
            machine_id=str(machine_id),
            is_anomaly=diagnostic.is_anomaly,
            score=diagnostic.score,
            severity=diagnostic.severity,
            model_version=self.ml_service.version,
            readings_analyzed=len(recent_readings),
        )
