# -*- coding: utf-8 -*-
# file tests/03_01_07_agent_agent_response_append_error_test.py
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
Method: append_error / _append_error

Tests the recording of process-level (fatal) exceptions and the behavior 
of the has_error property.
"""

import pytest
import logging
from org.slashlib.py.agent.agent_response import AgentResponse


def test_append_error_success():
    """
    What: Verify that an exception is correctly added to the error list.
    """
    response = AgentResponse()
    error = ValueError("Fatal connection error")
    
    response.append_error(error)
    
    assert response.has_error is True
    assert len(response._errors) == 1
    assert response._errors[0] == error


def test_append_error_multiple():
    """
    What: Verify that multiple errors can be recorded.
    """
    response = AgentResponse()
    errors = [RuntimeError("Error 1"), TypeError("Error 2")]
    
    for err in errors:
        response.append_error(err)
    
    assert len(response._errors) == 2
    assert response._errors == errors


def test_append_error_invalid_type():
    """
    What: Verify that only instances of Exception are recorded.
    Why: The implementation checks isinstance(error, Exception).
    """
    response = AgentResponse()
    
    # Passing a string instead of an Exception object
    response.append_error("Not an exception object") # type: ignore
    
    assert response.has_error is False
    assert len(response._errors) == 0


def test_append_error_logging(caplog):
    """
    What: Verify that recorded errors trigger a debug log entry.
    """
    response = AgentResponse()
    error = RuntimeError("Log test error")
    
    with caplog.at_level(logging.DEBUG):
        response.append_error(error)
        
    assert "Process error recorded in AgentResponse" in caplog.text
    assert "Log test error" in caplog.text


def test_has_error_state_transition():
    """
    What: Verify the has_error property transitions correctly.
    """
    response = AgentResponse()
    assert response.has_error is False
    
    response.append_error(Exception("Test"))
    assert response.has_error is True


# end of file tests/03_01_07_agent_agent_response_append_error_test.py