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
        
        The schema follows the standard expected by modern LLMs for tool calling.

        Returns:
            dict: A dictionary representing the tool's schema, including name, 
                description, and parameter definitions.
        """
        sig = inspect.signature(self._func)
        parameters = {"type": "object", "properties": {}, "required": []}

        for param_name, param in sig.parameters.items():
            # Skip 'self' or 'cls' if decorated inside a class (though unlikely here)
            if param_name in ("self", "cls"):
                continue

            param_type = self._map_type(param.annotation)
            
            param_info = {
                "type": param_type,
                "description": f"Parameter {param_name}"
            }

            # If there's a default value, mention it in the description
            if param.default is not inspect.Parameter.empty:
                param_info["default"] = param.default
                param_info["description"] += f" (defaults to {param.default})"
            else:
                parameters["required"].append(param_name)

            parameters["properties"][param_name] = param_info

        return {
            "name": self.name,
            "description": self.description.strip(),
            "parameters": parameters
        }

    async def __call__(self, *args, **kwargs):
        """
        Executes the wrapped function.
        
        Supports both synchronous and asynchronous functions transparently.

        Args:
            *args: Positional arguments for the wrapped function.
            **kwargs: Keyword arguments for the wrapped function.

        Returns:
            Any: The result of the function execution.
        """
        if inspect.iscoroutinefunction(self._func):
            return await self._func(*args, **kwargs)
        return self._func(*args, **kwargs)


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