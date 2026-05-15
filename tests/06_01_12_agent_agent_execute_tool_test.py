# -*- coding: utf-8 -*-
# file tests/06_01_12_agent_agent_execute_tool_test.py
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
Module: org.slashlib.py.agent.agent
Class: Agent
Method: _execute_tool

Special Considerations:
Using a raw string for this docstring to prevent 'invalid escape sequence' 
warnings related to the module path 'org.slashlib'.
Based on agent.py implementation: _execute_tool returns tool results as 
strings and raises ValueError if the tool is not found.
"""

import pytest
import asyncio
from unittest.mock import MagicMock
from org.slashlib.py.agent.agent import Agent
from org.slashlib.py.agent.inference_bases import InferenceAdapter
from org.slashlib.py.agent.tool import Tool

def test_existence_and_type():
    """
    What: Verify the integrity of the test object.
    Why: Mandatory first test.
    """
    mock_adapter = MagicMock(spec=InferenceAdapter)
    dummy_tool = Tool(lambda: None, name="dummy")
    agent = Agent(identifier="exec-tool-existence", tools=[dummy_tool], adapter=mock_adapter)
    
    assert hasattr(agent, "_execute_tool")
    assert asyncio.iscoroutinefunction(agent._execute_tool)

@pytest.mark.asyncio
async def test_execute_tool_success():
    """
    What: Verify successful tool execution with arguments.
    Why: Ensure results are returned correctly as strings.
    """
    mock_adapter = MagicMock(spec=InferenceAdapter)
    
    def add(a: int, b: int):
        return a + b
    
    calc_tool = Tool(add, name="calculator")
    agent = Agent(identifier="exec-success", tools=[calc_tool], adapter=mock_adapter)
    
    result = await agent._execute_tool(name="calculator", arguments={"a": 5, "b": 10})
    
    # Result is converted to string by the Agent implementation
    assert result == "15"

@pytest.mark.asyncio
async def test_execute_tool_not_found_raises_value_error():
    """
    What: Verify that a ValueError is raised if the tool name is missing.
    Why: Alignment with source code in agent.py:193.
    """
    mock_adapter = MagicMock(spec=InferenceAdapter)
    dummy_tool = Tool(lambda: None, name="dummy")
    agent = Agent(identifier="exec-missing", tools=[dummy_tool], adapter=mock_adapter)
    
    with pytest.raises(ValueError) as excinfo:
        await agent._execute_tool(name="non_existent", arguments={})
    
    assert "not found in agent's toolbox" in str(excinfo.value)

@pytest.mark.asyncio
async def test_execute_tool_exception_propagation():
    """
    What: Verify that tool exceptions propagate up to the caller.
    Why: Ensure the agent doesn't silently swallow tool logic errors.
    """
    def failing_function():
        raise RuntimeError("Tool failed intentionally")
        
    mock_adapter = MagicMock(spec=InferenceAdapter)
    broken_tool = Tool(failing_function, name="broken")
    agent = Agent(identifier="exec-propagate", tools=[broken_tool], adapter=mock_adapter)
    
    with pytest.raises(RuntimeError) as excinfo:
        await agent._execute_tool(name="broken", arguments={})
    
    assert "Tool failed intentionally" in str(excinfo.value)

@pytest.mark.asyncio
async def test_execute_tool_with_async_tool():
    """
    What: Verify handling of asynchronous tool functions.
    Why: Ensure coroutines are properly awaited.
    """
    async def async_tool_func(val: str):
        return f"processed {val}"
        
    mock_adapter = MagicMock(spec=InferenceAdapter)
    a_tool = Tool(async_tool_func, name="async_tool")
    agent = Agent(identifier="exec-async-tool", tools=[a_tool], adapter=mock_adapter)
    
    result = await agent._execute_tool(name="async_tool", arguments={"val": "data"})
    assert result == "processed data"

# end of file tests/06_01_12_agent_agent_execute_tool_test.py    