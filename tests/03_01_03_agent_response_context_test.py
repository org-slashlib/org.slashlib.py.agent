# -*- coding: utf-8 -*-
# file tests/03_01_03_agent_response_context_test.py
# @AI:
# - INTEGRITY RULES:
#   - STRICT PRESERVATION: Do not remove, move, or modify ANY existing lines of code or comments 
#     unless they are the explicit target of the requested change. 
#   - DEBUG MARKERS: Commented-out code (e.g., debug prints) MUST be kept exactly where they are.
#   - WHITESPACE & STRUCTURE: Maintain all original empty lines and the existing file structure. 
#     Structural integrity takes precedence over "clean code" or "elegance".
#   - LEAD-IN/OUT: The very first and last lines (and all comments in between) are immutable anchors.
# - MAINTENANCE:
#   - Only update pydoc strings (args, returns, raises) if the function signature changes.
#   - Do NOT delete existing examples or descriptions in pydoc.
# - LANGUAGE: en-US for all comments and documentation.
#

# Python imports
import typing

# Third party imports
import pytest

# Internal imports
from src.org.slashlib.py.agent.agent_response import AgentResponse


def test_get_context_full_list():
    """
    Targets the branch: return copy.deepcopy(self._context)
    Verifies that calling get_context without an index returns the entire list.
    """
    response = AgentResponse()
    response.append_context(role="user", content="First")
    response.append_context(role="assistant", content="Second")
    
    # Aufruf OHNE index Parameter
    full_context = response.get_context()
    
    assert isinstance(full_context, list)
    assert len(full_context) == 2
    assert full_context[0]["content"] == "First"
    assert full_context[1]["content"] == "Second"


def test_get_context_deep_copy_integrity():
    """
    Ensures that the full list returned is indeed a deep copy.
    """
    response = AgentResponse()
    response.append_context(role="user", content="Original")
    
    full_context = response.get_context()
    # Modify the returned list
    full_context[0]["content"] = "Mutated"
    
    # The original context inside the object must remain unchanged
    assert response.get_context(index=0)["content"] == "Original"
    
# end of file tests/03_01_03_agent_response_context_test.py