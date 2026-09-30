"""Identifiant métier immuable d'une machine industrielle."""

from dataclasses import dataclass


@dataclass(frozen=True)
class MachineId:
    """Valeur normalisée identifiant une machine dans le domaine."""

    value: str

    def __post_init__(self) -> None:
        normalized = self.value.strip()
        if not normalized:
            raise ValueError("L'identifiant de machine ne peut pas être vide")
        object.__setattr__(self, "value", normalized)

    def __str__(self) -> str:
        return self.value
