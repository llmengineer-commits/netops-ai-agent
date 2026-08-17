import logfire
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain.tools.retriever import create_retriever_tool
from dotenv import load_dotenv

from tools.mikrotik_api import (
    check_pppoe_status, get_recent_logs, reset_dhcp_lease, 
    check_router_health, ping_gateway
)
from rag.vector_store import build_vector_store

load_dotenv()
logfire.configure(pydantic_plugin=logfire.PydanticPlugin(record="all"))
logfire.instrument_langchain()

def create_agent():
    rag_tool = create_retriever_tool(
        build_vector_store(),
        "search_mikrotik_manuals",
        "Searches technical documentation for ISP troubleshooting."
    )
    tools = [check_pppoe_status, get_recent_logs, reset_dhcp_lease, check_router_health, ping_gateway, rag_tool]
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are an autonomous Network Support L2 Engineer. 
        Rules for Execution:
        1. If you diagnose a DHCP issue, you MUST use the reset_dhcp_lease tool.
        2. If a tool returns a timeout ERROR, execute the suggested fallback tool immediately. 
        3. Never invent tool responses. Cross-reference tool outputs with documentation."""),
        ("human", "{input}"),
        ("placeholder", "{agent_scratchpad}"),
    ])
    
    agent = create_tool_calling_agent(ChatOpenAI(model="gpt-4o-mini", temperature=0), tools, prompt)
    return AgentExecutor(agent=agent, tools=tools, verbose=True)

if __name__ == "__main__":
    agent_executor = create_agent()
    with logfire.span("diagnostic_session"):
        response = agent_executor.invoke({"input": "Check the health of router 192.168.88.1. If it fails, fix it."})
        print("\nAgent Diagnosis:\n", response["output"])
