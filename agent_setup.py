from langchain_openai import ChatOpenAI
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from travel_tools import (
    search_flights,
    search_hotels,
    suggest_places,
    get_weather,
    plan_trip as json_plan_trip,
    pick_options as json_pick,
)

session = {"last_flights": [], "last_hotels": []}


# ---------- LangChain agent (optional) ---------- #
def create_agent_executor(api_key: str):

    llm = ChatOpenAI(
        api_key=api_key,
        model="gpt-4.1-mini",
        temperature=0,
    )

    tools = []

    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful travel assistant."),
        ("human", "{input}"),
        MessagesPlaceholder("agent_scratchpad"),
    ])

    agent = create_tool_calling_agent(llm, tools, prompt)

    return AgentExecutor(agent=agent, tools=tools, verbose=True)


# ---------- Budgeted itinerary builder ---------- #
def build_itinerary(source, destination, days, budget):

    flights = search_flights(source, destination)
    hotels = search_hotels(destination)
    weather = get_weather(destination)
    places = suggest_places(destination)

    if not flights:
        return "No flights found."
    if not hotels:
        return "No hotels found."

    best_flight = flights[0]
    best_hotel = hotels[0]

    hotel_cost = best_hotel["price_per_night"] * days
    total = best_flight["price"] + hotel_cost

    text = f"""
🧳 Trip plan for {days} days
{source.title()} → {destination.title()}

✈️ Flight:
{best_flight['airline']} ({best_flight['flight_id']})
₹{best_flight['price']}

🏨 Hotel:
{best_hotel['name']}
₹{best_hotel['price_per_night']} × {days} nights = ₹{hotel_cost}

🌤 Weather:
{weather['desc']} | {weather['temp']}°C

📍 Places:
"""

    for p in places[:5]:
        text += f"- {p['name']}\n"

    text += f"\n💰 Total trip cost = ₹{total}\n"

    if total <= budget:
        text += "✅ Fits your budget!\n"
    else:
        text += "⚠️ Above your budget. I can suggest cheaper options.\n"

    text += "\n🗓 Itinerary\n"

    for d in range(1, days+1):
        text += f"\nDay {d}:\n- Sightseeing\n- Local food\n- Explore\n"

    return text


# ---------- Simple wrappers ---------- #
def plan_trip(source, destination):
    return json_plan_trip(source, destination)


def pick_options(flight_index, hotel_index, days=3):
    return json_pick(flight_index, hotel_index, days)
