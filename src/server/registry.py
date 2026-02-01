import logging
from typing import Callable, Dict, Generator, List, Optional, Set, Tuple, Type, TypeVar, Union

from .models import PolicyDecision, PolicyGuidance

logger = logging.getLogger(__name__)

InputType = TypeVar('InputType')
OutputType = TypeVar('OutputType', PolicyDecision, PolicyGuidance)

HandlerFunction = Callable[[InputType], Generator[Union[PolicyDecision, PolicyGuidance], None, None]]


class HookRegistry:
    """Generic registry for hook handlers using class types as keys."""

    def __init__(self):
        # Store handlers: {input_class: [handler, ...]}
        self.handlers: Dict[Type[InputType], List[HandlerFunction]] = {}

    def register_handler(self, input_class: Type[InputType], handler: HandlerFunction):
        """Register a handler for a specific input class type."""
        if input_class not in self.handlers:
            self.handlers[input_class] = []

        self.handlers[input_class].append(handler)
        logger.debug(
            f"Registered handler: {handler.__name__}",
            extra={
                "input_class": input_class.__name__,
                "handler": handler.__name__,
            }
        )

    def get_handlers(self, input_class: Type[InputType]) -> List[HandlerFunction]:
        """Get all handlers for input class."""
        return self.handlers.get(input_class, [])



registry: HookRegistry = HookRegistry()