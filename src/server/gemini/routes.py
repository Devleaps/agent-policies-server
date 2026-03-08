"""
Gemini hook routes.
"""

import logging

from fastapi import APIRouter

from ..executor import execute_handlers_generic
from . import mapper
from .api.after_tool import AfterToolInput, AfterToolOutput
from .api.before_tool import BeforeToolInput, BeforeToolOutput
from .api.common import GeminiRequestWrapper

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/policy/gemini")


@router.post("/BeforeTool", response_model=BeforeToolOutput, response_model_exclude_none=True)
async def before_tool_hook(wrapper: GeminiRequestWrapper) -> BeforeToolOutput:
    """Handle Gemini BeforeTool hook events."""
    input_data = BeforeToolInput(**wrapper.event)
    logger.info(f"Gemini BeforeTool: {input_data.tool_name} in session {input_data.session_id}")

    generic_input = mapper.map_before_tool_input(wrapper, input_data)
    results = execute_handlers_generic(generic_input)

    # No decision in default output — Gemini will apply its own default_policy_behavior
    default = BeforeToolOutput()
    result = mapper.map_to_before_tool_output(results, default)
    logger.info(f"Gemini BeforeTool result: {result.decision}")
    return result


@router.post("/AfterTool", response_model=AfterToolOutput, response_model_exclude_none=True)
async def after_tool_hook(wrapper: GeminiRequestWrapper) -> AfterToolOutput:
    """Handle Gemini AfterTool hook events."""
    input_data = AfterToolInput(**wrapper.event)
    logger.info(f"Gemini AfterTool: {input_data.tool_name} in session {input_data.session_id}")

    generic_input = mapper.map_after_tool_input(wrapper, input_data)
    results = execute_handlers_generic(generic_input)

    default = AfterToolOutput()
    result = mapper.map_to_after_tool_output(results, default)
    return result
