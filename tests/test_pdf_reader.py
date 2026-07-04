from pathlib import Path

from okf_generator.parser.pdf_reader import PDFReader


def test_pdf_reader_builds_structured_document():
    pdf_path = Path("MCA.pdf")
    document = PDFReader().read(pdf_path)

    assert document.source_path.endswith("MCA.pdf")
    assert document.pages
    assert document.pages[0].page_number == 1
    assert isinstance(document.pages[0].raw_blocks, list)
