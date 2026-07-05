from __future__ import annotations

from pathlib import Path
import os

from okf_generator.canonical import CanonicalJSONGenerator
from okf_generator.exporter import BundleExporter
from okf_generator.llm_enricher import LLMEnricher
from okf_generator.markdown_generator import MarkdownGenerator
from okf_generator.metadata import MetadataExtractor
from okf_generator.parser.pdf_reader import PDFReader
from okf_generator.parser.section_detector import SectionDetector
from okf_generator.parser.toc_parser import TOCParser
from okf_generator.validator import BundleValidator


def main() -> None:
    reader = PDFReader()
    pdf_path = Path("MCA.pdf")
    document = reader.read(pdf_path)
    toc_entries = TOCParser().parse(document)
    boundaries = SectionDetector().detect(document, toc_entries)
    print(f"Loaded {len(document.pages)} pages from {document.source_path}")
    print(f"Parsed {len(toc_entries)} TOC entries and {len(boundaries)} section boundaries")
    if boundaries:
        canonical_sections = []
        markdown_artifacts = []
        generator = CanonicalJSONGenerator(MetadataExtractor())
        markdown_generator = MarkdownGenerator()

        for boundary in boundaries:
            canonical = generator.generate(document, boundary)
            if os.getenv("OKF_ENABLE_LLM") == "1":
                enrichment = LLMEnricher().enrich(canonical)
                canonical = canonical.model_copy(update={"enrichment": enrichment})
            canonical_sections.append(canonical)
            markdown_artifacts.append(markdown_generator.generate(canonical))

        report = BundleValidator().validate(markdown_artifacts)
        print(f"Bundle valid: {report.is_valid}")
        for issue in report.issues:
            print(f"{issue.code}: {issue.message}")

        if report.is_valid:
            export_result = BundleExporter().export(markdown_artifacts, report)
            print(export_result.manifest_path)
            print(export_result.index_path)


if __name__ == "__main__":
    main()
