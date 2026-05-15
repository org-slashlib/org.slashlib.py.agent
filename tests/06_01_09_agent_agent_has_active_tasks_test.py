# -*- coding: utf-8 -*-
# file tests/06_01_09_agent_agent_has_active_tasks_test.py
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
Method: has_active_tasks (property)

Special Considerations:
This property reflects the state of background tasks. Tests must ensure that 
the background tasks do not crash due to malformed mock responses, as a 
crash triggers immediate removal from the active tasks set.
"""

import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock
from org.slashlib.py.agent.agent import Agent
from org.slashlib.py.agent.inference_bases import InferenceAdapter
from org.slashlib.py.agent.tool import Tool

def test_existence_and_type():
    """
    What: Verify the integrity of the test object.
    Why: Mandatory first test to ensure the property is accessible.
    Assumptions: The Agent class implementation includes a 'has_active_tasks' property.
    """
    mock_adapter = MagicMock(spec=InferenceAdapter)
    dummy_tool = Tool(lambda: None, name="dummy")
    agent = Agent(identifier="has-tasks-existence", tools=[dummy_tool], adapter=mock_adapter)
    
    assert hasattr(agent, "has_active_tasks")
    assert isinstance(getattr(type(agent), "has_active_tasks"), property)
    assert isinstance(agent.has_active_tasks, bool)

@pytest.mark.asyncio
async def test_has_active_tasks_transitions():
    """
    What: Verify property transitions based on task lifecycle.
    Why: To ensure the boolean correctly reflects the presence of tasks.
    Assumptions: Using a controlled mock result to prevent task crashes.
    """
    mock_adapter = MagicMock(spec=InferenceAdapter)
    stop_event = asyncio.Event()

    async def controlled_chat(*args, **kwargs):
        await stop_event.wait()
        res = MagicMock()
        res.role = "assistant"
        res.content = "done"
        res.tool_calls = None
        res.to_dict.return_value = {"role": "assistant", "content": "done"}
        return res

    mock_adapter.chat = AsyncMock(side_effect=controlled_chat)
    dummy_tool = Tool(lambda: "ok", name="dummy")
    agent = Agent(identifier="has-tasks-transition", tools=[dummy_tool], adapter=mock_adapter)

    assert agent.has_active_tasks is False

    task = agent.run(user_prompt="start")
    await asyncio.sleep(0.05)
    assert agent.has_active_tasks is True

    stop_event.set()
    await task
    await asyncio.sleep(0.05)
    assert agent.has_active_tasks is False

@pytest.mark.asyncio
async def test_has_active_tasks_with_multiple_tasks():
    """
    What: Verify property remains True if at least one task is active.
    Why: To ensure the logic checks for a non-empty collection of tasks.
    Assumptions: The side_effect must return a valid mock object to avoid AttributeError.
    """
    mock_adapter = MagicMock(spec=InferenceAdapter)
    
    async def slow_valid_response(*args, **kwargs):
        await asyncio.sleep(1) # Keep task alive
        res = MagicMock()
        res.to_dict.return_value = {"role": "assistant", "content": "slow"}
        return res

    mock_adapter.chat = AsyncMock(side_effect=slow_valid_response)
    dummy_tool = Tool(lambda: "ok", name="dummy")
    
    agent = Agent(identifier="has-tasks-multi-v2", tools=[dummy_tool], adapter=mock_adapter, multi=True)

    task1 = agent.run(user_prompt="task1")
    task2 = agent.run(user_prompt="task2")
    
    # Wait for tasks to register
    await asyncio.sleep(0.05)
    
    try:
        assert agent.has_active_tasks is True

        # Cancel one task
        task1.cancel()
        await asyncio.gather(task1, return_exceptions=True)
        
        # Should still be True because task2 is alive
        assert agent.has_active_tasks is True
    finally:
        # Cleanup remaining task
        task2.cancel()
        await asyncio.gather(task2, return_exceptions=True)

def test_has_active_tasks_is_read_only():
    """
    What: Test that has_active_tasks cannot be manually set.
    Why: Integrity of computed properties.
    Assumptions: No setter defined.
    """
    mock_adapter = MagicMock(spec=InferenceAdapter)
    dummy_tool = Tool(lambda: None, name="dummy")
    agent = Agent(identifier="has-tasks-readonly", tools=[dummy_tool], adapter=mock_adapter)
    
    with pytest.raises(AttributeError):
        agent.has_active_tasks = True

# end of file tests/06_01_09_agent_agent_has_active_tasks_test.py        