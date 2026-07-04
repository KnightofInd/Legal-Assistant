from okf_generator.parser.pdf_reader import PDFReader
from okf_generator.parser.section_detector import SectionDetector
from okf_generator.parser.toc_parser import TOCParser


def test_toc_parser_extracts_chapter_two_entries():
    document = PDFReader().read("MCA.pdf")
    entries = TOCParser().parse(document)

    assert entries
    assert entries[0].chapter == "Chapter I"
    assert entries[0].section == "1"
    assert entries[0].title.startswith("Short title")

    chapter_two_entries = [entry for entry in entries if entry.chapter == "Chapter II"]
    assert chapter_two_entries[0].section == "3"
    assert chapter_two_entries[0].title.startswith("Formation of company")


def test_section_detector_finds_body_start_pages():
    document = PDFReader().read("MCA.pdf")
    entries = TOCParser().parse(document)
    boundaries = SectionDetector().detect(document, entries)

    section_three = next(boundary for boundary in boundaries if boundary.section == "3")
    section_four = next(boundary for boundary in boundaries if boundary.section == "4")

    assert section_three.start_page == 27
    assert section_three.end_page_exclusive == 28
    assert section_four.start_page == 28
