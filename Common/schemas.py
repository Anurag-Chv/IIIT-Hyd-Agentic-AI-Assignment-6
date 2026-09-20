"""
Schemas for SkyVault Agent (Assignment 5).
Defines Gemini FunctionDeclaration objects for each tool in tools.py,
including persistent memory tools.

⚠️ Note: In Assignment 5, tool declarations are now fetched dynamically
via MCPClient.list_tools(). This file remains as a static reference only.
"""

from google.genai import types


def _make_tool(name: str, description: str, properties: dict, required: list):
    """
    Helper to create a FunctionDeclaration with consistent structure.
    """
    return types.FunctionDeclaration(
        name=name,
        description=description,
        parameters={
            "type": "OBJECT",
            "properties": properties,
            "required": required,
        },
    )


# Flight status tool
get_flight_status_tool = _make_tool(
    name="get_flight_status",
    description=(
        "Retrieve the current status of a flight. "
        "Use this when asked about delays, departure time, gate assignment, or whether "
        "a flight is on time, boarding, delayed, departed, or cancelled."
    ),
    properties={
        "flight_number": {
            "type": "STRING",
            "description": "Flight number, e.g. 'AI101', '6E204', 'UK873'.",
        },
    },
    required=["flight_number"],
)

# Passenger search tool
search_passenger_tool = _make_tool(
    name="search_passenger",
    description=(
        "Look up a passenger's booking details. "
        "Use this for seat assignment, booking reference (PNR), or destination. "
        "Do not use for flight status or gate queries."
    ),
    properties={
        "name": {
            "type": "STRING",
            "description": "Full passenger name, e.g. 'Rahul Sharma'.",
        },
    },
    required=["name"],
)

# Maintenance history tool
maintenance_history_tool = _make_tool(
    name="maintenance_history",
    description=(
        "Get maintenance and inspection records for an aircraft. "
        "Use this for last inspection date, total hours flown, or outstanding issues."
    ),
    properties={
        "tail_number": {
            "type": "STRING",
            "description": "Aircraft registration/tail number, e.g. 'VT-ABC', 'VT-VST'.",
        },
    },
    required=["tail_number"],
)

# Gate availability tool
find_available_gate_tool = _make_tool(
    name="find_available_gate",
    description=(
        "Find an available boarding gate at a terminal. "
        "Use this when asked which gates are open at T1, T2, T3, etc."
    ),
    properties={
        "terminal": {
            "type": "STRING",
            "description": "Terminal identifier, e.g. 'T1', 'T2', 'T3'.",
        },
    },
    required=["terminal"],
)

# Weather tool
get_weather_tool = _make_tool(
    name="get_weather",
    description=(
        "Get current weather conditions at an airport. "
        "Use this for visibility, wind, or temperature. Accepts IATA codes (DEL, BOM) or city names."
    ),
    properties={
        "airport": {
            "type": "STRING",
            "description": "Airport code or city name, e.g. 'DEL', 'Mumbai'.",
        },
    },
    required=["airport"],
)

# Aircraft lookup tool
lookup_aircraft_tool = _make_tool(
    name="lookup_aircraft",
    description=(
        "Look up technical specifications for an aircraft type. "
        "Use this for dimensions, seating capacity, or fuel capacity (A320, B737-800, ATR 72)."
    ),
    properties={
        "aircraft_type": {
            "type": "STRING",
            "description": "Aircraft type, e.g. 'A320', 'B737-800'.",
        },
    },
    required=["aircraft_type"],
)

# Memory tools
remember_tool = _make_tool(
    name="remember",
    description=(
        "Store a fact persistently in memory_store.json. "
        "Use this when asked to remember a preference, fact, or note across restarts."
    ),
    properties={
        "key": {"type": "STRING", "description": "Fact identifier, e.g. 'preferred_terminal'."},
        "value": {"type": "STRING", "description": "Fact value, e.g. 'Terminal 2'."},
        "source": {"type": "STRING", "description": "Origin of fact, e.g. 'manual'."},
    },
    required=["key", "value"],
)

recall_tool = _make_tool(
    name="recall",
    description=(
        "Retrieve a fact from persistent memory_store.json. "
        "Use this when asked to recall a stored preference or fact."
    ),
    properties={
        "query": {"type": "STRING", "description": "Fact identifier to recall, e.g. 'preferred_terminal'."},
    },
    required=["query"],
)

# Collect all tool declarations (static reference only)
skyvault_tool_declarations = [
    get_flight_status_tool,
    search_passenger_tool,
    maintenance_history_tool,
    find_available_gate_tool,
    get_weather_tool,
    lookup_aircraft_tool,
    remember_tool,
    recall_tool,
]

# Wrap into a Tool object for Gemini (reference only)
skyvault_tools = types.Tool(function_declarations=skyvault_tool_declarations)
