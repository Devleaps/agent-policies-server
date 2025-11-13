"""Controls WebFetch access to whitelisted domains only."""

from typing import Optional, Set
from urllib.parse import urlparse
from devleaps.policies.server.common.models import ToolUseEvent
from src.utils import PolicyHelper


ALLOWED_DOMAINS: Set[str] = {
    # Python ecosystem
    "pypi.org",
    "python.org",
    "docs.python.org",
    "peps.python.org",

    # Claude Code documentation
    "docs.claude.com",
    "claude.ai",
    "anthropic.com",

    # Development platforms
    "github.com",
    "docs.github.com",
    "gitlab.com",
    "bitbucket.org",

    # Documentation and learning
    "stackoverflow.com",
    "stackexchange.com",
    "readthedocs.io",
    "readthedocs.org",

    # Package managers and tools
    "npmjs.com",
    "crates.io",
    "rubygems.org",
    "packagist.org",

    # General development resources
    "developer.mozilla.org",
    "w3schools.com",
    "devdocs.io",

    # Cloud providers (documentation)
    "docs.aws.amazon.com",
    "cloud.google.com",
    "docs.microsoft.com",
    "azure.microsoft.com",

    # Popular frameworks and libraries
    "fastapi.tiangolo.com",
    "flask.palletsprojects.com",
    "django.readthedocs.io",
    "pydantic-docs.helpmanual.io",
    "requests.readthedocs.io",
    "backstage.io",

    # Devleaps and friends
    "devleaps.nl",
    "dataleaps.nl",
    "release-engineers.com",

    # Notion
    "notion.com",
    "notion.so",

    # Homebrew
    "brew.sh"
}


def _extract_domain(url: str) -> Optional[str]:
    """Extract domain from URL, handling various URL formats."""
    try:
        # Handle URLs without protocol
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url

        parsed = urlparse(url)
        domain = parsed.netloc.lower()

        # Remove www. prefix if present
        if domain.startswith('www.'):
            domain = domain[4:]

        return domain
    except Exception:
        return


def _is_domain_allowed(domain: str) -> bool:
    """Check if a domain is in the whitelist or is a subdomain of an allowed domain."""
    if domain in ALLOWED_DOMAINS:
        return True

    # Check for subdomain matches (e.g., api.github.com matches github.com)
    for allowed_domain in ALLOWED_DOMAINS:
        if domain.endswith('.' + allowed_domain):
            return True

    return False


def webfetch_whitelist_rule(input_data: ToolUseEvent):
    if input_data.tool_name != "WebFetch":
        return

    parameters = input_data.parameters
    if not isinstance(parameters, dict):
        return

    url = parameters.get("url", "")
    if not url:
        return

    domain = _extract_domain(url)
    if not domain:
        return

    if not _is_domain_allowed(domain):
        return

    # Domain is allowed
    yield PolicyHelper.allow(f"WebFetch allowed for whitelisted domain: {domain}")