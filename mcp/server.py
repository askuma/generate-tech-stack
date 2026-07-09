#!/usr/bin/env python3
"""Compatibility shim — the MCP server lives in generate_tech_stack_mcp/server.py.

Kept so existing MCP host configs pointing at this path keep working.
Preferred install:  pip install generate-tech-stack-mcp   (command: generate-tech-stack-mcp)
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from generate_tech_stack_mcp.server import main

if __name__ == "__main__":
    main()
