import streamlit as st
from agent_setup import create_agent_executor


st.set_page_config(page_title="AI Travel Planner", page_icon="✈️")
st.title("🌍 AI Travel Planner")


# -------- Load API Key --------
api_key = st.secrets.get("OPENAI_API_KEY")

if not api_key:
    with st.sidebar:
        api_key = st.text_input("Enter your OpenAI API Key", type="password")

if not api_key:
    st.warning("Please enter your OpenAI API Key to continue.")
    st.stop()


# -------- Create Agent --------
if "agent_executor" not in st.session_state:
    try:
        st.session_state.agent_executor = create_agent_executor(api_key)
    except Exception as e:
        st.error(f"Agent creation failed: {e}")
        st.stop()


# -------- Chat History --------
if "messages" not in st.session_state:
    st.session_state.messages = []


for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])


# -------- User Input --------
user_input = st.chat_input("Ask me about your travel plans...")

if user_input:

    st.session_state.messages.append({"role": "user", "content": user_input})
    st.chat_message("user").write(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                response = st.session_state.agent_executor.invoke({"input": user_input})
                output = response["output"]

                st.write(output)

                st.session_state.messages.append(
                    {"role": "assistant", "content": output}
                )

            except Exception as e:
                st.error(f"Error: {e}")
