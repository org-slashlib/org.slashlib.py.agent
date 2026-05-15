# -*- coding: utf-8 -*-
# file src/org/slashlib/py/agent/tool.py
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
import functools
import inspect
import typing
import json
import logging
import datetime
import uuid
import pathlib
from decimal import Decimal

# Third party imports


class Tool:
    """
    A wrapper class that transforms a Python function into a schema-aware tool.
    
    This class is designed to be used by AI agents (like Gemma 4) to understand 
    the capabilities, parameters, and requirements of a specific function.
    """

    def __init__(self, func, name=None, description=None):
        """
        Initialize the Tool instance.

        Args:
            func (Callable): The function to be wrapped as a tool.
            name (Optional[str]): Override for the function's name. Defaults to func.__name__.
            description (Optional[str]): Override for the function's description. 
                Defaults to the function's docstring.
        """
        self._func = func
        self.name = name or func.__name__
        self.description = description or func.__doc__ or "No description provided."
        # Wir kopieren Metadaten der Originalfunktion (für Dokumentation etc.)
        functools.update_wrapper(self, func)

    def _map_type(self, annotation: typing.Any) -> str:
        """
        Maps Python type annotations to JSON schema compatible type strings.

        Args:
            annotation (Any): The Python type annotation to map.

        Returns:
            str: The corresponding JSON schema type (e.g., 'string', 'integer', 'array').
        """
        # Handle Optional[T] or Union[T, None]
        origin = typing.get_origin(annotation)
        if origin is typing.Union:
            args = typing.get_args(annotation)
            # Filter out NoneType to find the actual type
            actual_types = [a for a in args if a is not type(None)]
            if actual_types:
                return self._map_type(actual_types[0])

        mapping = {
            int: "integer",
            float: "number",
            str: "string",
            bool: "boolean",
            list: "array",
            dict: "object",
            typing.List: "array",
            typing.Dict: "object",
        }
        
        return mapping.get(annotation if origin is None else origin, "string")

    def get_schema(self) -> dict:
        """
        Generates a JSON schema based on the function's signature and annotations.
        
        The schema follows the strict 'type: function' structure expected by 
        modern LLMs for tool calling.

        Returns:
            dict: A dictionary representing the tool's schema in the format:
                  {'type': 'function', 'function': {...}}
        """
        sig = inspect.signature(self._func)
        parameters = {"type": "object", "properties": {}, "required": []}

        for param_name, param in sig.parameters.items():
            # Skip 'self' or 'cls' if decorated inside a class
            if param_name in ("self", "cls"):
                continue

            param_type = self._map_type(param.annotation)
            
            param_info = {
                "type": param_type,
                "description": f"Parameter {param_name}"
            }

            # If there's a default value, mention it and add the 'default' key
            if param.default is not inspect.Parameter.empty:
                param_info["default"] = param.default
                param_info["description"] += f" (defaults to {param.default})"
            else:
                # Parameters without defaults are mandatory
                parameters["required"].append(param_name)

            parameters["properties"][param_name] = param_info

        # Encapsulate in the required 'function' envelope
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description.strip() if self.description else "No description provided.",
                "parameters": parameters
            }
        }

    async def __call__(self, *args, **kwargs) -> str:
        """
        Execute the tool with the provided arguments.

        This method wraps the execution of the underlying function, ensures
        error handling, and guarantees that the return value is a string
        suitable for LLM context inclusion (e.g., via JSON serialization).

        Returns:
            str: The result of the tool execution as a string.
        """
        try:
            # Execute the wrapped function (handles both async and sync)
            if inspect.iscoroutinefunction(self._func):
                result = await self._func(*args, **kwargs)
            else:
                result = self._func(*args, **kwargs)

            # 1. Handle standalone None immediately (returns empty string)
            if result is None:
                return ""

            # 2. Handle simple primitives immediately to avoid unnecessary JSON quotes
            if isinstance(result, (str, int, float, bool)):
                return str(result)

            # 3. Handle standalone Path immediately (avoids JSON quotes and ensures forward slashes)
            if isinstance(result, pathlib.Path):
                return result.as_posix()

            import json

            class ToolEncoder(json.JSONEncoder):
                """
                A recursive encoder that handles all special types even when 
                nested deep inside dicts, lists, or sets.
                """
                def default(self, obj):
                    # Note: We let None pass here so json.dumps converts it to 'null' (standard JSON)
                    if isinstance(obj, set):
                        return list(obj)
                    if isinstance(obj, bytes):
                        return obj.decode("utf-8", errors="replace")
                    if isinstance(obj, (datetime.datetime, datetime.date, datetime.time)):
                        return obj.isoformat()
                    if isinstance(obj, pathlib.Path):
                        return obj.as_posix()
                    if isinstance(obj, (uuid.UUID, Decimal)):
                        return str(obj)
                    # For everything else, try standard conversion
                    try:
                        return super().default(obj)
                    except TypeError:
                        return str(obj)

            # 4. For everything else (containers and special types), use the Encoder.
            # Containers like {"a": 1} or [1, 2] will be serialized correctly here.
            res_json = json.dumps(result, ensure_ascii=False, cls=ToolEncoder)
            
            # If it's a JSON string literal (like "2026-05-15"), strip the quotes.
            # Complex structures (starting with { or [) skip this and reach the final return.
            if res_json.startswith('"') and res_json.endswith('"'):
                return res_json[1:-1]
                
            return res_json

        except Exception as e:
            # We initialize the logger here to ensure it's available in the exception context
            logger = logging.getLogger(__name__)
            logger.error(f"Error executing tool '{self.name}': {e}")
            raise

def tool(name: str = None, description: str = None):
    """
    A decorator that converts a function into a Tool object.

    Args:
        name (Optional[str]): A custom name for the tool.
        description (Optional[str]): A custom description for the tool.

    Returns:
        Callable: A decorator function that wraps the target function in a Tool instance.
    """
    def decorator(func):
        # Wir geben eine Instanz von Tool zurück
        return Tool(func, name=name, description=description)
    return decorator


__all__ = ["tool", "Tool"]

# end of file src/org/slashlib/py/agent/tool.py