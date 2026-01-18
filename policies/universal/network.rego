package universal

import data.helpers

# Network command policies
# - curl: Only allow localhost and specific allowed domains

# Allowed domains for curl
allowed_curl_domains := [
	"agent-policies.dev.devleaps.nl",
	"agent-policies.devleaps.nl",
	"readthedocs.io",
]

# Helper to check if any argument contains localhost URL
has_localhost_url_arg if {
	some arg in input.parsed.arguments
	helpers.is_localhost_url(arg)
}

# Helper to check if any argument contains allowed external domain
has_allowed_domain_arg if {
	some arg in input.parsed.arguments
	some domain in allowed_curl_domains
	contains(arg, domain)
}

# curl with localhost - allow
decisions[decision] if {
	input.parsed.executable == "curl"
	has_localhost_url_arg
	decision := {"action": "allow"}
}

# curl with allowed external domain - allow
decisions[decision] if {
	input.parsed.executable == "curl"
	not has_localhost_url_arg
	has_allowed_domain_arg
	decision := {"action": "allow"}
}

# curl with disallowed URL - deny
decisions[decision] if {
	input.parsed.executable == "curl"
	not has_localhost_url_arg
	not has_allowed_domain_arg
	decision := {
		"action": "deny",
		"reason": "By policy, curl is only allowed to localhost or policy server endpoints.\nUse localhost, 127.0.0.1, or ::1",
	}
}
