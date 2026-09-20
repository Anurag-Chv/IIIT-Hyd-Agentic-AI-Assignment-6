"""
App module for SkyVault Agent (Assignment 5).
Runs unit tests for each tool and provides a manual demo mode.
Now also includes MCPClient/MCPServer integration tests.
"""

import sys
import unittest
from pathlib import Path

# Add Common/ folder to path
sys.path.insert(0, str(Path(__file__).resolve().parent / "Common"))

from tools import (
    find_available_gate,
    get_flight_status,
    get_weather,
    lookup_aircraft,
    maintenance_history,
    search_passenger,
    remember,
    recall,
)

from mcp_server import MCPServer, ToolRegistry
from mcp_client import MCPClient


class TestGetFlightStatus(unittest.TestCase):
    def test_known_flight(self):
        result = get_flight_status("AI101")
        self.assertEqual(result["status"], "On Time")
        self.assertEqual(result["gate"], "A12")
        self.assertEqual(result["departure_time"], "08:30")
        self.assertEqual(result["delay_minutes"], 0)

    def test_delayed_flight(self):
        result = get_flight_status("uk873")
        self.assertEqual(result["status"], "Delayed")
        self.assertEqual(result["delay_minutes"], 45)

    def test_cancelled_flight(self):
        result = get_flight_status("SG8152")
        self.assertEqual(result["status"], "Cancelled")
        self.assertIsNone(result["gate"])

    def test_unknown_flight(self):
        result = get_flight_status("XX999")
        self.assertIn("message", result)


class TestSearchPassenger(unittest.TestCase):
    def test_known_passenger(self):
        result = search_passenger("Rahul Sharma")
        self.assertEqual(result["booking_reference"], "AI7K2M")
        self.assertEqual(result["seat"], "14A")

    def test_case_insensitive(self):
        result = search_passenger("priya nair")
        self.assertEqual(result["destination"], "Bangalore")

    def test_unknown_passenger(self):
        result = search_passenger("Nobody")
        self.assertIn("message", result)


class TestMaintenanceHistory(unittest.TestCase):
    def test_no_issues(self):
        result = maintenance_history("VT-ABC")
        self.assertEqual(result["outstanding_issues"], [])

    def test_with_issues(self):
        result = maintenance_history("vt-vst")
        self.assertEqual(len(result["outstanding_issues"]), 1)

    def test_unknown_tail(self):
        result = maintenance_history("VT-XXX")
        self.assertIn("message", result)


class TestFindAvailableGate(unittest.TestCase):
    def test_terminal_t3(self):
        result = find_available_gate("T3")
        self.assertEqual(result["gate"], "A10")

    def test_terminal_without_prefix(self):
        result = find_available_gate("2")
        self.assertEqual(result["gate"], "B5")

    def test_unknown_terminal(self):
        result = find_available_gate("T9")
        self.assertIn("message", result)


class TestGetWeather(unittest.TestCase):
    def test_airport_code(self):
        result = get_weather("DEL")
        self.assertEqual(result["temperature_c"], 32)

    def test_city_name(self):
        result = get_weather("Mumbai")
        self.assertEqual(result["temperature_c"], 29)

    def test_unknown_airport(self):
        result = get_weather("XYZ")
        self.assertIn("message", result)


class TestLookupAircraft(unittest.TestCase):
    def test_known_aircraft(self):
        result = lookup_aircraft("A320")
        self.assertEqual(result["capacity"], 180)

    def test_regional_aircraft(self):
        result = lookup_aircraft("ATR 72")
        self.assertEqual(result["capacity"], 78)

    def test_unknown_aircraft(self):
        result = lookup_aircraft("A380")
        self.assertIn("message", result)


class TestMemoryTools(unittest.TestCase):
    def test_remember_and_recall(self):
        remember("preferred_terminal", "T2", "test")
        result = recall("preferred_terminal")
        self.assertEqual(result["value"], "T2")


class TestMCPIntegration(unittest.TestCase):
    def setUp(self):
        registry = ToolRegistry()
        server = MCPServer(registry)
        self.client = MCPClient(server)

    def test_initialize(self):
        self.assertIn("result", self.client.init_response)
        self.assertEqual(self.client.init_response["result"]["server_name"], "SkyVault MCPServer")

    def test_list_tools(self):
        tools = self.client.list_tools()
        names = [t["name"] for t in tools]
        self.assertIn("get_flight_status", names)
        self.assertIn("remember", names)

    def test_call_tool(self):
        result = self.client.call_tool("find_available_gate", {"terminal": "T2"})
        self.assertIn("gate", result)


def run_demo():
    """Manual demo: print sample outputs for each tool and MCP calls."""
    print("=" * 60)
    print("SkyVault tools – demo run")
    print("=" * 60)

    demos = [
        ("get_flight_status('AI101')", get_flight_status("AI101")),
        ("search_passenger('Rahul Sharma')", search_passenger("Rahul Sharma")),
        ("maintenance_history('VT-VST')", maintenance_history("VT-VST")),
        ("find_available_gate('T3')", find_available_gate("T3")),
        ("get_weather('DEL')", get_weather("DEL")),
        ("lookup_aircraft('B737-800')", lookup_aircraft("B737-800")),
        ("remember('preferred_terminal','T2')", remember("preferred_terminal", "T2")),
        ("recall('preferred_terminal')", recall("preferred_terminal")),
    ]

    for label, result in demos:
        print(f"\n{label}")
        print(f"  -> {result}")

    print("\n=== MCP Demo ===")
    registry = ToolRegistry()
    server = MCPServer(registry)
    client = MCPClient(server)
    result = client.call_tool("find_available_gate", {"terminal": "T2"})
    print("MCP call result:", result)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "demo":
        run_demo()
    else:
        unittest.main()
