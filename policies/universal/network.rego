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

# curl options whose value is a payload, header, file or credential, never
# the URL: a bare "localhost" there (curl -d localhost https://x) is data
curl_value_options := {
	"-d", "--data", "--data-raw", "--data-binary", "--data-urlencode",
	"--json", "-F", "--form", "-H", "--header", "-X", "--request",
	"-o", "--output", "-u", "--user", "-A", "--user-agent", "-e",
	"--referer", "-b", "--cookie", "-c", "--cookie-jar", "-T",
	"--upload-file", "-K", "--config", "-w", "--write-out", "-x", "--proxy",
}

# Helper to check if any option value contains localhost URL. With an
# explicit scheme it counts anywhere, as before; a scheme-less one only where
# curl reads a URL (--url, or a word the parser took as a flag's value, as in
# curl -s localhost)
has_localhost_url_option if {
	some key, value in input.parsed.options
	helpers.has_url_scheme(trim(value, "\"'"))
	helpers.is_localhost_url(value)
}

has_localhost_url_option if {
	some key, value in input.parsed.options
	not key in curl_value_options
	helpers.is_localhost_url(value)
}

# Helper to check if command has localhost URL (in args or options)
has_localhost_url if has_localhost_url_arg
has_localhost_url if has_localhost_url_option

# Helper to check if any argument contains allowed external domain
has_allowed_domain_arg if {
	some arg in input.parsed.arguments
	some domain in allowed_curl_domains
	contains(arg, domain)
}

# Helper to check if any option value contains allowed external domain
has_allowed_domain_option if {
	some key, value in input.parsed.options
	some domain in allowed_curl_domains
	contains(value, domain)
}

# Helper to check if command has allowed domain (in args or options)
has_allowed_domain if has_allowed_domain_arg
has_allowed_domain if has_allowed_domain_option

# curl with localhost - allow
decisions[decision] if {
	input.parsed.executable == "curl"
	has_localhost_url
	decision := {"action": "allow"}
}

# curl with allowed external domain - allow
decisions[decision] if {
	input.parsed.executable == "curl"
	not has_localhost_url
	has_allowed_domain
	decision := {"action": "allow"}
}

# curl with disallowed URL - deny
decisions[decision] if {
	input.parsed.executable == "curl"
	not has_localhost_url
	not has_allowed_domain
	decision := {
		"action": "deny",
		"reason": "By policy, curl is only allowed to localhost or policy server endpoints. Use localhost, 127.0.0.1, or ::1",
	}
}
