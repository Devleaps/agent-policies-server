package universal

# export - allow setting variables
# - Every argument must be NAME=value
# - Any value: $X only copies a variable, and a $(cmd) in it is either
#   evaluated as a command of its own or rejected by the parser
# - Variables that change which program runs, what it loads or how the shell
#   behaves get no decision, so the user's own settings decide:
#   export PATH=.:$PATH && git status could run a ./git from the workspace

export_assignment(arg) if {
	regex.match("^[A-Za-z_][A-Za-z0-9_]*=", arg)
}

export_sensitive_names := {
	"BASH_ENV",
	"ENV",
	"IFS",
	"HOME",
	"SHELLOPTS",
	"BASHOPTS",
	"PROMPT_COMMAND",
	"NODE_OPTIONS",
	"PYTHONSTARTUP",
	"PYTHONHOME",
	"PERL5OPT",
	"RUBYOPT",
	"JAVA_TOOL_OPTIONS",
	"PAGER",
	"EDITOR",
	"VISUAL",
	"SSH_ASKPASS",
	"SUDO_ASKPASS",
	"MANPAGER",
	"LESSOPEN",
	"LESSCLOSE",
	"BROWSER",
	"PS1",
	"PS4",
	"ZDOTDIR",
	"PERL5LIB",
	"RUBYLIB",
}

# PATH, PYTHONPATH, LD_LIBRARY_PATH, CDPATH, GIT_EXEC_PATH, ...
export_sensitive(name) if contains(name, "PATH")

# LD_PRELOAD, DYLD_INSERT_LIBRARIES, ...
export_sensitive(name) if startswith(name, "LD_")

export_sensitive(name) if startswith(name, "DYLD_")

# Git reads many variables that run commands or move its state:
# GIT_EXTERNAL_DIFF, GIT_SSH_COMMAND, GIT_CONFIG_*, GIT_DIR, ...
export_sensitive(name) if startswith(name, "GIT_")

export_sensitive(name) if name in export_sensitive_names

export_sets_sensitive if {
	some arg in input.parsed.arguments
	export_sensitive(split(arg, "=")[0])
}

decisions[decision] if {
	input.parsed.executable == "export"
	count(input.parsed.arguments) > 0
	count(input.parsed.flags) == 0
	count(input.parsed.options) == 0
	every arg in input.parsed.arguments {
		export_assignment(arg)
	}
	not export_sets_sensitive
	decision := {"action": "allow"}
}
