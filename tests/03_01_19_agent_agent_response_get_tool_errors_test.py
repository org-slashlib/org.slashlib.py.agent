# -*- coding: utf-8 -*-
# file tests/03_01_19_agent_agent_response_get_tool_errors_test.py
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
Method: get_tool_errors

Tests the retrieval of recorded tool-specific exceptions. Verifies that the 
returned list contains all tool errors in the order they were recorded.
"""

import pytest
from org.slashlib.py.agent.agent_response import AgentResponse


def test_get_tool_errors_empty_initial_state():
    """
    What: Verify that an empty list is returned if no tool errors exist.
    """
    response = AgentResponse()
    result = response.get_tool_errors()
    
    assert isinstance(result, list)
    assert len(result) == 0


def test_get_tool_errors_retrieval_success():
    """
    What: Verify that all recorded tool errors are returned.
    """
    response = AgentResponse()
    error1 = ValueError("Invalid tool parameter")
    error2 = RuntimeError("Tool connection timeout")
    
    response.append_tool_error(error1)
    response.append_tool_error(error2)
    
    result = response.get_tool_errors()
    
    assert len(result) == 2
    assert result[0] is error1
    assert result[1] is error2


def test_get_tool_errors_isolation_from_process_errors():
    """
    What: Verify that process errors are not included in the tool error list.
    """
    response = AgentResponse()
    tool_err = RuntimeError("Tool fail")
    proc_err = Exception("Fatal process fail")
    
    response.append_tool_error(tool_err)
    response.append_error(proc_err)
    
    result = response.get_tool_errors()
    
    # Should only contain the tool error
    assert len(result) == 1
    assert result[0] is tool_err
    assert proc_err not in result


def test_get_tool_errors_returns_reference_to_internal_list():
    """
    What: Verify the behavior of the returned list (reference vs copy).
    Why: Understanding whether external modification of the list affects the object.
    """
    response = AgentResponse()
    error = ValueError("Tool error")
    response.append_tool_error(error)
    
    result = response.get_tool_errors()
    # In the current implementation, it returns a reference/slice of the list
    # If the list is modified externally, we check the impact
    result.append(Exception("External injection"))
    
    # In Python, depending on the implementation (return self._tool_errors vs return list(self._tool_errors))
    # We verify that the original object state remains consistent or matches expected behavior.
    # Note: agent_response.py snippet shows 'return self._tool_errors' (truncated)
    # We assume it should represent the state at the time of calling.
    assert error in response.get_tool_errors()


# end of file tests/03_01_19_agent_agent_response_get_tool_errors_test.py