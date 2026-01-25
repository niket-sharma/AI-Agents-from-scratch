"""
Practical MCP Server: Notes Database
=====================================

This is a practical MCP server that provides a notes database.
Unlike the simple calculator example, this shows real-world patterns:
- SQLite database persistence
- CRUD operations as tools
- Resources for data access
- Error handling

Use Case:
---------
Give an AI assistant the ability to save, search, and manage notes.
"Save this code snippet", "Find my notes about Python", "Delete old notes"
"""

import asyncio
import json
import sqlite3
import os
from datetime import datetime
from typing import Any
from mcp.server import Server
from mcp.types import Tool, TextContent, Resource
import mcp.server.stdio


class NotesServer:
    """
    MCP Server that provides a notes database.

    This demonstrates real-world MCP patterns:
    - Database integration
    - Multiple related tools
    - Resources for data browsing
    - Proper error handling
    """

    def __init__(self, db_path: str = "notes.db"):
        self.db_path = db_path
        self.server = Server("notes-database-server")
        self._init_database()
        self._setup_handlers()

    def _init_database(self):
        """Initialize SQLite database with notes table."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                tags TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        conn.close()

    def _get_connection(self):
        """Get database connection."""
        return sqlite3.connect(self.db_path)

    def _setup_handlers(self):
        """Setup all MCP handlers."""

        # ========== TOOLS ==========

        @self.server.list_tools()
        async def list_tools() -> list[Tool]:
            """Define all available tools for the AI."""
            return [
                # Create a new note
                Tool(
                    name="create_note",
                    description="Create a new note with a title and content. Optionally add comma-separated tags.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "title": {
                                "type": "string",
                                "description": "Title of the note"
                            },
                            "content": {
                                "type": "string",
                                "description": "Content/body of the note"
                            },
                            "tags": {
                                "type": "string",
                                "description": "Comma-separated tags (optional)"
                            }
                        },
                        "required": ["title", "content"]
                    }
                ),

                # Search notes
                Tool(
                    name="search_notes",
                    description="Search notes by keyword in title, content, or tags",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Search query"
                            },
                            "limit": {
                                "type": "integer",
                                "description": "Maximum results to return (default: 10)"
                            }
                        },
                        "required": ["query"]
                    }
                ),

                # Get a specific note
                Tool(
                    name="get_note",
                    description="Get a specific note by its ID",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "note_id": {
                                "type": "integer",
                                "description": "ID of the note to retrieve"
                            }
                        },
                        "required": ["note_id"]
                    }
                ),

                # Update a note
                Tool(
                    name="update_note",
                    description="Update an existing note's title, content, or tags",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "note_id": {
                                "type": "integer",
                                "description": "ID of the note to update"
                            },
                            "title": {
                                "type": "string",
                                "description": "New title (optional)"
                            },
                            "content": {
                                "type": "string",
                                "description": "New content (optional)"
                            },
                            "tags": {
                                "type": "string",
                                "description": "New tags (optional)"
                            }
                        },
                        "required": ["note_id"]
                    }
                ),

                # Delete a note
                Tool(
                    name="delete_note",
                    description="Delete a note by its ID",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "note_id": {
                                "type": "integer",
                                "description": "ID of the note to delete"
                            }
                        },
                        "required": ["note_id"]
                    }
                ),

                # List all notes
                Tool(
                    name="list_notes",
                    description="List all notes with optional limit and tag filter",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "limit": {
                                "type": "integer",
                                "description": "Maximum notes to return (default: 20)"
                            },
                            "tag": {
                                "type": "string",
                                "description": "Filter by tag (optional)"
                            }
                        }
                    }
                ),

                # Get statistics
                Tool(
                    name="get_stats",
                    description="Get statistics about the notes database",
                    inputSchema={
                        "type": "object",
                        "properties": {}
                    }
                )
            ]

        @self.server.call_tool()
        async def call_tool(name: str, arguments: Any) -> list[TextContent]:
            """Handle tool calls from the AI."""

            try:
                if name == "create_note":
                    return await self._create_note(arguments)
                elif name == "search_notes":
                    return await self._search_notes(arguments)
                elif name == "get_note":
                    return await self._get_note(arguments)
                elif name == "update_note":
                    return await self._update_note(arguments)
                elif name == "delete_note":
                    return await self._delete_note(arguments)
                elif name == "list_notes":
                    return await self._list_notes(arguments)
                elif name == "get_stats":
                    return await self._get_stats(arguments)
                else:
                    return [TextContent(type="text", text=f"Unknown tool: {name}")]
            except Exception as e:
                return [TextContent(type="text", text=f"Error: {str(e)}")]

        # ========== RESOURCES ==========

        @self.server.list_resources()
        async def list_resources() -> list[Resource]:
            """List available resources (notes as resources)."""
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT id, title FROM notes ORDER BY updated_at DESC LIMIT 50")
            notes = cursor.fetchall()
            conn.close()

            resources = [
                Resource(
                    uri=f"notes://db/note/{note[0]}",
                    name=note[1],
                    mimeType="text/plain",
                    description=f"Note #{note[0]}: {note[1]}"
                )
                for note in notes
            ]

            # Add a summary resource
            resources.insert(0, Resource(
                uri="notes://db/summary",
                name="Notes Summary",
                mimeType="application/json",
                description="Summary of all notes in the database"
            ))

            return resources

        @self.server.read_resource()
        async def read_resource(uri: str) -> str:
            """Read a resource by URI."""
            if uri == "notes://db/summary":
                return await self._get_summary()
            elif uri.startswith("notes://db/note/"):
                note_id = int(uri.split("/")[-1])
                return await self._read_note_resource(note_id)
            else:
                return f"Unknown resource: {uri}"

    # ========== TOOL IMPLEMENTATIONS ==========

    async def _create_note(self, args: dict) -> list[TextContent]:
        """Create a new note."""
        title = args.get("title")
        content = args.get("content")
        tags = args.get("tags", "")

        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO notes (title, content, tags) VALUES (?, ?, ?)",
            (title, content, tags)
        )
        note_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return [TextContent(
            type="text",
            text=f"Created note #{note_id}: '{title}'"
        )]

    async def _search_notes(self, args: dict) -> list[TextContent]:
        """Search notes by keyword."""
        query = args.get("query")
        limit = args.get("limit", 10)

        conn = self._get_connection()
        cursor = conn.cursor()
        search_term = f"%{query}%"
        cursor.execute("""
            SELECT id, title, content, tags, created_at
            FROM notes
            WHERE title LIKE ? OR content LIKE ? OR tags LIKE ?
            ORDER BY updated_at DESC
            LIMIT ?
        """, (search_term, search_term, search_term, limit))

        notes = cursor.fetchall()
        conn.close()

        if not notes:
            return [TextContent(type="text", text=f"No notes found matching '{query}'")]

        results = []
        for note in notes:
            results.append(f"#{note[0]}: {note[1]}")
            results.append(f"   Tags: {note[3] or 'none'}")
            results.append(f"   Preview: {note[2][:100]}...")
            results.append("")

        return [TextContent(
            type="text",
            text=f"Found {len(notes)} notes:\n\n" + "\n".join(results)
        )]

    async def _get_note(self, args: dict) -> list[TextContent]:
        """Get a specific note."""
        note_id = args.get("note_id")

        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, title, content, tags, created_at, updated_at FROM notes WHERE id = ?",
            (note_id,)
        )
        note = cursor.fetchone()
        conn.close()

        if not note:
            return [TextContent(type="text", text=f"Note #{note_id} not found")]

        return [TextContent(
            type="text",
            text=f"""Note #{note[0]}
