# -*- coding: utf-8 -*-
# file tests/03_01_14_agent_agent_response_response_test.py
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
Module: org.slashlib.py.agent.agent_response
Class: AgentResponse
Property: response

Tests the logic for retrieving the final assistant response from the context.
Verifies correct filtering of roles and handling of empty or non-assistant histories.
"""

import pytest
from org.slashlib.py.agent.agent_response import AgentResponse


def test_response_returns_latest_assistant_message():
    """
    What: Verify that the property returns the content of the LAST assistant message.
    Why: The history might contain multiple assistant turns; the last one is the current result.
    """
    response = AgentResponse()
    response.append_context(role="assistant", content="First thought")
    response.append_context(role="user", content="Go on")
    response.append_context(role="assistant", content="Final answer")
    
    # Should return "Final answer" and skip "First thought"
    assert response.response == "Final answer"


def test_response_returns_none_if_no_assistant_message():
    """
    What: Verify that None is returned if the context contains no assistant role.
    """
    response = AgentResponse()
    response.append_context(role="system", content="Init")
    response.append_context(role="user", content="Hello")
    
    assert response.response is None


def test_response_with_tool_calls_interleaved():
    """
    What: Verify that assistant content is found even if tool messages follow it.
    """
    response = AgentResponse()
    response.append_context(role="assistant", content="I will call a tool")
    response.append_context(role="tool", content="Tool result", tool_call_id="1")
    
    # It should still find the last assistant message
    assert response.response == "I will call a tool"


def test_response_empty_context():
    """
    What: Verify behavior on a fresh AgentResponse object.
    """
    response = AgentResponse()
    assert response.response is None


def test_response_is_read_only():
    """
    What: Verify that the response property cannot be set directly.
    """
    response = AgentResponse()
    with pytest.raises(AttributeError):
        response.response = "Attempt to set" # type: ignore


# end of file tests/03_01_14_agent_agent_response_response_test.py