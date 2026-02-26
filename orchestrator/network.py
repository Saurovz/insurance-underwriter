"""
AgentNetwork — registry of all running A2A domain agents.
To add a new domain later: network.add("products", "http://localhost:8002")
That's the ONLY change needed in the orchestrator.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from python_a2a import AgentNetwork
from config import settings


def build_network() -> AgentNetwork:
    """
    Register all active domain agents.
    AgentNetwork fetches each agent's Card at /.well-known/agent.json
    so the router knows their capabilities automatically.
    """
    network = AgentNetwork(name="Personal Advisor Network")

    # ── Active domain agents ──────────────────────────────────────────────────
    network.add("books",    f"http://localhost:{settings.BOOKS_AGENT_PORT}")

    # ── Future domains (uncomment when ready) ─────────────────────────────────
    # network.add("products", f"http://localhost:{settings.PRODUCTS_AGENT_PORT}")
    # network.add("courses",  f"http://localhost:{settings.COURSES_AGENT_PORT}")

    return network
