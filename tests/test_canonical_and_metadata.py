from okf_generator.canonical import CanonicalJSONGenerator
from okf_generator.metadata import MetadataExtractor
from okf_generator.parser.pdf_reader import PDFReader
from okf_generator.parser.section_detector import SectionDetector
from okf_generator.parser.toc_parser import TOCParser


def test_metadata_extractor_builds_deterministic_metadata():
    document = PDFReader().read("MCA.pdf")
    entries = TOCParser().parse(document)
    boundary = next(item for item in SectionDetector().detect(document, entries) if item.section == "1")

    metadata = MetadataExtractor().extract(document, boundary)

    assert metadata.chapter == "Chapter I"
    assert metadata.section == "1"
    assert metadata.title == "Short title, extent, commencement and application."
    assert metadata.act == "COMPANIES ACT, 2013"
    assert metadata.jurisdiction == "India"
    assert metadata.page == 16
    assert metadata.source == "MCA.pdf"
    assert metadata.version == "1.0"


def test_canonical_generator_produces_json_ready_payload():
    document = PDFReader().read("MCA.pdf")
    entries = TOCParser().parse(document)
    boundary = next(item for item in SectionDetector().detect(document, entries) if item.section == "3")

    payload = CanonicalJSONGenerator().generate(document, boundary)

    assert payload.chapter == "Chapter II"
    assert payload.section == "3"
    assert payload.title == "Formation of company."
    assert payload.body.startswith("3. Formation of company")
    assert payload.references == []
    assert payload.metadata.section == "3"
