from __future__ import annotations

import yaml

from okf_generator.models.enrichment import RelationshipRecord
from okf_generator.models.okf import CanonicalSection


class YAMLGenerator:
    """Serialize canonical section JSON into YAML-ready front matter data."""

    def build_front_matter(self, section: CanonicalSection) -> dict:
        enrichment = section.enrichment
        tags = self._build_tags(section)
        relationships = [relationship.model_dump(mode="json") for relationship in (enrichment.relationships if enrichment else [])]

        return {
            "id": self._build_id(section),
            "title": section.title,
            "type": "section",
            "chapter": section.chapter,
            "section": section.section,
            "description": enrichment.summary if enrichment and enrichment.summary else section.title,
            "tags": tags,
            "entities": enrichment.entities if enrichment else [],
            "relationships": relationships,
            "references": section.references,
            "source": section.metadata.source,
            "page": section.metadata.page,
        }

    def serialize(self, section: CanonicalSection) -> str:
        return yaml.safe_dump(
            self.build_front_matter(section),
            sort_keys=False,
            allow_unicode=True,
            default_flow_style=False,
        ).strip()

    def _build_tags(self, section: CanonicalSection) -> list[str]:
        enrichment = section.enrichment
        tags: list[str] = [section.chapter, section.title]
        if enrichment:
            tags.extend(enrichment.keywords)
            tags.extend(enrichment.compliance_topics)
            tags.extend(enrichment.referenced_sections)
            tags.extend(enrichment.referenced_forms)
            tags.extend(enrichment.referenced_rules)
            tags.extend(enrichment.referenced_acts)
        return self._deduplicate([tag for tag in tags if tag])

    def _build_id(self, section: CanonicalSection) -> str:
        section_number = section.section.zfill(3)
        title_slug = self._slugify(section.title)
        return f"section-{section_number}-{title_slug}"

    def _slugify(self, value: str) -> str:
        normalized = []
        previous_dash = False
        for character in value.casefold():
            if character.isalnum():
                normalized.append(character)
                previous_dash = False
            elif not previous_dash:
                normalized.append("-")
                previous_dash = True
        slug = "".join(normalized).strip("-")
        return slug or "section"

    def _deduplicate(self, values: list[str]) -> list[str]:
        seen: set[str] = set()
        result: list[str] = []
        for value in values:
            normalized = value.strip()
            if normalized and normalized not in seen:
                seen.add(normalized)
                result.append(normalized)
        return result
