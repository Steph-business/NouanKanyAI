"""Use case de prévision de consommation pour une machine active."""

from app.application.dto.prediction_dto import (
    PredictConsumptionCommand,
    PredictConsumptionResult,
)
from app.application.ports.ml_service import MLService
from app.domain.exceptions.specific_exceptions import MachineNotFoundError
from app.domain.repositories.machine_repository import MachineRepository
from app.domain.value_objects.machine_id import MachineId


class PredictConsumptionUseCase:
    """Charge une machine puis demande une prévision au port ML."""

    def __init__(self, machine_repo: MachineRepository, ml_service: MLService) -> None:
        self.machine_repo = machine_repo
        self.ml_service = ml_service

    async def execute(self, cmd: PredictConsumptionCommand) -> PredictConsumptionResult:
        """Valide la demande, vérifie la machine et retourne ses valeurs prévues."""
        if not 1 <= cmd.horizon_hours <= 168:
            raise ValueError("L'horizon doit être compris entre 1 et 168 heures")
        machine_id = MachineId(cmd.machine_id)
        machine = await self.machine_repo.get_by_id(machine_id)
        if machine is None:
            raise MachineNotFoundError(str(machine_id))
        if not machine.is_active:
            raise ValueError("La prévision exige une machine active")

        forecast = await self.ml_service.forecast(str(machine_id), cmd.horizon_hours)
        if len(forecast.values) != cmd.horizon_hours:
            raise ValueError("Le service ML a retourné un horizon incomplet")
        return PredictConsumptionResult(
            machine_id=str(machine_id),
            predictions=forecast.values,
            confidence_interval=(forecast.lower, forecast.upper),
            model_version=self.ml_service.version,
        )
