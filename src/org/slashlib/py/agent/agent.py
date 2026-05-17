# -*- coding: utf-8 -*-
# file src/org/slashlib/py/agent/agent.py
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
import asyncio
import importlib.metadata
import logging
import pathlib
import typing

# Third party imports
import org.slashlib.py.configloader as config

# Internal imports
import org.slashlib.py.agent.tool as tool
import org.slashlib.py.agent.agent_response as response
import org.slashlib.py.agent.inference_bases as inference


# Module-level instance registry to implement the Multiton pattern
_instances: typing.Dict[str, "Agent"] = {}


class Agent:
    """
    Base class for an AI Agent.
    
    This class orchestrates the interaction between an inference adapter and a set of tools.
    """

    @classmethod
    def from_plugin(cls, identifier: str, plugin_name: str, tools: typing.List[tool.Tool] = (), adapter_kwargs: dict = None, **agent_kwargs):
        """
        Creates an Agent instance by loading an InferenceAdapter from a registered entry point.

        This method uses the Python entry points mechanism to dynamically discover and 
        instantiate InferenceAdapter implementations registered under the group 
        'org.slashlib.py.agent.inference'.

        Args:
            identifier (str): A unique identifier for the agent instance.
            plugin_name (str): The name of the registered entry point (e.g., 'ollama').
            tools (typing.List[tool.Tool]): A list of Tool objects the agent can use.
            adapter_kwargs (dict, optional): Keyword arguments passed to the constructor 
                of the discovered InferenceAdapter class. Defaults to None.
            **agent_kwargs: Additional keyword arguments passed to the Agent constructor 
                (e.g., 'multi').

        Returns:
            Agent: An initialized instance of the Agent class with the loaded adapter.

        Raises:
            ValueError: If no entry point with the name `plugin_name` is found in the 
                group 'org.slashlib.py.agent.inference'.
            TypeError: If the loaded entry point does not result in a valid 
                InferenceAdapter.
        """
        eps = importlib.metadata.entry_points(group='org.slashlib.py.agent.inference')
        entry = next((e for e in eps if e.name == plugin_name), None)
        
        if not entry:
            raise ValueError(f"Plugin '{plugin_name}' not found in group 'org.slashlib.py.agent.inference'")

        # Lädt die Adapter-Klasse (z.B. OllamaInferenceAdapter)
        adapter_class = entry.load()
        
        # Instanziiert den Adapter mit optionalen Parametern
        adapter_instance = adapter_class(**(adapter_kwargs or {}))
        
        # Gibt eine neue Agent-Instanz zurück
        return cls(identifier=identifier, adapter=adapter_instance, tools=tools, **agent_kwargs)

    @classmethod
    def list_plugins(cls) -> typing.List[str]:
        """
        Returns a list of all registered inference plugin names.
        
        Returns:
            typing.List[str]: A list of names (e.g., ['ollama', 'openai']) 
                              found under 'org.slashlib.py.agent.inference'.
        """
        eps = importlib.metadata.entry_points(group='org.slashlib.py.agent.inference')
        return [entry.name for entry in eps]        
        
    def __new__(cls, identifier: str, adapter: inference.InferenceAdapter, tools: typing.List[tool.Tool] = (), multi: bool = True):
        """
        Create a new instance or return an existing one based on the identifier.

        Args:
            identifier (str): A unique identifier for the agent instance.
            adapter (inference.InferenceAdapter): The adapter to use for inference.
            tools (typing.List[tool.Tool]): A list of Tool objects the agent can use.
            multi (bool): Whether the agent can run multiple tasks simultaneously.

        Returns:
            Agent: The new or existing agent instance.
        """
        if identifier in _instances:
            return _instances[identifier]
        
        instance = super(Agent, cls).__new__(cls)
        _instances[identifier] = instance
        return instance

    def __init__(self, identifier: str, adapter: inference.InferenceAdapter, tools: typing.List[tool.Tool] = (), multi: bool = True):
        """
        Initialize the Agent.

        Args:
            identifier (str): A unique identifier for the agent instance.
            adapter (inference.InferenceAdapter): The adapter providing the inference capabilities.
            tools (typing.List[tool.Tool]): A list of Tool objects. Must not be empty.
            multi (bool): If False, the agent allows only one active task at a time. Defaults to True.

        Raises:
            ValueError: If tools or adapter is None.
        """
        # Skip initialization if already initialized (for __new__ multiton logic)
        if hasattr(self, "_initialized") and self._initialized:
            return

        self.log = logging.getLogger(f"org.slashlib.py.agent.{pathlib.Path(__file__).stem}.{self.__class__.__name__}")
        self._identifier = identifier
        self._multi = multi
        
        if not adapter:
            raise ValueError("An InferenceAdapter is required.")

        self._tools = tools
        self._adapter = adapter
        self._active_tasks: typing.Set[asyncio.Task] = set()
        self._initialized = True
        self.log.debug(f"Agent initialized with {len(self._tools)} tools and adapter {type(adapter).__name__} (multi={self._multi})")

    def __del__(self):
        """
        Destructor called when the agent object is about to be destroyed.
        Ensures all running tasks are cancelled.
        """
        # Note: During interpreter shutdown, globals/imports might be None.
        try:
            if hasattr(self, "_active_tasks") and self._active_tasks:
                self.cancel()
        except Exception:
            # Destructors should not raise exceptions
            pass

    @property
    def identifier(self) -> str:
        """
        Get the identifier of the agent.

        Returns:
            str: The agent's identifier.
        """
        return self._identifier

    @property
    def tools(self) -> typing.List[tool.Tool]:
        """
        Get the list of tools available to the agent.
        
        Returns:
            List[tool.Tool]: The registered tools.
        """
        return self._tools

    @property
    def has_active_tasks(self) -> bool:
        """
        Check if the agent is currently processing any tasks.

        Returns:
            bool: True if there are running background tasks.
        """
        return len(self._active_tasks) > 0

    def get_tool_schemas(self) -> typing.List[dict]:
        """
        Collects all JSON schemas from the registered tools.

        Returns:
            typing.List[dict]: A list of tool schemas for LLM consumption.
        """
        return [tool_obj.get_schema() for tool_obj in self._tools]

    def _init_response_object(self, **kwargs) -> response.AgentResponse:
        """
        Initializes a new AgentResponse object and sets up the initial context.

        Args:
            **kwargs: Arguments containing 'user_prompt' and optional 'system_prompt'.

        Returns:
            response.AgentResponse: The initialized response object.
        """
        response_obj = response.AgentResponse()
        
        user_prompt = kwargs.get("user_prompt")
        system_prompt = kwargs.get("system_prompt")
        
        if not user_prompt:
            err = ValueError("A 'user_prompt' is required to run the agent.")
            response_obj.append_error(err)
            return response_obj

        if system_prompt:
            response_obj.append_context(role="system", content=system_prompt)
            
        response_obj.append_context(role="user", content=user_prompt)
        return response_obj

    async def _execute_tool(self, name: str, arguments: dict) -> typing.Any:
        """
        Internal helper to find and execute a tool by its name.

        Args:
            name (str): The name of the tool to execute.
            arguments (dict): The arguments to pass to the tool.

        Returns:
            Any: The result of the tool execution.

        Raises:
            ValueError: If no tool with the given name is found.
        """
        for tool_obj in self._tools:
            if tool_obj.name == name:
                self.log.info(f"Agent {self.identifier} executing tool '{name}' with {arguments}")
                return await tool_obj(**arguments)
        
        raise ValueError(f"Tool '{name}' not found in agent's toolbox.")

    async def _run_tool_calls(self, response_obj: response.AgentResponse, tool_calls: typing.Optional[typing.List[dict]]) -> bool:
        """
        Processes tool calls if present.

        Args:
            response_obj (response.AgentResponse): The current response object to update.
            tool_calls (Optional[List[dict]]): The list of tool calls from the LLM.

        Returns:
            bool: True if tool calls were processed, False otherwise.
        """
        if not tool_calls:
            return False

        self.log.info(f"Agent {self.identifier} received {len(tool_calls)} tool call(s).")
        
        for call in tool_calls:
            tool_name = call.get("function", {}).get("name")
            tool_args = call.get("function", {}).get("arguments")
            tool_call_id = call.get("id")
            
            # Basis-Argumente für den Kontext vorbereiten
            context_kwargs = {
                "role": "tool",
                "name": tool_name
            }

            # tool_call_id nur anfügen, wenn sie vorhanden und nicht leer ist
            if tool_call_id:
                context_kwargs["tool_call_id"] = tool_call_id
            
            try:
                result = await self._execute_tool(tool_name, tool_args)
                context_kwargs["content"] = result
                response_obj.append_context(**context_kwargs)
            except BaseException as tool_err:
                # Wir fangen ALLES ab (BaseException), damit has_tool_error garantiert True wird
                self.log.error(f"Tool execution failed: {tool_err}")
                
                # Das Flag im Response-Objekt setzen
                response_obj.append_tool_error(tool_err)
                
                # Den Fehler für das LLM in den Kontext schreiben
                context_kwargs["content"] = f"Error: {str(tool_err)}"
                response_obj.append_context(**context_kwargs)

                # Falls es ein KeyboardInterrupt oder SystemExit war, sollten wir 
                # es nach der Protokollierung ggf. trotzdem weiterreichen, 
                # aber für den Agent-Flow ist es erst einmal im Response-Objekt sicher.
                if isinstance(tool_err, (KeyboardInterrupt, SystemExit)):
                    raise
                    
        return True

    async def _run(self, **kwargs) -> response.AgentResponse:
        """
        Internal asynchronous task execution.
        
        Orchestrates the loop between the inference adapter and tool execution.

        Args:
            **kwargs: Arbitrary keyword arguments. 
                      Supports 'user_prompt', 'system_prompt', 'model', 'timeout' and 'think'.

        Returns:
            response.AgentResponse: The result object containing the history and any errors.
        """
        response_obj = self._init_response_object(**kwargs)
        
        if response_obj.has_error:
            return response_obj

        try:
            is_running = True
            while is_running:
                self.log.debug(f"Agent {self.identifier} initiating inference call...")
                
                tool_schemas = self.get_tool_schemas()
                
                # The adapter handles all provider-specific details and config resolution
                inference_result = await self._adapter.chat(
                    messages=response_obj.get_context(),
                    tools=tool_schemas if tool_schemas else None,
                    **kwargs
                )

                # Use the standardized to_dict() for AgentResponse
                response_obj.append_context(**inference_result.to_dict())

                if await self._run_tool_calls(response_obj, inference_result.tool_calls):
                    continue

                is_running = False
                self.log.info(f"Agent {self.identifier} finished task.")
                
        except asyncio.CancelledError:
            self.log.debug(f"Task for agent {self.identifier} was cancelled.")
            raise
        except inference.InferenceError as ie:
            self.log.error(f"Inference failed for agent {self.identifier}: {ie}")
            response_obj.append_error(ie)
        except Exception as e:
            self.log.error(f"Unexpected error in background task for agent {self.identifier}: {e}", exc_info=True)
            response_obj.append_error(e)
        finally:
            current_task = asyncio.current_task()
            if current_task in self._active_tasks:
                self._active_tasks.remove(current_task)
            
            return response_obj

    def run(self, **kwargs) -> asyncio.Task:
        """
        Starts the agent logic in a non-blocking background task.

        Args:
            **kwargs: Arbitrary keyword arguments passed to the internal _run method.

        Returns:
            asyncio.Task: The task object managing the background execution. 
                          The result of this task will be an AgentResponse object.

        Raises:
            RuntimeError: If multi is False and a task is already running.
        """
        if not self._multi and self.has_active_tasks:
            raise RuntimeError(f"Agent {self.identifier} is already running a task and multi-tasking is disabled.")

        task = asyncio.create_task(self._run(**kwargs))
        self._active_tasks.add(task)
        return task

    def cancel(self, task: typing.Optional[asyncio.Task] = None):
        """
        Cancels running tasks. 

        Args:
            task (Optional[asyncio.Task]): The specific task to cancel.
        """
        if task is not None:
            if task in self._active_tasks:
                task.cancel()
                self.log.debug(f"Specific task cancelled for agent {self.identifier}.")
            else:
                self.log.warning(f"Task cancel requested but task not found in active tasks for agent {self.identifier}.")
            return

        if not self._active_tasks:
            self.log.debug(f"No active tasks to cancel for agent {self.identifier}.")
            return

        self.log.debug(f"Cancelling all ({len(self._active_tasks)}) active tasks for agent {self.identifier}.")
        for t in list(self._active_tasks):
            t.cancel()


__all__ = ["Agent"]

# end of file src/org/slashlib/py/agent/agent.py