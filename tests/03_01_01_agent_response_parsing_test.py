# -*- coding: utf-8 -*-
# file tests/03_01_01_agent_response_parsing_test.py
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

# Python imports
import typing

# Third party imports
import pytest

# Internal imports
from org.slashlib.py.agent.agent_response import AgentResponse


def test_agent_response_init_and_empty():
    """
    Test the initial state of an AgentResponse instance.
    """
    response = AgentResponse()
    assert response.context_size == 0
    assert response.response is None
    assert response.has_error is False
    assert response.has_tool_error is False


def test_agent_response_append_text_context():
    """
    Test adding simple text context and retrieving it via the response property.
    """
    response = AgentResponse()
    response.append_context(role="user", content="Hello")
    response.append_context(role="assistant", content="Hi there!")
    
    assert response.context_size == 2
    assert response.response == "Hi there!"


def test_agent_response_json_serialization():
    """
    Test the automatic JSON serialization of dict/list content in append_context.
    This targets the internal _append_context logic.
    """
    response = AgentResponse()
    tool_content = {"tool": "weather", "result": "sunny"}
    
    response.append_context(role="tool", content=tool_content)
    
    # The content should now be a JSON string
    stored_context = response.get_context(0)
    assert isinstance(stored_context["content"], str)
    assert '"tool": "weather"' in stored_context["content"]


def test_agent_response_error_handling():
    """
    Test recording and raising of process errors.
    """
    response = AgentResponse()
    error = ValueError("Fatal system error")
    
    response.append_error(error)
    assert response.has_error is True
    
    with pytest.raises(ValueError, match="Fatal system error"):
        response.raise_errors()


def test_agent_response_tool_errors():
    """
    Test recording of non-fatal tool errors.
    """
    response = AgentResponse()
    t_error = RuntimeError("Tool failed")
    
    response.append_tool_error(t_error)
    assert response.has_tool_error is True
    assert len(response.get_tool_errors()) == 1
    
    # Tool errors should NOT be raised by raise_errors()
    response.raise_errors()  # Should not raise anything


# No __all__ export needed for test files as they are not meant to be imported as modules.