"""
Mock data for SkyVault  Agent.
Provides sample entries for flights, aircraft, passengers, maintenance, and weather.
These dictionaries are used by tools.py functions.
"""

# Flight information
FLIGHTS = {
    "AI101": {
        "flight_number": "AI101",
        "origin": "Delhi",
        "destination": "Mumbai",
        "status": "On Time",
        "gate": "A12",
        "terminal": "T3",
        "departure_time": "08:30",
        "delay_minutes": 0,
        "aircraft_type": "A320",
        "tail_number": "VT-ABC",
    },
    "6E204": {
        "flight_number": "6E204",
        "origin": "Mumbai",
        "destination": "Bangalore",
        "status": "Boarding",
        "gate": "B7",
        "terminal": "T2",
        "departure_time": "10:15",
        "delay_minutes": 0,
        "aircraft_type": "A320neo",
        "tail_number": "VT-IND",
    },
    "UK873": {
        "flight_number": "UK873",
        "origin": "Delhi",
        "destination": "Chennai",
        "status": "Delayed",
        "gate": "C2",
        "terminal": "T2",
        "departure_time": "09:15",
        "delay_minutes": 45,
        "aircraft_type": "A321",
        "tail_number": "VT-VST",
    },
    "SG8152": {
        "flight_number": "SG8152",
        "origin": "Delhi",
        "destination": "Kolkata",
        "status": "Cancelled",
        "gate": None,
        "terminal": "T1",
        "departure_time": "10:00",
        "delay_minutes": 0,
        "aircraft_type": "B737-800",
        "tail_number": "VT-SGA",
    },
}

# Aircraft specifications
AIRCRAFT = {
    "A320": {
        "type": "A320",
        "length_m": 37.57,
        "wingspan_m": 34.10,
        "capacity": 180,
        "fuel_capacity_liters": 24210,
        "range_km": 6100,
    },
    "A320neo": {
        "type": "A320neo",
        "length_m": 37.57,
        "wingspan_m": 35.80,
        "capacity": 186,
        "fuel_capacity_liters": 26350,
        "range_km": 6300,
    },
    "ATR 72": {
        "type": "ATR 72",
        "length_m": 27.17,
        "wingspan_m": 27.05,
        "capacity": 78,
        "fuel_capacity_liters": 5000,
        "range_km": 1500,
    },
}

# Passenger bookings
PASSENGERS = {
    "Rahul Sharma": {
        "name": "Rahul Sharma",
        "booking_reference": "AI7K2M",
        "seat": "14A",
        "destination": "Mumbai",
        "flight_number": "AI101",
    },
    "Priya Nair": {
        "name": "Priya Nair",
        "booking_reference": "6E9P4Q",
        "seat": "22C",
        "destination": "Bangalore",
        "flight_number": "6E204",
    },
    "Amit Verma": {
        "name": "Amit Verma",
        "booking_reference": "UK8X5Z",
        "seat": "18B",
        "destination": "Chennai",
        "flight_number": "UK873",
    },
}

# Maintenance records
MAINTENANCE = {
    "VT-ABC": {
        "tail_number": "VT-ABC",
        "aircraft_type": "A320",
        "last_inspection_date": "2026-08-10",
        "hours_flown": 12450,
        "outstanding_issues": [],
    },
    "VT-IND": {
        "tail_number": "VT-IND",
        "aircraft_type": "A320neo",
        "last_inspection_date": "2026-08-15",
        "hours_flown": 8320,
        "outstanding_issues": ["Cabin pressure sensor recalibration due in 120 hours"],
    },
    "VT-VST": {
        "tail_number": "VT-VST",
        "aircraft_type": "A321",
        "last_inspection_date": "2026-08-12",
        "hours_flown": 18760,
        "outstanding_issues": ["Hydraulic pump replacement due"],
    },
}

# Weather conditions
WEATHER = {
    "DEL": {
        "airport": "Delhi Indira Gandhi (DEL)",
        "visibility_km": 8,
        "wind": "12 km/h NW",
        "temperature_c": 32,
        "conditions": "Haze",
    },
    "BOM": {
        "airport": "Mumbai Chhatrapati Shivaji (BOM)",
        "visibility_km": 6,
        "wind": "18 km/h W",
        "temperature_c": 29,
        "conditions": "Light rain",
    },
    "MAA": {
        "airport": "Chennai International (MAA)",
        "visibility_km": 10,
        "wind": "15 km/h SE",
        "temperature_c": 34,
        "conditions": "Sunny",
    },
    "CCU": {
        "airport": "Kolkata Netaji Subhas (CCU)",
        "visibility_km": 7,
        "wind": "20 km/h NE",
        "temperature_c": 30,
        "conditions": "Cloudy",
    },
}
