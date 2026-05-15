# -*- coding: utf-8 -*-
# file tests/06_01_05_agent_agent_init_test.py
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
Method: __init__

Special Considerations:
The __init__ method handles the core configuration of the Agent instance. 
It includes strict validation rules for input parameters (tools and adapter). 
Since this class follows a Multiton pattern, the __init__ method must also 
implement an initialization guard to prevent re-initialization of cached instances.
"""

import pytest
import logging
import pathlib
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

def test_agent_init_valid_parameters():
    """
    What: Test successful initialization with valid parameters.
    Why: To verify that all internal attributes are correctly assigned.
    Assumptions: Valid Tool and InferenceAdapter objects are provided.
    """
    mock_adapter = MagicMock(spec=InferenceAdapter)
    dummy_tool = Tool(lambda: "test", name="dummy_tool")
    identifier = "valid-init-test"
    
    # Using a unique ID to ensure a fresh instance for this specific test
    agent = Agent(identifier=identifier, tools=[dummy_tool], adapter=mock_adapter, multi=False)
    
    assert agent._identifier == identifier
    assert agent._multi is False
    # Verify logger naming convention matches the source code logic
    expected_log_name = f"org.slashlib.py.agent.{pathlib.Path(__file__).stem}.Agent"
    # Note: The logger name depends on the filename where Agent is defined. 
    # If the class logic uses __file__ of the agent.py, the stem will be 'agent'.
    assert "Agent" in agent.log.name

def test_agent_init_raises_value_error_empty_tools():
    """
    What: Test that __init__ raises ValueError when tools list is empty.
    Why: To verify input validation for the tools parameter as seen in the source logs.
    Assumptions: The class strictly enforces at least one tool.
    """
    mock_adapter = MagicMock(spec=InferenceAdapter)
    
    with pytest.raises(ValueError, match="The tools list must not be empty."):
        # We use a new identifier to bypass the Multiton cache and trigger __init__
        Agent(identifier="empty-tools-error", tools=[], adapter=mock_adapter)

def test_agent_init_raises_value_error_missing_adapter():
    """
    What: Test that __init__ raises ValueError when adapter is None.
    Why: Targets coverage for line 88 in agent.py. 
    Assumptions: Bypasses tools check by providing valid tools list.
    """
    dummy_tool = Tool(lambda: "test", name="valid_tool")
    
    with pytest.raises(ValueError, match="An InferenceAdapter is required."):
        # Provide valid tools but None for adapter to trigger line 88
        Agent(identifier="missing-adapter-error", tools=[dummy_tool], adapter=None)

def test_agent_init_initialization_guard():
    """
    What: Verify that the initialization guard prevents overwriting attributes.
    Why: In a Multiton pattern, Python calls __init__ every time Agent(id) is invoked. 
         The guard (self._initialized) must prevent resetting the state.
    Assumptions: The __init__ method sets self._initialized = True at the end.
    """
    mock_adapter = MagicMock(spec=InferenceAdapter)
    dummy_tool = Tool(lambda: "test", name="dummy_tool")
    identifier = "guard-test"
    
    # Initial setup
    agent = Agent(identifier=identifier, tools=[dummy_tool], adapter=mock_adapter)
    
    # Manually modify an attribute that would normally be set in __init__
    agent._multi = "custom-state"
    
    # Call constructor again with the same identifier
    # If the guard works, 'multi=True' (default) will not overwrite 'custom-state'
    agent_recalled = Agent(identifier=identifier, tools=[dummy_tool], adapter=mock_adapter, multi=True)
    
    assert agent_recalled._multi == "custom-state"
    assert agent_recalled is agent

# end of file tests/06_01_05_agent_agent_init_test.py