[Bottom](#license) [AI](AI.md) [CHANGELOG](CHANGELOG.md) [LICENSE](LICENSE.md)
# org.slashlib.py.agent

A highly decoupled, asynchronous framework for building AI agents in Python.

[![PyPI version](https://img.shields.io/pypi/v/org.slashlib.py.agent.svg?color=blue)](https://pypi.org/project/org.slashlib.py.agent/) 
[![PyPI-Test version](https://img.shields.io/badge/pypitest-latest-blue)](https://test.pypi.org/project/org.slashlib.py.agent/) 
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

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

    # 3. Start task (non-blocking)
    task = my_agent.run(user_prompt="What is 123 + 456?")
    
    # 4. Retrieve result
    response = await task
    print(f"Response: {response.get_last_context()}")

if __name__ == "__main__":
    asyncio.run(main())
```

### Plugin Discovery

The framework supports dynamic loading of inference adapters. To use an external adapter (e.g., for Ollama), ensure the plugin package is installed and use the factory method:

```python
from org.slashlib.py.agent import Agent

# List all available inference plugins
available = Agent.list_plugins()
print(f"Available adapters: {available}")

# Create agent from a plugin (e.g., 'ollama')
my_agent = Agent.from_plugin(
    identifier="my-agent",
    tools=[my_tool],
    plugin_name="ollama",
    adapter_kwargs={"base_url": "http://localhost:11434"}
)

```

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