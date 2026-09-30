"""Traduction des erreurs métier en réponses HTTP standardisées."""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.domain.exceptions.domain_exception import DomainException
from app.domain.exceptions.specific_exceptions import MachineNotFoundError


async def domain_exception_handler(request: Request, exc: DomainException) -> JSONResponse:
    """Retourne une erreur 400 structurée pour une règle métier refusée."""
    return JSONResponse(
        status_code=400,
        content={"error": exc.code, "message": str(exc)},
    )


async def machine_not_found_handler(request: Request, exc: MachineNotFoundError) -> JSONResponse:
    """Traduit l'absence d'une machine métier en réponse HTTP 404."""
    return JSONResponse(
        status_code=404,
        content={"error": exc.code, "message": str(exc)},
    )


def register_exception_handlers(app: FastAPI) -> None:
    """Enregistre d'abord les handlers précis puis le handler métier générique."""
    app.add_exception_handler(MachineNotFoundError, machine_not_found_handler)
    app.add_exception_handler(DomainException, domain_exception_handler)
