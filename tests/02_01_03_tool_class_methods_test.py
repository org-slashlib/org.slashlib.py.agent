# -*- coding: utf-8 -*-
# file tests/02_01_03_tool_class_methods_test.py
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
from org.slashlib.py.agent.tool import Tool


def test_tool_skips_explicit_self_and_cls():
    """
    Test if 'self' and 'cls' are correctly excluded from the JSON schema parameters.
    This specifically targets the 'continue' branch by providing functions
    that explicitly include these names in their signature.
    """
    
    # 1. Simulate an unbound instance method signature
    def fake_instance_method(self, data: str):
        """Method with explicit self."""
        return data

    # 2. Simulate a class method signature
    def fake_class_method(cls, data: str):
        """Method with explicit cls."""
        return data

    # --- Test 'self' exclusion ---
    tool_self = Tool(fake_instance_method)
    schema_self = tool_self.get_schema()
    
    # Navigiere in den ["function"] Baum
    props_self = schema_self["function"]["parameters"]["properties"]
    
    assert "data" in props_self
    assert "self" not in props_self  # Verifiziert den 'continue' Block für 'self'
    assert "self" not in schema_self["function"]["parameters"].get("required", [])

    # --- Test 'cls' exclusion ---
    tool_cls = Tool(fake_class_method)
    schema_cls = tool_cls.get_schema()
    
    # Navigiere in den ["function"] Baum
    props_cls = schema_cls["function"]["parameters"]["properties"]
    
    assert "data" in props_cls
    assert "cls" not in props_cls   # Verifiziert den 'continue' Block für 'cls'
    assert "cls" not in schema_cls["function"]["parameters"].get("required", [])


def test_tool_unbound_method_from_class():
    """
    Passing the method directly from the class without an instance.
    """
    class Target:
        def method(self, arg1: int):
            pass

    test_tool = Tool(Target.method)
    schema = test_tool.get_schema()

    # Korrektur: Navigiere in den ["function"] Baum
    assert "arg1" in schema["function"]["parameters"]["properties"]
    assert "self" not in schema["function"]["parameters"]["properties"]

# No __all__ export needed for test files as they are not meant to be imported as modules.