from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class PredictionPayload(BaseModel):
    machine_id: str
    temperature_c: float
    vibration_hz: float
    pressure_bar: float
    hours_ahead: int = 24


@router.post("/predictions")
def get_predictions(payload: PredictionPayload):
    predicted_load = round(payload.temperature_c * 0.8 + payload.vibration_hz * 0.3 + payload.pressure_bar * 0.2, 2)
    return {
        "machine_id": payload.machine_id,
        "predicted_load_kw": predicted_load,
        "hours_ahead": payload.hours_ahead,
        "status": "ok",
    }
