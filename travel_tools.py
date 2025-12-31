import json
import os
import requests

DATA_PATH = "dataset"


def load_json(name):
    with open(os.path.join(DATA_PATH, name)) as f:
        return json.load(f)


# ---------------- Flights ---------------- #
def search_flights(source, destination):
    flights = load_json("flights.json")

    src = source.lower().strip()
    dst = destination.lower().strip()

    results = [
        f for f in flights
        if f["from"].lower() == src and f["to"].lower() == dst
    ]

    return sorted(results, key=lambda x: x["price"])


# ---------------- Hotels ---------------- #
def search_hotels(city):
    hotels = load_json("hotels.json")

    c = city.lower().strip()

    results = [h for h in hotels if h["city"].lower() == c]

    return sorted(results, key=lambda x: x["price_per_night"])


# ---------------- Places ---------------- #
def suggest_places(city):
    places = load_json("places.json")
    c = city.lower().strip()

    return [p for p in places if p["city"].lower() == c]


# ---------------- Weather (LIVE) ---------------- #
def get_weather(city):
    key = os.getenv("OPENWEATHER_KEY")

    if not key:
        return {"temp": "--", "desc": "Unavailable"}

    url = (
        f"https://api.openweathermap.org/data/2.5/weather"
        f"?q={city}&appid={key}&units=metric"
    )

    try:
        data = requests.get(url).json()
        return {
            "temp": round(data["main"]["temp"]),
            "desc": data["weather"][0]["description"].title()
        }
    except Exception:
        return {"temp": "--", "desc": "Unavailable"}


# ===================================================
#   MEMORY (keeps last results)
# ===================================================

session = {"last_flights": [], "last_hotels": []}


def plan_trip(source, destination, days=3):

    flights = search_flights(source, destination)
    hotels = search_hotels(destination)
    places = suggest_places(destination)
    weather = get_weather(destination)

    session["last_flights"] = flights
    session["last_hotels"] = hotels

    reply = ""

    if flights:
        reply += "✈️ Available Flights:\n"
        for i, f in enumerate(flights[:5], 1):
            reply += f"{i}. {f['airline']} ({f['flight_id']}) — ₹{f['price']}\n"
    else:
        reply += "❌ No flights found.\n"

    if hotels:
        reply += "\n🏨 Hotels:\n"
        for i, h in enumerate(hotels[:5], 1):
            reply += f"{i}. {h['name']} — ₹{h['price_per_night']}/night\n"
    else:
        reply += "\n❌ No hotels found.\n"

    reply += f"\n🌦 Weather in {destination}: {weather['desc']} | {weather['temp']}°C\n"

    if places:
        reply += "\n📍 Suggested Places:\n"
        for p in places[:5]:
            reply += f"- {p['name']}\n"

    reply += "\n💬 Reply like: option 2 flight + option 1 hotel"

    return reply


def pick_options(flight_index=None, hotel_index=None, days=3):

    flights = session.get("last_flights", [])
    hotels = session.get("last_hotels", [])

    if not flights or not hotels:
        return "Please search for a trip first 🙂"

    reply = ""
    total = 0

    # ---- Flight ---- #
    if flight_index and 1 <= flight_index <= len(flights):
        f = flights[flight_index - 1]
        reply += (
            f"🛫 **Selected Flight**\n"
            f"{f['airline']} ({f['flight_id']})\n"
            f"{f['from']} → {f['to']}\n"
            f"Price: ₹{f['price']}\n\n"
        )
        total += f["price"]
    else:
        reply += "Invalid flight option.\n\n"

    # ---- Hotel ---- #
    if hotel_index and 1 <= hotel_index <= len(hotels):
        h = hotels[hotel_index - 1]
        hotel_cost = h["price_per_night"] * days
        reply += (
            f"🏨 **Selected Hotel**\n"
            f"{h['name']}\n"
            f"₹{h['price_per_night']} × {days} nights = ₹{hotel_cost}\n\n"
        )
        total += hotel_cost
        destination = h["city"]
    else:
        reply += "Invalid hotel option.\n\n"
        destination = None

    # ---- Weather ---- #
    if destination:
        weather = get_weather(destination)
        reply += (
            f"🌤 **Weather in {destination}**\n"
            f"{weather['desc']} | {weather['temp']}°C\n\n"
        )

        # ---- Suggested Places ---- #
        reply += "📍 **Places to Visit**\n"
        for p in suggest_places(destination)[:5]:
            reply += f"- {p['name']}\n"

    # ---- Total ---- #
    reply += f"\n💰 **Estimated Total for {days} days: ₹{total}**\n\n"

    # ---- DAY-WISE ITINERARY ---- #
    reply += "🗓 **Day-wise Itinerary**\n"

    for d in range(1, days+1):
        reply += (
            f"\nDay {d}:\n"
            f"- Breakfast at hotel\n"
            f"- Visit local attractions\n"
            f"- Try local food\n"
            f"- Evening walk / shopping\n"
        )

    return reply
