from __future__ import annotations

import re

from okf_generator.models.document import PDFDocument
from okf_generator.models.section import TOCEntry


class TOCParser:
    """Parse the arrangement of sections into chapter/section roadmap entries."""

    def __init__(self, toc_page_limit: int = 16) -> None:
        self.toc_page_limit = toc_page_limit
        self._chapter_re = re.compile(r"^CHAPTER\s*([IVXLCDM]+)\b", re.IGNORECASE)
        self._section_re = re.compile(r"^(?P<section>\d+[A-Z]?)\.\s*(?P<title>.+)$")

    def parse(self, document: PDFDocument) -> list[TOCEntry]:
        entries: list[TOCEntry] = []
        current_chapter = ""
        current_chapter_title = ""
        current_entry: dict[str, str] | None = None
        waiting_for_chapter_title = False

        for page in document.pages[: self.toc_page_limit]:
            for line in self._iter_lines(page.text):
                if not line:
                    continue

                if line.isdigit():
                    continue

                chapter_match = self._chapter_re.match(line)
                if chapter_match:
                    current_entry = self._finalize_entry(current_entry, current_chapter, current_chapter_title, entries)
                    current_chapter = f"Chapter {chapter_match.group(1).upper()}"
                    current_chapter_title = ""
                    waiting_for_chapter_title = True
                    continue

                if line.upper() == "SECTIONS":
                    continue

                if line.upper().startswith("PART "):
                    continue

                section_match = self._section_re.match(line)
                if section_match:
                    current_entry = self._finalize_entry(current_entry, current_chapter, current_chapter_title, entries)
                    current_entry = {
                        "chapter": current_chapter,
                        "chapter_title": current_chapter_title,
                        "section": section_match.group("section"),
                        "title": self._clean_text(section_match.group("title")),
                    }
                    waiting_for_chapter_title = False
                    continue

                if waiting_for_chapter_title and not current_chapter_title:
                    current_chapter_title = self._clean_text(line)
                    continue

                if current_entry is not None:
                    current_entry["title"] = f"{current_entry['title']} {self._clean_text(line)}".strip()

        self._finalize_entry(current_entry, current_chapter, current_chapter_title, entries)
        return entries

    def _iter_lines(self, page_text: str) -> list[str]:
        return [self._clean_text(line) for line in page_text.splitlines()]

    def _clean_text(self, text: str) -> str:
        return re.sub(r"\s+", " ", text).strip()

    def _finalize_entry(
        self,
        current_entry: dict[str, str] | None,
        current_chapter: str,
        current_chapter_title: str,
        entries: list[TOCEntry],
    ) -> dict[str, str] | None:
        if current_entry and current_entry.get("section") and current_entry.get("title"):
            entries.append(
                TOCEntry(
                    chapter=current_entry.get("chapter", current_chapter),
                    chapter_title=current_entry.get("chapter_title", current_chapter_title),
                    section=current_entry["section"],
                    title=self._clean_text(current_entry["title"]),
                )
            )
        return None
