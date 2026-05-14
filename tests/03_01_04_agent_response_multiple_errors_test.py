# -*- coding: utf-8 -*-
# file tests/03_01_04_agent_response_multiple_errors_test.py
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
import typing

# Third party imports
import pytest

# Internal imports
from org.slashlib.py.agent.agent_response import AgentResponse


def test_raise_multiple_errors_warning(caplog):
    """
    Targets the branch: if len(self._errors) > 1:
    Verifies that a warning is logged when multiple errors exist and 
    the first one is raised.
    """
    response = AgentResponse()
    
    error_one = ValueError("First Error")
    error_two = TypeError("Second Error")
    
    # Add two errors to trigger the 'len > 1' logic
    response.append_error(error_one)
    response.append_error(error_two)
    
    # Verify the warning and the raised exception
    with pytest.raises(ValueError, match="First Error"):
        # This call should trigger the logging.warning line
        response.raise_errors()
    
    # Check if the warning message appears in the logs
    assert "Multiple process errors (2) found" in caplog.text
    assert "Raising the first one" in caplog.text


# end of file tests/03_01_04_agent_response_multiple_errors_test.py