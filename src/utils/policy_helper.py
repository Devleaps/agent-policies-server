"""
Helper functions for creating generic policy decisions and guidance.
"""
from devleaps.policies.server.common.models import PolicyDecision, PolicyGuidance, PolicyAction


class PolicyHelper:
    """Helper class for creating policy decisions and guidance."""

    @staticmethod
    def deny(reason: str) -> PolicyDecision:
        """Create a DENY decision with the given reason."""
        return PolicyDecision(
            action=PolicyAction.DENY,
            reason=reason
        )

    @staticmethod
    def allow(reason: str = None) -> PolicyDecision:
        """Create an ALLOW decision with an optional reason."""
        return PolicyDecision(
            action=PolicyAction.ALLOW,
            reason=reason
        )

    @staticmethod
    def ask(reason: str = None) -> PolicyDecision:
        """Create an ASK decision (prompt user) with an optional reason."""
        return PolicyDecision(
            action=PolicyAction.ASK,
            reason=reason
        )

    @staticmethod
    def halt(reason: str = None) -> PolicyDecision:
        """Create a HALT decision (stop entire process) with an optional reason."""
        return PolicyDecision(
            action=PolicyAction.HALT,
            reason=reason
        )

    @staticmethod
    def guidance(content: str, user_facing: bool = False) -> PolicyGuidance:
        """Create guidance without making a decision."""
        return PolicyGuidance(
            content=content,
            user_facing=user_facing
        )
