# -*- coding: utf-8 -*-
# file tests/03_01_17_agent_agent_response_has_tool_error_test.py
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
# - MAINTENANCE:
#    - Only update pydoc strings (args, returns, raises) if the function signature changes.
#    - Do NOT delete existing examples or descriptions in pydoc.
# - LANGUAGE: en-US for all comments and documentation.
#

"""
Module: org.slashlib.py.agent.agent_response
Class: AgentResponse
Property: has_tool_error

Tests the boolean indicator for tool-specific errors. Ensures that it 
correctly reflects the state of the internal tool error list.
"""

import pytest
from org.slashlib.py.agent.agent_response import AgentResponse


def test_has_tool_error_initial_state():
    """
    What: Verify that has_tool_error is False for a fresh instance.
    """
    response = AgentResponse()
    # Initial state should be tool-error-free
    assert response.has_tool_error is False


def test_has_tool_error_after_append_tool_error():
    """
    What: Verify that has_tool_error becomes True after a tool error is added.
    """
    response = AgentResponse()
    response.append_tool_error(RuntimeError("Tool failed"))
    
    # property should return True if list contains tool errors
    assert response.has_tool_error is True


def test_has_tool_error_ignores_process_errors():
    """
    What: Verify that has_tool_error stays False if only process errors are present.
    Why: AgentResponse distinguishes between process errors and tool errors.
    """
    response = AgentResponse()
    response.append_error(ValueError("Fatal process error"))
    
    # Process errors are fatal to the run, so has_tool_error remains False
    assert response.has_tool_error is False
    assert response.has_error is True


def test_has_tool_error_multiple_errors():
    """
    What: Verify that has_tool_error handles multiple tool errors correctly.
    """
    response = AgentResponse()
    response.append_tool_error(Exception("First tool issue"))
    response.append_tool_error(Exception("Second tool issue"))
    
    assert response.has_tool_error is True


def test_has_tool_error_is_read_only():
    """
    What: Verify that the property cannot be set manually.
    """
    response = AgentResponse()
    with pytest.raises(AttributeError):
        response.has_tool_error = True # type: ignore


# end of file tests/03_01_17_agent_agent_response_has_tool_error_test.py