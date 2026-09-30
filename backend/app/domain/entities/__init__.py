"""Entités portant l'identité et le cycle de vie des objets métier."""

from app.domain.entities.energy_consumption import EnergyConsumption
from app.domain.entities.invoice import Invoice
from app.domain.entities.machine import Machine
from app.domain.entities.sensor_reading import SensorReading

__all__ = ["EnergyConsumption", "Invoice", "Machine", "SensorReading"]
