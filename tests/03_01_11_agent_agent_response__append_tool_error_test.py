# -*- coding: utf-8 -*-
# file tests/03_01_11_agent_agent_response__append_tool_error_test.py
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
Method: _append_tool_error

Internal logic tests for recording tool errors. Verifies that non-fatal 
exceptions are correctly categorized and logged without affecting process errors.
"""

import pytest
import logging
from org.slashlib.py.agent.agent_response import AgentResponse


def test_internal_append_tool_error_adds_to_list():
    """
    What: Verify that _append_tool_error populates the internal _tool_errors list.
    """
    response = AgentResponse()
    error = RuntimeError("Tool calculation error")
    
    response._append_tool_error(error)
    
    # Check internal state directly
    assert len(response._tool_errors) == 1
    assert response._tool_errors[0] is error


def test_internal_append_tool_error_type_check():
    """
    What: Verify that the method ignores non-Exception inputs.
    Why: The implementation uses 'if isinstance(error, Exception):'.
    """
    response = AgentResponse()
    
    # Attempt to append invalid types
    response._append_tool_error("Not an exception") # type: ignore
    response._append_tool_error(None) # type: ignore
    
    assert len(response._tool_errors) == 0


def test_internal_append_tool_error_logging(caplog):
    """
    What: Verify that the internal method logs the tool error at DEBUG level.
    """
    response = AgentResponse()
    error = ValueError("Tool arg mismatch")
    
    with caplog.at_level(logging.DEBUG):
        response._append_tool_error(error)
        
    assert "Tool error recorded in AgentResponse: Tool arg mismatch" in caplog.text


def test_internal_append_tool_error_isolation():
    """
    What: Verify that tool errors do not contaminate process errors.
    Why: AgentResponse distinguishes between fatal (process) and non-fatal (tool) errors.
    """
    response = AgentResponse()
    
    response._append_tool_error(Exception("Minor Tool Issue"))
    
    # Verify isolation
    assert len(response._tool_errors) == 1
    assert response.has_tool_error is True
    assert len(response._errors) == 0
    assert response.has_error is False


# end of file tests/03_01_11_agent_agent_response__append_tool_error_test.py