Title: {note[1]}
Tags: {note[3] or 'none'}
Created: {note[4]}
Updated: {note[5]}

Content:
{note[2]}"""
        )]

    async def _update_note(self, args: dict) -> list[TextContent]:
        """Update an existing note."""
        note_id = args.get("note_id")

        conn = self._get_connection()
        cursor = conn.cursor()

        # Check if note exists
        cursor.execute("SELECT id FROM notes WHERE id = ?", (note_id,))
        if not cursor.fetchone():
            conn.close()
            return [TextContent(type="text", text=f"Note #{note_id} not found")]

        # Build update query
        updates = []
        values = []
        if "title" in args:
            updates.append("title = ?")
            values.append(args["title"])
        if "content" in args:
            updates.append("content = ?")
            values.append(args["content"])
        if "tags" in args:
            updates.append("tags = ?")
            values.append(args["tags"])

        if not updates:
            conn.close()
            return [TextContent(type="text", text="No updates provided")]

        updates.append("updated_at = CURRENT_TIMESTAMP")
        values.append(note_id)

        cursor.execute(
            f"UPDATE notes SET {', '.join(updates)} WHERE id = ?",
            values
        )
        conn.commit()
        conn.close()

        return [TextContent(type="text", text=f"Updated note #{note_id}")]

    async def _delete_note(self, args: dict) -> list[TextContent]:
        """Delete a note."""
        note_id = args.get("note_id")

        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM notes WHERE id = ?", (note_id,))
        deleted = cursor.rowcount
        conn.commit()
        conn.close()

        if deleted:
            return [TextContent(type="text", text=f"Deleted note #{note_id}")]
        else:
            return [TextContent(type="text", text=f"Note #{note_id} not found")]

    async def _list_notes(self, args: dict) -> list[TextContent]:
        """List all notes."""
        limit = args.get("limit", 20)
        tag_filter = args.get("tag")

        conn = self._get_connection()
        cursor = conn.cursor()

        if tag_filter:
            cursor.execute("""
                SELECT id, title, tags, created_at
                FROM notes
                WHERE tags LIKE ?
                ORDER BY updated_at DESC
                LIMIT ?
            """, (f"%{tag_filter}%", limit))
        else:
            cursor.execute("""
                SELECT id, title, tags, created_at
                FROM notes
                ORDER BY updated_at DESC
                LIMIT ?
            """, (limit,))

        notes = cursor.fetchall()
        conn.close()

        if not notes:
            return [TextContent(type="text", text="No notes found")]

        lines = [f"Found {len(notes)} notes:\n"]
        for note in notes:
            tags = f" [{note[2]}]" if note[2] else ""
            lines.append(f"  #{note[0]}: {note[1]}{tags}")

        return [TextContent(type="text", text="\n".join(lines))]

    async def _get_stats(self, args: dict) -> list[TextContent]:
        """Get database statistics."""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM notes")
        total = cursor.fetchone()[0]

        cursor.execute("""
            SELECT tags FROM notes WHERE tags IS NOT NULL AND tags != ''
        """)
        all_tags = []
        for row in cursor.fetchall():
            all_tags.extend([t.strip() for t in row[0].split(",")])

        from collections import Counter
        tag_counts = Counter(all_tags)

        cursor.execute("""
            SELECT date(created_at) as day, COUNT(*)
            FROM notes
            GROUP BY day
            ORDER BY day DESC
            LIMIT 7
        """)
        recent = cursor.fetchall()

        conn.close()

        stats = f"""Notes Database Statistics:
