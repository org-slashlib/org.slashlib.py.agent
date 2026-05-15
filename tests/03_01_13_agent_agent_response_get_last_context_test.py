# -*- coding: utf-8 -*-
# file tests/03_01_13_agent_agent_response_get_last_context_test.py
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
Method: get_last_context

Tests the retrieval of the most recent context entry. Verifies that it 
correctly delegates to get_context(index=-1) and returns a deep copy.
"""

import pytest
from org.slashlib.py.agent.agent_response import AgentResponse


def test_get_last_context_success():
    """
    What: Verify retrieval of the last message in a multi-message context.
    """
    response = AgentResponse()
    response.append_context(role="user", content="First message")
    response.append_context(role="assistant", content="Last message")
    
    last = response.get_last_context()
    
    assert isinstance(last, dict)
    assert last["role"] == "assistant"
    assert last["content"] == "Last message"


def test_get_last_context_single_entry():
    """
    What: Verify retrieval when only one message exists.
    """
    response = AgentResponse()
    response.append_context(role="system", content="System prompt")
    
    last = response.get_last_context()
    assert last["content"] == "System prompt"


def test_get_last_context_deep_copy():
    """
    What: Verify that the last context entry is a deep copy.
    Why: Modifications to the returned object must not affect the internal history.
    """
    response = AgentResponse()
    response.append_context(role="user", content="Original")
    
    last = response.get_last_context()
    last["content"] = "Modified"
    
    # Internal state must remain "Original"
    assert response.get_last_context()["content"] == "Original"


def test_get_last_context_empty_raises_index_error():
    """
    What: Verify behavior when the context is empty.
    Why: Since it calls get_context(index=-1), it should raise an IndexError.
    """
    response = AgentResponse()
    
    with pytest.raises(IndexError):
        response.get_last_context()


# end of file tests/03_01_13_agent_agent_response_get_last_context_test.py