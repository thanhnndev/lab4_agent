from __future__ import annotations

from langchain_core.tools import tool

from data.mock_data import FLIGHTS_DB, HOTELS_DB


def format_vnd(value: int) -> str:
    return f"{value:,} VND".replace(",", ".")


@tool
def search_flights(origin: str, destination: str) -> str:
    """Find flights between two cities using mock data."""
    routes = FLIGHTS_DB.get((origin, destination))
    if not routes:
        routes = FLIGHTS_DB.get((destination, origin))
    if not routes:
        return f"No flights found for route: {origin} -> {destination}."

    lines = [f"Flights for {origin} -> {destination}:"]
    for idx, item in enumerate(routes, 1):
        lines.append(
            f"{idx}. {item['airline']} | {item['departure']}-{item['arrival']} | "
            f"{item['class']} | {format_vnd(item['price'])}"
        )
    return "\n".join(lines)


@tool
def search_hotels(city: str, max_price_per_night: int = 99999999) -> str:
    """Find hotels in a city with optional max price filter."""
    hotels = HOTELS_DB.get(city, [])
    if not hotels:
        return f"No hotels found in {city}."

    filtered = [h for h in hotels if h["price_per_night"] <= max_price_per_night]
    if not filtered:
        return f"No hotels in {city} under {format_vnd(max_price_per_night)}."

    filtered.sort(key=lambda x: x["rating"], reverse=True)
    lines = [f"Hotels in {city}:"]
    for idx, item in enumerate(filtered, 1):
        lines.append(
            f"{idx}. {item['name']} ({item['stars']}*) - {item['area']} - "
            f"{format_vnd(item['price_per_night'])}/night - rating {item['rating']}"
        )
    return "\n".join(lines)


@tool
def calculate_budget(total_budget: int, expenses: str) -> str:
    """Calculate remaining budget. expenses format: name:amount,name:amount."""
    try:
        parsed: dict[str, int] = {}
        for pair in expenses.split(","):
            if not pair.strip():
                continue
            name, amount = pair.split(":")
            parsed[name.strip()] = int(amount.strip())
    except ValueError:
        return "Invalid expenses format. Use: item:amount,item:amount"

    total_expense = sum(parsed.values())
    remaining = total_budget - total_expense

    lines = ["Budget summary:"]
    for name, amount in parsed.items():
        lines.append(f"- {name}: {format_vnd(amount)}")
    lines.append(f"Total budget: {format_vnd(total_budget)}")
    lines.append(f"Total expenses: {format_vnd(total_expense)}")
    lines.append(f"Remaining: {format_vnd(remaining)}")
    if remaining < 0:
        lines.append("Warning: You are over budget.")

    return "\n".join(lines)
