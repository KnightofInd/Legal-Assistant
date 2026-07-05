from pathlib import Path

from okf_generator.canonical import CanonicalJSONGenerator
from okf_generator.exporter import BundleExporter
from okf_generator.markdown_generator import MarkdownGenerator
from okf_generator.metadata import MetadataExtractor
from okf_generator.parser.pdf_reader import PDFReader
from okf_generator.parser.section_detector import SectionDetector
from okf_generator.parser.toc_parser import TOCParser
from okf_generator.validator import ValidationIssue, BundleValidator


def _build_artifacts(limit: int = 2):
    document = PDFReader().read("MCA.pdf")
    entries = TOCParser().parse(document)
    boundaries = SectionDetector().detect(document, entries)[:limit]
    canonical_generator = CanonicalJSONGenerator(MetadataExtractor())
    markdown_generator = MarkdownGenerator()
    return [markdown_generator.generate(canonical_generator.generate(document, boundary)) for boundary in boundaries]


def test_bundle_exporter_writes_google_style_bundle(tmp_path: Path):
    artifacts = _build_artifacts()
    report = BundleValidator().validate(artifacts)

    export_result = BundleExporter(output_root=tmp_path).export(artifacts, report)

    assert export_result.bundle_root == tmp_path / "knowledge" / "companies-act"
    assert export_result.manifest_path.exists()
    assert export_result.index_path.exists()
    assert len(export_result.section_files) == len(artifacts)
    for artifact in artifacts:
        assert (tmp_path / "knowledge" / "companies-act" / "sections" / "definitions" / artifact.filename).exists()


def test_bundle_exporter_refuses_invalid_bundle(tmp_path: Path):
    artifacts = _build_artifacts()
    report = BundleValidator().validate(artifacts)
    report.issues.append(ValidationIssue(code="duplicate-id", message="Duplicate id", filename="x"))

    try:
        BundleExporter(output_root=tmp_path).export(artifacts, report)
    except ValueError as exc:
        assert "Bundle validation failed" in str(exc)
    else:
        raise AssertionError("Expected export to fail for invalid bundle")
