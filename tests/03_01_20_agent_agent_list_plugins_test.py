# -*- coding: utf-8 -*-
# file tests/03_01_20_agent_agent_list_plugins_test.py
# @AI:
# - INTEGRITY RULES:
#    - STRICT PRESERVATION: Do not remove, move, or modify ANY existing lines of code or comments 
#      unless they are the explicit target of the requested change. 
#    - DEBUG MARKERS: Commented-out code (e.g., debug prints) MUST be kept exactly where they are. 
#    - WHITESPACE & STRUCTURE: Maintain all original empty lines and the existing file structure. 
#      Structural integrity takes precedence over "clean code" or "elegance".
#    - LEAD-IN/OUT: The very first and last lines (and all comments in between) are immutable anchors.
# - MAINTENANCE:
#    - Only update pydoc strings (args, returns, raises) if the function signature changes.
#    - Do NOT delete existing examples or descriptions in pydoc.
# - LANGUAGE: en-US for all comments and documentation.
#

"""
Module: org.slashlib.py.agent.agent
Class: Agent
Method: list_plugins

Tests the dynamic discovery of inference plugins via entry points.
Verifies that the method correctly identifies and returns the names of registered plugins.
"""

import pytest
from unittest.mock import patch, MagicMock
from org.slashlib.py.agent.agent import Agent


def test_list_plugins_existence():
    """
    What: Verify the existence and type of the list_plugins method.
    Why: Required by existence validation rules.
    """
    assert hasattr(Agent, "list_plugins")
    assert callable(Agent.list_plugins)


def test_list_plugins_returns_list_of_strings():
    """
    What: Verify that the method returns a list of strings.
    Why: Ensure the return type matches the type hint and expectation.
    """
    # Mocking entry_points to avoid dependency on the actual environment
    with patch("importlib.metadata.entry_points") as mock_ep:
        mock_entry = MagicMock()
        mock_entry.name = "ollama"
        mock_ep.return_value = [mock_entry]

        result = Agent.list_plugins()

        assert isinstance(result, list)
        if len(result) > 0:
            assert isinstance(result[0], str)
            assert result[0] == "ollama"


def test_list_plugins_correct_group_access():
    """
    What: Verify that the method queries the correct entry point group.
    Why: Ensure it doesn't accidentally list plugins from other domains.
    """
    target_group = "org.slashlib.py.agent.inference"
    with patch("importlib.metadata.entry_points") as mock_ep:
        mock_ep.return_value = []
        
        Agent.list_plugins()
        
        # Verify the call was made with the specific group
        mock_ep.assert_called_once_with(group=target_group)


def test_list_plugins_empty_results():
    """
    What: Verify behavior when no plugins are registered.
    Why: Ensure the method handles empty environments gracefully without error.
    """
    with patch("importlib.metadata.entry_points") as mock_ep:
        mock_ep.return_value = []
        
        result = Agent.list_plugins()
        
        assert result == []


def test_list_plugins_multiple_results():
    """
    What: Verify retrieval of multiple registered plugins.
    Why: Ensure all names in the group are collected.
    """
    plugin_names = ["ollama", "openai", "custom_adapter"]
    
    with patch("importlib.metadata.entry_points") as mock_ep:
        mock_entries = []
        for name in plugin_names:
            m = MagicMock()
            m.name = name
            mock_entries.append(m)
        
        mock_ep.return_value = mock_entries
        
        result = Agent.list_plugins()
        
        assert len(result) == 3
        for name in plugin_names:
            assert name in result

# end of file tests/03_01_20_agent_agent_list_plugins_test.py