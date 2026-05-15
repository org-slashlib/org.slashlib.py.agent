# -*- coding: utf-8 -*-
# file tests/03_01_08_agent_agent_response_append_tool_error_test.py
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
Method: append_tool_error / _append_tool_error

Tests the recording of tool-specific (non-fatal) exceptions and the behavior 
of the has_tool_error property.
"""

import pytest
import logging
from org.slashlib.py.agent.agent_response import AgentResponse


def test_append_tool_error_success():
    """
    What: Verify that a tool exception is correctly added to the tool error list.
    """
    response = AgentResponse()
    error = RuntimeError("Tool execution failed")
    
    response.append_tool_error(error)
    
    assert response.has_tool_error is True
    assert len(response._tool_errors) == 1
    assert response._tool_errors[0] == error


def test_append_tool_error_multiple():
    """
    What: Verify that multiple tool errors can be recorded.
    """
    response = AgentResponse()
    errors = [ValueError("Invalid tool arg"), ZeroDivisionError("Math tool error")]
    
    for err in errors:
        response.append_tool_error(err)
    
    assert len(response._tool_errors) == 2
    assert response.get_tool_errors() == errors


def test_append_tool_error_invalid_type():
    """
    What: Verify that only instances of Exception are recorded.
    """
    response = AgentResponse()
    
    # Passing a string instead of an Exception object
    response.append_tool_error("Not an exception") # type: ignore
    
    assert response.has_tool_error is False
    assert len(response._tool_errors) == 0


def test_append_tool_error_logging(caplog):
    """
    What: Verify that recorded tool errors trigger a debug log entry.
    """
    response = AgentResponse()
    error = RuntimeError("Tool debug log test")
    
    with caplog.at_level(logging.DEBUG):
        response.append_tool_error(error)
        
    assert "Tool error recorded in AgentResponse" in caplog.text
    assert "Tool debug log test" in caplog.text


def test_has_tool_error_state_transition():
    """
    What: Verify the has_tool_error property transitions correctly.
    """
    response = AgentResponse()
    assert response.has_tool_error is False
    
    response.append_tool_error(Exception("Tool issue"))
    assert response.has_tool_error is True


def test_get_tool_errors():
    """
    What: Verify the public getter for tool errors.
    """
    response = AgentResponse()
    error = Exception("Fetch test")
    response.append_tool_error(error)
    
    result = response.get_tool_errors()
    assert isinstance(result, list)
    assert result[0] == error


# end of file tests/03_01_08_agent_agent_response_append_tool_error_test.py