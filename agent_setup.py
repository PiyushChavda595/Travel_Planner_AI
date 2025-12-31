from langchain_openai import ChatOpenAI
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

# ---- our local imports ---- #
from travel_tools import (
    get_tools,
    search_flights,
    search_hotels,
    suggest_places,
    get_weather,
)

# ---- memory to hold last search ---- #
session = {
    "last_flights": [],
    "last_hotels": []
}


# =======================================================================
# 1️⃣  LangChain Agent (used when LLM calls tools itself)
# =======================================================================

def create_agent_executor(api_key: str):

    llm = ChatOpenAI(
        api_key=api_key,
        model="gpt-4.1-mini",
        temperature=0,
    )

    tools = get_tools()

    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful AI travel assistant. Use tools when needed."),
        ("human", "{input}"),
        MessagesPlaceholder("agent_scratchpad"),
    ])

    agent = create_tool_calling_agent(llm, tools, prompt)

    executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
    )

    return executor


# =======================================================================
# 2️⃣  Manual planner which uses our JSON + weather API directly
# =======================================================================

def plan_trip(source, destination, days=3):

    flights = search_flights(source, destination)
    hotels = search_hotels(destination)
    places = suggest_places(destination)
    weather = get_weather(destination)

    # Save results for later selection
    session["last_flights"] = flights
    session["last_hotels"] = hotels

    reply = ""

    # ---- Flights ---- #
    if flights:
        reply += "✈️ Available Flights:\n"
        for i, f in enumerate(flights[:10], 1):
            reply += (
                f"{i}. {f['airline']} "
                f"({f['flight_id']}) — ₹{f['price']}\n"
            )
    else:
        reply += "❌ No flights found.\n"

    # ---- Hotels ---- #
    if hotels:
        reply += "\n🏨 Hotels:\n"
        for i, h in enumerate(hotels[:10], 1):
            reply += (
                f"{i}. {h['name']} — ₹{h['price_per_night']}/night\n"
            )
    else:
        reply += "\n❌ No hotels found.\n"

    # ---- Weather ---- #
    if weather:
        reply += (
            f"\n🌦 Weather in {destination}: "
            f"{weather['desc']} | {weather['temp']}°C\n"
        )

    # ---- Places ---- #
    if places:
        reply += "\n📍 Suggested Places:\n"
        for p in places[:10]:
            reply += f"- {p['name']}\n"

    reply += "\n💬 Reply like: option 2 flight + option 1 hotel"

    return reply


# =======================================================================
# 3️⃣  Select previously-listed options
# =======================================================================

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
