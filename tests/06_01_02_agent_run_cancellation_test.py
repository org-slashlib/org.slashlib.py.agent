# -*- coding: utf-8 -*-
# file tests/06_01_02_agent_run_cancellation_test.py
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
import pytest
import json
from unittest.mock import AsyncMock, MagicMock
from org.slashlib.py.agent.agent import Agent
from org.slashlib.py.agent.inference_bases import InferenceAdapter, InferenceResult
from org.slashlib.py.agent.tool import Tool

@pytest.mark.asyncio
async def test_agent_run_executes_tool_call_id_assignment():
    """
    Targets Line 224: context_kwargs["tool_call_id"] = tool_call_id
    """
    # 1. Mock für das erste Result (Assistant fordert Tool an)
    mock_result_tool = MagicMock(spec=InferenceResult)
    mock_result_tool.role = "assistant"
    mock_result_tool.content = "Ich rufe ein Tool auf."
    # WICHTIG: 'arguments' als dict, falls der Agent es direkt entpackt
    # 'id' muss vorhanden sein für Zeile 224
    mock_result_tool.tool_calls = [{
        "id": "call_12345",
        "function": {
            "name": "get_info",
            "arguments": {"query": "test"} 
        }
    }]
    # Der Agent ruft oft to_dict() auf, um den Kontext zu speichern
    mock_result_tool.to_dict.return_value = {
        "role": "assistant", 
        "content": "Ich rufe ein Tool auf.",
        "tool_calls": mock_result_tool.tool_calls
    }

    # 2. Mock für das finale Result
    mock_result_final = MagicMock(spec=InferenceResult)
    mock_result_final.role = "assistant"
    mock_result_final.content = "Hier ist deine Info."
    mock_result_final.tool_calls = None
    mock_result_final.to_dict.return_value = {
        "role": "assistant", 
        "content": "Hier ist deine Info."
    }

    mock_adapter = MagicMock(spec=InferenceAdapter)
    mock_adapter.chat = AsyncMock(side_effect=[mock_result_tool, mock_result_final])

    # 3. Das Tool
    async def get_info(query: str):
        return f"Info für {query}"

    test_tool = Tool(get_info, name="get_info")
    agent = Agent(identifier="test-id-224", tools=[test_tool], adapter=mock_adapter)

    # 4. Ausführung
    # Wir nutzen await agent.run(...) direkt, um an das AgentResponse Objekt zu kommen
    response = await agent.run(user_prompt="Frag nach Info")

    # Verifikation
    # Der Fehler 'None == Hier ist deine Info' lag oft daran, dass der Agent 
    # bei Tool-Fehlern den Durchlauf abbricht.
    assert response.response == "Hier ist deine Info."
    assert not response.has_error

# end of file tests/06_01_02_agent_run_cancellation_test.py    