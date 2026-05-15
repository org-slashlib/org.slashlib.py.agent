# -*- coding: utf-8 -*-
# file tests/06_01_16_agent_agent_cancel_test.py
# @AI:
# - INTEGRITY RULES:
#    - STRICT PRESERVATION: Do not remove, move, or modify ANY existing lines of code or comments 
#      unless they are the explicit target of the requested change. 
#    - DEBUG MARKERS: Commented-out code (e.g., debug prints) MUST be kept exactly where they are.
#    - WHITESPACE & STRUCTURE: Maintain all original empty lines and the existing file structure. 
#      Structural integrity takes precedence over "clean code" or "elegance".
#    - LEAD-IN/OUT: The very first and last lines (and all comments in between) are immutable anchors.
# - MAINTENANCE:
#    - Only update pydoc strings (args, returns, raises) if the function signature changes.
#    - Do NOT delete existing examples or descriptions in pydoc.
# - LANGUAGE: en-US for all comments and documentation.
#

"""
Module: org.slashlib.py.agent.agent
Class: Agent
Method: cancel

Special Considerations:
Testing the cancellation of specific tasks and all tasks. 
Focus on correctly hitting the internal registry _active_tasks.
"""

import pytest
import asyncio
import logging
from unittest.mock import MagicMock, patch
from org.slashlib.py.agent.agent import Agent
from org.slashlib.py.agent.tool import Tool

@pytest.fixture
def dummy_agent():
    mock_adapter = MagicMock()
    dummy_tool = Tool(lambda: "ok", name="dummy")
    return Agent(identifier="cancel-test", tools=[dummy_tool], adapter=mock_adapter)

def test_existence_and_type(dummy_agent):
    """
    What: Verify the integrity of the test object.
    """
    assert hasattr(dummy_agent, "cancel")
    assert not asyncio.iscoroutinefunction(dummy_agent.cancel)

@pytest.mark.asyncio
async def test_cancel_explicit_task_success(dummy_agent):
    """
    What: Verify cancellation of a task provided as an argument.
    Why: Targets coverage for lines 334-335.
    """
    async def work():
        await asyncio.sleep(5)
        
    task = asyncio.create_task(work())
    
    # We add the task to the real internal registry
    dummy_agent._active_tasks.add(task)
    
    try:
        dummy_agent.cancel(task)
        
        # Verify the task was actually cancelled
        assert task.cancelling() > 0 or task.cancelled()
    finally:
        # Cleanup
        if not task.done():
            task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass

@pytest.mark.asyncio
async def test_cancel_all_tasks(dummy_agent):
    """
    What: Verify that calling cancel() without arguments cancels all tasks.
    Why: Targets coverage for the 'for t in list(self._active_tasks)' loop.
    """
    async def work():
        await asyncio.sleep(5)
        
    t1 = asyncio.create_task(work())
    t2 = asyncio.create_task(work())
    
    dummy_agent._active_tasks.add(t1)
    dummy_agent._active_tasks.add(t2)
    
    try:
        dummy_agent.cancel()
        
        assert t1.cancelling() > 0 or t1.cancelled()
        assert t2.cancelling() > 0 or t2.cancelled()
    finally:
        for t in [t1, t2]:
            if not t.done():
                t.cancel()
            try:
                await t
            except asyncio.CancelledError:
                pass

@pytest.mark.asyncio
async def test_cancel_with_none_and_empty_registry(dummy_agent, caplog):
    """
    What: Verify behavior when no tasks are present.
    """
    dummy_agent._active_tasks.clear()
    
    with caplog.at_level(logging.DEBUG):
        dummy_agent.cancel(None)
        assert "No active tasks to cancel" in caplog.text

@pytest.mark.asyncio
async def test_cancel_missing_task_warning(dummy_agent, caplog):
    """
    What: Verify warning when trying to cancel a task not in the registry.
    """
    async def quick():
        pass
    task = asyncio.create_task(quick())
    
    dummy_agent._active_tasks.clear()
    
    with caplog.at_level(logging.WARNING):
        dummy_agent.cancel(task)
        assert "not found in active tasks" in caplog.text
    
    await task

@pytest.mark.asyncio
async def test_cancel_already_finished_task(dummy_agent):
    """
    What: Verify robustness when cancelling a task that is already done.
    """
    async def finished():
        return "ok"
    
    task = asyncio.create_task(finished())
    await task
    
    dummy_agent._active_tasks.add(task)
    # Should not raise any error
    dummy_agent.cancel(task)

# end of file tests/06_01_16_agent_agent_cancel_test.py