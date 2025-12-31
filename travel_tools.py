import json
from langchain.tools import tool

# ---------- helpers ----------
def load_json(path):
    with open(path, "r") as f:
        return json.load(f)


@tool
def search_flights(origin: str, destination: str) -> str:
    """Search real flights from dataset"""
    flights = load_json("dataset/flights.json")

    matches = [
        f for f in flights
        if f["source"].lower() == origin.lower()
        and f["destination"].lower() == destination.lower()
    ]

    if not matches:
        return f"No flights found from {origin} to {destination}"

    # sort by price or duration if you like
    matches = sorted(matches, key=lambda x: x["price"])

    result = "✈️ Available Flights:\n\n"
    for f in matches[:5]:  # show top 5
        result += (
            f"- {f['airline']} | ₹{f['price']} | "
            f"{f['duration']} | Flight: {f['flight_number']}\n"
        )

    return result


@tool
def search_hotels(city: str) -> str:
    """Search hotels from dataset"""
    hotels = load_json("dataset/hotels.json")

    matches = [
        h for h in hotels
        if h["city"].lower() == city.lower()
    ]

    if not matches:
        return f"No hotels found in {city}"

    matches = sorted(matches, key=lambda x: x["price_per_night"])

    result = f"🏨 Hotels in {city}:\n\n"
    for h in matches[:5]:
        result += (
            f"- {h['name']} | {h['stars']}⭐ | "
            f"₹{h['price_per_night']}/night\n"
        )

    return result


@tool
def get_weather(city: str) -> str:
    """Mock weather information"""
    return f"Weather in {city}: Clear sky, 28°C"


def get_tools():
    return [search_flights, search_hotels, get_weather]
