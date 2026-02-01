"""Package management guidance."""

from src.server.models import PostFileEditEvent, PolicyGuidance


def uv_pyproject_guidance_rule(input_data: PostFileEditEvent):
    """Provide guidance when pyproject.toml is modified.

    Detects if dependencies were added and suggests using 'uv add' instead,
    which has an integrated whitelist for security.
    """
    yield PolicyGuidance(content=
        "A change was detected on pyproject.toml. In the case that dependencies were modified:\n"
        "Use 'uv add package-name' instead, which has an integrated whitelist for security.\n"
        "Example: uv add requests"
    )
