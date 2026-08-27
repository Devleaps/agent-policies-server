package universal

import data.helpers

# WebFetch domain allowlist.
#
# The client parses the WebFetch URL and supplies the request host as
# input.event.parameters.host (never trust a substring match against the raw
# URL - "github.com.evil.tld" contains "github.com" but is not github.com).
# A host matches if it equals an allowed domain or is a subdomain of one.
#
# Unknown domains yield no decision at all (not deny), so the client's own
# permission system decides - matching the current behavior.
webfetch_allowed_domains := [
	"aider.chat",
	"block.github.io",
	"blog.devleaps.nl",
	"code.claude.com",
	"deepwiki.com",
	"developers.googleblog.com",
	"docs.anthropic.com",
	"developers.openai.com",
	"devleaps.nl",
	"docs.docker.com",
	"docs.github.com",
	"geminicli.com",
	"github.com",
	"goose-docs.ai",
	"google-gemini.github.io",
	"huggingface.co",
	"localhost",
	"opencode.ai",
	"prismml.com",
	"pypi.org",
	"raw.githubusercontent.com",
	"www.kimi.com",
]

decisions[decision] if {
	input.event.tool_name == "WebFetch"
	host := input.event.parameters.host
	some domain in webfetch_allowed_domains
	helpers.is_host_or_subdomain(host, domain)
	decision := {"action": "allow"}
}
