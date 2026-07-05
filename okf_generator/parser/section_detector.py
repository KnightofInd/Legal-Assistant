from __future__ import annotations

import re

from okf_generator.models.document import PDFDocument
from okf_generator.models.section import SectionBoundary, TOCEntry


class SectionDetector:
    """Locate each section in the body of the PDF using TOC entries."""

    def detect(self, document: PDFDocument, toc_entries: list[TOCEntry]) -> list[SectionBoundary]:
        boundaries: list[SectionBoundary] = []
        starts: list[tuple[TOCEntry, int]] = []

        for entry in toc_entries:
            start_page = self._find_last_matching_page(document, entry)
            if start_page is None:
                continue
            starts.append((entry, start_page))

        for index, (entry, start_page) in enumerate(starts):
            next_start_page = starts[index + 1][1] if index + 1 < len(starts) else document.pages[-1].page_number + 1
            if next_start_page <= start_page:
                next_start_page = start_page + 1
            boundaries.append(
                SectionBoundary(
                    chapter=entry.chapter,
                    chapter_title=entry.chapter_title,
                    section=entry.section,
                    title=entry.title,
                    next_section=starts[index + 1][0].section if index + 1 < len(starts) else None,
                    next_title=starts[index + 1][0].title if index + 1 < len(starts) else None,
                    start_page=start_page,
                    end_page_exclusive=next_start_page,
                )
            )

        return boundaries

    def _find_last_matching_page(self, document: PDFDocument, entry: TOCEntry) -> int | None:
        needle = self._normalize_for_match(f"{entry.section} {entry.title}")
        matched_pages = [
            page.page_number
            for page in document.pages
            if needle in self._normalize_for_match(page.text)
        ]
        return matched_pages[-1] if matched_pages else None

    def _normalize_for_match(self, text: str) -> str:
        return re.sub(r"[^a-z0-9]+", " ", text.casefold()).strip()
