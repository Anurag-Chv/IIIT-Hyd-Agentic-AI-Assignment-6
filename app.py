"""
Tests for InboxHero tools, memory and MCP integration.
"""

import sys
import unittest
from pathlib import Path

# Add Common/ to the Python path
sys.path.insert(0, str(Path(__file__).resolve().parent / "Common"))

from data import (
    load_inbox,
    get_message,
    get_thread,
    search_messages,
    get_unread_messages,
)
from tools import (
    get_inbox_summary,
    record_disposition,
    get_disposition,
    get_undecided_messages,
    remember,
    recall,
)
from mcp_server import MCPServer, ToolRegistry
from mcp_client import MCPClient


class TestInboxData(unittest.TestCase):

    def test_load_inbox(self):
        messages = load_inbox()
        self.assertEqual(len(messages), 100)

    def test_get_message(self):
        message = get_message("m003")
        self.assertIsNotNone(message)
        self.assertEqual(message["id"], "m003")

    def test_unknown_message(self):
        message = get_message("m999")
        self.assertIsNone(message)

    def test_get_thread(self):
        thread = get_thread("t-launch")
        self.assertGreater(len(thread), 1)
        self.assertEqual(thread[0]["thread_id"], "t-launch")

    def test_search_messages(self):
        results = search_messages("board review")
        self.assertGreater(len(results), 0)

    def test_get_unread_messages(self):
        messages = get_unread_messages()
        self.assertGreater(len(messages), 0)


class TestInboxTools(unittest.TestCase):

    def test_inbox_summary(self):
        result = get_inbox_summary()
        self.assertEqual(result["total_messages"], 100)
        self.assertIn("unread_messages", result)

    def test_record_disposition(self):
        result = record_disposition(
            "m051",
            "defer",
            "Personal message that does not need immediate action.",
        )

        self.assertEqual(result["message_id"], "m051")
        self.assertEqual(result["disposition"], "defer")

    def test_get_disposition(self):
        result = get_disposition("m051")
        self.assertEqual(result["disposition"], "defer")

    def test_invalid_disposition(self):
        result = record_disposition(
            "m051",
            "invalid_action",
            "Test",
        )

        self.assertIn("error", result)

    def test_undecided_messages(self):
        result = get_undecided_messages()
        self.assertIsInstance(result, list)


class TestMemory(unittest.TestCase):

    def test_remember_and_recall(self):
        remember(
            "test_preference",
            "Test value",
            "unit-test",
        )

        result = recall("test_preference")

        self.assertEqual(result["value"], "Test value")


class TestMCPIntegration(unittest.TestCase):

    def setUp(self):
        registry = ToolRegistry()
        server = MCPServer(registry)
        self.client = MCPClient(server)

    def test_initialize(self):
        self.assertIn("result", self.client.init_response)
        self.assertEqual(
            self.client.init_response["result"]["server_name"],
            "InboxHero MCPServer",
        )

    def test_list_tools(self):
        tools = self.client.list_tools()
        names = [tool["name"] for tool in tools]

        self.assertIn("get_message", names)
        self.assertIn("get_thread", names)
        self.assertIn("search_messages", names)
        self.assertIn("remember", names)

    def test_call_tool(self):
        result = self.client.call_tool(
            "get_message",
            {"message_id": "m003"},
        )

        self.assertEqual(result["id"], "m003")

    def test_call_memory_tool(self):
        self.client.call_tool(
            "remember",
            {
                "key": "mcp_test",
                "value": "works",
                "source": "test",
            },
        )

        result = self.client.call_tool(
            "recall",
            {"query": "mcp_test"},
        )

        self.assertEqual(result["value"], "works")


if __name__ == "__main__":
    unittest.main()