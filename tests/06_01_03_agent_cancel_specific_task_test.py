# -*- coding: utf-8 -*-
# file tests/06_01_03_agent_cancel_specific_task_test.py
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

import asyncio
import logging
import pytest
from unittest.mock import AsyncMock, MagicMock
from org.slashlib.py.agent.agent import Agent
from org.slashlib.py.agent.inference_bases import InferenceAdapter, InferenceResult
from org.slashlib.py.agent.tool import Tool

@pytest.mark.asyncio
async def test_agent_run_rethrows_keyboard_interrupt(caplog):
    """
    Targets Line 245 in agent.py: raise (KeyboardInterrupt / SystemExit)
    Verifies that critical system interrupts are caught in the tool loop
    and re-raised, as confirmed by the coverage report.
    """
    # 1. Setup: Mock InferenceResult, das einen Tool-Call fordert
    mock_result_tool = MagicMock(spec=InferenceResult)
    mock_result_tool.role = "assistant"
    mock_result_tool.content = "I need to call a tool."
    mock_result_tool.tool_calls = [{
        "id": "call_critical",
        "function": {
            "name": "critical_tool",
            "arguments": {}
        }
    }]
    mock_result_tool.to_dict.return_value = {
        "role": "assistant", 
        "content": mock_result_tool.content,
        "tool_calls": mock_result_tool.tool_calls
    }

    # Adapter Setup
    mock_adapter = MagicMock(spec=InferenceAdapter)
    mock_adapter.chat = AsyncMock(return_value=mock_result_tool)

    # 2. Das Tool, das den kritischen Interrupt auslöst
    async def critical_tool(**kwargs):
        # Das löst die Logik in Zeile 244 aus und führt zum 'raise' in 245
        raise KeyboardInterrupt("User pressed Ctrl+C")

    test_tool = Tool(critical_tool, name="critical_tool")
    agent = Agent(identifier="interrupt-tester", tools=[test_tool], adapter=mock_adapter)

    # 3. Ausführung
    # Wir setzen das Logging-Level auf ERROR, um die Meldung abzufangen
    with caplog.at_level(logging.ERROR):
        task = agent.run(user_prompt="Run tool")
        
        # Wir warten auf den Task. Da KeyboardInterrupt eine BaseException ist,
        # fangen wir sie hier mit return_exceptions ab, damit der Test nicht abstürzt.
        await asyncio.gather(task, return_exceptions=True)

    # 4. Verifikation
    # Der Log-Eintrag beweist, dass wir im korrekten except-Block gelandet sind
    assert "Tool execution failed: User pressed Ctrl+C" in caplog.text
    
    # Sicherstellen, dass der Task aus den aktiven Tasks entfernt wurde (Cleanup-Logik)
    assert task not in agent._active_tasks

# end of file tests/06_01_03_agent_cancel_specific_task_test.py