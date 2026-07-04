from __future__ import annotations

from okf_generator.metadata import MetadataExtractor
from okf_generator.models.document import PDFDocument
from okf_generator.models.okf import CanonicalSection
from okf_generator.models.section import SectionBoundary
from okf_generator.parser.section_parser import SectionParser


class CanonicalJSONGenerator:
    """Build canonical JSON records from section text and deterministic metadata."""

    def __init__(self, metadata_extractor: MetadataExtractor | None = None) -> None:
        self.metadata_extractor = metadata_extractor or MetadataExtractor()
        self.section_parser = SectionParser()

    def generate(self, document: PDFDocument, boundary: SectionBoundary) -> CanonicalSection:
        body = self.section_parser.extract_text(document, boundary)
        metadata = self.metadata_extractor.extract(document, boundary)
        return CanonicalSection(
            chapter=boundary.chapter,
            section=boundary.section,
            title=boundary.title,
            body=body,
            references=[],
            metadata=metadata,
        )
