# -*- coding: utf-8 -*-
# file tests/02_01_04_tool_sync_execution_test.py
# @AI:
# - INTEGRITY RULES:
#   - STRICT PRESERVATION: Do not remove, move, or modify ANY existing lines of code or comments 
#     unless they are the explicit target of the requested change. 
#   - DEBUG MARKERS: Commented-out code (e.g., debug prints) MUST be kept exactly where they are.
#   - WHITESPACE & STRUCTURE: Maintain all original empty lines and the existing file structure. 
#     Structural integrity takes precedence over "clean code" or "elegance".
#   - LEAD-IN/OUT: The very first and last lines (and all comments in between) are immutable anchors.
# - MAINTENANCE:
#   - Only update pydoc strings (args, returns, raises) if the function signature changes.
#   - Do NOT delete existing examples or descriptions in pydoc.
# - LANGUAGE: en-US for all comments and documentation.
#

# Python imports
import typing

# Third party imports
import pytest

# Internal imports
from src.org.slashlib.py.agent.tool import Tool


@pytest.mark.asyncio
async def test_tool_call_sync_function():
    """
    Test the execution of a regular synchronous function through the Tool wrapper.
    This specifically targets the 'return self._func(*args, **kwargs)' line
    in the __call__ method when inspect.iscoroutinefunction is False.
    """
    def sync_multiply(a: int, b: int) -> int:
        """Simple synchronous multiplication."""
        return a * b

    # Wrap the sync function in a Tool
    test_tool = Tool(sync_multiply)

    # Even though the wrapped function is sync, the Tool's __call__ is async.
    # We must await it. This will enter the 'return self._func' branch.
    result = await test_tool(a=5, b=10)

    assert result == 50
    assert result != 0


# No __all__ export needed for test files as they are not meant to be imported as modules.