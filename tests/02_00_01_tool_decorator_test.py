# -*- coding: utf-8 -*-
# file tests/02_00_01_tool_decorator_test.py
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


"""
Testsuite for the org.slashlib.py.agent.tool module.
Tested Class: None (Standalone Function)
Tested Function: tool

Special Considerations:
- Focuses on the decorator logic and its ability to handle different call styles.
- Ensures 100% branch coverage for the 'tool' function.
"""

import pytest
from org.slashlib.py.agent.tool import tool, Tool

def test_01_tool_decorator_integrity():
    """
    Verify that the tool decorator is importable and callable.
    
    Why: Existence validation as per QA standards.
    """
    assert tool is not None
    assert callable(tool)

def test_02_tool_without_parentheses():
    """
    Test the decorator usage without parentheses: @tool.
    
    Why: This targets the branch 'if len(args) == 1 and callable(args[0])' 
    to ensure the function is immediately wrapped in a Tool instance.
    """
    @tool
    def bare_func(x: int):
        """Docstring for bare_func."""
        return x

    # Assertions
    assert isinstance(bare_func, Tool)
    assert bare_func.name == "bare_func"
    assert bare_func.description == "Docstring for bare_func."

def test_03_tool_with_empty_parentheses():
    """
    Test the decorator usage with empty parentheses: @tool().
    
    Why: Verifies that the function returns the decorator factory first, 
    which then wraps the function.
    """
    @tool()
    def empty_parens_func(x: int):
        """Docstring for empty_parens."""
        return x

    # Assertions
    assert isinstance(empty_parens_func, Tool)
    assert empty_parens_func.name == "empty_parens_func"
    assert empty_parens_func.description == "Docstring for empty_parens."

def test_04_tool_with_custom_parameters():
    """
    Test the decorator usage with explicit name and description: @tool(name=..., description=...).
    
    Why: Ensures that parameters are correctly passed through the decorator factory 
    to the Tool instance.
    """
    custom_name = "overridden_name"
    custom_desc = "Overridden description"

    @tool(name=custom_name, description=custom_desc)
    def param_func(x: int):
        """Original docstring."""
        return x

    # Assertions
    assert isinstance(param_func, Tool)
    assert param_func.name == custom_name
    assert param_func.description == custom_desc

def test_05_tool_decorator_return_types():
    """
    Verify the return types of the tool function depending on arguments.
    
    Why: Validates the dual-nature of the tool function (returning a Tool 
    vs. returning a callable decorator).
    """
    def dummy(): pass

    # Case 1: Called with a function (no parentheses style)
    direct_result = tool(dummy)
    assert isinstance(direct_result, Tool)

    # Case 2: Called with parameters (parentheses style)
    factory_result = tool(name="test")
    assert callable(factory_result)
    assert not isinstance(factory_result, Tool)
    
    # Finalizing the wrap
    final_tool = factory_result(dummy)
    assert isinstance(final_tool, Tool)

# end of file tests/02_00_01_tool_decorator_test.py