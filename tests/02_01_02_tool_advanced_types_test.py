# -*- coding: utf-8 -*-
# file tests/02_01_02_tool_advanced_types_test.py
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
from typing import List, Optional, Union

# Third party imports
import pytest

# Internal imports
from org.slashlib.py.agent.tool import Tool


def test_tool_complex_list_type():
    """
    Check if List types are correctly mapped to 'array' in the JSON schema.
    """
    def process_items(items: List[str]):
        """Processes a list of strings."""
        return len(items)

    test_tool = Tool(process_items)
    schema = test_tool.get_schema()
    
    prop = schema["parameters"]["properties"]["items"]
    assert prop["type"] == "array"
    # Depending on your implementation, check for items type
    if "items" in prop:
        assert prop["items"]["type"] == "string"


def test_tool_optional_parameter():
    """
    Verify handling of Optional types (Union[T, None]).
    Optional parameters should not be in the 'required' list.
    """
    def greet(name: Optional[str] = None):
        """Greets someone."""
        return f"Hello {name}"

    test_tool = Tool(greet)
    schema = test_tool.get_schema()
    
    assert "name" in schema["parameters"]["properties"]
    assert "name" not in schema["parameters"].get("required", [])


def test_tool_no_docstring_fallback():
    """
    Ensure the tool doesn't crash if a function has no docstring.
    It should either provide a default description or an empty string.
    """
    def undocumented_func(x: int):
        return x

    test_tool = Tool(undocumented_func)
    schema = test_tool.get_schema()
    
    assert "description" in schema
    assert isinstance(schema["description"], str)


def test_tool_union_type_handling():
    """
    Test how Union types (excluding Optional) are handled.
    Most LLM schemas struggle with multi-type fields.
    """
    def compute(val: Union[int, float]):
        """Math on union types."""
        return val * 2

    test_tool = Tool(compute)
    schema = test_tool.get_schema()
    
    # Check if your implementation picks the first type or 'number'
    assert "type" in schema["parameters"]["properties"]["val"]


def test_tool_name_override_in_constructor():
    """
    Verify that the name and description can be explicitly overridden 
    regardless of the function's metadata.
    """
    def original_name():
        """original doc"""
        pass

    test_tool = Tool(original_name, name="forced_name", description="forced doc")
    schema = test_tool.get_schema()
    
    assert schema["name"] == "forced_name"
    assert schema["description"] == "forced doc"


# No __all__ export needed for test files as they are not meant to be imported as modules.