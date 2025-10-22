"""
Tutorial 03-D: MCP Client - Using MCP Servers
==============================================

This tutorial shows how to build a CLIENT that consumes MCP servers.

Most of the time, your AI assistant (like Claude Desktop) is the client.
But sometimes you want to build your own client to:
- Test your MCP servers
- Build custom integrations
- Understand how MCP works under the hood

This client can connect to any MCP server and use its tools.
"""

import asyncio
import json
from typing import Optional
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


class MCPClient:
    """
    A simple MCP client that can connect to MCP servers.

    This demonstrates how AI assistants interact with MCP servers.
    """

    def __init__(self):
        self.session: Optional[ClientSession] = None
        self.tools = []
        self.resources = []

    async def connect_to_server(self, server_script_path: str):
        """
        Connect to an MCP server.

        Args:
            server_script_path: Path to the server Python script
        """
        # Configure server parameters
        server_params = StdioServerParameters(
            command="python",  # Command to run
            args=[server_script_path],  # Script to execute
            env=None  # Environment variables (optional)
        )

        print(f"🔌 Connecting to MCP server: {server_script_path}")

        # Create stdio transport and connect
        stdio_transport = await stdio_client(server_params)
        self.read_stream, self.write_stream = stdio_transport

        # Create client session
        self.session = ClientSession(self.read_stream, self.write_stream)

        # Initialize the session
        await self.session.initialize()

        print("✅ Connected to MCP server!")

        # List available tools
        await self.list_available_tools()

        # List available resources
        await self.list_available_resources()

    async def list_available_tools(self):
        """Fetch and display available tools from the server."""
        if not self.session:
            print("❌ Not connected to server")
            return

        print("\n📋 Fetching available tools...")

        # List tools
        tools_result = await self.session.list_tools()
        self.tools = tools_result.tools

        if not self.tools:
            print("   No tools available")
            return

        print(f"   Found {len(self.tools)} tools:\n")

        for i, tool in enumerate(self.tools, 1):
            print(f"   {i}. {tool.name}")
            print(f"      Description: {tool.description}")
            if hasattr(tool, 'inputSchema'):
                params = tool.inputSchema.get('properties', {})
                if params:
                    print(f"      Parameters: {', '.join(params.keys())}")
            print()

    async def list_available_resources(self):
        """Fetch and display available resources from the server."""
        if not self.session:
            print("❌ Not connected to server")
            return

        print("📚 Fetching available resources...")

        try:
            # List resources
            resources_result = await self.session.list_resources()
            self.resources = resources_result.resources

            if not self.resources:
                print("   No resources available\n")
                return

            print(f"   Found {len(self.resources)} resources:\n")

            for i, resource in enumerate(self.resources[:5], 1):  # Show first 5
                print(f"   {i}. {resource.name}")
                print(f"      URI: {resource.uri}")
                print(f"      Type: {resource.mimeType}")
                print()

            if len(self.resources) > 5:
                print(f"   ... and {len(self.resources) - 5} more resources\n")

        except Exception as e:
            print(f"   (Resources not supported by this server)\n")

    async def call_tool(self, tool_name: str, arguments: dict):
        """
        Call a tool on the MCP server.

        Args:
            tool_name: Name of the tool to call
            arguments: Dictionary of arguments for the tool
        """
        if not self.session:
            print("❌ Not connected to server")
            return

        print(f"\n🛠️  Calling tool: {tool_name}")
        print(f"    Arguments: {json.dumps(arguments, indent=6)}")

        try:
            # Call the tool
            result = await self.session.call_tool(tool_name, arguments)

            print(f"\n✅ Tool Response:")
            print("-" * 60)

            # Display the result
            for content in result.content:
                if content.type == "text":
                    print(content.text)

            print("-" * 60)

        except Exception as e:
            print(f"\n❌ Error calling tool: {e}")

    async def read_resource(self, resource_uri: str):
        """
        Read a resource from the MCP server.

        Args:
            resource_uri: URI of the resource to read
        """
        if not self.session:
            print("❌ Not connected to server")
            return

        print(f"\n📖 Reading resource: {resource_uri}")

        try:
            # Read the resource
            result = await self.session.read_resource(resource_uri)

            print(f"\n✅ Resource Content:")
            print("-" * 60)
            print(result.contents)
            print("-" * 60)

        except Exception as e:
            print(f"\n❌ Error reading resource: {e}")

    async def disconnect(self):
        """Disconnect from the server."""
        if self.session:
            print("\n👋 Disconnecting from server...")
            await self.session.close()
            self.session = None


async def demo_calculator_server():
    """Demo: Connect to the calculator server and use it."""
    print("="*70)
    print(" DEMO: Calculator MCP Server ".center(70, "="))
    print("="*70)

    client = MCPClient()

    # Connect to the simple calculator server
    server_path = "tutorials/03-mcp-servers/basic/simple_mcp_server.py"
    await client.connect_to_server(server_path)

    # Use the calculator tools
    print("\n" + "="*70)
    print(" Testing Calculator Tools ".center(70, "="))
    print("="*70)

    # Test 1: Addition
    await client.call_tool("add", {"a": 10, "b": 5})

    await asyncio.sleep(1)

    # Test 2: Multiplication
    await client.call_tool("multiply", {"a": 7, "b": 8})

    await asyncio.sleep(1)

    # Test 3: Power
    await client.call_tool("power", {"base": 2, "exponent": 10})

    await client.disconnect()


