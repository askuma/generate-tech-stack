#!/usr/bin/env python3
"""
generate-tech-stack MCP Server
Universal — works with Claude Desktop, VS Code (Copilot via MCP), Cursor,
Zed, Windsurf, Continue, Antigravity, and any MCP-compatible host.

Install:
    pip install mcp

Run (stdio transport — used by most hosts):
    python3 ~/.claude/skills/generate-tech-stack/mcp/server.py

Add to your MCP host config (e.g. claude_desktop_config.json):
    {
      "mcpServers": {
        "generate-tech-stack": {
          "command": "python3",
          "args": ["/home/<you>/.claude/skills/generate-tech-stack/mcp/server.py"]
        }
      }
    }

Then ask: /generate-tech-stack  or  "generate my tech stack"
"""

import asyncio
import json
import os
import sys
from pathlib import Path

_HERE    = Path(__file__).parent
_SCRIPTS = _HERE.parent / "scripts"
sys.path.insert(0, str(_SCRIPTS))

try:
    import analyze as _analyze
except ImportError:
    _analyze = None

try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    import mcp.types as types
except ImportError:
    print("ERROR: mcp package not found. Run: pip install mcp", file=sys.stderr)
    sys.exit(1)


server = Server("generate-tech-stack")


@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="generate_tech_stack",
            description=(
                "Scan a project directory and generate a TECH_STACK.html visual page. "
                "Includes a stat row, layered architecture diagram, bar chart summary, "
                "and colour-coded tool cards. Detects languages, frameworks, databases, "
                "AI SDKs, testing, observability, security, and infrastructure tools."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "project_dir": {
                        "type": "string",
                        "description": "Absolute path to the project root. Defaults to cwd.",
                    },
                    "output_file": {
                        "type": "string",
                        "description": "Path for the output HTML. Defaults to <project_dir>/TECH_STACK.html.",
                    },
                    "open_browser": {
                        "type": "boolean",
                        "description": "Open the file in the default browser after creation.",
                        "default": True,
                    },
                },
                "required": [],
            },
        ),
        types.Tool(
            name="list_tech_stack",
            description=(
                "Scan a project and return the tech stack as structured JSON "
                "(no HTML file written). Good for programmatic use."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "project_dir": {
                        "type": "string",
                        "description": "Absolute path to the project root.",
                    },
                },
                "required": [],
            },
        ),
    ]


@server.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    project_dir = Path(arguments.get("project_dir") or os.getcwd()).resolve()

    if not project_dir.exists():
        return [types.TextContent(type="text", text=f"ERROR: Directory not found: {project_dir}")]

    if _analyze is None:
        return [types.TextContent(type="text",
            text="ERROR: analyze.py not found. Ensure ~/.claude/skills/generate-tech-stack/scripts/analyze.py exists.")]

    if name == "list_tech_stack":
        tools = _analyze.collect(project_dir)
        total = sum(len(v) for v in tools.values())
        result = {
            "project":     project_dir.name,
            "total_tools": total,
            "categories": {
                cat: [{"name": t["name"], "desc": t["desc"]} for t in items]
                for cat, items in tools.items()
            },
        }
        return [types.TextContent(type="text", text=json.dumps(result, indent=2))]

    if name == "generate_tech_stack":
        output_file = Path(
            arguments.get("output_file") or (project_dir / "TECH_STACK.html")
        ).resolve()

        tools = _analyze.collect(project_dir)
        if not tools:
            return [types.TextContent(type="text",
                text=f"No recognizable dependency files found in: {project_dir}")]

        project_name = project_dir.name.replace("-", " ").replace("_", " ").title()
        output_file.write_text(_analyze.render_html(tools, project_name))

        total = sum(len(v) for v in tools.values())
        lines = [
            f"Tech stack generated: {output_file}",
            f"Detected {total} tools across {len(tools)} categories:",
        ]
        for cat, items in tools.items():
            meta  = _analyze.CATEGORY_META.get(cat, _analyze.CATEGORY_META["other"])
            names = ", ".join(t["name"] for t in items)
            lines.append(f"  {meta['icon']} {meta['label']}: {names}")

        if arguments.get("open_browser", True):
            import subprocess
            for cmd in ["xdg-open", "open", "start"]:
                try:
                    subprocess.Popen([cmd, str(output_file)],
                                     stdout=subprocess.DEVNULL,
                                     stderr=subprocess.DEVNULL)
                    break
                except FileNotFoundError:
                    continue

        return [types.TextContent(type="text", text="\n".join(lines))]

    return [types.TextContent(type="text", text=f"Unknown tool: {name}")]


async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options(),
        )


if __name__ == "__main__":
    asyncio.run(main())
