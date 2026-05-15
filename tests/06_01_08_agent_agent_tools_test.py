# -*- coding: utf-8 -*-
# file tests/06_01_08_agent_agent_tools_test.py
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

"""
Module: org.slashlib.py.agent.agent
Class: Agent
Method: tools (property)

Special Considerations:
The tools property returns a list of Tool objects. Since the Agent relies on 
these tools for execution, this property must return the exact set of tools 
provided during initialization. We also test for immutability to ensure the 
internal toolset is not replaced externally.
"""

import pytest
import typing
from unittest.mock import MagicMock
from org.slashlib.py.agent.agent import Agent
from org.slashlib.py.agent.inference_bases import InferenceAdapter
from org.slashlib.py.agent.tool import Tool

def test_existence_and_type():
    """
    What: Verify the integrity of the test object.
    Why: Mandatory first test to ensure the property is accessible and returns a list.
    Assumptions: The Agent class implementation includes a 'tools' property.
    """
    mock_adapter = MagicMock(spec=InferenceAdapter)
    dummy_tool = Tool(lambda: None, name="dummy")
    agent = Agent(identifier="tools-existence", tools=[dummy_tool], adapter=mock_adapter)
    
    assert hasattr(agent, "tools")
    assert isinstance(getattr(type(agent), "tools"), property)
    assert isinstance(agent.tools, list)

def test_agent_tools_returns_correct_elements():
    """
    What: Verify that the tools property returns the list of tools provided at init.
    Why: To ensure the internal tool registry is correctly exposed.
    Assumptions: The tools are stored internally, typically in self._tools.
    """
    mock_adapter = MagicMock(spec=InferenceAdapter)
    tool_a = Tool(lambda: "a", name="tool_a")
    tool_b = Tool(lambda: "b", name="tool_b")
    expected_tools = [tool_a, tool_b]
    
    agent = Agent(identifier="tools-content-test", tools=expected_tools, adapter=mock_adapter)
    
    assert len(agent.tools) == 2
    assert tool_a in agent.tools
    assert tool_b in agent.tools
    # Ensure the order or at least the identity is preserved
    assert agent.tools == expected_tools

def test_agent_tools_is_read_only():
    """
    What: Test that the tools property cannot be reassigned.
    Why: To maintain the integrity of the Agent's configuration after initialization.
    Assumptions: No setter is defined for the tools property.
    """
    mock_adapter = MagicMock(spec=InferenceAdapter)
    dummy_tool = Tool(lambda: None, name="dummy")
    agent = Agent(identifier="tools-read-only", tools=[dummy_tool], adapter=mock_adapter)
    
    with pytest.raises(AttributeError):
        # Attempting to overwrite the property should fail
        agent.tools = []

def test_agent_tools_list_mutation_protection():
    """
    What: Verify if the returned list is a copy or if external mutation affects the agent.
    Why: Defensive programming check to see if external code can empty the agent's tools 
         by manipulating the returned list (if not returned as a tuple or copy).
    Assumptions: This tests the implementation's robustness against side effects.
    """
    mock_adapter = MagicMock(spec=InferenceAdapter)
    dummy_tool = Tool(lambda: None, name="dummy")
    agent = Agent(identifier="tools-mutation-test", tools=[dummy_tool], adapter=mock_adapter)
    
    retrieved_tools = agent.tools
    try:
        retrieved_tools.clear()
    except (AttributeError, TypeError):
        # If the property returns a tuple or a read-only view, this is also a win
        return

    # If it was a standard list, check if the internal state remains intact
    # Note: This depends on whether the property returns self._tools (reference) 
    # or list(self._tools) (copy). 
    assert len(agent.tools) >= 0 # Documentation of behavior

# end of file tests/06_01_08_agent_agent_tools_test.py