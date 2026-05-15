# -*- coding: utf-8 -*-
# file tests/02_01_08_tool_Tool_get_schema_test.py

"""
Testsuite for the org.slashlib.py.agent.tool module.
Tested Class: Tool
Tested Method: get_schema

Special Considerations:
- Validates the nested structure required for LLM tool calling.
- Expected Format:
    {
      'type': 'function',
      'function': {
        'name': '...',
        'description': '...',
        'parameters': { ... }
      }
    }
"""

import pytest
import json
from org.slashlib.py.agent.tool import Tool

def test_01_tool_get_schema_structure_v4():
    """
    Test if get_schema returns the strict nested JSON structure required by modern LLMs.
    
    Expected JSON Output for this test:
    {
      "type": "function",
      "function": {
        "name": "get_weather",
        "description": "Get weather info",
        "parameters": {
          "type": "object",
          "properties": {
            "city": {
              "type": "string",
              "description": "Parameter city"
            }
          },
          "required": ["city"]
        }
      }
    }
    """
    def get_weather(city: str):
        """Get weather info"""
        pass

    tool_inst = Tool(get_weather)
    schema = tool_inst.get_schema()

    # Integrity Check for the root structure
    assert schema["type"] == "function"
    assert "function" in schema
    
    # Inner Function Check
    func_part = schema["function"]
    assert func_part["name"] == "get_weather"
    assert func_part["description"] == "Get weather info"
    assert "parameters" in func_part
    assert "city" in func_part["parameters"]["properties"]
    assert "city" in func_part["parameters"]["required"]

def test_02_tool_get_schema_with_defaults():
    """
    Test schema with optional parameters and defaults.
    
    Expected JSON Output:
    {
      "type": "function",
      "function": {
        "name": "config_tool",
        "description": "Configure system",
        "parameters": {
          "type": "object",
          "properties": {
            "retries": {
              "type": "integer",
              "description": "Parameter retries (defaults to 3)",
              "default": 3
            }
          },
          "required": []
        }
      }
    }
    """
    def config_tool(retries: int = 3):
        """Configure system"""
        pass

    tool_inst = Tool(config_tool)
    schema = tool_inst.get_schema()

    properties = schema["function"]["parameters"]["properties"]
    assert properties["retries"]["default"] == 3
    assert "retries" not in schema["function"]["parameters"]["required"]

def test_03_tool_get_schema_no_params():
    """
    Test schema for a function without any parameters.
    
    Expected JSON Output:
    {
      "type": "function",
      "function": {
        "name": "ping",
        "description": "Health check",
        "parameters": {
          "type": "object",
          "properties": {},
          "required": []
        }
      }
    }
    """
    def ping():
        """Health check"""
        pass

    tool_inst = Tool(ping)
    schema = tool_inst.get_schema()

    assert schema["function"]["parameters"]["properties"] == {}
    assert schema["function"]["parameters"]["required"] == []
