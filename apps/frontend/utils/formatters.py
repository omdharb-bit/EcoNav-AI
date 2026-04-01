from __future__ import annotations


def parse_improvement_percent(improvement: str) -> float | None:
    if not improvement or improvement == "N/A":
        return None
    token = improvement.split("%", maxsplit=1)[0].strip()
    try:
        return float(token)
    except ValueError:
        return None


def route_to_string(path: list[str]) -> str:
    return " → ".join(path)
