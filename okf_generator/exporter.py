from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from okf_generator.markdown_generator import MarkdownArtifact
from okf_generator.validator import ValidationReport


@dataclass(frozen=True)
class BundleFile:
    """A file emitted into the exported bundle."""

    path: str
    filename: str


@dataclass(frozen=True)
class BundleExportResult:
    """Result of exporting a validated bundle."""

    bundle_root: Path
    manifest_path: Path
    index_path: Path
    section_files: list[BundleFile] = field(default_factory=list)


class BundleExporter:
    """Export validated markdown artifacts into the Google OKF bundle layout."""

    def __init__(self, output_root: str | Path = "output", bundle_slug: str = "companies-act") -> None:
        self.output_root = Path(output_root)
        self.bundle_slug = bundle_slug

    def export(self, artifacts: list[MarkdownArtifact], validation_report: ValidationReport) -> BundleExportResult:
        if not validation_report.is_valid:
            issue_summary = ", ".join(f"{issue.code}: {issue.message}" for issue in validation_report.issues)
            raise ValueError(f"Bundle validation failed: {issue_summary}")

        bundle_root = self.output_root / "knowledge" / self.bundle_slug
        sections_root = bundle_root / "sections" / "definitions"
        sections_root.mkdir(parents=True, exist_ok=True)

        section_files: list[BundleFile] = []
        for artifact in artifacts:
            file_path = sections_root / artifact.filename
            file_path.write_text(artifact.content, encoding="utf-8")
            section_files.append(BundleFile(path=self._relative_path(file_path), filename=artifact.filename))

        index_path = sections_root / "index.md"
        index_path.write_text(self._build_index_markdown(section_files), encoding="utf-8")

        manifest_path = bundle_root / "manifest.yaml"
        manifest_path.write_text(self._build_manifest(bundle_root, index_path, section_files), encoding="utf-8")

        return BundleExportResult(
            bundle_root=bundle_root,
            manifest_path=manifest_path,
            index_path=index_path,
            section_files=section_files,
        )

    def _build_index_markdown(self, section_files: list[BundleFile]) -> str:
        lines = [
            "---",
            "title: Companies Act Sections",
            "type: index",
            "---",
            "",
            "# Companies Act Sections",
            "",
            "This index lists the exported section files in the bundle.",
            "",
        ]
        for section_file in section_files:
            lines.append(f"- {section_file.filename} ({section_file.path})")
        lines.append("")
        return "\n".join(lines)

    def _build_manifest(self, bundle_root: Path, index_path: Path, section_files: list[BundleFile]) -> str:
        manifest: dict[str, Any] = {
            "bundle": {
                "name": "Companies Act",
                "slug": self.bundle_slug,
                "root": self._relative_path(bundle_root),
                "index": self._relative_path(index_path),
                "sections": [
                    {"filename": section_file.filename, "path": section_file.path} for section_file in section_files
                ],
            }
        }
        return yaml.safe_dump(manifest, sort_keys=False, allow_unicode=True, default_flow_style=False)

    def _relative_path(self, path: Path) -> str:
        return path.relative_to(self.output_root).as_posix()
