"""
app/ai/query_cache.py — Cache intelligent des requêtes et résultats RAG (LRU + TTL).

Évite les calculs redondants d'embeddings et les recherches vectorielles répétitives
pour les questions fréquentes sur les procédures, fiches machines ou réglementations.
"""

from collections import OrderedDict
import hashlib
import json
import logging
import threading
import time
from typing import Any, Dict, List, Optional
from app.ai.types import DocumentChunk

logger = logging.getLogger("nouankany.ai")


class RAGQueryCache:
    """
    Cache mémoire LRU thread-safe avec expiration temporelle (TTL).
    """

    def __init__(self, max_size: int = 500, default_ttl_seconds: int = 3600) -> None:
        """
        :param max_size: Nombre maximal de requêtes en cache.
        :param default_ttl_seconds: Durée de validité des entrées (par défaut 1 heure).
        """
        self.max_size = max_size
        self.default_ttl = default_ttl_seconds
        self._cache: OrderedDict[str, tuple[List[DocumentChunk], float]] = OrderedDict()
        self._lock = threading.RLock()
        self._hits = 0
        self._misses = 0
        logger.debug(f"[RAGQueryCache] Initialisé (max_size={max_size}, ttl={default_ttl_seconds}s).")

    def _build_key(
        self,
        query: str,
        collection: Optional[str] = None,
        top_k: int = 3,
        filters: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Génère une clé de hachage SHA-256 déterministe."""
        raw_key = {
            "q": query.strip().lower(),
            "col": collection or "all",
            "top_k": top_k,
            "filters": sorted(filters.items()) if filters else [],
        }
        return hashlib.sha256(json.dumps(raw_key, sort_keys=True).encode("utf-8")).hexdigest()

    def get(
        self,
        query: str,
        collection: Optional[str] = None,
        top_k: int = 3,
        filters: Optional[Dict[str, Any]] = None,
    ) -> Optional[List[DocumentChunk]]:
        """Récupère les résultats en cache s'ils existent et ne sont pas expirés."""
        key = self._build_key(query, collection, top_k, filters)
        now = time.time()

        with self._lock:
            if key in self._cache:
                chunks, expire_at = self._cache[key]
                if now < expire_at:
                    self._cache.move_to_end(key)
                    self._hits += 1
                    logger.debug(f"[RAGQueryCache] HIT pour la requête '{query[:30]}...'")
                    return chunks
                else:
                    del self._cache[key]

            self._misses += 1
            return None

    def set(
        self,
        query: str,
        chunks: List[DocumentChunk],
        collection: Optional[str] = None,
        top_k: int = 3,
        filters: Optional[Dict[str, Any]] = None,
        ttl_seconds: Optional[int] = None,
    ) -> None:
        """Enregistre les résultats dans le cache LRU."""
        key = self._build_key(query, collection, top_k, filters)
        ttl = ttl_seconds or self.default_ttl
        expire_at = time.time() + ttl

        with self._lock:
            if key in self._cache:
                self._cache.move_to_end(key)
            self._cache[key] = (chunks, expire_at)

            # Éviction LRU si dépassement de capacité
            while len(self._cache) > self.max_size:
                self._cache.popitem(last=False)

    def clear(self) -> None:
        """Vide l'intégralité du cache."""
        with self._lock:
            self._cache.clear()
            self._hits = 0
            self._misses = 0

    def stats(self) -> Dict[str, Any]:
        """Retourne les métriques de performance du cache."""
        with self._lock:
            total = self._hits + self._misses
            hit_ratio = round((self._hits / total) * 100.0, 2) if total > 0 else 0.0
            return {
                "size": len(self._cache),
                "max_size": self.max_size,
                "hits": self._hits,
                "misses": self._misses,
                "hit_ratio_pct": hit_ratio,
            }
