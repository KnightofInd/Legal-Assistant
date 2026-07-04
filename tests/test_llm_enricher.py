from okf_generator.llm_enricher import LLMEnricher
from okf_generator.models.okf import CanonicalSection
from okf_generator.models.metadata import SectionMetadata


class FakeLLMClient:
    def __init__(self, responses: list[str]) -> None:
        self.responses = responses
        self.calls: list[str] = []

    def generate(self, prompt: str) -> str:
        self.calls.append(prompt)
        return self.responses[len(self.calls) - 1]


def test_llm_enricher_merges_summary_keywords_and_relationships():
    client = FakeLLMClient(
        [
            '{"summary":"Company formation rules.","keywords":["incorporation","memorandum"],"business_domain":"company law","referenced_sections":["7"],"referenced_forms":["INC-32"],"referenced_rules":["Rule 18"],"referenced_acts":["Companies Act, 2013"],"entities":["Registrar"],"compliance_topics":["incorporation"]}',
            '{"relationships":[{"source":"Section 3","target":"Section 7","relation":"depends_on","evidence":"incorporation filing"},{"source":"Section 3","target":"INC-32","relation":"mentions_form","evidence":"filing form"}]}'
        ]
    )
    enricher = LLMEnricher(client=client, model="qwen3")
    section = CanonicalSection(
        chapter="Chapter II",
        section="3",
        title="Formation of company.",
        body="3. Formation of company...",
        references=[],
        metadata=SectionMetadata(
            act="COMPANIES ACT, 2013",
            jurisdiction="India",
            chapter="Chapter II",
            section="3",
            title="Formation of company.",
            page=27,
            source="MCA.pdf",
            version="1.0",
        ),
    )

    enrichment = enricher.enrich(section)

    assert len(client.calls) == 2
    assert enrichment.summary == "Company formation rules."
    assert enrichment.keywords == ["incorporation", "memorandum"]
    assert enrichment.business_domain == "company law"
    assert enrichment.referenced_sections == ["7"]
    assert enrichment.referenced_forms == ["INC-32"]
    assert enrichment.relationships[0].target == "Section 7"
    assert enrichment.relationships[1].relation == "mentions_form"


def test_llm_enricher_detect_relationships_only():
    client = FakeLLMClient([
        '{"relationships":[{"source":"Section 3","target":"Registrar","relation":"mentions","evidence":"filing with Registrar"}]}'
    ])
    enricher = LLMEnricher(client=client, model="qwen3")
    section = CanonicalSection(
        chapter="Chapter II",
        section="3",
        title="Formation of company.",
        body="3. Formation of company...",
        references=[],
        metadata=SectionMetadata(
            act="COMPANIES ACT, 2013",
            jurisdiction="India",
            chapter="Chapter II",
            section="3",
            title="Formation of company.",
            page=27,
            source="MCA.pdf",
            version="1.0",
        ),
    )

    relationships = enricher.detect_relationships(section)

    assert len(client.calls) == 1
    assert relationships[0].source == "Section 3"
    assert relationships[0].target == "Registrar"
