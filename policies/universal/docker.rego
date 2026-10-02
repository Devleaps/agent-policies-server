package universal

# docker run/create with extra privileges - deny
docker_privilege_keys := {"--cap-add", "--privileged"}

docker_starts_container if {
	input.parsed.subcommand in {"run", "create"}
}

docker_starts_container if {
	input.parsed.subcommand == "container"
	count(input.parsed.arguments) > 0
	input.parsed.arguments[0] in {"run", "create"}
}

docker_adds_privileges if {
	some key, _ in input.parsed.options
	key in docker_privilege_keys
}

docker_adds_privileges if {
	some flag in input.parsed.flags
	flag in docker_privilege_keys
}

decisions[decision] if {
	input.parsed.executable == "docker"
	docker_starts_container
	docker_adds_privileges
	decision := {
		"action": "deny",
		"reason": "By policy, docker containers may not be started with --cap-add or --privileged. These grant the container access to the host.",
	}
}
