import streamlit as st
from agent_setup import plan_trip, pick_options, build_itinerary

st.set_page_config(page_title="AI Travel Planner", page_icon="✈️")
st.title("🌍 AI Travel Planner")


msg = st.chat_input("Ask me anything about your trip...")


if msg:

    st.chat_message("user").write(msg)

    text = msg.lower()

    # ----- pick option flow ----- #
    if "option" in text:
        nums = [int(s) for s in text.split() if s.isdigit()]
        flight = nums[0] if nums else None
        hotel = nums[1] if len(nums) > 1 else None
        reply = pick_options(flight, hotel)

    # ----- budget itinerary flow ----- #
    elif "budget" in text and "day" in text:
        words = text.split()
        days = int([w for w in words if "day" in w][0].replace("day", ""))
        budget = int([w for w in words if w.isdigit()][0])

        parts = text.split("from")[1].split("to")
        source = parts[0].strip()
        destination = parts[1].split("in")[0].strip()

        reply = build_itinerary(source, destination, days, budget)

    # ----- normal trip search ----- #
    else:
        parts = text.split("from")[1].split("to")
        source = parts[0].strip()
        destination = parts[1].strip()

        reply = plan_trip(source, destination)

    st.chat_message("assistant").write(reply)