- Total notes: {total}
- Unique tags: {len(set(all_tags))}
- Top tags: {', '.join(f'{t}({c})' for t, c in tag_counts.most_common(5))}

Recent activity:
"""
        for day, count in recent:
            stats += f"  {day}: {count} notes\n"

        return [TextContent(type="text", text=stats)]

    # ========== RESOURCE IMPLEMENTATIONS ==========

    async def _get_summary(self) -> str:
        """Get notes summary as JSON."""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM notes")
        total = cursor.fetchone()[0]

        cursor.execute("SELECT id, title, tags FROM notes ORDER BY updated_at DESC LIMIT 10")
        recent = cursor.fetchall()

        conn.close()

        return json.dumps({
            "total_notes": total,
            "recent_notes": [
                {"id": n[0], "title": n[1], "tags": n[2]}
                for n in recent
            ]
        }, indent=2)

    async def _read_note_resource(self, note_id: int) -> str:
        """Read a note as a resource."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT title, content, tags FROM notes WHERE id = ?",
            (note_id,)
        )
        note = cursor.fetchone()
        conn.close()

        if not note:
            return f"Note #{note_id} not found"

        return f"""# {note[0]}

Tags: {note[2] or 'none'}

{note[1]}"""

    async def run(self):
        """Run the MCP server."""
        import sys
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            print("Notes MCP Server started!", file=sys.stderr)
            print(f"Database: {self.db_path}", file=sys.stderr)
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options()
            )


async def main():
    """Main entry point."""
    import sys

    # Allow custom database path
    db_path = sys.argv[1] if len(sys.argv) > 1 else "notes.db"

    print("=" * 60, file=sys.stderr)
    print("NOTES MCP SERVER", file=sys.stderr)
    print("=" * 60, file=sys.stderr)
    print(f"\nDatabase: {db_path}", file=sys.stderr)
    print("\nAvailable tools:", file=sys.stderr)
    print("  - create_note: Create a new note", file=sys.stderr)
    print("  - search_notes: Search by keyword", file=sys.stderr)
    print("  - get_note: Get note by ID", file=sys.stderr)
    print("  - update_note: Update a note", file=sys.stderr)
    print("  - delete_note: Delete a note", file=sys.stderr)
    print("  - list_notes: List all notes", file=sys.stderr)
    print("  - get_stats: Get database stats", file=sys.stderr)
    print("=" * 60, file=sys.stderr)

    server = NotesServer(db_path)
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())
