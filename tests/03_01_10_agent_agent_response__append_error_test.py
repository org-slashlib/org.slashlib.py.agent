# -*- coding: utf-8 -*-
# file tests/03_01_10_agent_agent_response__append_error_test.py
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
Method: _append_error

Internal logic tests for recording process errors. Verifies strict type 
checking for Exception instances and debug logging behavior.
"""

import pytest
import logging
from org.slashlib.py.agent.agent_response import AgentResponse


def test_internal_append_error_adds_to_list():
    """
    What: Verify that _append_error populates the internal _errors list.
    """
    response = AgentResponse()
    error = RuntimeError("Internal process failure")
    
    response._append_error(error)
    
    # Check internal state directly
    assert len(response._errors) == 1
    assert response._errors[0] is error


def test_internal_append_error_type_check():
    """
    What: Verify that the method ignores non-Exception inputs.
    Why: The implementation uses 'if isinstance(error, Exception):'.
    """
    response = AgentResponse()
    
    # Attempt to append something that is not an Exception
    response._append_error("Not an exception") # type: ignore
    response._append_error(None) # type: ignore
    response._append_error(404) # type: ignore
    
    assert len(response._errors) == 0


def test_internal_append_error_logging(caplog):
    """
    What: Verify that the internal method logs the error at DEBUG level.
    """
    response = AgentResponse()
    error = ValueError("Log verification error")
    
    with caplog.at_level(logging.DEBUG):
        response._append_error(error)
        
    assert "Process error recorded in AgentResponse: Log verification error" in caplog.text


def test_internal_append_error_integrity():
    """
    What: Verify that appending an error doesn't affect other fields.
    """
    response = AgentResponse()
    
    response._append_error(Exception("Test Error"))
    
    # Process errors should not leak into tool errors
    assert len(response._errors) == 1
    assert len(response._tool_errors) == 0
    assert response._context == []


# end of file tests/03_01_10_agent_agent_response__append_error_test.py