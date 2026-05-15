# -*- coding: utf-8 -*-
# file tests/02_01_09_tool_Tool___call___test.py

"""
Testsuite for the org.slashlib.py.agent.tool module.
Tested Class: Tool
Tested Method: __call__

Special Considerations:
- Focuses on deep recursive serialization.
- Verifies that None at top-level becomes "" but nested None becomes null.
- Tests bytes, datetime, and other types hidden deep inside structures.
"""

import datetime
import decimal
import json
import logging
import pathlib
import pytest
import typing
import uuid

from org.slashlib.py.agent.tool import Tool

@pytest.mark.asyncio
async def test_01_tool_call_none_top_level():
    """
    Test that a standalone None return value becomes an empty string.
    """
    tool_inst = Tool(lambda: None)
    result = await tool_inst()
    assert result == ""

@pytest.mark.asyncio
async def test_02_tool_call_none_nested():
    """
    Test that None inside a dictionary becomes JSON 'null'.
    """
    tool_inst = Tool(lambda: {"key": None})
    result = await tool_inst()
    assert result == '{"key": null}'

@pytest.mark.asyncio
async def test_03_tool_call_recursive_hell():
    """
    The 'Hell Test': Mixed types deep inside nested structures.
    Tests: bytes, datetime, set, decimal.Decimal, and UUID all at once.
    """
    ts = datetime.datetime(2026, 5, 15, 10, 0, 0)
    u = uuid.UUID("796d00c3-c8c6-41c8-bc85-6dd766a5f7ff")
    
    def hell_func():
        return {
            "a": [b"binary", {"set_inside": {1, 2}}],
            "b": {
                "time": ts,
                "meta": [u, decimal.Decimal("10.5"), pathlib.Path("/tmp")]
            },
            "c": None
        }

    tool_inst = Tool(hell_func)
    result = await tool_inst()
    
    parsed = json.loads(result)
    
    # Check recursive decoding/conversion
    assert parsed["a"][0] == "binary"
    assert set(parsed["a"][1]["set_inside"]) == {1, 2}
    assert parsed["b"]["time"] == ts.isoformat()
    assert parsed["b"]["meta"][0] == str(u)
    assert parsed["b"]["meta"][1] == "10.5"
    assert parsed["b"]["meta"][2] == str(pathlib.Path("/tmp").as_posix())
    assert parsed["c"] is None  # Nested None should be JSON null

@pytest.mark.asyncio
async def test_04_tool_call_standalone_special_types():
    """
    Test that standalone special types don't have extra JSON quotes.
    """
    ts = datetime.datetime(2026, 5, 15)
    test_path = pathlib.Path("/bin/sh")

    t1 = Tool(lambda: ts)
    t2 = Tool(lambda: b"raw")
    t3 = Tool(lambda: test_path)

    assert await t1() == ts.isoformat()
    assert await t2() == "raw"
    # Hier prüfen wir gegen as_posix(), da unser Tool das jetzt auch liefert
    assert await t3() == test_path.as_posix()

@pytest.mark.asyncio
async def test_05_tool_call_bytes_nested_error_handling():
    """
    Test that invalid bytes within a structure are handled gracefully.
    """
    def bad_bytes():
        return {"data": b"\xff\xfe\xfd"} # Invalid UTF-8

    tool_inst = Tool(bad_bytes)
    result = await tool_inst()
    parsed = json.loads(result)
    # Encoder should use 'replace' for errors
    assert isinstance(parsed["data"], str)

@pytest.mark.asyncio
async def test_06_tool_call_sync_vs_async_integrity():
    """
    Verify both sync and async functions return strings.
    """
    async def a_func(): return 1
    def s_func(): return 2

    assert await Tool(a_func)() == "1"
    assert await Tool(s_func)() == "2"

@pytest.mark.asyncio
async def test_07_tool_call_encoder_fallback_custom_object():
    """
    Test the fallback mechanism of ToolEncoder.
    Why: Triggers the 'except TypeError' branch in ToolEncoder.default 
    by providing an object that the standard JSONEncoder cannot handle.
    """
    class UnserializableObject:
        def __str__(self):
            return "CustomObjectString"

    obj = UnserializableObject()
    
    # Test nested (to trigger ToolEncoder.default)
    tool_nested = Tool(lambda: {"data": obj})
    result_nested = await tool_nested()
    assert result_nested == '{"data": "CustomObjectString"}'

    # Test standalone (to ensure it also uses the fallback)
    tool_standalone = Tool(lambda: obj)
    result_standalone = await tool_standalone()
    assert result_standalone == "CustomObjectString"

@pytest.mark.asyncio
async def test_08_tool_map_type_unknown_annotation():
    """
    Test _map_type with an unknown annotation to trigger the 'string' fallback.
    """
    class UnknownType:
        pass

    def func(x: UnknownType):
        return x

    tool_inst = Tool(func)
    schema = tool_inst.get_schema()
    # Should fallback to "string" for UnknownType
    assert schema["function"]["parameters"]["properties"]["x"]["type"] == "string"

@pytest.mark.asyncio
async def test_09_tool_call_json_container_reaches_final_return():
    """
    Triggers the 'return res_json' branch.
    By passing a dict, res_json starts with '{', so the quote-stripping is skipped.
    """
    tool_inst = Tool(lambda: {"status": "ok"})
    result = await tool_inst()
    assert result == '{"status": "ok"}'

@pytest.mark.asyncio
async def test_10_tool_call_exception_logging(caplog):
    """
    Triggers the 'except Exception' branch and verifies logging.
    """
    def broken_func():
        raise RuntimeError("Tool failure")

    tool_inst = Tool(broken_func)
    
    with caplog.at_level(logging.ERROR):
        with pytest.raises(RuntimeError, match="Tool failure"):
            await tool_inst()
            
    assert "Error executing tool 'broken_func'" in caplog.text

@pytest.mark.asyncio
async def test_11_tool_map_type_fallback():
    """
    Triggers the 'string' fallback in _map_type for unknown annotations.
    """
    def unknown_type_func(arg: typing.Any):
        return arg

    tool_inst = Tool(unknown_type_func)
    schema = tool_inst.get_schema()
    # Check if 'Any' (unmapped) defaults to 'string'
    assert schema["function"]["parameters"]["properties"]["arg"]["type"] == "string"
