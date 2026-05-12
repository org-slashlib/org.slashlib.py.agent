# -*- coding: utf-8 -*-
# file src/org/slashlib/py/agent/__main__.py
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
# pragma: no cover
#
"""
Entry point for the org.slashlib.py.agent package.
"""

# Import python packages
import argparse
import logging
import pathlib
import sys
from importlib import metadata

# Compatibility layer for TOML (Python 3.11+ uses tomllib, older use tomli)
if sys.version_info >= (3, 11):
    import tomllib
else:
    try:
        import tomli as tomllib
    except ImportError:
        tomllib = None

# Import thirdparty packages
import org.slashlib.py.configloader

# setup logging
org.slashlib.py.configloader.setup_logging()

log = logging.getLogger(f"org.slashlib.py.agent.{pathlib.Path(__file__).stem}")

def get_version() -> str:
    """
    Retrieve the version of the package from metadata or local pyproject.toml.
    """
    # 1. Try metadata (works if installed via pip)
    try:
        return metadata.version("org.slashlib.py.agent")
    except metadata.PackageNotFoundError:
        pass

    # 2. Fallback: Parse pyproject.toml directly (works during development)
    if tomllib is not None:
        try:
            # Search for pyproject.toml relative to this file's location
            # Path: src/org/slashlib/py/agent/__main__.py -> root is 4 levels up
            root_path = pathlib.Path(__file__).parents[5]
            toml_path = root_path / "pyproject.toml"
            
            if toml_path.exists():
                with open(toml_path, "rb") as f:
                    data = tomllib.load(f)
                    return data.get("project", {}).get("version", "unknown (local)")
        except Exception:
            pass

    return "unknown"

def start():
    """
    Bootstrap function to instantiate and run the bot.
    """
    parser = argparse.ArgumentParser(description="org.slashlib.py.agent CLI")
    parser.add_argument("--version", action="store_true", help="Show the package version and exit")
    
    args, unknown = parser.parse_known_args()

    if args.version:
        print(f"org.slashlib.py.agent version {get_version()}")
        sys.exit(0)
    else:
        parser.print_help()
 
if __name__ == "__main__":
    start()
    
# end of file src/org/slashlib/py/agent/__main__.py