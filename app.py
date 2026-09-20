import unittest

from Common.data import (
    load_inbox,
    get_message,
    get_thread,
    search_messages,
    get_unread_messages,
)
from Common.tools import (
    get_inbox_summary,
    record_disposition,
    get_disposition,
)
from mcp_server import MCPServer, ToolRegistry
from mcp_client import MCPClient


class TestInboxData(unittest.TestCase):

    def test_load_inbox(self):
        self.assertEqual(len(load_inbox()), 100)

    def test_get_message(self):
        message = get_message("m003")
        self.assertEqual(message["id"], "m003")

    def test_unknown_message(self):
        self.assertIsNone(get_message("m999"))

    def test_get_thread(self):
        thread = get_thread("t-launch")
        self.assertGreater(len(thread), 1)

    def test_search(self):
        self.assertGreater(len(search_messages("board review")), 0)

    def test_unread(self):
        self.assertGreater(len(get_unread_messages()), 0)


class TestInboxTools(unittest.TestCase):

    def test_summary(self):
        result = get_inbox_summary()
        self.assertEqual(result["total_messages"], 100)

    def test_disposition(self):
        result = record_disposition(
            "m051",
            "defer",
            "Personal message.",
        )

        self.assertEqual(result["disposition"], "defer")
        self.assertEqual(
            get_disposition("m051")["disposition"],
            "defer",
        )


class TestMCP(unittest.TestCase):

    def setUp(self):
        self.client = MCPClient(
            MCPServer(ToolRegistry())
        )

    def test_initialize(self):
        self.assertEqual(
            self.client.init_response["server_name"],
            "InboxHero MCPServer",
        )

    def test_tools(self):
        names = [
            tool["name"]
            for tool in self.client.list_tools()
        ]

        self.assertIn("get_message", names)
        self.assertIn("search_messages", names)
        self.assertIn("remember", names)

    def test_call_tool(self):
        result = self.client.call_tool(
            "get_message",
            {"message_id": "m003"},
        )

        self.assertEqual(result["id"], "m003")

    def test_memory_tool(self):
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