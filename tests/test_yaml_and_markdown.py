from okf_generator.canonical import CanonicalJSONGenerator
from okf_generator.llm_enricher import LLMEnricher
from okf_generator.markdown_generator import MarkdownGenerator
from okf_generator.metadata import MetadataExtractor
from okf_generator.parser.pdf_reader import PDFReader
from okf_generator.parser.section_detector import SectionDetector
from okf_generator.parser.toc_parser import TOCParser
from okf_generator.yaml_generator import YAMLGenerator


class FakeLLMClient:
    def __init__(self, responses: list[str]) -> None:
        self.responses = responses
        self.calls: list[str] = []

    def generate(self, prompt: str) -> str:
        self.calls.append(prompt)
        return self.responses[len(self.calls) - 1]


def _build_enriched_section():
    document = PDFReader().read("MCA.pdf")
    entries = TOCParser().parse(document)
    boundary = next(item for item in SectionDetector().detect(document, entries) if item.section == "3")
    section = CanonicalJSONGenerator(MetadataExtractor()).generate(document, boundary)
    client = FakeLLMClient(
        [
            '{"summary":"Company formation rules.","keywords":["incorporation","memorandum"],"business_domain":"company law","referenced_sections":["7"],"referenced_forms":["INC-32"],"referenced_rules":["Rule 18"],"referenced_acts":["Companies Act, 2013"],"entities":["Registrar"],"compliance_topics":["incorporation"]}',
            '{"relationships":[{"source":"Section 3","target":"Section 7","relation":"depends_on","evidence":"incorporation filing"}]}'
        ]
    )
    section = section.model_copy(update={"enrichment": LLMEnricher(client=client, model="qwen3:1.7b").enrich(section)})
    return section


def test_yaml_generator_serializes_front_matter_from_json():
    section = _build_enriched_section()
    yaml_text = YAMLGenerator().serialize(section)

    assert 'id: section-003-formation-of-company' in yaml_text
    assert 'type: section' in yaml_text
    assert 'chapter: Chapter II' in yaml_text
    assert 'description: Company formation rules.' in yaml_text
    assert '- incorporation' in yaml_text
    assert 'target: Section 7' in yaml_text


def test_markdown_generator_renders_jinja_template_and_filename():
    section = _build_enriched_section()
    artifact = MarkdownGenerator().generate(section)

    assert artifact.filename == 'section-003-formation-of-company.md'
    assert artifact.content.startswith('---\n')
    assert 'title: Formation of company.' in artifact.content
    assert 'Company formation rules.' in artifact.content
    assert '3. Formation of company' in artifact.content
