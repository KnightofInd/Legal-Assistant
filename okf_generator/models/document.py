from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class PDFBlock(BaseModel):
    """A raw block extracted from a PDF page."""

    number: int = Field(ge=0)
    bbox: tuple[float, float, float, float]
    text: str = ""
    lines: list[dict[str, Any]] = Field(default_factory=list)


class PDFPage(BaseModel):
    """A single PDF page with preserved extraction structure."""

    page_number: int = Field(ge=1)
    text: str = ""
    raw_blocks: list[PDFBlock] = Field(default_factory=list)


class PDFDocument(BaseModel):
    """In-memory representation of the extracted PDF."""

    source_path: str
    pages: list[PDFPage] = Field(default_factory=list)
