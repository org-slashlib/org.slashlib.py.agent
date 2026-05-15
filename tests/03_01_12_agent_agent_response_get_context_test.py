# -*- coding: utf-8 -*-
# file tests/03_01_12_agent_agent_response_get_context_test.py
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
Method: get_context

Tests the retrieval of the context history, ensuring that deep copies are 
returned to prevent external modification of the internal state.
"""

import pytest
from org.slashlib.py.agent.agent_response import AgentResponse


def test_get_context_all():
    """
    What: Verify retrieval of the entire context list.
    """
    response = AgentResponse()
    msgs = [
        {"role": "system", "content": "You are a helper"},
        {"role": "user", "content": "Hello"}
    ]
    for msg in msgs:
        response.append_context(**msg)
        
    result = response.get_context()
    
    assert isinstance(result, list)
    assert len(result) == 2
    assert result == msgs


def test_get_context_by_index():
    """
    What: Verify retrieval of a specific message by index.
    """
    response = AgentResponse()
    response.append_context(role="user", content="First")
    response.append_context(role="assistant", content="Second")
    
    # Positive index
    assert response.get_context(index=0)["content"] == "First"
    # Negative index
    assert response.get_context(index=-1)["content"] == "Second"


def test_get_context_deep_copy_integrity():
    """
    What: Verify that the returned object is a deep copy.
    Why: External modifications to the returned dict/list must not affect the internal state.
    """
    response = AgentResponse()
    original_msg = {"role": "user", "content": "Safe data"}
    response.append_context(**original_msg)
    
    # Get the context and modify it
    leaked_ref = response.get_context(index=0)
    assert isinstance(leaked_ref, dict)
    leaked_ref["content"] = "HACKED"
    
    # Internal state must remain unchanged
    assert response.get_context(index=0)["content"] == "Safe data"


def test_get_context_index_out_of_bounds():
    """
    What: Verify behavior when an invalid index is provided.
    """
    response = AgentResponse()
    
    with pytest.raises(IndexError):
        response.get_context(index=99)


def test_get_context_empty_init():
    """
    What: Verify that an empty list is returned if no context exists.
    """
    response = AgentResponse()
    assert response.get_context() == []


# end of file tests/03_01_12_agent_agent_response_get_context_test.py