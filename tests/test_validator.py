from okf_generator.validator import BundleValidator
from okf_generator.markdown_generator import MarkdownArtifact


def test_bundle_validator_accepts_valid_bundle():
    artifact = MarkdownArtifact(
        filename="section-003-formation-of-company.md",
        content=(
            "---\n"
            "id: section-003-formation-of-company\n"
            "title: Formation of company.\n"
            "type: section\n"
            "chapter: Chapter II\n"
            "section: '3'\n"
            "description: Company formation rules.\n"
            "tags:\n"
            "- Chapter II\n"
            "references: []\n"
            "---\n"
            "3. Formation of company\n"
        ),
    )

    report = BundleValidator().validate([artifact])

    assert report.is_valid
    assert report.issues == []


def test_bundle_validator_reports_duplicate_id_filename_and_missing_body():
    artifact_one = MarkdownArtifact(
        filename="section-003-formation-of-company.md",
        content=(
            "---\n"
            "id: section-003-formation-of-company\n"
            "title: Formation of company.\n"
            "references: []\n"
            "---\n"
            "3. Formation of company\n"
        ),
    )
    artifact_two = MarkdownArtifact(
        filename="section-003-formation-of-company.md",
        content=(
            "---\n"
            "id: section-003-formation-of-company\n"
            "title: \n"
            "references: [section-999-missing]\n"
            "---\n"
        ),
    )

    report = BundleValidator().validate([artifact_one, artifact_two])

    codes = {issue.code for issue in report.issues}
    assert "duplicate-id" in codes
    assert "duplicate-filename" in codes
    assert "missing-title" in codes
    assert "missing-body" in codes
    assert "broken-reference" in codes


def test_bundle_validator_reports_invalid_yaml():
    artifact = MarkdownArtifact(
        filename="section-001-short-title.md",
        content="---\nid: [unterminated\n---\nbody",
    )

    report = BundleValidator().validate([artifact])

    assert any(issue.code == "invalid-yaml" for issue in report.issues)
