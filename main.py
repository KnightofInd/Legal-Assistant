from __future__ import annotations

import argparse
import os
from pathlib import Path

from okf_generator.canonical import CanonicalJSONGenerator
from okf_generator.exporter import BundleExporter
from okf_generator.llm_enricher import LLMEnricher
from okf_generator.markdown_generator import MarkdownGenerator
from okf_generator.metadata import MetadataExtractor
from okf_generator.parser.pdf_reader import PDFReader
from okf_generator.parser.section_detector import SectionDetector
from okf_generator.parser.toc_parser import TOCParser
from okf_generator.validator import BundleValidator


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate a Google OKF bundle from the Companies Act PDF.")
    parser.add_argument("--pdf", default="MCA.pdf", help="Path to the Companies Act PDF")
    parser.add_argument("--output-root", default="output", help="Root directory for the exported bundle")
    parser.add_argument("--bundle-slug", default="companies-act", help="Bundle slug used under output/knowledge")
    parser.add_argument(
        "--limit",
        type=int,
        default=0,
        help="Optional limit for the number of sections to process. Use 0 to process all sections.",
    )
    return parser


def run_pipeline(pdf_path: str | Path, output_root: str | Path, bundle_slug: str, limit: int = 0) -> None:
    reader = PDFReader()
    document = reader.read(pdf_path)
    toc_entries = TOCParser().parse(document)
    boundaries = SectionDetector().detect(document, toc_entries)

    if limit > 0:
        boundaries = boundaries[:limit]

    print(f"Loaded {len(document.pages)} pages from {document.source_path}")
    print(f"Parsed {len(toc_entries)} TOC entries and {len(boundaries)} section boundaries")

    if not boundaries:
        print("No section boundaries were detected.")
        return

    canonical_generator = CanonicalJSONGenerator(MetadataExtractor())
    markdown_generator = MarkdownGenerator()

    markdown_artifacts = []
    for boundary in boundaries:
        canonical = canonical_generator.generate(document, boundary)
        if os.getenv("OKF_ENABLE_LLM") == "1":
            enrichment = LLMEnricher().enrich(canonical)
            canonical = canonical.model_copy(update={"enrichment": enrichment})
        markdown_artifacts.append(markdown_generator.generate(canonical))

    report = BundleValidator().validate(markdown_artifacts)
    print(f"Bundle valid: {report.is_valid}")
    for issue in report.issues:
        print(f"{issue.code}: {issue.message}")

    if not report.is_valid:
        raise SystemExit(1)

    export_result = BundleExporter(output_root=output_root, bundle_slug=bundle_slug).export(markdown_artifacts, report)
    print(f"Exported bundle root: {export_result.bundle_root}")
    print(f"Manifest: {export_result.manifest_path}")
    print(f"Index: {export_result.index_path}")
    for section_file in export_result.section_files[:5]:
        print(f"Section file: {section_file.path}")
    if len(export_result.section_files) > 5:
        print(f"... and {len(export_result.section_files) - 5} more section files")


def main() -> None:
    args = build_parser().parse_args()
    run_pipeline(args.pdf, args.output_root, args.bundle_slug, args.limit)


if __name__ == "__main__":
    main()
