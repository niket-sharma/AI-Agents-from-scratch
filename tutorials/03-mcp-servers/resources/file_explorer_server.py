"""
Tutorial 03-C: MCP Server with Resources
=========================================

This tutorial demonstrates MCP RESOURCES - data that AI can read.

Resources vs Tools:
-------------------
- TOOLS: AI can CALL them (like functions)
- RESOURCES: AI can READ them (like files, database records)

Resources are identified by URIs like:
- file:///path/to/file.txt
- db://database/table/id
- api://service/endpoint

This server exposes the local file system as resources.
"""

import asyncio
import os
import json
from pathlib import Path
from typing import Any
from mcp.server import Server
from mcp.types import Resource, TextContent, Tool
import mcp.server.stdio


class FileExplorerServer:
    """
    MCP server that exposes files and directories as resources.

    The AI can:
    1. List available resources (files)
    2. Read resource content
    3. Use tools to search and filter files
    """

    def __init__(self, root_dir: str = "."):
        self.server = Server("file-explorer-server")
        self.root_dir = Path(root_dir).resolve()
        self.setup_handlers()

    def setup_handlers(self):
        """Register resource and tool handlers."""

        # List available resources
        @self.server.list_resources()
        async def list_resources() -> list[Resource]:
            """
            List all files in the root directory as resources.

            Each file becomes a resource with a URI like:
            file:///path/to/file.txt
            """
            resources = []

            # List text files in the root directory
            for file_path in self.root_dir.glob("*.txt"):
                if file_path.is_file():
                    resources.append(Resource(
                        uri=f"file:///{file_path}",
                        name=file_path.name,
                        description=f"Text file: {file_path.name}",
                        mimeType="text/plain"
                    ))

            # List JSON files
            for file_path in self.root_dir.glob("*.json"):
                if file_path.is_file():
                    resources.append(Resource(
                        uri=f"file:///{file_path}",
                        name=file_path.name,
                        description=f"JSON file: {file_path.name}",
                        mimeType="application/json"
                    ))

            # List Python files
            for file_path in self.root_dir.glob("*.py"):
                if file_path.is_file():
                    resources.append(Resource(
                        uri=f"file:///{file_path}",
                        name=file_path.name,
                        description=f"Python file: {file_path.name}",
                        mimeType="text/x-python"
                    ))

            return resources

        # Read a specific resource
        @self.server.read_resource()
        async def read_resource(uri: str) -> str:
            """
            Read the content of a resource.

            The AI will call this when it wants to read a file.

            Args:
                uri: The resource URI (e.g., file:///path/to/file.txt)

            Returns:
                The file content
            """
            # Extract file path from URI
            if not uri.startswith("file:///"):
                raise ValueError(f"Unsupported URI scheme: {uri}")

            file_path = Path(uri.replace("file:///", ""))

            # Security check: ensure file is within root directory
            if not str(file_path).startswith(str(self.root_dir)):
                raise ValueError("Access denied: file outside root directory")

            if not file_path.exists():
                raise ValueError(f"File not found: {file_path}")

            # Read file content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            return content

        # Also provide tools for file operations
        @self.server.list_tools()
        async def list_tools() -> list[Tool]:
            """List available file operation tools."""
            return [
                Tool(
                    name="search_files",
                    description="Search for files by name pattern",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "pattern": {
                                "type": "string",
                                "description": "File name pattern (e.g., '*.txt', 'test*')"
                            }
                        },
                        "required": ["pattern"]
                    }
                ),
                Tool(
                    name="count_lines",
                    description="Count lines in a file",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "filename": {
                                "type": "string",
                                "description": "Name of the file"
                            }
                        },
                        "required": ["filename"]
                    }
                ),
                Tool(
                    name="get_file_info",
                    description="Get detailed information about a file",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "filename": {
                                "type": "string",
                                "description": "Name of the file"
                            }
                        },
                        "required": ["filename"]
                    }
                )
            ]

        @self.server.call_tool()
        async def call_tool(name: str, arguments: Any) -> list[TextContent]:
            """Execute file operation tools."""

            if name == "search_files":
                pattern = arguments["pattern"]
                matches = list(self.root_dir.glob(pattern))
                files = [str(f.name) for f in matches if f.is_file()]

                return [TextContent(
                    type="text",
                    text=json.dumps({
                        "pattern": pattern,
                        "matches": files,
                        "count": len(files)
                    }, indent=2)
                )]

            elif name == "count_lines":
                filename = arguments["filename"]
                file_path = self.root_dir / filename

                if not file_path.exists():
                    return [TextContent(
                        type="text",
                        text=f"File not found: {filename}"
                    )]

                with open(file_path, 'r', encoding='utf-8') as f:
                    line_count = sum(1 for _ in f)

                return [TextContent(
                    type="text",
                    text=f"File '{filename}' has {line_count} lines"
                )]

            elif name == "get_file_info":
                filename = arguments["filename"]
                file_path = self.root_dir / filename

                if not file_path.exists():
                    return [TextContent(
                        type="text",
                        text=f"File not found: {filename}"
                    )]

                stat = file_path.stat()
                info = {
                    "name": filename,
                    "size": f"{stat.st_size} bytes",
                    "size_kb": f"{stat.st_size / 1024:.2f} KB",
                    "modified": str(os.path.getmtime(file_path)),
                    "is_file": file_path.is_file(),
                    "extension": file_path.suffix
                }

                return [TextContent(
                    type="text",
                    text=json.dumps(info, indent=2)
                )]

            else:
                raise ValueError(f"Unknown tool: {name}")

    async def run(self):
        """Run the MCP server."""
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options()
            )


async def main():
    """Run the file explorer MCP server."""
    import sys

    # Allow specifying a directory via command line
    root_dir = sys.argv[1] if len(sys.argv) > 1 else "."

    print("="*60, file=sys.stderr)
    print("FILE EXPLORER MCP SERVER", file=sys.stderr)
    print("="*60, file=sys.stderr)
    print(f"\nRoot Directory: {Path(root_dir).resolve()}", file=sys.stderr)
    print("\nResources:", file=sys.stderr)
    print("  • Exposes .txt, .json, and .py files", file=sys.stderr)
    print("  • AI can list and read these files", file=sys.stderr)
    print("\nTools:", file=sys.stderr)
    print("  • search_files - Search by pattern", file=sys.stderr)
    print("  • count_lines - Count lines in a file", file=sys.stderr)
    print("  • get_file_info - Get file metadata", file=sys.stderr)
    print("\nServer running...", file=sys.stderr)
    print("="*60, file=sys.stderr)
    print("", file=sys.stderr)

    server = FileExplorerServer(root_dir)
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())
