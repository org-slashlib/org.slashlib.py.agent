# -*- coding: utf-8 -*-
# file src/org/slashlib/py/agent/inference_bases.py
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

# Python imports
import abc
import typing


class InferenceError(Exception):
    """Base exception for all inference related errors."""
    pass


class InferenceConnectionError(InferenceError):
    """Raised when the connection to the AI provider fails."""
    pass


class InferenceConfigError(InferenceError):
    """Raised when the model configuration (e.g. model name) is invalid."""
    pass


class InferencePayloadError(InferenceError):
    """Raised when the response payload is malformed or invalid."""
    pass


class InferenceResult(abc.ABC):
    """
    Abstract interface for the result of an inference execution.
    Standardizes how the Agent accesses model responses and tool calls.
    """

    @property
    @abc.abstractmethod
    def role(self) -> str:
        """Returns the role of the message (e.g., 'assistant')."""
        pass

    @property
    @abc.abstractmethod
    def content(self) -> typing.Optional[str]:
        """Returns the text content of the response."""
        pass

    @property
    @abc.abstractmethod
    def tool_calls(self) -> typing.Optional[typing.List[typing.Dict[str, typing.Any]]]:
        """
        Returns tool calls in a standardized format:
        [{"function": {"name": str, "arguments": dict}}]
        """
        pass

    @abc.abstractmethod
    def to_dict(self) -> typing.Dict[str, typing.Any]:
        """
        Converts the result into a dictionary compatible with the 
        internal storage format of AgentResponse.
        """
        pass


class InferenceAdapter(abc.ABC):
    """
    Abstract interface for an Inference Adapter.
    Encapsulates the communication with a specific AI model provider.
    """

    @abc.abstractmethod
    async def chat(
        self, 
        model: typing.Optional[str] = None, 
        messages: typing.List[typing.Dict[str, typing.Any]] = None, 
        tools: typing.Optional[typing.List[typing.Dict[str, typing.Any]]] = None,
        **kwargs
    ) -> InferenceResult:
        """
        Executes a chat request and returns a standardized InferenceResult.

        Args:
            model (str): The name/identifier of the model to use.
            messages (list): The full conversation context.
            tools (list, optional): Available tool schemas.
            **kwargs: Provider-specific options (timeout, think, temperature, etc.)

        Returns:
            InferenceResult: The validated and standardized result.

        Raises:
            InferenceConnectionError: If the provider is unreachable.
            InferencePayloadError: If the response is malformed.
            InferenceConfigError: If configuration/model is wrong.
        """
        pass


__all__ = [
    "InferenceResult", 
    "InferenceAdapter", 
    "InferenceError", 
    "InferenceConnectionError", 
    "InferenceConfigError", 
    "InferencePayloadError"
]

# end of file src/org/slashlib/py/agent/inference_bases.py