# -*- coding: utf-8 -*-
# file tests/03_01_06_agent_agent_response_append_context_test.py
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
Method: append_context / _append_context

Tests the addition of messages to the context, including JSON serialization 
of structured content and type validation.
"""

import pytest
import json
import logging
from org.slashlib.py.agent.agent_response import AgentResponse


def test_append_context_success():
    """
    What: Verify basic string content addition.
    """
    response = AgentResponse()
    response.append_context(role="user", content="Hello Agent")
    
    assert response.context_size == 1
    ctx = response.get_context(index=0)
    assert ctx["role"] == "user"
    assert ctx["content"] == "Hello Agent"


def test_append_context_json_serialization_dict():
    """
    What: Verify that a dictionary content is serialized to a JSON string.
    Why: LLM interactions often require stringified JSON for tool arguments or structured data.
    """
    response = AgentResponse()
    data = {"key": "value", "nested": [1, 2, 3]}
    response.append_context(role="assistant", content=data)
    
    ctx = response.get_context(index=0)
    assert isinstance(ctx["content"], str)
    assert json.loads(ctx["content"]) == data


def test_append_context_json_serialization_list():
    """
    What: Verify that a list content is serialized to a JSON string.
    """
    response = AgentResponse()
    data = ["item1", "item2"]
    response.append_context(role="tool", content=data)
    
    ctx = response.get_context(index=0)
    assert ctx["content"] == json.dumps(data, ensure_ascii=False)


def test_append_context_missing_role_or_content(caplog):
    """
    What: Verify that missing mandatory keys results in a skip and a warning.
    """
    response = AgentResponse()
    
    with caplog.at_level(logging.WARNING):
        # Missing content
        response.append_context(role="user")
        # Missing role
        response.append_context(content="test")
        
    assert response.context_size == 0
    assert "Skipped context update" in caplog.text


def test_append_context_unsupported_type():
    """
    What: Verify that unsupported types (like int) raise a TypeError.
    """
    response = AgentResponse()
    
    with pytest.raises(TypeError) as exc_info:
        response.append_context(role="user", content=123)
    
    assert "Unsupported content type" in str(exc_info.value)


def test_append_context_extra_kwargs():
    """
    What: Verify that additional metadata (like tool_call_id) is preserved.
    """
    response = AgentResponse()
    response.append_context(role="tool", content="Result", tool_call_id="call_123", name="my_tool")
    
    ctx = response.get_context(index=0)
    assert ctx["tool_call_id"] == "call_123"
    assert ctx["name"] == "my_tool"


# end of file tests/03_01_06_agent_agent_response_append_context_test.py