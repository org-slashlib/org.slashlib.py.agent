# -*- coding: utf-8 -*-
# file src/org/slashlib/py/agent/agent_response.py
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
import copy
import json
import logging
import pathlib
import typing


class AgentResponse:
    """
    Represents the result of an Agent execution, including history and errors.
    
    Separates process errors (fatal to the run) from tool errors (non-fatal execution errors).
    """

    def __init__(self):
        """
        Initialize a new AgentResponse instance.
        """
        self.log = logging.getLogger(f"org.slashlib.py.agent.{pathlib.Path(__file__).stem}.{self.__class__.__name__}")
        self._context: typing.List[typing.Dict[str, typing.Any]] = []
        self._errors: typing.List[Exception] = []
        self._tool_errors: typing.List[Exception] = []

    def append_context(self, **kwargs):
        """
        Public interface to add a message to the context.

        Args:
            **kwargs: Arbitrary keyword arguments (e.g., role, content).
        """
        self._append_context(**kwargs)

    def append_error(self, error: Exception):
        """
        Public interface to record a process error.

        Args:
            error (Exception): The exception instance to record.
        """
        self._append_error(error)

    def append_tool_error(self, error: Exception):
        """
        Public interface to record a tool error.

        Args:
            error (Exception): The exception instance to record.
        """
        self._append_tool_error(error)

    def _append_context(self, **kwargs):
        """
        Internal method to append a message to the context.

        Args:
            **kwargs: Arbitrary keyword arguments. Expected to contain 'role' (str)
                and 'content' (str, dict, or list).

        Raises:
            TypeError: If 'content' is not a string, dict, or list.
            ValueError: If 'content' cannot be serialized to JSON.
        """
        role = kwargs.get("role")
        content = kwargs.get("content")

        if (not role) or (content is None):
            self.log.warning(f"Skipped context update: 'role' or 'content' missing in {kwargs}")
            return

        # Ensure content is a string (convert if it's a JSON-like structure)
        if isinstance(content, (dict, list)):
            try:
                kwargs["content"] = json.dumps(content, ensure_ascii=False)
            except (TypeError, ValueError) as e:
                self.log.error(f"Failed to serialize context content to JSON: {e}")
                raise
        elif not isinstance(content, str):
            msg = f"Unsupported content type: {type(content)}. Expected str, dict or list."
            self.log.error(msg)
            raise TypeError(msg)

        self._context.append(kwargs)

    def _append_error(self, error: Exception):
        """
        Appends a process exception (fatal) to the error list.

        Args:
            error (Exception): The exception instance to record.
        """
        if isinstance(error, Exception):
            self._errors.append(error)
            self.log.debug(f"Process error recorded in AgentResponse: {error}")

    def _append_tool_error(self, error: Exception):
        """
        Appends a tool-specific exception (non-fatal) to the tool error list.

        Args:
            error (Exception): The exception instance to record.
        """
        if isinstance(error, Exception):
            self._tool_errors.append(error)
            self.log.debug(f"Tool error recorded in AgentResponse: {error}")

    def get_context(self, index: typing.Optional[int] = None) -> typing.Union[typing.List[dict], dict]:
        """
        Returns a deep copy of the context.

        Args:
            index (Optional[int]): If provided, returns only the node at this index.
                Otherwise, returns the entire list. Defaults to None.

        Returns:
            Union[List[dict], dict]: A deep copy of the entire context list or a single 
                context dictionary if an index was provided.
        """
        if index is not None:
            return copy.deepcopy(self._context[index])
        return copy.deepcopy(self._context)

    @property
    def response(self) -> typing.Optional[str]:
        """
        Returns the content of the last assistant message in the context.
        
        Returns:
            Optional[str]: The final response string from the assistant, 
                or None if no assistant message exists in the history.
        """
        for msg in reversed(self._context):
            if msg.get("role") == "assistant":
                return msg.get("content")
        return None

    @property
    def context_size(self) -> int:
        """
        Returns the number of messages in the context.

        Returns:
            int: The total count of context entries.
        """
        return len(self._context)

    @property
    def has_error(self) -> bool:
        """
        Checks if any process errors occurred during execution.

        Returns:
            bool: True if one or more process errors were recorded.
        """
        return len(self._errors) > 0

    @property
    def has_tool_error(self) -> bool:
        """
        Checks if any tool-specific errors occurred during execution.

        Returns:
            bool: True if one or more tool errors were recorded.
        """
        return len(self._tool_errors) > 0

    def raise_errors(self):
        """
        Raises the first process error if any exist. 
        Tool errors are ignored by this method as they are non-fatal.

        Raises:
            Exception: The first process exception stored in the error list.
        """
        if self.has_error:
            if len(self._errors) > 1:
                self.log.warning(f"Multiple process errors ({len(self._errors)}) found. Raising the first one.")
            raise self._errors[0]

    def get_tool_errors(self) -> typing.List[Exception]:
        """
        Returns all recorded tool errors.

        Returns:
            List[Exception]: A list of exceptions that occurred during tool execution.
        """
        return self._tool_errors


__all__ = ["AgentResponse"]

# end of file src/org/slashlib/py/agent/agent_response.py