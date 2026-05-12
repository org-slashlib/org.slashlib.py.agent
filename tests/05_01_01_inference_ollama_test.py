# -*- coding: utf-8 -*-
# file tests/05_01_01_inference_ollama_test.py
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
from unittest.mock import AsyncMock, patch, MagicMock

# Third party imports
import pytest
import ollama

# Internal imports
from src.org.slashlib.py.agent.inference_complements_for_ollama import (
    OllamaInferenceResult, 
    OllamaInferenceAdapter
)
from src.org.slashlib.py.agent.inference_bases import (
    InferencePayloadError,
    InferenceConfigError,
    InferenceConnectionError,
    InferenceError
)


# --- Tests for OllamaInferenceResult ---

def test_ollama_result_valid_text():
    """Test valid text response parsing."""
    raw = {"role": "assistant", "content": "Hello world", "tool_calls": None}
    result = OllamaInferenceResult(raw)
    assert result.role == "assistant"
    assert result.content == "Hello world"
    assert result.to_dict()["content"] == "Hello world"


def test_ollama_result_valid_tool():
    """Test valid tool call response (content may be None)."""
    raw = {"role": "assistant", "content": None, "tool_calls": [{"function": {"name": "test"}}]}
    result = OllamaInferenceResult(raw)
    assert result.tool_calls[0]["function"]["name"] == "test"


def test_ollama_result_invalid_missing_role():
    """Trigger InferencePayloadError due to missing role."""
    with pytest.raises(InferencePayloadError, match="role' is missing"):
        OllamaInferenceResult({"content": "no role"})


def test_ollama_result_invalid_empty():
    """Trigger InferencePayloadError when both content and tools are missing."""
    with pytest.raises(InferencePayloadError, match="Both 'content' and 'tool_calls' are empty"):
        OllamaInferenceResult({"role": "assistant", "content": None, "tool_calls": []})


# --- Tests for OllamaInferenceAdapter ---

@pytest.mark.asyncio
@patch("org.slashlib.py.configloader.resolve")
@patch("ollama.AsyncClient")
async def test_ollama_adapter_chat_success(mock_client_class, mock_config):
    """
    Test successful chat call and parameter resolution.
    Targeting the priority chain: kwargs -> method arg -> config.
    """
    # Setup mocks
    mock_config.side_effect = lambda key: "config_val" if "model" in key else 30
    mock_instance = AsyncMock()
    mock_client_class.return_value = mock_instance
    mock_instance.chat.return_value = {
        "message": {"role": "assistant", "content": "AI response"}
    }

    adapter = OllamaInferenceAdapter()
    
    # 1. Test priority: Explicit 'model' arg should win over config
    result = await adapter.chat(model="explicit-model", messages=[{"role": "user", "content": "hi"}])
    
    assert result.content == "AI response"
    mock_instance.chat.assert_called_once()
    args, kwargs = mock_instance.chat.call_args
    assert kwargs["model"] == "explicit-model"


@pytest.mark.asyncio
@patch("org.slashlib.py.configloader.resolve")
@patch("ollama.AsyncClient")
async def test_ollama_adapter_error_mapping(mock_client_class, mock_config):
    """
    Test mapping of ollama exceptions to internal inference exceptions.
    """
    mock_instance = AsyncMock()
    mock_client_class.return_value = mock_instance
    adapter = OllamaInferenceAdapter()

    # Test ResponseError -> InferenceConfigError
    mock_instance.chat.side_effect = ollama.ResponseError("Model not found")
    with pytest.raises(InferenceConfigError):
        await adapter.chat(messages=[])

    # Test RequestError -> InferenceConnectionError
    mock_instance.chat.side_effect = ollama.RequestError("Conn failed")
    with pytest.raises(InferenceConnectionError):
        await adapter.chat(messages=[])

    # Test Generic Exception -> InferenceError
    mock_instance.chat.side_effect = RuntimeError("Boom")
    with pytest.raises(InferenceError, match="Internal adapter error"):
        await adapter.chat(messages=[])


@pytest.mark.asyncio
@patch("ollama.AsyncClient")
async def test_ollama_adapter_empty_message_payload(mock_client_class):
    """Targets the 'if not message' branch in chat."""
    mock_instance = AsyncMock()
    mock_client_class.return_value = mock_instance
    mock_instance.chat.return_value = {"something": "else"} # no 'message' key
    
    adapter = OllamaInferenceAdapter()
    with pytest.raises(InferencePayloadError, match="returned an empty response"):
        await adapter.chat(messages=[])


# end of file tests/05_01_01_inference_ollama_test.py