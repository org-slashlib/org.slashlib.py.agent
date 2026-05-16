[BOTTOM](#100---2021-07-26) [AI](AI.md) [LICENSE](LICENSE) [README](README.md)

# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

### Added

- No additions yet

### Fixed

- No Fixes yet

---
## [0.1.5] - 2026-05-16

### Added

- Plugin mechanism added to pyproject.toml:
  [project.entry-points."org.slashlib.py.agent.inference"]
  my-inference-adapter = "my.adapter:AIInferenceAdapter"

- Added Agent.list_plugins()

- Added Agent.from_plugin(identifier: str, tools: typing.List[tool.Tool], plugin_name: str, adapter_kwargs: dict = None, **agent_kwargs):

## [0.1.4] - 2026-05-15

Quickfix: ollama inference adapter removed. See `pip install org.slashlib.py.inference.ollama`

## [0.1.3] - 2026-05-15

### Fixed

- Tool description structure is now:
  ```
  {
    'type': 'function',
    'function': {
      'name': 'some_function',
      'description': 'Some function description',
      'parameters': {
        'type': 'object',
        'properties': {
          'paramname': {
            'type': 'string',
            'description': 'Description of the param using paramname',
          },
        },
        'required': ['paramname'],
      },
    },
  }
  ```
- Tool.__call__ now only returns strings.

---
## [0.1.1] - 2026-05-14

### Added

- AgentResponse now supports `get_last_context`.

### Fixed

-  README.md changed `response.get_last_content()` to `response.get_last_context()`

---
## [0.1.1] - 2026-05-14

### Fixed

-  Missing dependency `org.slashlib.py.configloader` in `pyproject.toml`

---
## [0.1.0] - 2026-05-12

Initial release

[TOP](#changelog) [AI](AI.md) [LICENSE](LICENSE) [README](README.md)