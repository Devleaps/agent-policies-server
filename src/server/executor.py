import logging
from typing import List, Union

from .models import PolicyDecision, PolicyGuidance, BaseEvent
from .registry import registry
from .session import (
    cleanup_expired_flags,
    decrement_invocation_flags,
    set_flag
)

logger = logging.getLogger(__name__)


def execute_handlers_generic(input_data) -> List[Union[PolicyDecision, PolicyGuidance]]:
    """
    Execute handlers with generic event input and return generic results.

    This is the core policy execution pipeline:
    1. Clean up expired flags
    2. Decrement invocation counters for active flags
    3. Execute all registered handlers
    4. Process any flags set by policies
    5. Return raw policy results (decisions and guidance)

    Args:
        input_data: The input event data (bundles read from input_data.enabled_bundles)

    Aggregation of results is done by the mapper layer for each editor.
    Bundle filtering is done by Rego policies, not by the Python registry.
    """
    # Cleanup and decrement flags before policy execution
    if isinstance(input_data, BaseEvent):
        cleanup_expired_flags(input_data.session_id)
        decrement_invocation_flags(input_data.session_id)

    handlers = registry.get_handlers(type(input_data))
    all_results = []

    for handler in handlers:
        try:
            yielded_results = list(handler(input_data))
            all_results.extend(yielded_results)
            logger.debug(
                f"Handler {handler.__name__} yielded {len(yielded_results)} results",
                extra={
                    "handler": handler.__name__,
                    "result_count": len(yielded_results),
                }
            )
        except Exception as e:
            logger.error(
                f"Error in handler {handler.__name__}: {e}",
                extra={
                    "handler": handler.__name__,
                    "error": str(e),
                },
                exc_info=True
            )
            continue

    # Process flags from policy decisions
    if isinstance(input_data, BaseEvent):
        for result in all_results:
            if isinstance(result, PolicyDecision) and result.flags:
                for flag_spec in result.flags:
                    try:
                        set_flag(input_data.session_id, flag_spec)
                        logger.debug(
                            f"Set flag '{flag_spec.get('name')}' for session {input_data.session_id}",
                            extra={"flag": flag_spec}
                        )
                    except Exception as e:
                        logger.error(
                            f"Error setting flag: {e}",
                            extra={"flag": flag_spec, "error": str(e)},
                            exc_info=True
                        )

    return all_results
