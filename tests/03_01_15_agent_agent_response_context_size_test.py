# -*- coding: utf-8 -*-
# file tests/03_01_15_agent_agent_response_context_size_test.py
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
Property: context_size

Tests the integrity of the context_size property, ensuring it reflects 
the correct number of messages stored in the internal history.
"""

import pytest
from org.slashlib.py.agent.agent_response import AgentResponse


def test_context_size_initial_state():
    """
    What: Verify that context_size is 0 for a new instance.
    """
    response = AgentResponse()
    assert response.context_size == 0


def test_context_size_after_appends():
    """
    What: Verify that context_size increments correctly with each added message.
    """
    response = AgentResponse()
    
    response.append_context(role="system", content="A")
    assert response.context_size == 1
    
    response.append_context(role="user", content="B")
    assert response.context_size == 2
    
    response.append_context(role="assistant", content="C")
    assert response.context_size == 3


def test_context_size_ignores_failed_appends():
    """
    What: Verify that context_size does not increment if append_context skips an entry.
    Why: Missing role or content results in a skipped update.
    """
    response = AgentResponse()
    
    # Valid append
    response.append_context(role="user", content="Valid")
    
    # Invalid append (missing content)
    response.append_context(role="system")
    
    assert response.context_size == 1


def test_context_size_is_read_only():
    """
    What: Verify that context_size cannot be manually overwritten.
    """
    response = AgentResponse()
    with pytest.raises(AttributeError):
        response.context_size = 10 # type: ignore


# end of file tests/03_01_15_agent_agent_response_context_size_test.py