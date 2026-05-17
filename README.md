[Bottom](#license) [AI](AI.md) [CHANGELOG](CHANGELOG.md) [LICENSE](LICENSE.md)
# org.slashlib.py.agent

A highly decoupled, asynchronous framework for building AI agents in Python.

[![PyPI version](https://img.shields.io/pypi/v/org.slashlib.py.agent.svg?color=blue)](https://pypi.org/project/org.slashlib.py.agent/)  [![PyPI-Test version](https://img.shields.io/badge/pypitest-latest-blue)](https://test.pypi.org/project/org.slashlib.py.agent/)  [![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

---
## Core Concept

This package provides a robust infrastructure to connect AI models (Inference Engines) with functional tools. The focus lies on **Provider Agnosticism**: The agent does not need to know whether it is communicating with Ollama, OpenAI, or a local model—it uses standardized adapters to ensure seamless integration.

### Key Features
- **Asynchronous Core**: Built on `asyncio` for non-blocking task execution.
- **Provider Agnostic**: Easily swap the AI engine using the Adapter pattern.
- **Automatic Tool Schemas**: Automatically transforms Python functions into JSON schemas for LLMs via decorators.
- **Multiton Pattern**: Ensures unique agent instances by identifier, preventing redundant resource allocation.
- **Robust Exception Hierarchy**: Clearly separates connection, configuration, and tool execution errors.
- **Plugin System:** Discover and load inference adapters dynamically via Python entry points.

---
## Installation

Install the package via pip:

```bash
pip install org.slashlib.py.agent
```

---
### Configuration

The framework can automatically ingest default settings from a pyproject.json file located in your project root. This allows you to manage model parameters without changing your code.

**pyproject.json:**
```json
{
  "name": "My App",
  "version": "0.0.1",
  "paths": {
    "ROOT":   "{ROOT}",
    "assets": "{ROOT}/assets"
  },
  "assets": {
    "logging": "{path.assets}/logging.json"
  },
  "plugins": {
    "my-inference-adapter": {
      "default-setting": "foo"
    }
  }
}
```

---
## Quick Start

Setting up an agent with a tool and the Ollama adapter is straightforward:

```python
import asyncio
from org.slashlib.py.inference.ollama import OllamaInferenceAdapter
from org.slashlib.py.agent import Agent, tool

# 1. Define a tool
@tool(description="Adds two numbers.")
async def add_numbers(a: int, b: int) -> int:
    return a + b

async def main():
    # 2. Configure Adapter and Agent
    adapter = OllamaInferenceAdapter()
    my_agent = Agent(
        identifier="MathExpert",
        tools=[add_numbers],
        adapter=adapter
    )

    # 3. Start task and retrieve result
    response = await my_agent.run(user_prompt="What is 123 + 456?")
    print(f"Response: {response.get_last_context()}")

if __name__ == "__main__":
    asyncio.run(main())
```

---
### The `@tool` Decorator

The @tool decorator is the bridge between standard Python functions and AI logic. It transforms a function into an instance of the Tool class. This class automatically generates the metadata and JSON schemas required by Large Language Models (LLMs) like Gemma or Llama to understand how to interact with your code.

#### Key Features
- **Schema Generation:** Automatically extracts the tool name, description (from docstrings), and parameter types (from type hints).
- **Flexible Invocation:** Can be used with or without parentheses and optional parameters.
- **Execution Wrapper:** Handles both synchronous and asynchronous functions, ensuring results are formatted as strings or JSON suitable for LLM context.
- **Type Mapping:** Maps Python types (int, str, list, etc.) to their corresponding JSON schema types.

#### Usage Rules
1. **Flexible Decoration:** The decorator can be used as `@tool` or `@tool()`. If parameters like `name` or `description` are omitted, they are automatically derived from the function's own name and its docstring.
2. **Type Hints are Mandatory:** Use Python type hints (e.g., `a: int`, `names: list`). These are essential to build the "parameters" section of the JSON schema.
3. **Docstrings Matter:** Unless an explicit description is provided in the decorator, the function's docstring serves as the tool's description. Be precise, as this is the "manual" the AI reads to decide when and how to use the tool.
4. **Metadata Fallback:** If neither a decorator parameter nor a docstring is present, a generic placeholder is used for the description to ensure schema validity.

#### Examples: A Mathematical Tool

```python
from org.slashlib.py.agent import tool

@tool
def add_numbers(a: int, b: int) -> int:
    """
    Adds two integers together and returns the sum.
    
    Args:
        a (int): The first number.
        b (int): The second number.
        
    Returns:
        int: The sum of a and b.
    """
    return a + b

# The function 'add_numbers' is now a Tool object and can be 
# passed directly to an Agent:
# my_agent = Agent(..., tools=[add_numbers])
```

```python
from org.slashlib.py.agent import tool

@tool(name="sum_integers", description="Calculates the sum of two whole numbers.")
def add_numbers(a: int, b: int) -> int:
    """
    Adds two integers together and returns the sum.
    
    Args:
        a (int): The first number.
        b (int): The second number.
        
    Returns:
        int: The sum of a and b.
    """
    return a + b

# Explanation of metadata prioritization:
# ----------------------------------------
# In this scenario, the schema values are determined as follows:
#
# 1. Name: "sum_integers" 
#    -> Because the 'name' parameter is explicitly provided in the decorator, 
#       it overrides the actual function name 'add_numbers'.
#
# 2. Description: "Calculates the sum of two whole numbers."
#    -> The 'description' parameter in the decorator takes precedence. 
#       The function's docstring is ignored in this specific case.
```

```python
from org.slashlib.py.agent import tool

@tool(name="sum_integers", description="Calculates the sum of two whole numbers.")
def add_numbers(a: int, b: int) -> int:
    return a + b

# Explanation of metadata prioritization (No Docstring):
# ------------------------------------------------------
# In this scenario, the schema values are determined as follows:
#
# 1. Name: "sum_integers" 
#    -> The 'name' parameter in the decorator is used, overriding the 
#       function name 'add_numbers'.
#
# 2. Description: "Calculates the sum of two whole numbers."
#    -> The 'description' parameter in the decorator is used. 
#       Since the function has no docstring, this is the only source 
#       of information for the tool's description.
#
# Note: If the 'description' parameter were also omitted, the Tool 
# class would fall back to a generic "No description provided." 
# because func.__doc__ is None.
```

---
### Async Execution

The framework is built on Python's `asyncio`. The `Agent.run` method is an asynchronous coroutine. This allows your application to remain responsive or handle multiple agents concurrently.

#### Correct Async Flow

```python
import asyncio
from org.slashlib.py.agent import Agent

async def main():
    # 1. Initialize Agent (via plugin or direct)
    my_agent = Agent.from_plugin(
        identifier="MathExpert",
        tools=[add_numbers],
        plugin_name="ollama-inference-adapter"
    )

    # 2. Execute run (awaits the completion of the inference cycle)
    # The method returns an AgentResponse object directly.
    response = await my_agent.run(
        user_prompt="What is 123 + 456?",
        model="gemma4"
    )
    
    # 3. Handle the result
    if not response.has_error:
        print(f"Response: {response.response}")
    else:
        response.raise_errors()

if __name__ == "__main__":
    asyncio.run(main())

```

---
### Understanding `AgentResponse`

The `Agent.run()` method does not return a simple string, but an `AgentResponse` object. This container manages the execution results, the conversation history (context), and any errors that may have occurred.

#### Key Properties & Methods

* **`.response`**: Returns the final text response from the assistant. Use this to get the AI's answer.
* **`.has_error`**: A boolean flag indicating if a fatal process error (e.g., connection issues, missing models) occurred.
* **`.raise_errors()`**: A helper method that raises the first recorded process error as an exception. Useful for debugging failed runs.
* **`.context_size`**: Returns the number of messages exchanged in the current run.
* **`.get_context()`**: Returns the full conversation history (messages, tool calls, and results).

#### Example: Handling the Response

```python
response = await my_agent.run(user_prompt="Calculate 123 + 456", model="gemma4")

if response.has_error:
    print(f"An error occurred!")
    response.raise_errors()
else:
    print(f"Assistant says: {response.response}")
    print(f"Conversation steps: {response.context_size}")
    
#### Process Errors vs. Tool Errors
```

The `AgentResponse` distinguishes between two types of issues to give you fine-grained control over error handling:

* **Process Errors (`.has_error` / `._errors`)**: These are **fatal** errors that prevented the Agent from completing its task (e.g., connection loss to Ollama, model not found, or authentication issues).
* **Tool Errors (`.has_tool_error` / `.get_tool_errors()`)**: These are **non-fatal** errors that occurred inside a specific tool execution. The Agent might still be able to provide a final response even if one or more tool calls failed.

**Pro-Tip:** If you want your application to be extra robust, always check both:

```python
response = await my_agent.run(...)

if response.has_error:
    # Fatal: The agent couldn't finish
    response.raise_errors()

if response.has_tool_error:
    # Non-fatal: One or more tools failed, but the agent still replied
    for err in response.get_tool_errors():
        print(f"Warning: Tool execution failed: {err}")
```

---
### Plugin Discovery & Dynamic Loading

The framework utilizes Python's entry points to support dynamic discovery and loading of inference adapters. This allows you to extend the agent's capabilities with external adapters without modifying the core package.

#### Using `Agent.from_plugin`

To use an external adapter, ensure the corresponding plugin package is installed in your environment. You can then instantiate an agent using the discovery interface:

```python
from org.slashlib.py.agent import Agent

# 1. List all discovered inference adapter plugins
# This scans the environment for registered 'org.slashlib.py.inference.adapter' entry points.
available = Agent.list_plugins()
print(f"Available adapters: {available}")

# 2. Create an agent using a specific plugin
# In this example, we load the Ollama adapter dynamically.
my_agent = Agent.from_plugin(
    identifier="my-dynamic-agent",
    tools=[my_tool],                      # Must be a list of @tool() objects
    plugin_name="ollama-inference-adapter", # The name registered in entry_points
    adapter_kwargs={                      # Arguments passed directly to the Adapter __init__
        "base_url": "http://localhost:11434"
    },
    multi=True                            # Optional: Agent-specific keyword arguments
)
```

#### Why use Discovery?

- **Decoupling:** The core agent logic remains independent of specific LLM providers (Ollama, OpenAI, etc.).

- **Extensibility:** Simply install a new adapter package, and it becomes immediately available via list_plugins().

- **Flexible Config:** adapter_kwargs allows for provider-specific configuration (like API keys or base URLs) while keeping the Agent initialization clean.

---
## Documentation & Obsidian

The project root is pre-configured as an **Obsidian Vault**. If you open this folder directly in Obsidian, all settings and documentation links will be available immediately via the included `.obsidian` directory.

The following community plugins are pre-configured in the vault to enhance the documentation experience:

* **[File Include](https://github.com/tillahoffmann/obsidian-file-include)**: Embed code files directly into your markdown documentation.
* **[Folder Notes](https://github.com/LostPaul/obsidian-folder-notes)**: Add descriptions at the folder level.
* **[Front Matter Title](https://github.com/snezhig/obsidian-front-matter-title)**: Use metadata for descriptive file titles.
* **[Hide Folders](https://github.com/JonasDoesThings/obsidian-hide-folders)**: Keeps the structure clean by hiding internal directories.
* **[Iconic](https://github.com/gfxholo/iconic)** & **[Icons](https://github.com/visini/obsidian-icons-plugin)**: Improved visual navigation.

[More docs](docs/docs.md)

---
## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE.md) file for details.

---
© 2026 org.slashlib

[TOP](#org-slashlib-py-agent) [AI](AI.md) [CHANGELOG](CHANGELOG.md) [LICENSE](LICENSE.md)