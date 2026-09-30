"""Création différée du client Supabase configuré."""

from supabase import Client, create_client

from app.config.settings import settings


def create_supabase_client() -> Client:
    """Crée le client Supabase ou échoue clairement si ses identifiants manquent."""
    if not settings.SUPABASE_URL or not settings.SUPABASE_SERVICE_ROLE_KEY:
        raise RuntimeError("SUPABASE_URL et SUPABASE_SERVICE_ROLE_KEY sont requis")
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_ROLE_KEY)
