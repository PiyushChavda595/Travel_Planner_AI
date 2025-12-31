import json
import os
import requests
from datetime import datetime

DATA_PATH = "dataset"


# ---------------- Load JSON helpers ---------------- #

def load_json(name):
    path = os.path.join(DATA_PATH, name)
    with open(path, "r") as f:
        return json.load(f)


# ---------------- Flights ---------------- #

def search_flights(source, destination):
    flights = load_json("flights.json")

    source = source.title()
    destination = destination.title()

    results = [
        f for f in flights
        if f["from"].lower() == source.lower()
        and f["to"].lower() == destination.lower()
    ]

    # sort by price (better UX)
    return sorted(results, key=lambda x: x["price"])


# ---------------- Hotels ---------------- #

def search_hotels(city):
    hotels = load_json("hotels.json")

    city = city.title()

    results = [
        h for h in hotels
        if h["city"].lower() == city.lower()
    ]

    return sorted(results, key=lambda x: x["price_per_night"])


# ---------------- Places ---------------- #

def suggest_places(city):
    places = load_json("places.json")

    city = city.title()

    return [
        p for p in places
        if p["city"].lower() == city.lower()
    ]


# ---------------- Weather (LIVE) ---------------- #

def get_weather(city):

    api_key = os.getenv("OPENWEATHER_KEY")

    if not api_key:
        return {"desc": "Weather key missing", "temp": "--"}

    url = (
        f"https://api.openweathermap.org/data/2.5/weather"
        f"?q={city}&appid={api_key}&units=metric"
    )

    try:
        res = requests.get(url)
        data = res.json()

        return {
            "temp": round(data["main"]["temp"]),
            "desc": data["weather"][0]["description"].title()
        }

    except Exception:
        return {"desc": "Unavailable", "temp": "--"}


# ===================================================
#   MANUAL SESSION MEMORY
# ===================================================

session = {
    "last_flights": [],
    "last_hotels": []
}


def plan_trip(source, destination, days=3):

    flights = search_flights(source, destination)
    hotels = search_hotels(destination)
    places = suggest_places(destination)
    weather = get_weather(destination)

    session["last_flights"] = flights
    session["last_hotels"] = hotels

    reply = ""

    # Flights
    if flights:
        reply += "✈️ Available Flights:\n"
        for i, f in enumerate(flights[:5], 1):
            reply += (
                f"{i}. {f['airline']} "
                f"({f['flight_id']}) — ₹{f['price']}\n"
            )
    else:
        reply += "❌ No flights found.\n"

    # Hotels
    if hotels:
        reply += "\n🏨 Hotels:\n"
        for i, h in enumerate(hotels[:5], 1):
            reply += (
                f"{i}. {h['name']} — ₹{h['price_per_night']}/night\n"
            )
    else:
        reply += "\n❌ No hotels found.\n"

    # Weather
    if weather:
        reply += (
            f"\n🌦 Weather in {destination}: "
            f"{weather['desc']} | {weather['temp']}°C\n"
        )

    # Places
    if places:
        reply += "\n📍 Suggested Places:\n"
        for p in places[:5]:
            reply += f"- {p['name']}\n"

    reply += "\n💬 Reply example: option 2 flight and option 1 hotel"

    return reply


def pick_options(flight_index=None, hotel_index=None):

    flights = session.get("last_flights", [])
    hotels = session.get("last_hotels", [])

    reply = ""

    if flight_index and 1 <= flight_index <= len(flights):
        f = flights[flight_index - 1]
        reply += (
            f"🛫 Selected Flight:\n"
            f"{f['airline']} ({f['flight_id']})\n"
            f"Price: ₹{f['price']}\n\n"
        )

    if hotel_index and 1 <= hotel_index <= len(hotels):
        h = hotels[hotel_index - 1]
        reply += (
            f"🏨 Selected Hotel:\n"
            f"{h['name']}\n"
            f"₹{h['price_per_night']} per night\n"
        )

    if reply == "":
        reply = "Please provide valid option numbers."

    return reply


# ===================================================
#   LANGCHAIN TOOL WRAPPERS
# ===================================================

def get_tools():
    from langchain.tools import Tool

    return [
        Tool(
            name="Search Flights",
            func=lambda q: search_flights(q["from"], q["to"]),
            description="Find flights between two cities"
        ),
        Tool(
            name="Search Hotels",
            func=lambda q: search_hotels(q["city"]),
            description="Find hotels in a city"
        ),
        Tool(
            name="Get Weather",
            func=lambda q: get_weather(q["city"]),
            description="Get live weather for a city"
        ),
        Tool(
            name="Suggest Places",
            func=lambda q: suggest_places(q["city"]),
            description="Tourist places in a city"
        ),
    ]
