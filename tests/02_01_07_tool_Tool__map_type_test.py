# -*- coding: utf-8 -*-
# file tests/02_01_07_tool_Tool__map_type_test.py

"""
Testsuite for the org.slashlib.py.agent.tool module.
Tested Class: Tool
Tested Method: _map_type

Special Considerations:
- Full path coverage for the type mapping logic.
- Tests basic types, typing generics, and Union/Optional unwrapping.
- Ensures fallback to 'string' for unknown types to maintain LLM compatibility.
"""

import pytest
import typing
from org.slashlib.py.agent.tool import Tool

def test_01_tool_map_type_integrity():
    """
    Test the integrity and access of the _map_type method.
    
    Why: To ensure the internal method is available and follows the expected 
    signature before running functional tests.
    """
    def dummy(): pass
    tool_inst = Tool(dummy)
    assert hasattr(tool_inst, "_map_type")
    assert callable(tool_inst._map_type)

def test_02_tool_map_type_primitives():
    """
    Test mapping of all basic Python primitive types defined in the mapping dict.
    
    Why: Validates the core dictionary mapping for standard types.
    """
    def dummy(): pass
    tool_inst = Tool(dummy)
    
    assert tool_inst._map_type(int) == "integer"
    assert tool_inst._map_type(float) == "number"
    assert tool_inst._map_type(str) == "string"
    assert tool_inst._map_type(bool) == "boolean"
    assert tool_inst._map_type(list) == "array"
    assert tool_inst._map_type(dict) == "object"

def test_03_tool_map_type_typing_generics():
    """
    Test mapping of typing module aliases (List, Dict).
    
    Why: Ensures that older typing aliases or subscripted generics are 
    correctly identified via their origin.
    """
    def dummy(): pass
    tool_inst = Tool(dummy)
    
    # Non-subscripted typing aliases
    assert tool_inst._map_type(typing.List) == "array"
    assert tool_inst._map_type(typing.Dict) == "object"
    
    # Subscripted generics (origin check)
    assert tool_inst._map_type(typing.List[int]) == "array"
    assert tool_inst._map_type(typing.Dict[str, typing.Any]) == "object"

def test_04_tool_map_type_optional_unwrapping():
    """
    Test the recursive unwrapping of Optional types.
    
    Why: LLMs require the underlying base type. Optional[T] is internally 
    Union[T, None], which the method must resolve to T.
    """
    def dummy(): pass
    tool_inst = Tool(dummy)
    
    # Standard Optional
    assert tool_inst._map_type(typing.Optional[int]) == "integer"
    assert tool_inst._map_type(typing.Optional[typing.List[str]]) == "array"
    
    # Explicit Union with None
    assert tool_inst._map_type(typing.Union[str, None]) == "string"
    assert tool_inst._map_type(typing.Union[None, float]) == "number"

def test_05_tool_map_type_complex_union_logic():
    """
    Test how the method handles Unions with multiple actual types.
    
    Why: The current implementation returns the mapping of the first 
    non-None type in the Union.
    """
    def dummy(): pass
    tool_inst = Tool(dummy)
    
    # Should take the first type (int -> integer)
    assert tool_inst._map_type(typing.Union[int, str]) == "integer"
    # Should skip None and take float
    assert tool_inst._map_type(typing.Union[type(None), float, int]) == "number"

def test_06_tool_map_type_nested_unwrapping():
    """
    Test recursive behavior for nested Unions/Optionals.
    
    Why: Stress test for the recursive call within the Union handling logic.
    """
    def dummy(): pass
    tool_inst = Tool(dummy)
    
    nested_type = typing.Optional[typing.Union[typing.List[int], None]]
    assert tool_inst._map_type(nested_type) == "array"

def test_07_tool_map_type_fallback_cases():
    """
    Test fallback to 'string' for any unmapped or complex types.
    
    Why: Ensures the schema generation is robust and doesn't fail 
    on custom classes or unhandled typing constructs.
    """
    class MyCustomClass: pass
    
    def dummy(): pass
    tool_inst = Tool(dummy)
    
    # Custom class
    assert tool_inst._map_type(MyCustomClass) == "string"
    # Any type (usually not in mapping)
    assert tool_inst._map_type(typing.Any) == "string"
    # Empty Union (edge case, though unlikely in valid Python)
    # Note: typing.Union without args is not valid, but we test None
    assert tool_inst._map_type(None) == "string"

def test_08_tool_map_type_iterable_types():
    """
    Test other iterable types like set or tuple.
    
    Why: To verify that types not explicitly in the mapping dict 
    correctly default to 'string' (unless we decide to map them to 'array').
    """
    def dummy(): pass
    tool_inst = Tool(dummy)
    
    # Set and Tuple are currently not in the mapping -> should be 'string'
    assert tool_inst._map_type(set) == "string"
    assert tool_inst._map_type(tuple) == "string"
 
