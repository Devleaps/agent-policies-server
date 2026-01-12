import re
from typing import Optional, Set
from urllib.parse import urlparse
from devleaps.policies.server.common.models import ToolUseEvent
from src.utils import PolicyHelper, url_is_localhost
from src.core import command, is_not
from src.core.command_parser import ParsedCommand

ALLOWED_CURL_DOMAINS = [
    "agent-policies.dev.devleaps.nl",
    "agent-policies.devleaps.nl",
]

ALLOWED_WEBFETCH_DOMAINS: Set[str] = {
    "pypi.org",
    "python.org",
    "docs.python.org",
    "peps.python.org",
    "docs.claude.com",
    "claude.ai",
    "anthropic.com",
    "github.com",
    "docs.github.com",
    "gitlab.com",
    "bitbucket.org",
    "stackoverflow.com",
    "stackexchange.com",
    "readthedocs.io",
    "readthedocs.org",
    "npmjs.com",
    "crates.io",
    "rubygems.org",
    "packagist.org",
    "developer.mozilla.org",
    "w3schools.com",
    "devdocs.io",
    "docs.aws.amazon.com",
    "cloud.google.com",
    "docs.microsoft.com",
    "azure.microsoft.com",
    "fastapi.tiangolo.com",
    "flask.palletsprojects.com",
    "django.readthedocs.io",
    "pydantic-docs.helpmanual.io",
    "requests.readthedocs.io",
    "backstage.io",
    "devleaps.nl",
    "dataleaps.nl",
    "release-engineers.com",
    "notion.com",
    "notion.so",
    "brew.sh",
}


def url_is_allowed_external(url: str) -> bool:
    return any(domain in url for domain in ALLOWED_CURL_DOMAINS)


def has_localhost_or_allowed_url(cmd: ParsedCommand):
    """Check if curl command has localhost or allowed external URL."""
    words = cmd.get_command_text().split()
    for word in words:
        if url_is_localhost(word) or url_is_allowed_external(word):
            return True, ""
    return False, ""


curl_localhost_allow_rule = (
    command("curl")
    .when(has_localhost_or_allowed_url)
    .allow()
)

curl_deny_rule = (
    command("curl")
    .when(is_not(has_localhost_or_allowed_url))
    .deny(
        "By policy, curl is only allowed to localhost or policy server endpoints.\n"
        "Use localhost, 127.0.0.1, or ::1"
    )
)


def _extract_domain(url: str) -> Optional[str]:
    try:
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url

        parsed = urlparse(url)
        domain = parsed.netloc.lower()

        if domain.startswith('www.'):
            domain = domain[4:]

        return domain
    except Exception:
        return None


def _is_domain_allowed(domain: str) -> bool:
    if domain in ALLOWED_WEBFETCH_DOMAINS:
        return True

    for allowed_domain in ALLOWED_WEBFETCH_DOMAINS:
        if domain.endswith('.' + allowed_domain):
            return True

    return False


def webfetch_whitelist_rule(event: ToolUseEvent, parsed):
    if event.tool_name != "WebFetch":
        return

    parameters = event.parameters
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

    yield PolicyHelper.allow(f"WebFetch allowed for whitelisted domain: {domain}")


def websearch_allow_rule(event: ToolUseEvent, parsed):
    if event.tool_name != "WebSearch":
        return

    yield PolicyHelper.allow("WebSearch always allowed")


all_rules = [
    curl_localhost_allow_rule,
    curl_deny_rule,
    webfetch_whitelist_rule,
    websearch_allow_rule,
]
