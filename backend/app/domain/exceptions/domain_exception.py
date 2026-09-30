"""Classe de base des erreurs exprimant une règle métier violée."""


class DomainException(Exception):
    """Erreur métier destinée à être traduite par une couche externe."""

    code = "DOMAIN_ERROR"
