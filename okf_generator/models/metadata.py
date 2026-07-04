from __future__ import annotations

from pydantic import BaseModel, Field


class SectionMetadata(BaseModel):
    """Deterministic metadata attached to a canonical section record."""

    act: str = ""
    jurisdiction: str = ""
    chapter: str = ""
    section: str = ""
    title: str = ""
    page: int = Field(ge=1)
    source: str = ""
    version: str = ""
