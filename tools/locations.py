"""Location validation tool for TravelBuddy AI Agent.

This tool helps the agent check which cities and routes are valid
before calling other tools like search_flights or search_hotels.
"""

from langchain_core.tools import tool

from data.mock_data import FLIGHTS_DB, HOTELS_DB


@tool
def check_valid_locations() -> dict:
    """Check all valid locations available in the system.

    This tool returns:
        - List of cities that have flight routes
        - List of available flight routes (origin -> destination pairs)
        - List of cities that have hotels

    Use this tool first to validate city names before calling
    search_flights or search_hotels to avoid errors.

    Returns:
        Dictionary with three keys:
        - 'flight_cities': Set of all cities with flight connections
        - 'flight_routes': List of route tuples (origin, destination)
        - 'hotel_cities': List of cities with available hotels
    """
    flight_cities = set()
    flight_routes = []

    for (origin, destination), flights in FLIGHTS_DB.items():
        flight_cities.add(origin)
        flight_cities.add(destination)
        flight_routes.append(
            {
                "origin": origin,
                "destination": destination,
                "flights_count": len(flights),
            }
        )

    hotel_cities = list(HOTELS_DB.keys())

    return {
        "flight_cities": sorted(flight_cities),
        "flight_routes": flight_routes,
        "hotel_cities": sorted(hotel_cities),
    }
