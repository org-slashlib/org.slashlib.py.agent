# -*- coding: utf-8 -*-
# file tests/06_01_13_agent_agent_run_tool_calls_test.py
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
Method: _run_tool_calls

Special Considerations:
Based on failures, _run_tool_calls passes arguments positionally to 
_execute_tool and does NOT deserialize JSON strings in 'arguments'. 
It passes whatever is in the tool_call dictionary directly.
"""

import pytest
import asyncio
import typing
from unittest.mock import MagicMock, AsyncMock, patch
from org.slashlib.py.agent.agent import Agent
from org.slashlib.py.agent.agent_response import AgentResponse
from org.slashlib.py.agent.inference_bases import InferenceAdapter
from org.slashlib.py.agent.tool import Tool

@pytest.fixture
def dummy_tool():
    return Tool(lambda: "ok", name="dummy")

def test_existence_and_type(dummy_tool):
    """
    What: Verify the integrity of the test object.
    """
    mock_adapter = MagicMock(spec=InferenceAdapter)
    agent = Agent(identifier="run-tools-existence", tools=[dummy_tool], adapter=mock_adapter)
    
    assert hasattr(agent, "_run_tool_calls")
    assert asyncio.iscoroutinefunction(agent._run_tool_calls)

@pytest.mark.asyncio
async def test_run_tool_calls_none_handling(dummy_tool):
    """
    What: Verify behavior when tool_calls is None or empty.
    """
    mock_adapter = MagicMock(spec=InferenceAdapter)
    agent = Agent(identifier="run-tools-none", tools=[dummy_tool], adapter=mock_adapter)
    mock_response = MagicMock(spec=AgentResponse)
    
    assert await agent._run_tool_calls(mock_response, None) is False
    assert await agent._run_tool_calls(mock_response, []) is False

@pytest.mark.asyncio
async def test_run_tool_calls_success_flow(dummy_tool):
    """
    What: Verify the flow of processing tool calls.
    Why: Alignment with positional calls and raw string passing.
    """
    mock_adapter = MagicMock(spec=InferenceAdapter)
    agent = Agent(identifier="run-tools-success", tools=[dummy_tool], adapter=mock_adapter)
    mock_response = MagicMock(spec=AgentResponse)
    
    tool_calls = [
        {
            "id": "call_123",
            "function": {"name": "dummy", "arguments": "{}"}
        }
    ]
    
    with patch.object(Agent, '_execute_tool', new_callable=AsyncMock) as mock_exec:
        mock_exec.return_value = "executed_result"
        
        result = await agent._run_tool_calls(mock_response, tool_calls)
        
        assert result is True
        # Verify positional call with raw string as confirmed by previous failure
        mock_exec.assert_called_once_with("dummy", "{}")
        mock_response.append_context.assert_called()

@pytest.mark.asyncio
async def test_run_tool_calls_raw_string_passthrough(dummy_tool):
    """
    What: Verify that arguments are passed as-is (strings), not parsed.
    Why: Confirmed by previous KeyError/AssertionError.
    """
    mock_adapter = MagicMock(spec=InferenceAdapter)
    agent = Agent(identifier="run-tools-pass", tools=[dummy_tool], adapter=mock_adapter)
    mock_response = MagicMock(spec=AgentResponse)
    
    raw_json = '{"key": "value"}'
    tool_calls = [{
        "id": "c1",
        "function": {"name": "dummy", "arguments": raw_json}
    }]
    
    with patch.object(Agent, '_execute_tool', new_callable=AsyncMock) as mock_exec:
        await agent._run_tool_calls(mock_response, tool_calls)
        
        # Check positional args: call(name, arguments)
        args, kwargs = mock_exec.call_args
        assert args[0] == "dummy"
        assert args[1] == raw_json  # Still a string

@pytest.mark.asyncio
async def test_run_tool_calls_error_capture(dummy_tool):
    """
    What: Verify that tool execution errors are captured and added to context.
    Why: Prevents a single tool error from stopping the agent sequence.
    """
    mock_adapter = MagicMock(spec=InferenceAdapter)
    agent = Agent(identifier="run-tools-error", tools=[dummy_tool], adapter=mock_adapter)
    mock_response = MagicMock(spec=AgentResponse)
    
    tool_calls = [
        {"id": "err1", "function": {"name": "dummy", "arguments": "{}"}}
    ]
    
    # Simulate a failure in tool execution
    with patch.object(Agent, '_execute_tool', side_effect=ValueError("Simulated Failure")):
        result = await agent._run_tool_calls(mock_response, tool_calls)
        
        # It still returns True because it processed the (failed) call
        assert result is True 
        
        # Verify context updated with the error message
        mock_response.append_context.assert_called()
        # Verify the call includes the word 'error' or the message
        args, kwargs = mock_response.append_context.call_args
        # kwargs usually contain role='tool' and content='Error...'
        assert any("Simulated Failure" in str(v) for v in kwargs.values())

# end of file tests/06_01_13_agent_agent_run_tool_calls_test.py