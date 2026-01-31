import logging
from typing import List, Union

from .common.models import PolicyDecision, PolicyGuidance
from .registry import registry

logger = logging.getLogger(__name__)


def execute_handlers_generic(input_data) -> List[Union[PolicyDecision, PolicyGuidance]]:
    """
    Execute handlers with generic event input and return generic results.

    This is the core policy execution pipeline:
    1. Execute all registered handlers
    2. Return raw policy results (decisions and guidance)

    Args:
        input_data: The input event data (bundles read from input_data.enabled_bundles)

    Aggregation of results is done by the mapper layer for each editor.
    Bundle filtering is done by Rego policies, not by the Python registry.
    """
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

    return all_results
