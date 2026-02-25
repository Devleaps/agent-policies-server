package universal

# Podman policies
# - machine: read-only ops (list, ps, inspect, exists) allowed; init/start/stop allowed
# - container inspection (ps, inspect): allowed
# - image inspection (images): allowed
# - volume inspection (volume ls): allowed
# - network inspection (network ls): allowed
# - system inspection (version, info, system df): allowed

# podman machine list/ps/inspect/exists - read-only, allow
decisions[decision] if {
	input.parsed.executable == "podman"
	input.parsed.subcommand == "machine"
	count(input.parsed.arguments) >= 1
	input.parsed.arguments[0] in {"list", "ps", "inspect", "exists"}
	decision := {"action": "allow"}
}

# podman machine init/start/stop - allow
decisions[decision] if {
	input.parsed.executable == "podman"
	input.parsed.subcommand == "machine"
	count(input.parsed.arguments) >= 1
	input.parsed.arguments[0] in {"init", "start", "stop"}
	decision := {"action": "allow"}
}

# podman ps - list containers (read-only)
decisions[decision] if {
	input.parsed.executable == "podman"
	input.parsed.subcommand == "ps"
	decision := {"action": "allow"}
}

# podman inspect - inspect container or image details (read-only)
decisions[decision] if {
	input.parsed.executable == "podman"
	input.parsed.subcommand == "inspect"
	decision := {"action": "allow"}
}

# podman images - list images (read-only)
decisions[decision] if {
	input.parsed.executable == "podman"
	input.parsed.subcommand == "images"
	decision := {"action": "allow"}
}

# podman volume ls - list volumes (read-only)
decisions[decision] if {
	input.parsed.executable == "podman"
	input.parsed.subcommand == "volume"
	count(input.parsed.arguments) >= 1
	input.parsed.arguments[0] == "ls"
	decision := {"action": "allow"}
}

# podman network ls - list networks (read-only)
decisions[decision] if {
	input.parsed.executable == "podman"
	input.parsed.subcommand == "network"
	count(input.parsed.arguments) >= 1
	input.parsed.arguments[0] == "ls"
	decision := {"action": "allow"}
}

# podman version - show podman version (read-only)
decisions[decision] if {
	input.parsed.executable == "podman"
	input.parsed.subcommand == "version"
	decision := {"action": "allow"}
}

# podman info - show system information (read-only)
decisions[decision] if {
	input.parsed.executable == "podman"
	input.parsed.subcommand == "info"
	decision := {"action": "allow"}
}

# podman system df - show disk usage (read-only)
decisions[decision] if {
	input.parsed.executable == "podman"
	input.parsed.subcommand == "system"
	count(input.parsed.arguments) >= 1
	input.parsed.arguments[0] == "df"
	decision := {"action": "allow"}
}
