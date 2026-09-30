"""Routeurs HTTP publiés par l'API versionnée."""

from app.presentation.api.v1.routes import (
    admin,
    billing,
    copilot,
    health,
    machines,
    ml,
    predictions,
    recommendations,
    reports,
)

__all__ = [
    "admin",
    "billing",
    "copilot",
    "health",
    "machines",
    "ml",
    "predictions",
    "recommendations",
    "reports",
]
