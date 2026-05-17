# -*- coding: utf-8 -*-
# file tests/03_01_21_agent_agent_from_plugin_test.py
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
Method: from_plugin

Tests the dynamic creation of an Agent instance using the entry point mechanism.
Verifies plugin discovery, class loading, and correct instantiation of both 
the adapter and the agent.
"""

import pytest
from unittest.mock import patch, MagicMock
from org.slashlib.py.agent.agent import Agent
from org.slashlib.py.agent.inference_bases import InferenceAdapter
from org.slashlib.py.agent.tool import Tool


def test_from_plugin_existence():
    """
    What: Verify the existence and type of the from_plugin method.
    Why: Required by existence validation rules.
    """
    assert hasattr(Agent, "from_plugin")
    assert callable(Agent.from_plugin)


def test_from_plugin_success():
    """
    What: Verify successful Agent creation via a mocked plugin.
    Why: Ensure the entry point is loaded and the Agent is correctly initialized.
    """
    plugin_name = "test_adapter"
    agent_id = "plugin_agent_success"
    
    # We need at least one tool to satisfy Agent.__init__ validation
    mock_tool = MagicMock(spec=Tool)
    
    # Mock for the Adapter class that will be returned by entry.load()
    MockAdapterClass = MagicMock(spec=InferenceAdapter)
    mock_adapter_instance = MagicMock(spec=InferenceAdapter)
    MockAdapterClass.return_value = mock_adapter_instance

    # Mock for the entry point
    mock_entry = MagicMock()
    mock_entry.name = plugin_name
    mock_entry.load.return_value = MockAdapterClass

    with patch("importlib.metadata.entry_points") as mock_ep:
        mock_ep.return_value = [mock_entry]

        # Call the method
        agent = Agent.from_plugin(
            identifier=agent_id,
            tools=[mock_tool],
            plugin_name=plugin_name,
            adapter_kwargs={"api_key": "secret"}
        )

        # Assertions
        assert isinstance(agent, Agent)
        assert agent.identifier == agent_id
        # Verify the adapter class was instantiated with the correct kwargs
        MockAdapterClass.assert_called_once_with(api_key="secret")
        mock_ep.assert_called_once_with(group='org.slashlib.py.agent.inference')


def test_from_plugin_not_found_raises_value_error():
    """
    What: Verify that a ValueError is raised if the plugin name is unknown.
    Why: Proper error handling for missing dependencies/configuration.
    """
    with patch("importlib.metadata.entry_points") as mock_ep:
        mock_ep.return_value = []
        
        with pytest.raises(ValueError) as excinfo:
            Agent.from_plugin(
                identifier="fail_agent",
                tools=[MagicMock(spec=Tool)],
                plugin_name="non_existent"
            )
        
        assert "Plugin 'non_existent' not found" in str(excinfo.value)


def test_from_plugin_passes_agent_kwargs():
    """
    What: Verify that **agent_kwargs are passed to the Agent constructor.
    Why: Ensure configuration like 'multi=True' reaches the Agent instance.
    """
    mock_tool = MagicMock(spec=Tool)
    MockAdapterClass = MagicMock()
    mock_entry = MagicMock()
    mock_entry.name = "kwarg_plugin"
    mock_entry.load.return_value = MockAdapterClass

    with patch("importlib.metadata.entry_points") as mock_ep:
        mock_ep.return_value = [mock_entry]

        agent = Agent.from_plugin(
            identifier="kwarg_agent",
            tools=[mock_tool],
            plugin_name="kwarg_plugin",
            multi=True  # This is an agent_kwarg
        )
        
        # Accessing the private attribute to verify initialization
        assert agent._multi is True


def test_from_plugin_multiton_behavior():
    """
    What: Verify that from_plugin respects the Multiton pattern.
    Why: Consistency with the standard Agent constructor.
    """
    agent_id = "multiton_plugin_test"
    mock_tool = MagicMock(spec=Tool)
    
    MockAdapterClass = MagicMock()
    mock_entry = MagicMock()
    mock_entry.name = "multiton_plugin"
    mock_entry.load.return_value = MockAdapterClass

    with patch("importlib.metadata.entry_points") as mock_ep:
        mock_ep.return_value = [mock_entry]

        # First creation
        agent1 = Agent.from_plugin(agent_id, "multiton_plugin", [mock_tool])
        # Second creation with same ID
        agent2 = Agent.from_plugin(agent_id, "multiton_plugin", [mock_tool])

        assert agent1 is agent2

# end of file tests/03_01_21_agent_agent_from_plugin_test.py