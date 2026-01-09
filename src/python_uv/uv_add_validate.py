"""Validate uv add against PyPI metadata."""

import re
from datetime import datetime, timedelta
from typing import Optional
import httpx
from devleaps.policies.server.common.models import ToolUseEvent
from src.utils import PolicyHelper


def get_package_metadata(package_name: str, timeout: int = 5) -> Optional[dict]:
    """Fetch package metadata from PyPI API."""
    try:
        response = httpx.get(
            f"https://pypi.org/pypi/{package_name}/json",
            timeout=timeout,
            follow_redirects=True
        )
        if response.status_code == 200:
            return response.json()
        return None
    except Exception:
        return None


def is_package_allowed(package_name: str) -> tuple[bool, str]:
    """Check if package meets criteria for auto-whitelisting."""
    metadata = get_package_metadata(package_name)

    if metadata is None:
        return False, f"Package '{package_name}' not found on PyPI or API request failed."

    try:
        # Get first upload date
        releases = metadata.get("releases", {})
        if not releases:
            return False, f"Package '{package_name}' has no releases."

        # Find earliest release date
        earliest_date = None
        for version, files in releases.items():
            if files:
                for file_info in files:
                    upload_time = file_info.get("upload_time_iso_8601")
                    if upload_time:
                        upload_datetime = datetime.fromisoformat(upload_time.replace("Z", "+00:00"))
                        if earliest_date is None or upload_datetime < earliest_date:
                            earliest_date = upload_datetime

        if earliest_date is None:
            return False, f"Package '{package_name}' has no upload date information."

        # Check if package is at least 1 year old
        one_year_ago = datetime.now(earliest_date.tzinfo) - timedelta(days=365)
        if earliest_date <= one_year_ago:
            age_years = (datetime.now(earliest_date.tzinfo) - earliest_date).days / 365
            return True, f"Package '{package_name}' is {age_years:.1f} years old (meets 1+ year requirement)."

        # If not 1 year old, deny
        age_days = (datetime.now(earliest_date.tzinfo) - earliest_date).days
        return False, f"Package '{package_name}' is only {age_days} days old (requires 1+ year)."

    except Exception as e:
        return False, f"Error checking package '{package_name}': {str(e)}"


def uv_add_validate_rule(input_data: ToolUseEvent):
    """Validate uv add commands against PyPI metadata."""
    if not input_data.tool_is_bash:
        return

    command = input_data.command.strip()

    # Match: uv add package-name
    match = re.match(r'^uv\s+add\s+([a-zA-Z0-9_-]+)', command)
    if not match:
        return

    package_name = match.group(1)

    # Check if package is allowed
    allowed, reason = is_package_allowed(package_name)

    if allowed:
        yield PolicyHelper.allow(reason)
    else:
        yield PolicyHelper.deny(
            f"{reason}\n"
            f"Only packages that are 1+ year old are auto-whitelisted.\n"
            f"For newer packages, request manual approval."
        )
