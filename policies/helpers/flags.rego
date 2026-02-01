package helpers.flags

# Check if a flag exists and has a truthy value
# Usage: flags.is_set(name)
is_set(name) if {
    name in object.keys(input.session_flags)
    input.session_flags[name]
}

# Check if a flag has a specific value
# Usage: flags.equals(name, value)
equals(name, value) if {
    name in object.keys(input.session_flags)
    input.session_flags[name] == value
}
