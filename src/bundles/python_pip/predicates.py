"""PyPI package validation utilities for age-based whitelisting."""

import re
from datetime import datetime, timedelta
from typing import Optional, Tuple
import httpx


def is_python(cmd) -> Tuple[bool, str]:
    """Match python, python3, python3.9, etc."""
    if re.match(r'^python(\d+(\.\d+)?)?$', cmd.executable):
        return True, ""
    return False, ""


def get_package_metadata(package_name: str, timeout: int = 5) -> Optional[dict]:
    """Fetch package metadata from PyPI API.

    Args:
        package_name: Name of the package to fetch
        timeout: Request timeout in seconds

    Returns:
        Package metadata dict or None if request fails
    """
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


def pypi_package_age_predicate(package_name: str, min_age_days: int = 365) -> Tuple[bool, str]:
    """Predicate function that validates package age via PyPI API.

    Args:
        package_name: Name of the package to validate
        min_age_days: Minimum age in days (default: 365 = 1 year)

    Returns:
        Tuple of (is_valid, reason_message)
    """
    metadata = get_package_metadata(package_name)

    if metadata is None:
        return False, f"Package '{package_name}' not found on PyPI or API request failed.\nOnly packages {min_age_days}+ days old are auto-whitelisted.\nFor newer packages, request manual approval."

    try:
        releases = metadata.get("releases", {})
        if not releases:
            return False, f"Package '{package_name}' has no releases.\nOnly packages {min_age_days}+ days old are auto-whitelisted.\nFor newer packages, request manual approval."

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
            return False, f"Package '{package_name}' has no upload date information.\nOnly packages {min_age_days}+ days old are auto-whitelisted.\nFor newer packages, request manual approval."

        min_date = datetime.now(earliest_date.tzinfo) - timedelta(days=min_age_days)
        if earliest_date <= min_date:
            age_years = (datetime.now(earliest_date.tzinfo) - earliest_date).days / 365
            return True, f"Package '{package_name}' is {age_years:.1f} years old (meets {min_age_days}+ day requirement)."

        age_days = (datetime.now(earliest_date.tzinfo) - earliest_date).days
        return False, f"Package '{package_name}' is only {age_days} days old (requires {min_age_days}+ days).\nOnly packages {min_age_days}+ days old are auto-whitelisted.\nFor newer packages, request manual approval."

    except Exception as e:
        return False, f"Error checking package '{package_name}': {str(e)}\nOnly packages {min_age_days}+ days old are auto-whitelisted.\nFor newer packages, request manual approval."
