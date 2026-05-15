# -*- coding: utf-8 -*-
# file tests/02_01_05_tool_Tool___init___test.py

"""
Testsuite for the org.slashlib.py.agent.tool module.
Tested Class: Tool
Tested Method: __init__

Special Considerations:
- Focuses on the correct wrapping of functions (sync and async).
- Validates the metadata extraction (name, docstring).
- Checks the functionality of the functools.update_wrapper integration.
"""

import pytest
import asyncio
from org.slashlib.py.agent.tool import Tool

def test_01_tool_init_integrity():
    """
    Test the integrity and type of the Tool class and its constructor.
    
    Why: To ensure the class is importable and follows the expected structure 
    before running deeper functional tests.
    """
    assert Tool is not None
    assert isinstance(Tool, type)
    assert hasattr(Tool, "__init__")

def test_02_tool_init_with_defaults():
    """
    Test initialization of Tool with default values extracted from the function.
    
    Why: Verifies that the Tool class correctly extracts the function name 
    and docstring if no overrides are provided.
    """
    def sample_func(a: int, b: int):
        """This is a sample docstring."""
        return a + b

    tool_inst = Tool(sample_func)
    
    assert tool_inst.name == "sample_func"
    assert tool_inst.description == "This is a sample docstring."
    assert tool_inst._func == sample_func

def test_03_tool_init_with_overrides():
    """
    Test initialization of Tool with explicit name and description overrides.
    
    Why: Verifies that the constructor respects user-provided metadata 
    instead of using the function's defaults.
    """
    def sample_func():
        pass

    custom_name = "custom_tool_name"
    custom_desc = "Custom tool description."
    
    tool_inst = Tool(sample_func, name=custom_name, description=custom_desc)
    
    assert tool_inst.name == custom_name
    assert tool_inst.description == custom_desc

def test_04_tool_init_missing_docstring_fallback():
    """
    Test the fallback mechanism when a function has no docstring.
    
    Why: Ensures the agent always has at least a default description 
    to prevent errors in schema generation or LLM processing.
    """
    def no_doc_func():
        pass

    tool_inst = Tool(no_doc_func)
    assert tool_inst.description == "No description provided."

def test_05_tool_init_wrapper_metadata():
    """
    Test if functools.update_wrapper correctly preserves function attributes.
    
    Why: Essential for debugging and compatibility with other decorators 
    or inspection tools that rely on __name__ or __module__.
    """
    def metadata_func():
        pass

    tool_inst = Tool(metadata_func)
    
    assert tool_inst.__name__ == metadata_func.__name__
    assert tool_inst.__module__ == metadata_func.__module__

@pytest.mark.asyncio
async def test_06_tool_init_async_function_support():
    """
    Test if the Tool class correctly accepts and stores asynchronous functions.
    
    Why: The framework is built on asyncio, so it must handle coroutines 
    identically to standard functions during initialization.
    """
    async def async_func(x: int):
        await asyncio.sleep(0)
        return x

    tool_inst = Tool(async_func)
    assert tool_inst.name == "async_func"
    assert asyncio.iscoroutinefunction(tool_inst._func)
    