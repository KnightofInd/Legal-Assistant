from __future__ import annotations

from pathlib import Path
import os

from okf_generator.canonical import CanonicalJSONGenerator
from okf_generator.llm_enricher import LLMEnricher
from okf_generator.metadata import MetadataExtractor
from okf_generator.parser.pdf_reader import PDFReader
from okf_generator.parser.section_detector import SectionDetector
from okf_generator.parser.toc_parser import TOCParser


def main() -> None:
    reader = PDFReader()
    pdf_path = Path("MCA.pdf")
    document = reader.read(pdf_path)
    toc_entries = TOCParser().parse(document)
    boundaries = SectionDetector().detect(document, toc_entries)
    print(f"Loaded {len(document.pages)} pages from {document.source_path}")
    print(f"Parsed {len(toc_entries)} TOC entries and {len(boundaries)} section boundaries")
    if boundaries:
        first = boundaries[0]
        print(f"First section: {first.section} starts on page {first.start_page}")

        canonical = CanonicalJSONGenerator(MetadataExtractor()).generate(document, first)
        print(canonical.model_dump_json(indent=2)[:500])

        if os.getenv("OKF_ENABLE_LLM") == "1":
            enrichment = LLMEnricher().enrich(canonical)
            canonical = canonical.model_copy(update={"enrichment": enrichment})
            print(canonical.enrichment.model_dump_json(indent=2)[:500])


if __name__ == "__main__":
    main()
