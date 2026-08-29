"""
app/ai/citations.py — Traçabilité, citations et références documentaires pour le RAG.

Extrait les métadonnées de provenance (source, collection, section, document_id, score)
et génère des citations structurées et des notes de bas de page claires pour l'utilisateur.
"""

import logging
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field
from app.ai.types import DocumentChunk

logger = logging.getLogger("nouankany.ai")


class Citation(BaseModel):
    """
    Référence documentaire unitaire pour justifier une réponse RAG.
    """

    model_config = ConfigDict(frozen=True)

    index: int = Field(..., description="Numéro d'ordre de la citation (ex: [1])")
    document_id: str = Field(..., description="Identifiant du document source")
    collection: str = Field(..., description="Collection documentaire")
    title: str = Field(..., description="Titre ou nom du document")
    section: str = Field(default="Général", description="Section ou paragraphe d'origine")
    source: str = Field(default="interne", description="Chemin ou URL source")
    snippet: str = Field(..., description="Extrait textuel concis")
    score: Optional[float] = Field(default=None, description="Score de pertinence")


class SourceCitationFormatter:
    """
    Formateur de citations et de références documentaires.
    """

    @classmethod
    def extract_citations(cls, chunks: List[DocumentChunk]) -> List[Citation]:
        """Convertit une liste de `DocumentChunk` en liste ordonnée de `Citation`."""
        citations: List[Citation] = []
        for idx, c in enumerate(chunks, start=1):
            meta = c.metadata or {}
            snippet_text = c.content[:200].replace("\n", " ").strip()
            if len(c.content) > 200:
                snippet_text += "..."

            citations.append(
                Citation(
                    index=idx,
                    document_id=c.document_id,
                    collection=meta.get("collection", "général"),
                    title=meta.get("title", c.document_id),
                    section=meta.get("section", "Général"),
                    source=meta.get("source", "interne"),
                    snippet=snippet_text,
                    score=c.score,
                )
            )
        return citations

    @classmethod
    def format_sources_for_prompt(cls, chunks: List[DocumentChunk]) -> str:
        """Formate les chunks sous forme de bloc Markdown prêt pour l'injection dans le prompt."""
        if not chunks:
            return ""

        blocks = []
        for idx, c in enumerate(chunks, start=1):
            meta = c.metadata or {}
            title = meta.get("title", c.document_id)
            section = meta.get("section", "Général")
            collection = meta.get("collection", "général")
            score_str = f" (Score: {c.score:.2f})" if c.score is not None else ""

            header = f"[{idx}] Source: {title} | Section: {section} | Collection: {collection}{score_str}"
            blocks.append(f"{header}\n{c.content}")

        return "\n\n".join(blocks)

    @classmethod
    def format_footnotes(cls, citations: List[Citation]) -> str:
        """Génère la section des références en bas de réponse pour l'utilisateur final."""
        if not citations:
            return ""

        lines = ["\n\n### 📚 Références & Sources Documentaires :"]
        for cite in citations:
            score_badge = f" — Pertinence: {int(cite.score * 100)}%" if cite.score else ""
            lines.append(
                f"- **[{cite.index}]** *{cite.title}* ({cite.collection}) — Section *{cite.section}*{score_badge}\n"
                f"  > « {cite.snippet} »"
            )

        return "\n".join(lines)
