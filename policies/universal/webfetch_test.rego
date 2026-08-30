package universal

import data.helpers

# Real allowlisted domain, exact host match.
test_webfetch_github_exact_allowed if {
	decisions[{"action": "allow"}] with input as {"event": {
		"tool_name": "WebFetch",
		"parameters": {"host": "github.com"},
	}}
}

# Real allowlisted domain, legitimate subdomain.
test_webfetch_docs_github_subdomain_allowed if {
	decisions[{"action": "allow"}] with input as {"event": {
		"tool_name": "WebFetch",
		"parameters": {"host": "docs.github.com"},
	}}
}

test_webfetch_developers_googleblog_allowed if {
	decisions[{"action": "allow"}] with input as {"event": {
		"tool_name": "WebFetch",
		"parameters": {"host": "developers.googleblog.com"},
	}}
}

# Unknown domain: no decision at all (client's own permission system decides),
# not an explicit deny.
test_webfetch_unknown_domain_no_decision if {
	count(decisions) == 0 with input as {"event": {
		"tool_name": "WebFetch",
		"parameters": {"host": "evil.com"},
	}}
}

# Security: a naive substring match on the raw URL would let
# "github.com.evil.tld" through because it contains "github.com". The host
# comparison must reject it.
test_webfetch_suffix_attack_denied if {
	count(decisions) == 0 with input as {"event": {
		"tool_name": "WebFetch",
		"parameters": {"host": "github.com.evil.tld"},
	}}
}

# Security: a naive substring match would also let "evilgithub.com" through.
# Only an exact host or a true dot-boundary subdomain may match.
test_webfetch_prefix_attack_denied if {
	count(decisions) == 0 with input as {"event": {
		"tool_name": "WebFetch",
		"parameters": {"host": "evilgithub.com"},
	}}
}

# Non-WebFetch tool: this policy must not fire at all.
test_webfetch_ignores_other_tools if {
	count(decisions) == 0 with input as {"event": {
		"tool_name": "Bash",
		"parameters": {"host": "github.com"},
	}}
}
