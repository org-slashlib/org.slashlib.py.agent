# -*- coding: utf-8 -*-
# file tests/06_01_06_agent_agent_del_test.py
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
Method: __del__

Special Considerations:
Testing __del__ requires careful handling of the asyncio event loop. 
Since __initating__ a cancellation is synchronous but completing it is 
asynchronous, the test must yield control back to the loop to verify 
that the tasks transitioned from 'cancelling' to 'done/cancelled'.
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
    Why: Mandatory first test to ensure the class is importable and the method exists.
    Assumptions: The Agent class implementation includes a __del__ method.
    """
    assert Agent is not None
    assert hasattr(Agent, "__del__")
    assert callable(Agent.__del__)

@pytest.mark.asyncio
async def test_agent_del_cancels_active_tasks():
    """
    What: Verify that __del__ initiates cancellation for all tasks in _active_tasks.
    Why: To ensure proper resource management.
    Assumptions: The Agent class stores running tasks in self._active_tasks. 
                 Cancellation requires a loop cycle to complete.
    """
    mock_adapter = MagicMock(spec=InferenceAdapter)
    
    async def hanging_task(*args, **kwargs):
        try:
            await asyncio.sleep(100)
        except asyncio.CancelledError:
            # Task acknowledges cancellation
            raise

    mock_adapter.chat = AsyncMock(side_effect=hanging_task)
    dummy_tool = Tool(lambda: None, name="dummy")
    
    agent = Agent(identifier="del-cleanup-test-v3", tools=[dummy_tool], adapter=mock_adapter)
    task = agent.run(user_prompt="Run forever")
    
    # Let the task reach the 'chat' await point
    await asyncio.sleep(0.05)
    
    assert task in agent._active_tasks
    assert not task.done()

    # Trigger destructor logic (synchronous call)
    agent.__del__()

    # Crucial: Yield to the event loop so the CancelledError can be 
    # processed by the 'hanging_task' coroutine.
    await asyncio.sleep(0.05)

    # Now the task should be fully done/cancelled
    assert task.done(), "Task should be done after event loop processing"
    # Note: .cancelled() is True only if the task was cancelled and NOT caught 
    # and suppressed. .done() covers both successful cancellation and completion.
    assert task not in agent._active_tasks

def test_agent_del_handles_empty_tasks():
    """
    What: Test __del__ when no tasks are active.
    Why: To ensure robustness.
    Assumptions: Calling __del__ on an idle agent is a valid operation.
    """
    mock_adapter = MagicMock(spec=InferenceAdapter)
    dummy_tool = Tool(lambda: None, name="dummy")
    agent = Agent(identifier="del-empty-test", tools=[dummy_tool], adapter=mock_adapter)
    
    try:
        agent.__del__()
    except Exception as e:
        pytest.fail(f"__del__ raised an unexpected exception: {e}")

def test_agent_del_idempotency_check():
    """
    What: Test if calling __del__ multiple times causes issues.
    Why: Destructors should be safe even if triggered multiple times.
    Assumptions: The method is re-entrant safe.
    """
    mock_adapter = MagicMock(spec=InferenceAdapter)
    dummy_tool = Tool(lambda: None, name="dummy")
    agent = Agent(identifier="del-idempotency-test", tools=[dummy_tool], adapter=mock_adapter)
    
    agent.__del__()
    agent.__del__()

# end of file tests/06_01_06_agent_agent_del_test.py