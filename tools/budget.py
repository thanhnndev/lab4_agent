"""Budget calculation tool for TravelBuddy AI Agent."""

from langchain_core.tools import tool


def format_vnd(value: int) -> str:
    """Format integer as Vietnamese Dong string."""
    return f"{value:,} VND".replace(",", ".")


@tool
def calculate_budget(total_budget: int, expenses: str) -> str:
    """Calculate remaining budget after subtracting expenses.

    Required params:
        total_budget: Total budget in VND (e.g., 5000000 for 5 million VND)
        expenses: Comma-separated list of expense items in format "name:amount"
                  Example: "flight:1200000,hotel:800000,food:500000"

    Returns:
        Detailed budget summary with each expense, total spent, remaining amount,
        and warning if over budget.
        Error message if format is invalid.
    """
    if not isinstance(total_budget, (int, float)):
        return "Error: total_budget must be a number (integer in VND)."

    if not expenses or not isinstance(expenses, str):
        return (
            "Error: expenses must be a string in format 'name:amount,name:amount'. "
            "Example: 'flight:1200000,hotel:800000'"
        )

    try:
        parsed: dict[str, int] = {}
        for pair in expenses.split(","):
            if not pair.strip():
                continue
            parts = pair.strip().split(":")
            if len(parts) != 2:
                return (
                    f"Error: Invalid expense format '{pair.strip()}'. "
                    f"Use format: name:amount (e.g., flight:1200000)"
                )
            name, amount = parts
            name = name.strip()
            amount_str = amount.strip()
            if not name:
                return f"Error: Expense name cannot be empty in '{pair.strip()}'."
            if not amount_str.isdigit():
                return (
                    f"Error: Amount must be a positive number, got '{amount_str}' "
                    f"in '{pair.strip()}'. Example: flight:1200000"
                )
            parsed[name] = int(amount_str)
    except Exception as e:
        return f"Error parsing expenses: {str(e)}. Use format: name:amount,name:amount"

    if not parsed:
        return "Error: No valid expenses found. Use format: name:amount,name:amount"

    total_expense = sum(parsed.values())
    remaining = total_budget - total_expense

    lines = ["Budget summary:"]
    for name, amount in parsed.items():
        lines.append(f"- {name}: {format_vnd(amount)}")
    lines.append(f"Total budget: {format_vnd(total_budget)}")
    lines.append(f"Total expenses: {format_vnd(total_expense)}")
    lines.append(f"Remaining: {format_vnd(remaining)}")

    if remaining < 0:
        lines.append("WARNING: You are over budget!")
    elif remaining < total_budget * 0.1:
        lines.append("Note: You have less than 10% of budget remaining.")

    return "\n".join(lines)
