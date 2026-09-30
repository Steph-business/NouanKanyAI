"""Client Supabase et implémentations des dépôts métier."""

from app.infrastructure.persistence.supabase.client import create_supabase_client
from app.infrastructure.persistence.supabase.machine_repository_impl import (
    SupabaseMachineRepository,
)
from app.infrastructure.persistence.supabase.reading_repository_impl import (
    SupabaseReadingRepository,
)

__all__ = ["SupabaseMachineRepository", "SupabaseReadingRepository", "create_supabase_client"]
