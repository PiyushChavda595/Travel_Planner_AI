import streamlit as st
from agent_setup import (
    create_agent_executor,
    plan_trip,
    pick_options
)

# ----------------------------------------------------
# Page UI
# ----------------------------------------------------
st.set_page_config(page_title="AI Travel Planner", page_icon="✈️")
st.title("🌍 AI Travel Planner")


# ----------------------------------------------------
# Load API key
# ----------------------------------------------------
api_key = st.secrets.get("OPENAI_API_KEY")

if not api_key:
    with st.sidebar:
        api_key = st.text_input("Enter your OpenAI API Key", type="password")

if not api_key:
    st.warning("Please enter your OpenAI API Key to continue.")
    st.stop()


# ----------------------------------------------------
# Create Agent
# ----------------------------------------------------
if "agent_executor" not in st.session_state:
    try:
        st.session_state.agent_executor = create_agent_executor(api_key)
    except Exception as e:
        st.error(f"Agent creation failed: {e}")
        st.stop()


# ----------------------------------------------------
# Chat History
# ----------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []


for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])


# ----------------------------------------------------
# Get user input
# ----------------------------------------------------
user_input = st.chat_input("Ask me about your travel plans...")

if user_input:

    # Show user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.chat_message("user").write(user_input)

    reply_text = ""

    # ------------------------------------------------
    # Case 1 — user selects flights/hotels by number
    # ------------------------------------------------
    if "option" in user_input.lower():
        nums = [int(s) for s in user_input.split() if s.isdigit()]
        flight = nums[0] if len(nums) > 0 else None
        hotel = nums[1] if len(nums) > 1 else None

        reply_text = pick_options(flight, hotel)

    # ------------------------------------------------
    # Case 2 — user asks for a trip plan
    # ------------------------------------------------
    elif "trip" in user_input.lower() and "to" in user_input.lower():

        text = user_input.lower()

        # simple extraction like:
        # plan a trip from mumbai to delhi
        try:
            parts = text.split("from")[1].strip().split("to")
            source = parts[0].strip().title()
            destination = parts[1].strip().title()

            reply_text = plan_trip(source, destination)

        except Exception:
            reply_text = "Sorry, I could not understand the cities. Please say like: Plan a trip from Mumbai to Delhi."

    # ------------------------------------------------
    # Case 3 — fallback to LangChain agent
    # ------------------------------------------------
    else:
        with st.spinner("Thinking..."):
            try:
                response = st.session_state.agent_executor.invoke(
                    {"input": user_input}
                )
                reply_text = response["output"]

            except Exception as e:
                reply_text = f"Error: {e}"

    # ------------------------------------------------
    # Show assistant reply
    # ------------------------------------------------
    st.chat_message("assistant").write(reply_text)

    st.session_state.messages.append({
        "role": "assistant",
        "content": reply_text
    })
