"""Hotel search tool for TravelBuddy AI Agent."""

from langchain_core.tools import tool

from data.mock_data import HOTELS_DB


def format_vnd(value: int) -> str:
    """Format integer as Vietnamese Dong string."""
    return f"{value:,} VND".replace(",", ".")


@tool
def search_hotels(city: str, max_price_per_night: int = 99999999) -> str:
    """Find hotels in a city with optional max price filter.

    Required params:
        city: City name to search for hotels (e.g., "Ha Noi", "Da Nang", "Ho Chi Minh", "Phu Quoc")

    Optional params:
        max_price_per_night: Maximum price per night in VND (default: 99999999)

    Returns:
        Formatted list of hotels sorted by rating (highest first) with name, stars, area, price, and rating.
        Error message with suggestions if no hotels found.
    """
    if not city:
        return "Error: City name is required. Use check_valid_locations to see available cities with hotels."

    if not isinstance(city, str):
        return "Error: City must be a string (city name)."

    hotels = HOTELS_DB.get(city, [])
    if not hotels:
        available_cities = list(HOTELS_DB.keys())
        return (
            f"No hotels found in {city}. "
            f"Available cities: {', '.join(sorted(available_cities))}. "
            f"Use check_valid_locations to see all available locations."
        )

    filtered = [h for h in hotels if h["price_per_night"] <= max_price_per_night]
    if not filtered:
        return (
            f"No hotels in {city} under {format_vnd(max_price_per_night)}. "
            f"Cheapest option: {format_vnd(min(h['price_per_night'] for h in hotels))}. "
            f"Try increasing your budget or search in a different city."
        )

    filtered.sort(key=lambda x: x["rating"], reverse=True)
    lines = [f"Hotels in {city}:"]
    for idx, item in enumerate(filtered, 1):
        lines.append(
            f"{idx}. {item['name']} ({item['stars']}*) - {item['area']} - "
            f"{format_vnd(item['price_per_night'])}/night - rating {item['rating']}"
        )
    return "\n".join(lines)
