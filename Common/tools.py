# tools.py (Assignment 5 extension)
# Roll number: evernorth-aai-1155338

"""
Tools for FlightOps Agent.
Each function provides operational data by reading from mock dictionaries in data.py.
"""


from Common.data import AIRCRAFT, FLIGHTS, MAINTENANCE, PASSENGERS, WEATHER
import memory   # new import

from Common.data import AIRCRAFT, FLIGHTS, MAINTENANCE, PASSENGERS, WEATHER

# Gate inventory per terminal – used to find gates not currently assigned
TERMINAL_GATES = {
    "T1": ["A1", "A2", "A3", "B1", "D18", "D19"],
    "T2": ["B5", "B6", "B7", "B8", "C1"],
    "T3": ["A10", "A11", "A12", "C3", "C4", "C5"],
}

# Map city names to IATA codes
CITY_TO_AIRPORT = {
    "delhi": "DEL",
    "mumbai": "BOM",
    "bangalore": "BLR",
    "kochi": "COK",
    "hyderabad": "HYD",
    "kolkata": "CCU",
    "chennai": "MAA",
}


def get_flight_status(flight_number: str) -> dict:
    """
    Return status, gate, departure time, and delay for a flight.
    """
    flight = FLIGHTS.get(flight_number.upper())
    if not flight:
        return {"message": f"No flight found with number {flight_number}."}

    return {
        "status": flight["status"],
        "gate": flight["gate"],
        "departure_time": flight["departure_time"],
        "delay_minutes": flight["delay_minutes"],
    }


def search_passenger(name: str) -> dict:
    """
    Return booking reference, seat, and destination for a passenger.
    """
    for passenger_name, info in PASSENGERS.items():
        if passenger_name.lower() == name.lower():
            return {
                "booking_reference": info["booking_reference"],
                "seat": info["seat"],
                "destination": info["destination"],
            }
    return {"message": f"No passenger found with name {name}."}


def maintenance_history(tail_number: str) -> dict:
    """
    Return last inspection date, hours flown, and outstanding issues for an aircraft.
    """
    record = MAINTENANCE.get(tail_number.upper())
    if not record:
        return {"message": f"No maintenance record found for tail number {tail_number}."}

    return {
        "last_inspection_date": record["last_inspection_date"],
        "hours_flown": record["hours_flown"],
        "outstanding_issues": record["outstanding_issues"],
    }


def find_available_gate(terminal: str) -> dict:
    """
    Return an open gate number for the given terminal.
    """
    terminal_key = terminal.upper()
    if not terminal_key.startswith("T"):
        terminal_key = f"T{terminal_key}"

    gates = TERMINAL_GATES.get(terminal_key)
    if not gates:
        return {"message": f"No gates listed for terminal {terminal}."}

    # Find gates already occupied
    occupied = {
        flight["gate"]
        for flight in FLIGHTS.values()
        if flight.get("terminal") == terminal_key and flight.get("gate")
    }
    available = [gate for gate in gates if gate not in occupied]

    if not available:
        return {"message": f"No open gates available at terminal {terminal_key}."}

    return {"gate": available[0]}


def get_weather(airport: str) -> dict:
    """
    Return visibility, wind, and temperature for an airport.
    Accepts either IATA code or city name.
    """
    airport_key = airport.upper()
    if airport_key not in WEATHER:
        airport_key = CITY_TO_AIRPORT.get(airport.lower(), airport_key)

    record = WEATHER.get(airport_key)
    if not record:
        return {"message": f"No weather data found for airport {airport}."}

    return {
        "visibility_km": record["visibility_km"],
        "wind": record["wind"],
        "temperature_c": record["temperature_c"],
    }


def lookup_aircraft(aircraft_type: str) -> dict:
    """
    Return dimensions, capacity, and fuel figures for an aircraft type.
    """
    record = AIRCRAFT.get(aircraft_type)
    if not record:
        return {"message": f"No aircraft data found for type {aircraft_type}."}

    return {
        "length_m": record["length_m"],
        "wingspan_m": record["wingspan_m"],
        "capacity": record["capacity"],
        "fuel_capacity_liters": record["fuel_capacity_liters"],
    }


def remember(key: str, value: str, source: str = "manual") -> dict:
    """
    Store a fact persistently in memory_store.json.
    """
    result = memory.remember(key, value, source)
    return {"message": result}

def recall(query: str) -> dict:
    """
    Retrieve a fact from persistent memory_store.json.
    """
    result = memory.recall(query)
    if result:
        return {"value": result["value"], "source": result["source"], "timestamp": result["timestamp"]}
    return {"message": f"No memory found for {query}."}
