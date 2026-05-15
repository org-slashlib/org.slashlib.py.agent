# -*- coding: utf-8 -*-
# file tests/06_01_15_agent_agent_run_test.py
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
Method: run

Special Considerations:
asyncio.create_task() requires a real coroutine object. 
Mocks must be configured to return a coroutine when called.
"""

import pytest
import asyncio
from unittest.mock import MagicMock, patch, AsyncMock
from org.slashlib.py.agent.agent import Agent
from org.slashlib.py.agent.tool import Tool

@pytest.fixture
def dummy_agent():
    mock_adapter = MagicMock()
    dummy_tool = Tool(lambda: "ok", name="dummy")
    return Agent(identifier="public-run-test", tools=[dummy_tool], adapter=mock_adapter)

def test_existence_and_type(dummy_agent):
    """
    What: Verify the integrity of the test object.
    """
    assert hasattr(dummy_agent, "run")
    assert not asyncio.iscoroutinefunction(dummy_agent.run)

@pytest.mark.asyncio
async def test_run_returns_task(dummy_agent):
    """
    What: Verify that run() returns an asyncio.Task.
    """
    # We use a simple async function to ensure a real coroutine is returned
    async def mock_coro(**kwargs):
        return MagicMock()

    with patch.object(Agent, '_run', side_effect=mock_coro):
        task = dummy_agent.run(user_input="Hello")
        try:
            assert isinstance(task, asyncio.Task)
            assert not task.done()
        finally:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass

@pytest.mark.asyncio
async def test_run_executes_internal_run(dummy_agent):
    """
    What: Verify that the task actually executes the internal logic.
    Why: Fixed TypeError by ensuring _run returns a coroutine.
    """
    mock_response = MagicMock()
    
    # Define a local coroutine to act as the implementation
    async def fake_run(**kwargs):
        return mock_response

    with patch.object(Agent, '_run', side_effect=fake_run) as mock_internal:
        task = dummy_agent.run(user_input="Execute logic")
        result = await task
        
        assert result == mock_response
        mock_internal.assert_called_once_with(user_input="Execute logic")

@pytest.mark.asyncio
async def test_run_with_multiple_kwargs(dummy_agent):
    """
    What: Verify passthrough of all keyword arguments.
    """
    async def fake_run(**kwargs):
        return True

    with patch.object(Agent, '_run', side_effect=fake_run) as mock_internal:
        kwargs = {"prompt": "test", "temperature": 0.7}
        task = dummy_agent.run(**kwargs)
        await task
        
        mock_internal.assert_called_once_with(**kwargs)

# end of file tests/06_01_15_agent_agent_run_test.py