# -*- coding: utf-8 -*-
# file tests/03_01_05_agent_agent_response_init_test.py
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
Method: __init__

Verifies that the AgentResponse object is correctly initialized with empty 
containers for context, errors, and tool errors.
"""

import pytest
import logging
from org.slashlib.py.agent.agent_response import AgentResponse


def test_existence_and_type():
    """
    What: Verify the existence of the class and correct instantiation.
    """
    response = AgentResponse()
    assert isinstance(response, AgentResponse)


def test_init_state():
    """
    What: Verify that the internal state is correctly initialized as empty.
    Why: Ensure no data leakage between different response objects.
    """
    response = AgentResponse()
    
    # Internal list checks
    assert isinstance(response._context, list)
    assert len(response._context) == 0
    
    assert isinstance(response._errors, list)
    assert len(response._errors) == 0
    
    assert isinstance(response._tool_errors, list)
    assert len(response._tool_errors) == 0


def test_init_logger():
    """
    What: Verify that the logger is correctly set up.
    """
    response = AgentResponse()
    assert isinstance(response.log, logging.Logger)
    assert "AgentResponse" in response.log.name


def test_property_initial_values():
    """
    What: Verify that public properties return correct initial values.
    """
    response = AgentResponse()
    
    assert response.has_error is False
    assert response.has_tool_error is False
    assert response.context_size == 0
    assert response.response is None


# end of file tests/03_01_05_agent_agent_response_init_test.py