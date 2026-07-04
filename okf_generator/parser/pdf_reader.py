from __future__ import annotations

from pathlib import Path

import fitz

from okf_generator.models.document import PDFBlock, PDFDocument, PDFPage


class PDFReader:
    """Extract a PDF into a structured document without flattening pages."""

    def read(self, pdf_path: str | Path) -> PDFDocument:
        source_path = Path(pdf_path)
        if not source_path.exists():
            raise FileNotFoundError(f"PDF not found: {source_path}")

        pages: list[PDFPage] = []
        with fitz.open(source_path) as document:
            for page_index in range(document.page_count):
                page = document.load_page(page_index)
                page_dict = page.get_text("dict")
                blocks = [self._convert_block(block) for block in page_dict.get("blocks", [])]
                pages.append(
                    PDFPage(
                        page_number=page_index + 1,
                        text=page.get_text("text"),
                        raw_blocks=blocks,
                    )
                )

        return PDFDocument(source_path=str(source_path), pages=pages)

    def _convert_block(self, block: dict) -> PDFBlock:
        return PDFBlock(
            number=block.get("number", 0),
            bbox=tuple(block.get("bbox", (0.0, 0.0, 0.0, 0.0))),
            text=self._extract_block_text(block),
            lines=block.get("lines", []),
        )

    def _extract_block_text(self, block: dict) -> str:
        texts: list[str] = []
        for line in block.get("lines", []):
            spans = line.get("spans", [])
            line_text = "".join(span.get("text", "") for span in spans)
            if line_text:
                texts.append(line_text)
        return "\n".join(texts)
