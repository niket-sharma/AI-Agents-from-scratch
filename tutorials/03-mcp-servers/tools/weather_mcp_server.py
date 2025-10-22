"""
Tutorial 03-B: MCP Server with Advanced Tools
==============================================

This tutorial shows how to build a more realistic MCP server
with practical tools like weather lookups, file operations, etc.

Tools vs Resources:
-------------------
- Tools: Functions the AI can CALL (like API endpoints)
- Resources: Data the AI can READ (like files or database records)

This example focuses on TOOLS.
"""

import asyncio
import json
import os
import random
from datetime import datetime
from typing import Any
from mcp.server import Server
from mcp.types import Tool, TextContent
import mcp.server.stdio


class WeatherMCPServer:
    """
    MCP server that provides weather-related tools.

    In a real application, you would connect to an actual weather API.
    For this tutorial, we'll simulate weather data.
    """

    def __init__(self):
        self.server = Server("weather-tools-server")
        self.setup_handlers()

        # Simulated weather database
        self.weather_db = {
            "new york": {"temp": 72, "condition": "Sunny", "humidity": 60},
            "london": {"temp": 65, "condition": "Cloudy", "humidity": 75},
            "tokyo": {"temp": 80, "condition": "Clear", "humidity": 55},
            "paris": {"temp": 68, "condition": "Partly Cloudy", "humidity": 65},
            "sydney": {"temp": 75, "condition": "Sunny", "humidity": 70}
        }

    def setup_handlers(self):
        """Register tool handlers."""

        @self.server.list_tools()
        async def list_tools() -> list[Tool]:
            """List all available weather tools."""
            return [
                Tool(
                    name="get_current_weather",
                    description="Get the current weather for a city",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "city": {
                                "type": "string",
                                "description": "The city name (e.g., 'New York', 'London')"
                            },
                            "units": {
                                "type": "string",
                                "enum": ["fahrenheit", "celsius"],
                                "description": "Temperature units",
                                "default": "fahrenheit"
                            }
                        },
                        "required": ["city"]
                    }
                ),
                Tool(
                    name="get_forecast",
                    description="Get a 3-day weather forecast for a city",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "city": {
                                "type": "string",
                                "description": "The city name"
                            },
                            "days": {
                                "type": "number",
                                "description": "Number of days (1-7)",
                                "default": 3
                            }
                        },
                        "required": ["city"]
                    }
                ),
                Tool(
                    name="compare_weather",
                    description="Compare weather between two cities",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "city1": {"type": "string", "description": "First city"},
                            "city2": {"type": "string", "description": "Second city"}
                        },
                        "required": ["city1", "city2"]
                    }
                ),
                Tool(
                    name="save_weather_alert",
                    description="Save a weather alert to a file",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "city": {"type": "string", "description": "City name"},
                            "alert_type": {
                                "type": "string",
                                "enum": ["rain", "storm", "heat", "cold"],
                                "description": "Type of weather alert"
                            },
                            "message": {"type": "string", "description": "Alert message"}
                        },
                        "required": ["city", "alert_type", "message"]
                    }
                )
            ]

        @self.server.call_tool()
        async def call_tool(name: str, arguments: Any) -> list[TextContent]:
            """Execute the requested tool."""

            if name == "get_current_weather":
                return await self._get_current_weather(arguments)

            elif name == "get_forecast":
                return await self._get_forecast(arguments)

            elif name == "compare_weather":
                return await self._compare_weather(arguments)

            elif name == "save_weather_alert":
                return await self._save_weather_alert(arguments)

            else:
                raise ValueError(f"Unknown tool: {name}")

    async def _get_current_weather(self, args: dict) -> list[TextContent]:
        """Get current weather for a city."""
        city = args["city"].lower()
        units = args.get("units", "fahrenheit")

        if city not in self.weather_db:
            return [TextContent(
                type="text",
                text=f"Sorry, weather data for '{city}' is not available. Available cities: {', '.join(self.weather_db.keys())}"
            )]

        weather = self.weather_db[city]
        temp = weather["temp"]

        # Convert to celsius if needed
        if units == "celsius":
            temp = round((temp - 32) * 5/9, 1)
            unit_symbol = "°C"
        else:
            unit_symbol = "°F"

        result = {
            "city": city.title(),
            "temperature": f"{temp}{unit_symbol}",
            "condition": weather["condition"],
            "humidity": f"{weather['humidity']}%",
            "timestamp": datetime.now().isoformat()
        }

        return [TextContent(
            type="text",
            text=json.dumps(result, indent=2)
        )]

    async def _get_forecast(self, args: dict) -> list[TextContent]:
        """Generate a weather forecast."""
        city = args["city"].lower()
        days = min(int(args.get("days", 3)), 7)

        if city not in self.weather_db:
            return [TextContent(
                type="text",
                text=f"Sorry, weather data for '{city}' is not available."
            )]

        base_weather = self.weather_db[city]

        # Generate forecast (simulated)
        forecast = []
        for i in range(days):
            temp_variation = random.randint(-5, 5)
            forecast.append({
                "day": f"Day {i+1}",
                "date": datetime.now().strftime(f"%Y-%m-%d"),
                "temp_high": base_weather["temp"] + temp_variation + 5,
                "temp_low": base_weather["temp"] + temp_variation - 5,
                "condition": random.choice(["Sunny", "Cloudy", "Partly Cloudy", "Rainy"]),
                "precipitation": f"{random.randint(0, 50)}%"
            })

        result = {
            "city": city.title(),
            "forecast": forecast
        }

        return [TextContent(
            type="text",
            text=json.dumps(result, indent=2)
        )]

    async def _compare_weather(self, args: dict) -> list[TextContent]:
        """Compare weather between two cities."""
        city1 = args["city1"].lower()
        city2 = args["city2"].lower()

        if city1 not in self.weather_db or city2 not in self.weather_db:
            return [TextContent(
                type="text",
                text=f"Sorry, one or both cities not found in database."
            )]

        w1 = self.weather_db[city1]
        w2 = self.weather_db[city2]

        comparison = {
            "city1": {
                "name": city1.title(),
                "temperature": f"{w1['temp']}°F",
                "condition": w1["condition"],
                "humidity": f"{w1['humidity']}%"
            },
            "city2": {
                "name": city2.title(),
                "temperature": f"{w2['temp']}°F",
                "condition": w2["condition"],
                "humidity": f"{w2['humidity']}%"
            },
            "difference": {
                "temperature": f"{abs(w1['temp'] - w2['temp'])}°F",
                "warmer_city": city1.title() if w1['temp'] > w2['temp'] else city2.title()
            }
        }

        return [TextContent(
            type="text",
            text=json.dumps(comparison, indent=2)
        )]

    async def _save_weather_alert(self, args: dict) -> list[TextContent]:
        """Save a weather alert to file."""
        city = args["city"]
        alert_type = args["alert_type"]
        message = args["message"]

        # Create alerts directory if it doesn't exist
        os.makedirs("weather_alerts", exist_ok=True)

        # Save alert
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"weather_alerts/{city}_{alert_type}_{timestamp}.json"

        alert_data = {
            "city": city,
            "alert_type": alert_type,
            "message": message,
            "timestamp": datetime.now().isoformat()
        }

        with open(filename, 'w') as f:
            json.dump(alert_data, f, indent=2)

        return [TextContent(
            type="text",
            text=f"Weather alert saved successfully to {filename}"
        )]

    async def run(self):
        """Run the MCP server."""
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options()
            )


async def main():
    """Run the weather MCP server."""
    import sys
    print("="*60, file=sys.stderr)
    print("WEATHER MCP SERVER", file=sys.stderr)
    print("="*60, file=sys.stderr)
    print("\nAvailable Tools:", file=sys.stderr)
    print("  • get_current_weather - Get current weather for a city", file=sys.stderr)
    print("  • get_forecast - Get weather forecast", file=sys.stderr)
    print("  • compare_weather - Compare weather between cities", file=sys.stderr)
    print("  • save_weather_alert - Save weather alerts", file=sys.stderr)
    print("\nServer running... waiting for MCP client connection.", file=sys.stderr)
    print("="*60, file=sys.stderr)
    print("", file=sys.stderr)

    server = WeatherMCPServer()
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())
