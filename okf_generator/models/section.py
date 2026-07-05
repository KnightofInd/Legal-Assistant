from __future__ import annotations

from pydantic import BaseModel, Field


class TOCEntry(BaseModel):
    """A single section entry parsed from the arrangement of sections."""

    chapter: str
    chapter_title: str = ""
    section: str
    title: str


class SectionBoundary(BaseModel):
    """The location of a section within the source PDF."""

    chapter: str
    chapter_title: str = ""
    section: str
    title: str
    next_section: str | None = None
    next_title: str | None = None
    start_page: int = Field(ge=1)
    end_page_exclusive: int = Field(ge=1)
