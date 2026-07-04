from __future__ import annotations

import re
from pathlib import Path

from okf_generator.models.document import PDFDocument
from okf_generator.models.metadata import SectionMetadata
from okf_generator.models.section import SectionBoundary


class MetadataExtractor:
    """Extract deterministic metadata from the source PDF and section boundary."""

    def __init__(self, jurisdiction: str = "India", version: str = "1.0") -> None:
        self.jurisdiction = jurisdiction
        self.version = version

    def extract(self, document: PDFDocument, boundary: SectionBoundary) -> SectionMetadata:
        return SectionMetadata(
            act=self._extract_act_name(document),
            jurisdiction=self.jurisdiction,
            chapter=boundary.chapter,
            section=boundary.section,
            title=boundary.title,
            page=boundary.start_page,
            source=Path(document.source_path).name,
            version=self.version,
        )

    def _extract_act_name(self, document: PDFDocument) -> str:
        if not document.pages:
            return ""

        first_page_text = document.pages[0].text
        match = re.search(r"THE\s+(.+?ACT,\s*\d{4})", first_page_text, re.IGNORECASE | re.DOTALL)
        if match:
            return re.sub(r"\s+", " ", match.group(1)).strip()
        return ""
