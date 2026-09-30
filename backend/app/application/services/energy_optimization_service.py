"""Service métier d'application proposant une réduction lors d'une surcharge."""

from dataclasses import dataclass

from app.domain.entities.machine import Machine


@dataclass(frozen=True)
class OptimizationRecommendation:
    """Action suggérée et puissance cible à appliquer à une machine."""

    machine_id: str
    overloaded: bool
    current_power_kw: float
    recommended_power_kw: float
    message: str


class EnergyOptimizationService:
    """Transforme les limites d'une machine en recommandation actionnable."""

    def recommend(self, machine: Machine, current_power_kw: float) -> OptimizationRecommendation:
        """Propose de rester à 90 % de la puissance max si la machine est surchargée."""
        if current_power_kw < 0:
            raise ValueError("La puissance mesurée ne peut pas être négative")
        overloaded = machine.is_overloaded(current_power_kw)
        target = min(current_power_kw, machine.max_power_kw * 0.9)
        message = (
            "Réduire la charge pour revenir sous le seuil de 90 %."
            if overloaded
            else "La puissance reste dans la plage de fonctionnement recommandée."
        )
        return OptimizationRecommendation(
            machine_id=str(machine.id),
            overloaded=overloaded,
            current_power_kw=current_power_kw,
            recommended_power_kw=target,
            message=message,
        )
