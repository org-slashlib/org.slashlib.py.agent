[BOTTOM](#100---2021-07-26) [AI](AI.md) [LICENSE](LICENSE) [README](README.md)

# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

### Added

- No additions yet

### Fixed

- No Fixes yet

---
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