async def demo_weather_server():
    """Demo: Connect to the weather server and use it."""
    print("\n\n" + "="*70)
    print(" DEMO: Weather MCP Server ".center(70, "="))
    print("="*70)

    client = MCPClient()

    # Connect to the weather server
    server_path = "tutorials/03-mcp-servers/tools/weather_mcp_server.py"
    await client.connect_to_server(server_path)

    # Use the weather tools
    print("\n" + "="*70)
    print(" Testing Weather Tools ".center(70, "="))
    print("="*70)

    # Test 1: Get current weather
    await client.call_tool("get_current_weather", {
        "city": "New York",
        "units": "fahrenheit"
    })

    await asyncio.sleep(1)

    # Test 2: Compare weather
    await client.call_tool("compare_weather", {
        "city1": "New York",
        "city2": "London"
    })

    await asyncio.sleep(1)

    # Test 3: Get forecast
    await client.call_tool("get_forecast", {
        "city": "Tokyo",
        "days": 3
    })

    await client.disconnect()


async def demo_file_server():
    """Demo: Connect to the file explorer server."""
    print("\n\n" + "="*70)
    print(" DEMO: File Explorer MCP Server ".center(70, "="))
    print("="*70)

    client = MCPClient()

    # Connect to the file explorer server
    server_path = "tutorials/03-mcp-servers/resources/file_explorer_server.py"
    await client.connect_to_server(server_path)

    # Use the file tools
    print("\n" + "="*70)
    print(" Testing File Tools ".center(70, "="))
    print("="*70)

    # Test 1: Search for Python files
    await client.call_tool("search_files", {"pattern": "*.py"})

    await asyncio.sleep(1)

    # Test 2: Get file info
    await client.call_tool("get_file_info", {"filename": "requirements.txt"})

    # Test 3: Read a resource (if available)
    if client.resources:
        print("\n" + "="*70)
        print(" Reading a Resource ".center(70, "="))
        print("="*70)
        first_resource = client.resources[0]
        await client.read_resource(first_resource.uri)

    await client.disconnect()


async def interactive_mode():
    """Interactive mode for testing any MCP server."""
    print("="*70)
    print(" MCP CLIENT - Interactive Mode ".center(70, "="))
    print("="*70)

    print("\nChoose a server to connect to:\n")
    print("1. Calculator Server (basic tools)")
    print("2. Weather Server (advanced tools)")
    print("3. File Explorer Server (resources)")
    print("4. Custom server path")
    print()

    choice = input("Enter choice (1-4): ").strip()

    server_paths = {
        "1": "tutorials/03-mcp-servers/basic/simple_mcp_server.py",
        "2": "tutorials/03-mcp-servers/tools/weather_mcp_server.py",
        "3": "tutorials/03-mcp-servers/resources/file_explorer_server.py"
    }

    if choice in server_paths:
        server_path = server_paths[choice]
    elif choice == "4":
        server_path = input("Enter server script path: ").strip()
    else:
        print("Invalid choice")
        return

    client = MCPClient()
    await client.connect_to_server(server_path)

    # Interactive loop
    while True:
        print("\n" + "-"*70)
        print("What would you like to do?")
        print("1. Call a tool")
        print("2. Read a resource")
        print("3. List tools again")
        print("4. List resources again")
        print("5. Disconnect and exit")
        print()

        action = input("Enter choice (1-5): ").strip()

        if action == "1":
            if not client.tools:
                print("No tools available")
                continue

            print("\nAvailable tools:")
            for i, tool in enumerate(client.tools, 1):
                print(f"{i}. {tool.name}")

            tool_choice = input("\nEnter tool number: ").strip()
            try:
                tool_idx = int(tool_choice) - 1
                tool = client.tools[tool_idx]

                print(f"\nTool: {tool.name}")
                print(f"Required parameters: {list(tool.inputSchema.get('properties', {}).keys())}")

                args_json = input("\nEnter arguments as JSON: ").strip()
                arguments = json.loads(args_json)

                await client.call_tool(tool.name, arguments)

            except (ValueError, IndexError, json.JSONDecodeError) as e:
                print(f"Error: {e}")

        elif action == "2":
            if not client.resources:
                print("No resources available")
                continue

            print("\nAvailable resources:")
            for i, resource in enumerate(client.resources, 1):
                print(f"{i}. {resource.name} ({resource.uri})")

            res_choice = input("\nEnter resource number: ").strip()
            try:
                res_idx = int(res_choice) - 1
                resource = client.resources[res_idx]
                await client.read_resource(resource.uri)
            except (ValueError, IndexError) as e:
                print(f"Error: {e}")

        elif action == "3":
            await client.list_available_tools()

        elif action == "4":
            await client.list_available_resources()

        elif action == "5":
            await client.disconnect()
            break


async def main():
    """Main entry point."""
    print("\n" + "="*70)
    print(" MCP CLIENT DEMO ".center(70, "="))
    print("="*70)
    print("\nThis client demonstrates how to connect to and use MCP servers.")
    print("\nChoose a mode:\n")
    print("1. Run all demos automatically")
    print("2. Interactive mode (test servers manually)")
    print()

    mode = input("Enter choice (1 or 2): ").strip()

    if mode == "1":
        # Run all demos
        await demo_calculator_server()
        await demo_weather_server()
        await demo_file_server()

        print("\n\n" + "="*70)
        print(" ALL DEMOS COMPLETE! ".center(70, "="))
        print("="*70)
        print("\n✨ You've successfully tested MCP servers using a custom client!")
        print("   In real applications, Claude Desktop or other AI assistants")
        print("   act as the MCP client, connecting to your servers.\n")

    elif mode == "2":
        await interactive_mode()

    else:
        print("Invalid choice")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 Exiting...")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nMake sure you have installed the MCP package:")
        print("   pip install mcp")
