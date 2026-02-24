package universal

# Podman policies
# Machine management: init, start, stop, inspect, exists, ssh, list, ps
# Container inspection: ps
# Image inspection: images
# Volume inspection: volume ls
# Network inspection: network ls
# System inspection: version, info, system df

# Helper to check if executable is podman
is_podman if {
	input.parsed.executable == "podman"
}

# Machine management commands

# podman machine list - show available machines (read-only)
decisions[decision] if {
	is_podman
	count(input.parsed.arguments) >= 2
	input.parsed.arguments[0] == "machine"
	input.parsed.arguments[1] == "list"
	decision := {"action": "allow"}
}

# podman machine ps - alternative to list (read-only)
decisions[decision] if {
	is_podman
	count(input.parsed.arguments) >= 2
	input.parsed.arguments[0] == "machine"
	input.parsed.arguments[1] == "ps"
	decision := {"action": "allow"}
}

# podman machine inspect - view machine configuration (read-only)
decisions[decision] if {
	is_podman
	count(input.parsed.arguments) >= 2
	input.parsed.arguments[0] == "machine"
	input.parsed.arguments[1] == "inspect"
	decision := {"action": "allow"}
}

# podman machine exists - check if machine exists (read-only)
decisions[decision] if {
	is_podman
	count(input.parsed.arguments) >= 2
	input.parsed.arguments[0] == "machine"
	input.parsed.arguments[1] == "exists"
	decision := {"action": "allow"}
}

# podman machine ssh - SSH into a machine (non-destructive access)
decisions[decision] if {
	is_podman
	count(input.parsed.arguments) >= 2
	input.parsed.arguments[0] == "machine"
	input.parsed.arguments[1] == "ssh"
	decision := {"action": "allow"}
}

# podman machine init - initialize a new machine
decisions[decision] if {
	is_podman
	count(input.parsed.arguments) >= 2
	input.parsed.arguments[0] == "machine"
	input.parsed.arguments[1] == "init"
	decision := {"action": "allow"}
}

# podman machine start - start a machine
decisions[decision] if {
	is_podman
	count(input.parsed.arguments) >= 2
	input.parsed.arguments[0] == "machine"
	input.parsed.arguments[1] == "start"
	decision := {"action": "allow"}
}

# podman machine stop - stop a machine
decisions[decision] if {
	is_podman
	count(input.parsed.arguments) >= 2
	input.parsed.arguments[0] == "machine"
	input.parsed.arguments[1] == "stop"
	decision := {"action": "allow"}
}

# Container inspection

# podman ps - list containers (read-only)
decisions[decision] if {
	is_podman
	count(input.parsed.arguments) >= 1
	input.parsed.arguments[0] == "ps"
	decision := {"action": "allow"}
}

# podman inspect - inspect container or image details (read-only)
decisions[decision] if {
	is_podman
	count(input.parsed.arguments) >= 1
	input.parsed.arguments[0] == "inspect"
	decision := {"action": "allow"}
}

# Image inspection

# podman images - list images (read-only)
decisions[decision] if {
	is_podman
	count(input.parsed.arguments) >= 1
	input.parsed.arguments[0] == "images"
	decision := {"action": "allow"}
}

# Volume inspection

# podman volume ls - list volumes (read-only)
decisions[decision] if {
	is_podman
	count(input.parsed.arguments) >= 2
	input.parsed.arguments[0] == "volume"
	input.parsed.arguments[1] == "ls"
	decision := {"action": "allow"}
}

# Network inspection

# podman network ls - list networks (read-only)
decisions[decision] if {
	is_podman
	count(input.parsed.arguments) >= 2
	input.parsed.arguments[0] == "network"
	input.parsed.arguments[1] == "ls"
	decision := {"action": "allow"}
}

# System inspection

# podman version - show podman version (read-only)
decisions[decision] if {
	is_podman
	count(input.parsed.arguments) >= 1
	input.parsed.arguments[0] == "version"
	decision := {"action": "allow"}
}

# podman info - show system information (read-only)
decisions[decision] if {
	is_podman
	count(input.parsed.arguments) >= 1
	input.parsed.arguments[0] == "info"
	decision := {"action": "allow"}
}

# podman system df - show disk usage (read-only)
decisions[decision] if {
	is_podman
	count(input.parsed.arguments) >= 2
	input.parsed.arguments[0] == "system"
	input.parsed.arguments[1] == "df"
	decision := {"action": "allow"}
}
