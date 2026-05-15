# -*- coding: utf-8 -*-
# file tests/02_01_01_tool_schema_test.py
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
from org.slashlib.py.agent.tool import Tool, tool


def test_tool_schema_generation_basic():
    def multiply(a: int, b: float, name: str = "default"):
        """Multiplies two numbers."""
        return a * b

    test_tool = Tool(multiply)
    schema = test_tool.get_schema()

    # Zugriff über ["function"]
    assert schema["type"] == "function"
    inner = schema["function"]
    assert inner["name"] == "multiply"
    assert inner["description"] == "Multiplies two numbers."
    
    properties = inner["parameters"]["properties"]
    assert properties["a"]["type"] == "integer"
    assert properties["b"]["type"] == "number"

def test_tool_required_parameters():
    def mixed_params(req: int, opt: int = 1):
        return req + opt

    test_tool = Tool(mixed_params)
    schema = test_tool.get_schema()
    
    # Zugriff über ["function"]
    required = schema["function"]["parameters"]["required"]
    assert "req" in required
    assert "opt" not in required

@pytest.mark.asyncio
async def test_tool_execution_async():
    """
    Verify that the Tool class can handle and execute async functions.
    """
    async def async_add(x: int, y: int):
        return x + y

    test_tool = Tool(async_add)
    result = await test_tool(x=10, y=20)
    assert result == "30"


def test_tool_decorator_syntax():
    @tool(name="custom_name", description="custom desc")
    def my_func(data: typing.List[str]):
        return len(data)

    assert isinstance(my_func, Tool)
    assert my_func.name == "custom_name"
    # Zugriff über ["function"]
    assert my_func.get_schema()["function"]["description"] == "custom desc"

# No __all__ export needed for test files as they are not meant to be imported as modules.