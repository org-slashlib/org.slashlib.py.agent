# -*- coding: utf-8 -*-
# file tests/03_01_18_agent_agent_response_raise_errors_test.py
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
Method: raise_errors

Tests the error escalation logic. Verifies that only process errors trigger 
an exception, and that multiple errors are handled with appropriate logging.
"""

import pytest
import logging
from org.slashlib.py.agent.agent_response import AgentResponse


def test_raise_errors_no_errors_noop():
    """
    What: Verify that raise_errors() does nothing when no errors exist.
    """
    response = AgentResponse()
    # Should not raise anything
    response.raise_errors()


def test_raise_errors_single_process_error():
    """
    What: Verify that the stored process error is raised.
    """
    response = AgentResponse()
    error = RuntimeError("Specific process failure")
    response.append_error(error)
    
    with pytest.raises(RuntimeError) as exc_info:
        response.raise_errors()
    
    assert str(exc_info.value) == "Specific process failure"
    assert exc_info.value is error


def test_raise_errors_multiple_process_errors_logs_warning(caplog):
    """
    What: Verify that the first error is raised and a warning is logged if multiple exist.
    Why: Targets coverage for lines 135-136.
    """
    response = AgentResponse()
    err1 = ValueError("First Error")
    err2 = TypeError("Second Error")
    
    response.append_error(err1)
    response.append_error(err2)
    
    with caplog.at_level(logging.WARNING):
        with pytest.raises(ValueError) as exc_info:
            response.raise_errors()
        
        assert exc_info.value is err1
        assert "Multiple process errors (2) found" in caplog.text


def test_raise_errors_ignores_tool_errors():
    """
    What: Verify that tool errors do not trigger raise_errors().
    Why: Tool errors are designed to be non-fatal.
    """
    response = AgentResponse()
    response.append_tool_error(ArithmeticError("Tool math error"))
    
    # Despite having a tool error, this should be a no-op
    assert response.has_tool_error is True
    assert response.has_error is False
    response.raise_errors()


def test_raise_errors_mixed_errors():
    """
    What: Verify escalation logic when both process and tool errors are present.
    """
    response = AgentResponse()
    proc_error = RuntimeError("Fatal")
    tool_error = ValueError("Non-fatal")
    
    response.append_tool_error(tool_error)
    response.append_error(proc_error)
    
    # Should still raise the process error
    with pytest.raises(RuntimeError) as exc_info:
        response.raise_errors()
    
    assert exc_info.value is proc_error


# end of file tests/03_01_18_agent_agent_response_raise_errors_test.py