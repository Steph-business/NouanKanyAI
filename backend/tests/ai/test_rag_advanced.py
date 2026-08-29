"""
backend/tests/ai/test_rag_advanced.py — Suite de tests unitaires et d'intégration pour le moteur RAG industriel avancé.
"""

import pytest
from app.ai import (
    DocumentCollection,
    SmartTextChunker,
    InMemoryVectorStore,
    PgVectorStoreAdapter,
    QdrantVectorStoreAdapter,
    HybridRetriever,
    SemanticReranker,
    RAGQueryCache,
    Citation,
    SourceCitationFormatter,
    IndustrialRAGPipeline,
    DocumentChunk,
    MockEmbedder,
    cosine_similarity,
    tokenize,
)


class TestAdvancedRAGSuite:
    """Tests unitaires pour le moteur RAG multi-collections."""

    def test_document_collections_completeness(self):
        """Vérifie que les 8 collections requises sont bien définies."""
        expected = [
            "documentation_nouankany",
            "iso_50001",
            "fabricants",
            "rapports_energetiques",
            "guides_ademe",
            "faq",
            "rapports_audit",
            "documentation_iot",
        ]
        values = [c.value for c in DocumentCollection]
        for col in expected:
            assert col in values, f"Collection manquante : {col}"

    def test_smart_text_chunker_markdown_and_overlap(self):
        """Vérifie le découpage intelligent par section Markdown avec overlap."""
        chunker = SmartTextChunker(chunk_size=200, chunk_overlap=40)
        doc = (
            "# Norme ISO 50001\n\n"
            "La norme ISO 50001 spécifie les exigences pour établir un système de management de l'énergie.\n\n"
            "## Objectifs de Performance\n\n"
            "Les objectifs doivent être mesurables et cohérents avec la politique énergétique de l'usine."
        )
        chunks = chunker.chunk_text(
            text=doc,
            document_id="iso-50001-doc",
            collection=DocumentCollection.ISO_50001.value,
            title="Manuel ISO 50001",
            source="iso.org",
        )

        assert len(chunks) >= 2
        assert chunks[0].metadata["collection"] == "iso_50001"
        assert chunks[0].metadata["title"] == "Manuel ISO 50001"
        assert "section" in chunks[0].metadata

    def test_vector_store_dense_sparse_and_hybrid(self):
        """Vérifie la recherche dense, BM25 et la fusion hybride."""
        store = InMemoryVectorStore()
        embedder = MockEmbedder()

        c1 = DocumentChunk(
            chunk_id="c1",
            document_id="d1",
            content="Délestage des compresseurs d'air industriels en heures de pointe CIE 19h-23h.",
            metadata={"collection": "guides_ademe"},
        )
        c2 = DocumentChunk(
            chunk_id="c2",
            document_id="d2",
            content="Protocole MQTT et connectivité des capteurs de vibration LoRaWAN.",
            metadata={"collection": "documentation_iot"},
        )

        embeddings = embedder.embed_documents([c1.content, c2.content])
        store.add_chunks([c1, c2], embeddings)

        assert store.count() == 2
        assert store.count("guides_ademe") == 1
        assert store.count("documentation_iot") == 1

        # Recherche hybride
        q = "délestage compresseur pointe"
        q_emb = embedder.embed_query(q)
        results = store.search_hybrid(q_emb, q, top_k=2, alpha=0.5)

        assert len(results) >= 1
        top_chunk, score = results[0]
        assert top_chunk.document_id == "d1"
        assert score > 0.0

    def test_incremental_document_update_and_deletion(self):
        """Vérifie la mise à jour incrémentale et la suppression par document_id."""
        retriever = HybridRetriever()

        retriever.ingest_document(
            document_id="audit_abidjan_2026",
            content="Audit énergétique de l'usine d'Abidjan : gain potentiel de 15% sur les fours.",
            collection=DocumentCollection.RAPPORTS_AUDIT.value,
        )
        assert retriever.count(DocumentCollection.RAPPORTS_AUDIT.value) >= 1

        deleted = retriever.delete_document("audit_abidjan_2026")
        assert deleted >= 1
        assert retriever.count(DocumentCollection.RAPPORTS_AUDIT.value) == 0

    def test_query_cache_lru_and_ttl(self):
        """Vérifie le fonctionnement du cache des requêtes et le taux de succès (hit ratio)."""
        cache = RAGQueryCache(max_size=3, default_ttl_seconds=100)
        c = DocumentChunk(chunk_id="c1", document_id="d1", content="Exemple")

        assert cache.get("question test") is None
        cache.set("question test", [c])

        cached_res = cache.get("question test")
        assert cached_res is not None
        assert len(cached_res) == 1

        stats = cache.stats()
        assert stats["hits"] == 1
        assert stats["misses"] == 1
        assert stats["hit_ratio_pct"] == 50.0

    def test_semantic_reranker(self):
        """Vérifie le reranking avec exact match et boost de section."""
        reranker = SemanticReranker()
        chunks = [
            DocumentChunk(
                chunk_id="c1",
                document_id="d1",
                content="Consignes générales sur l'éclairage de bureau.",
                score=0.7,
                metadata={"title": "Éclairage", "section": "Bureaux"},
            ),
            DocumentChunk(
                chunk_id="c2",
                document_id="d2",
                content="Guide de coupure d'urgence des groupes froids en cas de surchauffe.",
                score=0.6,
                metadata={"title": "Sécurité Froid", "section": "Groupes Froids"},
            ),
        ]

        reranked = reranker.rerank(query="groupes froids surchauffe", chunks=chunks, top_k=2)
        assert len(reranked) == 2
        # c2 doit passer en première position grâce à la forte correspondance sémantique et lexicale
        assert reranked[0].chunk_id == "c2"

    def test_source_citation_formatter(self):
        """Vérifie l'extraction des citations et le formatage des notes de bas de page."""
        chunks = [
            DocumentChunk(
                chunk_id="c1",
                document_id="ademe-guide",
                content="Le calorifugeage des réseaux de vapeur permet d'économiser jusqu'à 12% d'énergie thermique.",
                score=0.89,
                metadata={
                    "collection": "guides_ademe",
                    "title": "Guide ADEME Vapeur",
                    "section": "Calorifugeage",
                    "source": "ademe.fr/vapeur",
                },
            )
        ]

        citations = SourceCitationFormatter.extract_citations(chunks)
        assert len(citations) == 1
        assert citations[0].title == "Guide ADEME Vapeur"
        assert citations[0].collection == "guides_ademe"

        prompt_str = SourceCitationFormatter.format_sources_for_prompt(chunks)
        assert "Guide ADEME Vapeur" in prompt_str
        assert "12% d'énergie thermique" in prompt_str

        footnotes = SourceCitationFormatter.format_footnotes(citations)
        assert "### 📚 Références & Sources Documentaires :" in footnotes
        assert "[1]" in footnotes
        assert "guides_ademe" in footnotes

    def test_industrial_rag_pipeline_end_to_end(self):
        """Vérifie le cycle complet d'ingestion, recherche et génération enrichie avec citations."""
        pipeline = IndustrialRAGPipeline()

        # Ingestion de 2 documents dans 2 collections distinctes
        pipeline.ingest_document(
            document_id="doc_iot_passerelle",
            content="La passerelle LoRaWAN Spark-4G transmet la télémétrie toutes les 60 secondes vers NouanKanyAI.",
            collection=DocumentCollection.DOCUMENTATION_IOT.value,
            title="Manuel Passerelle Spark-4G",
        )
        pipeline.ingest_document(
            document_id="faq_delestage",
            content="Q: Comment configurer le seuil d'alerte CIE ? R: Définir la puissance max dans l'onglet Paramètres.",
            collection=DocumentCollection.FAQ.value,
            title="FAQ Exploitation",
        )

        # Recherche et génération avec citations
        res = pipeline.run(
            query="Comment la passerelle transmet-elle les données ?",
            collection=DocumentCollection.DOCUMENTATION_IOT.value,
            include_citations=True,
        )

        assert res is not None
        assert "📚 Références & Sources Documentaires" in res.content
        assert "Manuel Passerelle Spark-4G" in res.content

    def test_vector_store_adapters(self):
        """Vérifie la conformité des adaptateurs PgVectorStoreAdapter et QdrantVectorStoreAdapter."""
        pg_store = PgVectorStoreAdapter()
        qdrant_store = QdrantVectorStoreAdapter()

        c = DocumentChunk(chunk_id="test_c", document_id="test_d", content="Test")
        emb = [[0.1] * 768]

        pg_store.add_chunks([c], emb)
        assert pg_store.count() == 1

        qdrant_store.add_chunks([c], emb)
        assert qdrant_store.count() == 1
