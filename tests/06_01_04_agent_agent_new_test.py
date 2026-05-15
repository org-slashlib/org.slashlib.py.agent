# -*- coding: utf-8 -*-
# file tests/06_01_04_agent_agent_new_test.py
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
Method: __new__

Special Considerations:
The Agent class implements a Multiton pattern (or a scoped Singleton). 
The __new__ method is responsible for managing instance caching based on 
the 'identifier' parameter. This Testsuite focuses on ensuring that 
identical identifiers return the exact same object instance.
"""

import pytest
from unittest.mock import MagicMock
from org.slashlib.py.agent.agent import Agent
from org.slashlib.py.agent.inference_bases import InferenceAdapter
from org.slashlib.py.agent.tool import Tool

def test_existence_and_type():
    """
    What: Verify the integrity of the test object.
    Why: Mandatory first test to ensure the class is importable and correctly defined.
    Assumptions: The project structure is correctly set in the PYTHONPATH.
    """
    assert Agent is not None
    assert callable(Agent)

def test_agent_new_multiton_identity():
    """
    What: Test the identity of instances created with the same identifier.
    Why: To verify the Multiton pattern implementation in __new__.
    Assumptions: The Agent class uses an internal registry (e.g., a class attribute) 
                 to store instances.
    """
    mock_adapter = MagicMock(spec=InferenceAdapter)
    dummy_tool = Tool(lambda: None, name="dummy")
    
    unique_id = "multiton-identity-check"
    
    # Create two instances with the same ID
    agent_instance_1 = Agent(identifier=unique_id, tools=[dummy_tool], adapter=mock_adapter)
    agent_instance_2 = Agent(identifier=unique_id, tools=[dummy_tool], adapter=mock_adapter)
    
    # Assert they are the exact same object in memory
    assert agent_instance_1 is agent_instance_2
    assert id(agent_instance_1) == id(agent_instance_2)

def test_agent_new_different_identifiers():
    """
    What: Test that different identifiers result in different instances.
    Why: To ensure the Multiton pattern does not incorrectly share instances 
         across different identifiers.
    Assumptions: Identifiers are treated as unique keys for instance lookups.
    """
    mock_adapter = MagicMock(spec=InferenceAdapter)
    dummy_tool = Tool(lambda: None, name="dummy")
    
    agent_alpha = Agent(identifier="alpha", tools=[dummy_tool], adapter=mock_adapter)
    agent_beta = Agent(identifier="beta", tools=[dummy_tool], adapter=mock_adapter)
    
    # Assert they are different objects
    assert agent_alpha is not agent_beta
    assert agent_alpha.identifier != agent_beta.identifier

def test_agent_initialization_guard_integrity():
    """
    What: Verify that __init__ logic is not re-executed in a way that overrides 
          existing state when an instance is retrieved via __new__.
    Why: When __new__ returns an existing instance, Python still calls __init__. 
         We need to ensure the class handles this gracefully (Initialization Guard).
    Assumptions: The Agent class sets an internal flag (e.g., _initialized) 
                 during the first run.
    """
    mock_adapter = MagicMock(spec=InferenceAdapter)
    dummy_tool = Tool(lambda: None, name="dummy")
    
    identifier = "init-guard-test"
    
    # First instantiation
    agent = Agent(identifier=identifier, tools=[dummy_tool], adapter=mock_adapter)
    
    # Inject a custom attribute to simulate state
    agent.canary_attribute = "alive"
    
    # Retrieve the same agent again
    agent_recalled = Agent(identifier=identifier, tools=[dummy_tool], adapter=mock_adapter)
    
    # Verify the state (canary) is still present and not wiped by a second __init__
    assert hasattr(agent_recalled, "canary_attribute")
    assert agent_recalled.canary_attribute == "alive"

# end of file tests/06_01_04_agent_agent_new_test.py