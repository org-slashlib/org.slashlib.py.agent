# -*- coding: utf-8 -*-
# file tests/04_01_01_inference_bases_test.py
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
from org.slashlib.py.agent.inference_bases import (
    InferenceError,
    InferenceConnectionError,
    InferenceConfigError,
    InferencePayloadError,
    InferenceResult,
    InferenceAdapter
)


def test_inference_exceptions_hierarchy():
    """
    Verify that all specific inference exceptions inherit from InferenceError.
    """
    assert issubclass(InferenceConnectionError, InferenceError)
    assert issubclass(InferenceConfigError, InferenceError)
    assert issubclass(InferencePayloadError, InferenceError)
    assert issubclass(InferenceError, Exception)


def test_inference_result_is_abstract():
    """
    Ensure InferenceResult cannot be instantiated directly due to abstract methods.
    """
    with pytest.raises(TypeError) as excinfo:
        InferenceResult()
    assert "Can't instantiate abstract class InferenceResult" in str(excinfo.value)


def test_inference_adapter_is_abstract():
    """
    Ensure InferenceAdapter cannot be instantiated directly.
    """
    with pytest.raises(TypeError) as excinfo:
        InferenceAdapter()
    assert "Can't instantiate abstract class InferenceAdapter" in str(excinfo.value)


def test_concrete_inference_result_implementation():
    """
    Test a minimal valid implementation of InferenceResult to ensure 
    the interface works as expected.
    """
    class MockResult(InferenceResult):
        @property
        def role(self) -> str:
            return "assistant"
        
        @property
        def content(self) -> str:
            return "test content"
            
        @property
        def tool_calls(self):
            return None
            
        def to_dict(self):
            return {"role": self.role, "content": self.content}

    result = MockResult()
    assert result.role == "assistant"
    assert result.to_dict()["content"] == "test content"


@pytest.mark.asyncio
async def test_concrete_inference_adapter_implementation():
    """
    Test a minimal valid implementation of InferenceAdapter.
    """
    class MockAdapter(InferenceAdapter):
        async def chat(self, model=None, messages=None, tools=None, **kwargs):
            return "success"

    adapter = MockAdapter()
    result = await adapter.chat()
    assert result == "success"


# No __all__ export needed for test files as they are not meant to be imported as modules.