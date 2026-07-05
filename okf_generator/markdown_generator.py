from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from okf_generator.models.okf import CanonicalSection
from okf_generator.yaml_generator import YAMLGenerator


@dataclass(frozen=True)
class MarkdownArtifact:
    """Rendered markdown file and filename for a canonical section."""

    filename: str
    content: str


class MarkdownGenerator:
    """Render canonical section JSON into markdown using a Jinja template."""

    def __init__(self, templates_dir: str | Path | None = None, yaml_generator: YAMLGenerator | None = None) -> None:
        base_dir = Path(templates_dir) if templates_dir is not None else Path(__file__).resolve().parent.parent / "templates"
        self.yaml_generator = yaml_generator or YAMLGenerator()
        self.environment = Environment(
            loader=FileSystemLoader(str(base_dir)),
            autoescape=select_autoescape(enabled_extensions=()),
            trim_blocks=True,
            lstrip_blocks=True,
        )

    def generate(self, section: CanonicalSection) -> MarkdownArtifact:
        template = self.environment.get_template("section.md.jinja")
        front_matter_yaml = self.yaml_generator.serialize(section)
        content = template.render(front_matter_yaml=front_matter_yaml, body=section.body)
        return MarkdownArtifact(filename=self._build_filename(section), content=content)

    def _build_filename(self, section: CanonicalSection) -> str:
        section_number = section.section.zfill(3)
        title_slug = self.yaml_generator._slugify(section.title)
        return f"section-{section_number}-{title_slug}.md"
