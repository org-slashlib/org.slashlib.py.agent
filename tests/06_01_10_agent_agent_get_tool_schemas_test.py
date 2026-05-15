# -*- coding: utf-8 -*-
# file tests/06_01_10_agent_agent_get_tool_schemas_test.py
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
Method: get_tool_schemas

Special Considerations:
This method aggregates the schemas of all tools assigned to the agent. 
The test failure indicates the Agent calls 'get_schema()' on Tool objects.
The test must verify that the result list contains the return values of 
these method calls.
"""

import pytest
from unittest.mock import MagicMock
from org.slashlib.py.agent.agent import Agent
from org.slashlib.py.agent.inference_bases import InferenceAdapter
from org.slashlib.py.agent.tool import Tool

def test_existence_and_type():
    """
    What: Verify the integrity of the test object.
    Why: Mandatory first test.
    Assumptions: The Agent class implementation includes the 'get_tool_schemas' method.
    """
    mock_adapter = MagicMock(spec=InferenceAdapter)
    dummy_tool = Tool(lambda: None, name="dummy")
    agent = Agent(identifier="schemas-existence", tools=[dummy_tool], adapter=mock_adapter)
    
    assert hasattr(agent, "get_tool_schemas")
    assert callable(agent.get_tool_schemas)
    
    schemas = agent.get_tool_schemas()
    assert isinstance(schemas, list)

def test_get_tool_schemas_aggregation():
    """
    What: Verify that the method correctly aggregates schemas from multiple tools.
    Why: To ensure the agent correctly prepares the toolset for the InferenceAdapter.
    Assumptions: Tool objects have a 'get_schema()' method (confirmed by previous failure).
    """
    mock_adapter = MagicMock(spec=InferenceAdapter)
    
    # Create Mock Tools with specific schemas
    schema_1 = {"name": "tool_1", "parameters": {}}
    schema_2 = {"name": "tool_2", "parameters": {}}
    
    tool_1 = MagicMock(spec=Tool)
    tool_1.get_schema.return_value = schema_1
    
    tool_2 = MagicMock(spec=Tool)
    tool_2.get_schema.return_value = schema_2
    
    agent = Agent(identifier="schemas-aggregation-v2", tools=[tool_1, tool_2], adapter=mock_adapter)
    
    result = agent.get_tool_schemas()
    
    assert len(result) == 2
    assert schema_1 in result
    assert schema_2 in result
    assert result[0] == schema_1
    assert result[1] == schema_2
    
    # Verify the correct method was called
    tool_1.get_schema.assert_called_once()
    tool_2.get_schema.assert_called_once()

def test_get_tool_schemas_with_real_tool_objects():
    """
    What: Verify the method using actual Tool instances.
    Why: To ensure compatibility between Agent and Tool implementations.
    Assumptions: Tool.get_schema() exists and returns a dict.
    """
    def sample_function(param1: str):
        """A sample function."""
        return param1

    real_tool = Tool(sample_function, name="sample_tool")
    mock_adapter = MagicMock(spec=InferenceAdapter)
    
    agent = Agent(identifier="schemas-real-tools", tools=[real_tool], adapter=mock_adapter)
    
    result = agent.get_tool_schemas()
    
    assert len(result) == 1
    assert isinstance(result[0], dict)
    # Standard OpenAI/LLM schema structure
    assert result[0]["function"]["name"] == "sample_tool"

def test_get_tool_schemas_immutability():
    """
    What: Verify that modifying the returned list does not affect the agent.
    Why: Defensive programming.
    """
    mock_adapter = MagicMock(spec=InferenceAdapter)
    dummy_tool = Tool(lambda: None, name="dummy")
    agent = Agent(identifier="schemas-immutability", tools=[dummy_tool], adapter=mock_adapter)
    
    schemas = agent.get_tool_schemas()
    original_count = len(schemas)
    schemas.append({"malicious": "schema"})
    
    assert len(agent.get_tool_schemas()) == original_count

# end of file tests/06_01_10_agent_agent_get_tool_schemas_test.py