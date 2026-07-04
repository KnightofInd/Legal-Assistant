from __future__ import annotations

from pydantic import BaseModel, Field

from okf_generator.models.enrichment import SectionEnrichment
from okf_generator.models.metadata import SectionMetadata


class CanonicalSection(BaseModel):
    """Canonical JSON payload for one legal section."""

    chapter: str = ""
    section: str = ""
    title: str = ""
    body: str = ""
    references: list[str] = Field(default_factory=list)
    metadata: SectionMetadata
    enrichment: SectionEnrichment | None = None

