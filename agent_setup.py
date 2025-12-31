from langchain_openai import ChatOpenAI
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from travel_tools import get_tools


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
