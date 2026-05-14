# -*- coding: utf-8 -*-
# file tests/03_01_02_agent_response_validation_test.py
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
from org.slashlib.py.agent.agent_response import AgentResponse


def test_append_context_missing_role_or_content(caplog):
    """
    Targets the branch: if (not role) or (content is None):
    Verifies that a warning is logged and nothing is appended.
    """
    response = AgentResponse()
    
    # Missing role
    response.append_context(content="Some content")
    assert response.context_size == 0
    assert "role' or 'content' missing" in caplog.text

    # Content is None
    response.append_context(role="user", content=None)
    assert response.context_size == 0


def test_append_context_unsupported_type():
    """
    Targets the branch: elif not isinstance(content, str):
    Verifies that a TypeError is raised for unsupported types like int or float.
    """
    response = AgentResponse()
    
    with pytest.raises(TypeError, match="Unsupported content type"):
        response.append_context(role="user", content=123.45)


def test_append_context_serialization_error(monkeypatch):
    """
    Targets the branch: except (TypeError, ValueError) as e:
    Forces a serialization error by passing a non-serializable object 
    inside a dictionary.
    """
    response = AgentResponse()
    
    # A class instance is usually not JSON serializable by default
    class NonSerializable:
        pass

    bad_content = {"data": NonSerializable()}

    with pytest.raises(TypeError):
        response.append_context(role="system", content=bad_content)


def test_get_context_with_index():
    """
    Targets the branch: if index is not None: in get_context.
    Verifies that we can retrieve a specific node and that it's a deep copy.
    """
    response = AgentResponse()
    msg = {"role": "user", "content": "test"}
    response.append_context(**msg)
    
    # Test index access
    node = response.get_context(index=0)
    assert node["role"] == "user"
    
    # Verify deep copy (modifying the copy shouldn't affect the original)
    node["content"] = "changed"
    assert response.get_context(index=0)["content"] == "test"


def test_response_property_fallback():
    """
    Targets the final 'return None' in the response property if no assistant role exists.
    """
    response = AgentResponse()
    response.append_context(role="user", content="Hello")
    
    assert response.response is None

# end of file tests/03_01_02_agent_response_validation_test.py    