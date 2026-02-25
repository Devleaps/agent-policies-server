package helpers.bundles

# Check if a specific bundle is active for the current request.
# Usage: import data.helpers.bundles
#        bundles.is_active("python_uv")
is_active(bundle_name) if {
    bundle_name in input.event.enabled_bundles
}
