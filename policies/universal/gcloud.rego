package universal

# gcloud policies
# - Allow read-only commands: a read verb (describe, list, read, ...) and no
#   verb that changes state or hands out credentials
# - Everything else defers to the user
#
# gcloud commands are GROUP... COMMAND [NAME], so the verb is not at a fixed
# position; every positional word is checked.

gcloud_read_verbs := {
	"describe",
	"list",
	"read",
	"get-iam-policy",
	"get-value",
	"info",
	"version",
}

gcloud_write_verbs := {
	"create",
	"delete",
	"update",
	"patch",
	"deploy",
	"set",
	"unset",
	"set-iam-policy",
	"add-iam-policy-binding",
	"remove-iam-policy-binding",
	"import",
	"export",
	"ssh",
	"scp",
	"reset",
	"start",
	"stop",
	"resize",
	"submit",
	"execute",
	"cancel",
	"publish",
	"pull",
	"ack",
	"seek",
	"login",
	"revoke",
	"activate-service-account",
	"print-access-token",
	"print-identity-token",
	"get-credentials",
}

gcloud_positionals := array.concat([input.parsed.subcommand], input.parsed.arguments) if {
	input.parsed.subcommand != null
}

gcloud_positionals := input.parsed.arguments if {
	input.parsed.subcommand == null
}

gcloud_is_read_only if {
	some word in gcloud_positionals
	word in gcloud_read_verbs
	not gcloud_has_write_verb
}

gcloud_has_write_verb if {
	some word in gcloud_positionals
	word in gcloud_write_verbs
}

decisions[decision] if {
	input.parsed.executable == "gcloud"
	gcloud_is_read_only
	decision := {"action": "allow"}
}

# gcloud --version - allow
decisions[decision] if {
	input.parsed.executable == "gcloud"
	input.parsed.subcommand == null
	"--version" in input.parsed.flags
	decision := {"action": "allow"}
}
