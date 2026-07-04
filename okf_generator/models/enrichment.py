from __future__ import annotations

from pydantic import BaseModel, Field


class RelationshipRecord(BaseModel):
    """A structured legal relationship extracted from a section."""

    source: str
    target: str
    relation: str = "references"
    evidence: str = ""


class SectionEnrichment(BaseModel):
    """LLM-generated enrichment attached to canonical section JSON."""

    summary: str = ""
    keywords: list[str] = Field(default_factory=list)
    business_domain: str = ""
    referenced_sections: list[str] = Field(default_factory=list)
    referenced_forms: list[str] = Field(default_factory=list)
    referenced_rules: list[str] = Field(default_factory=list)
    referenced_acts: list[str] = Field(default_factory=list)
    entities: list[str] = Field(default_factory=list)
    compliance_topics: list[str] = Field(default_factory=list)
    relationships: list[RelationshipRecord] = Field(default_factory=list)
