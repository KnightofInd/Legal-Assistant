from __future__ import annotations

import re

from okf_generator.models.document import PDFDocument
from okf_generator.models.section import SectionBoundary


class SectionParser:
    """Extract the textual body for a detected section boundary."""

    def extract_text(self, document: PDFDocument, boundary: SectionBoundary) -> str:
        pages = [page.text for page in document.pages if boundary.start_page <= page.page_number < boundary.end_page_exclusive]
        normalized_pages = []
        for index, page_text in enumerate(pages):
            stripped_page = self._strip_page_header(page_text)
            if index == 0:
                stripped_page = self._slice_from_heading(stripped_page, boundary)
            normalized_pages.append(stripped_page)
        return "\n\n".join(page.strip() for page in normalized_pages if page.strip())

    def _strip_page_header(self, page_text: str) -> str:
        lines = page_text.splitlines()
        if not lines:
            return page_text

        index = 0
        while index < len(lines) and not lines[index].strip():
            index += 1

        if index < len(lines) and lines[index].strip().isdigit():
            index += 1

        while index < len(lines) and not lines[index].strip():
            index += 1

        return "\n".join(lines[index:])

    def _slice_from_heading(self, page_text: str, boundary: SectionBoundary) -> str:
        section_number = re.escape(boundary.section)
        title = re.escape(boundary.title.rstrip("."))
        heading_pattern = re.compile(rf"(?is)(?:^|\n)\s*{section_number}\.\s*{title}")
        match = heading_pattern.search(page_text)
        if match:
            return page_text[match.start():]
        return page_text
