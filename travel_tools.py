from langchain.tools import tool


@tool
def search_flights(origin: str, destination: str) -> str:
    """Search flights between two cities and return a sample result."""
    return f"Flight Found: {origin} to {destination} | Indigo (₹5,200) | 2h 15m"


@tool
def search_hotels(city: str) -> str:
    """Search hotels in a given city and return a sample result."""
    return f"Hotel Found: {city} Grand Resort | ₹3,500/night | 4 Stars"


@tool
def get_weather(city: str) -> str:
    """Get the current weather for a given city."""
    return f"Weather in {city}: Clear Sky, 28°C"


def get_tools():
    """Return the list of agent tools."""
    return [search_flights, search_hotels, get_weather]
