import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))

from python_a2a.langchain import to_a2a_server
from python_a2a import AgentCard
from langchain_core.runnables import RunnableLambda
from agents.books.agent import create_books_agent
from config import settings


def build_books_server():
    print("📚 Initialising Books Agent (loading tools + LLM config)...")
    agent_executor = create_books_agent()

    def run_agent(input_data):
        # ✅ Converts plain string → {"input": text} before AgentExecutor sees it
        if isinstance(input_data, str):
            result = agent_executor.invoke({"input": input_data})
        elif isinstance(input_data, dict) and "input" not in input_data:
            text   = next(iter(input_data.values()), str(input_data))
            result = agent_executor.invoke({"input": text})
        else:
            result = agent_executor.invoke(input_data)

        # Return only the final answer text, not the full dict
        if isinstance(result, dict):
            return result.get("output", str(result))
        return str(result)

    # ✅ Wrap in RunnableLambda — to_a2a_server gets a Runnable, not AgentExecutor
    server = to_a2a_server(RunnableLambda(run_agent))

    server.agent_card = AgentCard(
        name        = "Books Advisor Agent",
        description = "Recommends books, manages reading lists, searches OpenLibrary.",
        url         = f"http://localhost:{settings.BOOKS_AGENT_PORT}",
        version     = "1.0.0",
    )

    print(f"📚 Books Agent ready → will serve on port {settings.BOOKS_AGENT_PORT}")
    return server
