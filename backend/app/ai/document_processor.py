"""
app/ai/document_processor.py — Ingestion documentaire et découpage intelligent (Smart Chunking).

Découpe les documents textuels, Markdown et JSON en segments optimisés (chunks)
tout en préservant la hiérarchie des titres, les paragraphes et les métadonnées de collection.
"""

from enum import Enum
import logging
import re
import time
from typing import Any, Dict, List, Optional
import uuid

from app.ai.types import DocumentChunk

logger = logging.getLogger("nouankany.ai")


class DocumentCollection(str, Enum):
    """
    Collections documentaires officielles de NouanKanyAI.
    """

    DOCUMENTATION_NOUANKANY = "documentation_nouankany"
    ISO_50001 = "iso_50001"
    FABRICANTS = "fabricants"
    RAPPORTS_ENERGETIQUES = "rapports_energetiques"
    GUIDES_ADEME = "guides_ademe"
    FAQ = "faq"
    RAPPORTS_AUDIT = "rapports_audit"
    DOCUMENTATION_IOT = "documentation_iot"


class SmartTextChunker:
    """
    Découpeur de texte intelligent avec préservation contextuelle.
    """

    def __init__(
        self,
        chunk_size: int = 500,
        chunk_overlap: int = 80,
    ) -> None:
        """
        :param chunk_size: Taille cible maximale d'un chunk (en caractères).
        :param chunk_overlap: Nombre de caractères de chevauchement entre chunks consécutifs.
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk_text(
        self,
        text: str,
        document_id: str,
        collection: str = DocumentCollection.DOCUMENTATION_NOUANKANY.value,
        title: Optional[str] = None,
        source: Optional[str] = None,
        extra_metadata: Optional[Dict[str, Any]] = None,
    ) -> List[DocumentChunk]:
        """
        Découpe un texte en préservant les sections Markdown et paragraphes.

        :param text: Contenu textuel brut.
        :param document_id: Identifiant du document source.
        :param collection: Collection cible.
        :param title: Titre du document.
        :param source: Origine ou chemin du fichier.
        :param extra_metadata: Métadonnées additionnelles.
        :return: Liste ordonnée de `DocumentChunk`.
        """
        if not text or not text.strip():
            return []

        # 1. Découpage préalable par sections Markdown (# Titre) ou double saut de ligne
        sections = self._split_into_sections(text)
        chunks: List[DocumentChunk] = []
        chunk_index = 0

        for section_title, section_body in sections:
            paragraphs = [p.strip() for p in section_body.split("\n\n") if p.strip()]
            current_buffer = ""

            for p in paragraphs:
                if len(current_buffer) + len(p) + 1 <= self.chunk_size:
                    current_buffer = f"{current_buffer}\n\n{p}".strip() if current_buffer else p
                else:
                    if current_buffer:
                        chunks.append(
                            self._create_chunk(
                                content=current_buffer,
                                document_id=document_id,
                                collection=collection,
                                section_title=section_title,
                                title=title,
                                source=source,
                                chunk_index=chunk_index,
                                extra_metadata=extra_metadata,
                            )
                        )
                        chunk_index += 1
                        # Conserver l'overlap
                        overlap_start = max(0, len(current_buffer) - self.chunk_overlap)
                        current_buffer = current_buffer[overlap_start:].strip()

                    # Si le paragraphe seul est plus grand que chunk_size, découpage par phrases
                    if len(p) > self.chunk_size:
                        sub_chunks = self._split_by_sentences(p)
                        for sub in sub_chunks:
                            chunks.append(
                                self._create_chunk(
                                    content=sub,
                                    document_id=document_id,
                                    collection=collection,
                                    section_title=section_title,
                                    title=title,
                                    source=source,
                                    chunk_index=chunk_index,
                                    extra_metadata=extra_metadata,
                                )
                            )
                            chunk_index += 1
                        current_buffer = ""
                    else:
                        current_buffer = p

            if current_buffer:
                chunks.append(
                    self._create_chunk(
                        content=current_buffer,
                        document_id=document_id,
                        collection=collection,
                        section_title=section_title,
                        title=title,
                        source=source,
                        chunk_index=chunk_index,
                        extra_metadata=extra_metadata,
                    )
                )
                chunk_index += 1

        logger.debug(
            f"[SmartTextChunker] Document '{document_id}' découpé en {len(chunks)} chunks (collection={collection})."
        )
        return chunks

    def _split_into_sections(self, text: str) -> List[tuple[str, str]]:
        """Sépare le texte par en-têtes Markdown (#, ##, ###)."""
        lines = text.splitlines()
        sections: List[tuple[str, str]] = []
        current_header = "Général"
        current_lines: List[str] = []

        header_pattern = re.compile(r"^(#{1,4})\s+(.+)$")

        for line in lines:
            match = header_pattern.match(line.strip())
            if match:
                if current_lines:
                    sections.append((current_header, "\n".join(current_lines).strip()))
                    current_lines = []
                current_header = match.group(2).strip()
            else:
                current_lines.append(line)

        if current_lines:
            sections.append((current_header, "\n".join(current_lines).strip()))

        return sections if sections else [("Général", text)]

    def _split_by_sentences(self, text: str) -> List[str]:
        """Découpe un long texte par phrases."""
        sentences = re.split(r"(?<=[.!?])\s+", text)
        result: List[str] = []
        buf = ""

        for s in sentences:
            if len(buf) + len(s) + 1 <= self.chunk_size:
                buf = f"{buf} {s}".strip() if buf else s
            else:
                if buf:
                    result.append(buf)
                buf = s
        if buf:
            result.append(buf)
        return result

    def _create_chunk(
        self,
        content: str,
        document_id: str,
        collection: str,
        section_title: str,
        title: Optional[str],
        source: Optional[str],
        chunk_index: int,
        extra_metadata: Optional[Dict[str, Any]],
    ) -> DocumentChunk:
        """Instancie un `DocumentChunk` avec toutes ses métadonnées de traçabilité."""
        meta = {
            "collection": collection,
            "section": section_title,
            "title": title or document_id,
            "source": source or "internal",
            "chunk_index": chunk_index,
            "char_count": len(content),
            "created_at": time.time(),
        }
        if extra_metadata:
            meta.update(extra_metadata)

        return DocumentChunk(
            chunk_id=f"{document_id}_chk_{chunk_index}_{uuid.uuid4().hex[:6]}",
            document_id=document_id,
            content=content.strip(),
            metadata=meta,
        )
