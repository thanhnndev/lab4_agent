"""Flight search tool for TravelBuddy AI Agent."""

from langchain_core.tools import tool

from data.mock_data import FLIGHTS_DB


def format_vnd(value: int) -> str:
    """Format integer as Vietnamese Dong string."""
    return f"{value:,} VND".replace(",", ".")


@tool
def search_flights(origin: str, destination: str) -> str:
    """Find flights between two cities.

    Required params:
        origin: Departure city name (e.g., "Ha Noi", "Ho Chi Minh", "Da Nang", "Phu Quoc")
        destination: Arrival city name

    Returns:
        Formatted list of available flights with airline, time, class, and price.
        Error message with suggestions if route not found.
    """
    if not origin or not destination:
        return "Error: Both origin and destination are required. Use check_valid_locations to see available cities."

    if not isinstance(origin, str) or not isinstance(destination, str):
        return "Error: Origin and destination must be city names (strings)."

    routes = FLIGHTS_DB.get((origin, destination))
    if not routes:
        routes = FLIGHTS_DB.get((destination, origin))

    if not routes:
        available_cities = set()
        for src, dst in FLIGHTS_DB.keys():
            available_cities.add(src)
            available_cities.add(dst)
        return (
            f"No flights found for route: {origin} <-> {destination}. "
            f"Available cities: {', '.join(sorted(available_cities))}. "
            f"Use check_valid_locations to see all available routes."
        )

    lines = [f"Flights for {origin} -> {destination}:"]
    for idx, item in enumerate(routes, 1):
        lines.append(
            f"{idx}. {item['airline']} | {item['departure']}-{item['arrival']} | "
            f"{item['class']} | {format_vnd(item['price'])}"
        )
    return "\n".join(lines)
