from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from typing import Protocol
from urllib import error, request

from okf_generator.models.enrichment import RelationshipRecord, SectionEnrichment
from okf_generator.models.okf import CanonicalSection


class LLMClient(Protocol):
    """Minimal client interface for LLM-backed enrichment."""

    def generate(self, prompt: str) -> str:
        raise NotImplementedError


@dataclass
class OllamaClient:
    """Talk to a local Ollama instance using the generate API."""

    model: str = "qwen3:1.7b"
    base_url: str = "http://localhost:11434"

    def generate(self, prompt: str) -> str:
        payload = json.dumps({"model": self.model, "prompt": prompt, "stream": False}).encode("utf-8")
        req = request.Request(
            f"{self.base_url.rstrip('/')}/api/generate",
            data=payload,
            headers={"Content-Type": "application/json"},
        )

        try:
            with request.urlopen(req, timeout=60) as response:
                data = json.loads(response.read().decode("utf-8"))
        except error.URLError as exc:
            raise RuntimeError(f"Unable to reach Ollama at {self.base_url}: {exc}") from exc

        output = data.get("response", "")
        if not isinstance(output, str):
            raise RuntimeError("Unexpected Ollama response format")
        return output


class LLMEnricher:
    """Generate deterministic enrichment prompts and parse structured LLM output."""

    def __init__(self, client: LLMClient | None = None, model: str | None = None) -> None:
        self.model = model or os.getenv("OLLAMA_MODEL", "qwen3:1.7b")
        self.client = client or OllamaClient(model=self.model)

    def enrich(self, section: CanonicalSection) -> SectionEnrichment:
        enrichment_payload = self._parse_json_response(self.client.generate(self._build_enrichment_prompt(section)))
        relationship_payload = self._parse_json_response(
            self.client.generate(self._build_relationship_prompt(section))
        )

        relationships = [RelationshipRecord(**item) for item in relationship_payload.get("relationships", [])]
        return SectionEnrichment(
            summary=self._as_str(enrichment_payload.get("summary")),
            keywords=self._as_list(enrichment_payload.get("keywords")),
            business_domain=self._as_str(enrichment_payload.get("business_domain")),
            referenced_sections=self._as_list(enrichment_payload.get("referenced_sections")),
            referenced_forms=self._as_list(enrichment_payload.get("referenced_forms")),
            referenced_rules=self._as_list(enrichment_payload.get("referenced_rules")),
            referenced_acts=self._as_list(enrichment_payload.get("referenced_acts")),
            entities=self._as_list(enrichment_payload.get("entities")),
            compliance_topics=self._as_list(enrichment_payload.get("compliance_topics")),
            relationships=relationships,
        )

    def detect_relationships(self, section: CanonicalSection) -> list[RelationshipRecord]:
        payload = self._parse_json_response(self.client.generate(self._build_relationship_prompt(section)))
        return [RelationshipRecord(**item) for item in payload.get("relationships", [])]

    def _build_enrichment_prompt(self, section: CanonicalSection) -> str:
        return (
            "Read this section and return JSON only. "
            "Generate summary, keywords, business_domain, referenced_sections, referenced_forms, "
            "referenced_rules, referenced_acts, entities, and compliance_topics.\n\n"
            f"Chapter: {section.chapter}\n"
            f"Section: {section.section}\n"
            f"Title: {section.title}\n"
            f"Body:\n{section.body}\n"
        )

    def _build_relationship_prompt(self, section: CanonicalSection) -> str:
        return (
            "Read this section and return JSON only. Which legal objects are referenced? "
            "Return a relationships array with objects containing source, target, relation, and evidence.\n\n"
            f"Chapter: {section.chapter}\n"
            f"Section: {section.section}\n"
            f"Title: {section.title}\n"
            f"Body:\n{section.body}\n"
        )

    def _parse_json_response(self, raw_text: str) -> dict:
        cleaned = raw_text.strip()
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"\s*```$", "", cleaned)
        return json.loads(cleaned)

    def _as_list(self, value: object) -> list[str]:
        if value is None:
            return []
        if isinstance(value, list):
            return [str(item).strip() for item in value if str(item).strip()]
        if isinstance(value, str) and value.strip():
            return [value.strip()]
        return []

    def _as_str(self, value: object) -> str:
        if value is None:
            return ""
        return str(value).strip()
