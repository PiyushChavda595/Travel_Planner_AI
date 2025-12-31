import streamlit as st
from agent_setup import plan_trip, pick_options, build_itinerary

st.set_page_config(page_title="AI Travel Planner", page_icon="✈️")
st.title("🌍 AI Travel Planner")

# --------------- Chat Memory --------------- #
if "messages" not in st.session_state:
    st.session_state.messages = []

# Re-display chat history
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# --------------- User Input --------------- #
msg = st.chat_input("Ask me anything about your trip...")

if msg:

    # store + show user message
    st.session_state.messages.append({"role": "user", "content": msg})
    st.chat_message("user").write(msg)

    text = msg.lower().strip()

    reply = ""

    try:

        # ---------------- Option picking ---------------- #
        if "option" in text:
            nums = [int(s) for s in text.split() if s.isdigit()]
            flight = nums[0] if len(nums) >= 1 else None
            hotel = nums[1] if len(nums) >= 2 else None

            reply = pick_options(flight, hotel, days=3)

        # ---------------- Budgeted itinerary ---------------- #
        elif "budget" in text and "day" in text:

            words = text.split()
            days = int([w.replace("day", "") for w in words if "day" in w][0])
            budget = int([w for w in words if w.isdigit()][0])

            parts = text.split("from")[1].split("to")
            source = parts[0].strip()
            destination = parts[1].split("in")[0].strip()

            reply = build_itinerary(source, destination, days, budget)

        # ---------------- Normal trip search ---------------- #
        elif "from" in text and "to" in text:

            parts = text.split("from")[1].split("to")
            source = parts[0].strip()
            destination = parts[1].strip()

            reply = plan_trip(source, destination)

        else:
            reply = (
                "I can help with things like:\n"
                "- plan a 3 day trip from bangalore to mumbai\n"
                "- option 1 flight and option 2 hotel\n"
                "- plan a 5 day trip from delhi to goa in budget 50000\n"
            )

    except Exception as e:
        reply = f"Sorry, I could not understand that. Error: {e}"

    # store + show assistant reply
    st.session_state.messages.append({"role": "assistant", "content": reply})
    st.chat_message("assistant").write(reply)
