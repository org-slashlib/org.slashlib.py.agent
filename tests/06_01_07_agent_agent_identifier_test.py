# -*- coding: utf-8 -*-
# file tests/06_01_07_agent_agent_identifier_test.py
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
Method: identifier (property)

Special Considerations:
The identifier is a read-only property. It should return the value assigned 
during initialization. As the Agent follows a Multiton pattern, this 
identifier is the key used for instance management.
"""

import pytest
from unittest.mock import MagicMock
from org.slashlib.py.agent.agent import Agent
from org.slashlib.py.agent.inference_bases import InferenceAdapter
from org.slashlib.py.agent.tool import Tool

def test_existence_and_type():
    """
    What: Verify the integrity of the test object.
    Why: Mandatory first test to ensure the property is accessible and of correct type.
    Assumptions: The Agent class implementation includes an 'identifier' property.
    """
    mock_adapter = MagicMock(spec=InferenceAdapter)
    dummy_tool = Tool(lambda: None, name="dummy")
    agent = Agent(identifier="test-id", tools=[dummy_tool], adapter=mock_adapter)
    
    assert hasattr(agent, "identifier")
    # Verify it is a property (not a regular method)
    assert isinstance(getattr(type(agent), "identifier"), property)

def test_agent_identifier_returns_correct_value():
    """
    What: Verify that the identifier property returns the string provided at init.
    Why: To ensure the internal state is correctly exposed via the property.
    Assumptions: The internal attribute used is typically self._identifier.
    """
    expected_id = "agent-123"
    mock_adapter = MagicMock(spec=InferenceAdapter)
    dummy_tool = Tool(lambda: None, name="dummy")
    
    agent = Agent(identifier=expected_id, tools=[dummy_tool], adapter=mock_adapter)
    
    assert agent.identifier == expected_id
    assert isinstance(agent.identifier, str)

def test_agent_identifier_is_read_only():
    """
    What: Test that the identifier property cannot be overwritten.
    Why: To ensure the immutability of the Agent's identity after creation.
    Assumptions: No setter is defined for the identifier property.
    """
    mock_adapter = MagicMock(spec=InferenceAdapter)
    dummy_tool = Tool(lambda: None, name="dummy")
    agent = Agent(identifier="immutable-id", tools=[dummy_tool], adapter=mock_adapter)
    
    with pytest.raises(AttributeError):
        # This should fail as there should be no setter
        agent.identifier = "new-id"

def test_agent_identifier_consistency_across_multiton():
    """
    What: Verify identifier consistency when retrieving existing instances.
    Why: To ensure the Multiton pattern maintains the correct identifier state.
    Assumptions: Agent(id) returns the cached instance associated with that id.
    """
    shared_id = "shared-multiton-id"
    mock_adapter = MagicMock(spec=InferenceAdapter)
    dummy_tool = Tool(lambda: None, name="dummy")
    
    agent_1 = Agent(identifier=shared_id, tools=[dummy_tool], adapter=mock_adapter)
    agent_2 = Agent(identifier=shared_id, tools=[dummy_tool], adapter=mock_adapter)
    
    assert agent_1.identifier == shared_id
    assert agent_2.identifier == shared_id
    assert agent_1.identifier == agent_2.identifier

# end of file tests/06_01_07_agent_agent_identifier_test.py