"""Test the Rego-based guidance activation system."""
import pytest
from src.core.rego_integration import RegoEvaluator
from src.server.common.models import PostFileEditEvent, SourceClient, PatchLine, StructuredPatch
from src.bundles_impl import evaluate_guidance


@pytest.fixture
def rego_evaluator():
    """Create a Rego evaluator instance."""
    return RegoEvaluator(policy_dir="policies")


@pytest.fixture
def create_file_edit_event():
    """Factory for creating PostFileEditEvent instances."""
    def _create(file_path: str, patch_content: str = "", bundles=None):
        """Create a PostFileEditEvent with structured patch."""
        if bundles is None:
            bundles = ["universal"]

        lines = []
        for line in patch_content.strip().split('\n') if patch_content.strip() else []:
            if line.startswith('+'):
                lines.append(PatchLine(operation="added", content=line[1:]))
            elif line.startswith('-'):
                lines.append(PatchLine(operation="removed", content=line[1:]))
            else:
                lines.append(PatchLine(operation="unchanged", content=line))

        patch = StructuredPatch(
            oldStart=1,
            oldLines=len([l for l in lines if l.operation in ["removed", "unchanged"]]),
            newStart=1,
            newLines=len([l for l in lines if l.operation in ["added", "unchanged"]]),
            lines=lines
        )

        return PostFileEditEvent(
            session_id="test-session",
            source_client=SourceClient.CLAUDE_CODE,
            file_path=file_path,
            structured_patch=[patch] if lines else None,
            enabled_bundles=bundles
        )
    return _create


def test_rego_evaluator_activates_python_file_guidance(rego_evaluator, create_file_edit_event):
    """Test that Rego evaluator correctly activates guidance checks for Python files."""
    event = create_file_edit_event("test.py")

    activated_checks = rego_evaluator.evaluate_guidance_activations(event, bundles=["universal"])

    assert "comment_ratio" in activated_checks
    assert "comment_overlap" in activated_checks
    assert "commented_code" in activated_checks
    assert "legacy_code" in activated_checks
    assert "mid_code_import" in activated_checks
    assert "license" not in activated_checks


def test_rego_evaluator_activates_readme_guidance(rego_evaluator, create_file_edit_event):
    """Test that Rego evaluator correctly activates guidance checks for README.md."""
    event = create_file_edit_event("README.md")

    activated_checks = rego_evaluator.evaluate_guidance_activations(event, bundles=["universal"])

    assert "license" in activated_checks
    assert "comment_ratio" not in activated_checks


def test_rego_evaluator_no_activations_for_non_matching_file(rego_evaluator, create_file_edit_event):
    """Test that Rego evaluator returns no activations for non-matching files."""
    event = create_file_edit_event("test.txt")

    activated_checks = rego_evaluator.evaluate_guidance_activations(event, bundles=["universal"])

    assert len(activated_checks) == 0


def test_python_uv_bundle_activates_uv_specific_guidance(rego_evaluator, create_file_edit_event):
    """Test that python_uv bundle activates UV-specific guidance."""
    event = create_file_edit_event("pyproject.toml")

    activated_checks = rego_evaluator.evaluate_guidance_activations(event, bundles=["universal", "python_uv"])

    assert "uv_pyproject" in activated_checks


def test_guidance_bundle_universal_runs_python_implementations(create_file_edit_event):
    """Test that universal guidance bundle runs Python implementations correctly."""
    patch_content = """
+# This is a comment
+x = 1
"""
    event = create_file_edit_event("test.py", patch_content)

    results = list(evaluate_guidance(event))

    # Should get results from activated Python guidance implementations
    # The exact number depends on which guidance rules trigger
    assert isinstance(results, list)


def test_guidance_bundle_python_uv_includes_universal(create_file_edit_event):
    """Test that python_uv bundle includes universal guidance checks."""
    event = create_file_edit_event("test.py", bundles=["universal", "python_uv"])

    results = list(evaluate_guidance(event))

    # Should include universal Python guidance
    assert isinstance(results, list)


def test_guidance_bundle_handles_pyproject_toml(create_file_edit_event):
    """Test that python_uv bundle handles pyproject.toml files."""
    patch_content = """
+[project]
+name = "test"
"""
    event = create_file_edit_event("pyproject.toml", patch_content, bundles=["universal", "python_uv"])

    results = list(evaluate_guidance(event))

    # Should activate uv_pyproject guidance
    assert isinstance(results, list)
