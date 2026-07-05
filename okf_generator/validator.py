from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import yaml

from okf_generator.markdown_generator import MarkdownArtifact


@dataclass(frozen=True)
class ValidationIssue:
    """A single validation problem found in a bundle."""

    code: str
    message: str
    filename: str = ""


@dataclass
class ValidationReport:
    """Bundle validation outcome."""

    issues: list[ValidationIssue] = field(default_factory=list)

    @property
    def is_valid(self) -> bool:
        return not self.issues


class BundleValidator:
    """Validate rendered markdown artifacts before export."""

    def validate(self, artifacts: list[MarkdownArtifact]) -> ValidationReport:
        issues: list[ValidationIssue] = []
        seen_ids: set[str] = set()
        seen_filenames: set[str] = set()
        ids_in_bundle: set[str] = set()
        parsed_documents: list[tuple[MarkdownArtifact, dict[str, Any], str]] = []

        for artifact in artifacts:
            front_matter_text, body = self._split_markdown(artifact.content)
            if not front_matter_text:
                issues.append(ValidationIssue(code="missing-front-matter", message="Missing YAML front matter", filename=artifact.filename))
                continue

            try:
                front_matter = yaml.safe_load(front_matter_text) or {}
            except yaml.YAMLError as exc:
                issues.append(ValidationIssue(code="invalid-yaml", message=f"Invalid YAML: {exc}", filename=artifact.filename))
                continue

            if not isinstance(front_matter, dict):
                issues.append(ValidationIssue(code="invalid-yaml", message="Front matter must be a YAML mapping", filename=artifact.filename))
                continue

            parsed_documents.append((artifact, front_matter, body))

            section_id = str(front_matter.get("id", "")).strip()
            if not section_id:
                issues.append(ValidationIssue(code="missing-id", message="Missing id in front matter", filename=artifact.filename))
            elif section_id in seen_ids:
                issues.append(ValidationIssue(code="duplicate-id", message=f"Duplicate id: {section_id}", filename=artifact.filename))
            else:
                seen_ids.add(section_id)
                ids_in_bundle.add(section_id)

            if artifact.filename in seen_filenames:
                issues.append(ValidationIssue(code="duplicate-filename", message=f"Duplicate filename: {artifact.filename}", filename=artifact.filename))
            else:
                seen_filenames.add(artifact.filename)

            title = front_matter.get("title", None)
            if title is None or not str(title).strip():
                issues.append(ValidationIssue(code="missing-title", message="Missing title in front matter", filename=artifact.filename))

            if not body.strip():
                issues.append(ValidationIssue(code="missing-body", message="Missing markdown body", filename=artifact.filename))

        for artifact, front_matter, _body in parsed_documents:
            references = front_matter.get("references", [])
            if references is None:
                continue
            if not isinstance(references, list):
                issues.append(ValidationIssue(code="invalid-references", message="references must be a list", filename=artifact.filename))
                continue

            for reference in references:
                reference_id = str(reference).strip()
                if reference_id and reference_id not in ids_in_bundle:
                    issues.append(
                        ValidationIssue(
                            code="broken-reference",
                            message=f"Broken reference: {reference_id}",
                            filename=artifact.filename,
                        )
                    )

        return ValidationReport(issues=issues)

    def _split_markdown(self, content: str) -> tuple[str, str]:
        if not content.startswith("---\n"):
            return "", content

        closing_index = content.find("\n---\n", 4)
        if closing_index == -1:
            return "", content

        front_matter_text = content[4:closing_index]
        body = content[closing_index + 5 :]
        return front_matter_text, body
