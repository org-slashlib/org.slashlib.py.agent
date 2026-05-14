# -*- coding: utf-8 -*-
# file tests/00_00_00_importlibs_test.py
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
import importlib

# Third party imports
import pytest


def test_import_configloader():
    """
    Check if 'org.slashlib.py.configloader' is installed and accessible.
    This is a core dependency for the Agent framework.
    """
    try:
        importlib.import_module("org.slashlib.py.configloader")
    except ImportError as e:
        pytest.fail(f"Critical error: 'org.slashlib.py.configloader' not found. Error: {e}")


def test_import_ollama():
    """
    Verify that the 'ollama' library is present.
    Required for the OllamaInferenceAdapter.
    """
    try:
        importlib.import_module("ollama")
    except ImportError as e:
        pytest.fail(f"Critical error: 'ollama' library is missing. Install it via 'pip install ollama'. Error: {e}")


def test_import_internal_modules():
    """
    Ensure the project's internal structure is correctly resolved.
    This validates the PYTHONPATH and package layout.
    """
    internal_modules = [
        "org.slashlib.py.agent.agent",
        "org.slashlib.py.agent.tool",
        "org.slashlib.py.agent.agent_response",
        "org.slashlib.py.agent.inference_bases",
        "org.slashlib.py.agent.inference_complements_for_ollama"
    ]
    for module_name in internal_modules:
        try:
            importlib.import_module(module_name)
        except ImportError as e:
            pytest.fail(f"Internal Import Error: {module_name} could not be loaded. Error: {e}")


# No __all__ export needed for test files as they are not meant to be imported as modules.