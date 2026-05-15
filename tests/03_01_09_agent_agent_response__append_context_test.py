# -*- coding: utf-8 -*-
# file tests/03_01_09_agent_agent_response__append_context_test.py
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
Method: _append_context

Internal logic tests for context management, focusing on JSON serialization 
of complex types and strict type enforcement for the 'content' field.
"""

import pytest
import json
import logging
from org.slashlib.py.agent.agent_response import AgentResponse


def test_internal_append_context_serialization_error(caplog):
    """
    What: Verify handling of non-serializable objects in content.
    Why: Targets coverage for the try-except block during json.dumps.
    """
    response = AgentResponse()
    
    # Objects like sets are not JSON serializable by default
    bad_content = {"set_data": {1, 2, 3}}
    
    with caplog.at_level(logging.ERROR):
        with pytest.raises(TypeError):
            response._append_context(role="user", content=bad_content)
            
    assert "Failed to serialize context content to JSON" in caplog.text


def test_internal_append_context_unsupported_type_exception():
    """
    What: Verify TypeError for completely unsupported types (e.g., float).
    Why: Ensure the explicit type check for str, dict, list works.
    """
    response = AgentResponse()
    
    with pytest.raises(TypeError) as exc_info:
        response._append_context(role="assistant", content=42.0)
        
    assert "Unsupported content type" in str(exc_info.value)


def test_internal_append_context_preserves_raw_data():
    """
    What: Verify that correctly formatted data is stored in the internal list.
    """
    response = AgentResponse()
    payload = {"role": "user", "content": "test message", "metadata": "extra"}
    
    response._append_context(**payload)
    
    assert response._context[0] == payload


def test_internal_append_context_skips_on_missing_data(caplog):
    """
    What: Verify early return when role or content is missing.
    """
    response = AgentResponse()
    
    with caplog.at_level(logging.WARNING):
        # content is None case
        response._append_context(role="user", content=None)
        # role is empty case
        response._append_context(role="", content="text")
        
    assert len(response._context) == 0
    assert "Skipped context update" in caplog.text


def test_internal_append_context_json_ensure_ascii_false():
    """
    What: Verify that non-ASCII characters are preserved in JSON serialization.
    Why: Implementation uses ensure_ascii=False.
    """
    response = AgentResponse()
    content_with_umlaut = {"city": "München"}
    
    response._append_context(role="user", content=content_with_umlaut)
    
    stored_content = response._context[0]["content"]
    assert "ü" in stored_content
    assert stored_content == '{"city": "München"}'


# end of file tests/03_01_09_agent_agent_response__append_context_test.py