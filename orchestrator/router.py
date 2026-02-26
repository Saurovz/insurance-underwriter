# # """
# # Router — uses Mistral (HF API) to detect the domain, then routes the query
# # via A2A protocol to the correct domain agent.

# # Flow:
# #   user_query
# #     → domain_detection (Mistral decides: books? products? courses?)
# #     → A2AClient.ask(query) on the matched agent
# #     → returns the domain agent's response
# # """
# # import sys, os
# # sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# # from python_a2a import AgentNetwork, AIAgentRouter, A2AClient
# # from langchain_huggingface import HuggingFaceEndpoint
# # from config import settings


# # class AdvisorRouter:
# #     """
# #     Wraps python-a2a's AIAgentRouter with the HuggingFace Mistral LLM.
# #     Falls back to direct A2AClient call for single-domain prototypes.
# #     """

# #     def __init__(self, network: AgentNetwork):
# #         self.network = network
# #         self._llm    = None
# #         self._router = None

# #     def _get_llm(self):
# #         if self._llm is None:
# #             self._llm = HuggingFaceEndpoint(
# #                 repo_id              = settings.LLM_MODEL,
# #                 huggingfacehub_api_token = settings.HF_API_TOKEN,
# #                 max_new_tokens       = 64,       # routing only needs short output
# #                 temperature          = 0.0,      # deterministic routing
# #                 task                 = "text-generation",
# #             )
# #         return self._llm

# #     def _get_router(self):
# #         if self._router is None:
# #             self._router = AIAgentRouter(
# #                 llm          = self._get_llm(),
# #                 agent_network= self.network,
# #             )
# #         return self._router

# #     def route(self, user_query: str) -> str:
# #         """
# #         Route a user query to the correct domain agent and return its response.
# #         For single-domain prototype, routes directly to books agent.
# #         """
# #         agents = self.network.agents          # dict: {name: url}

# #         # ── Single domain shortcut (prototype with only books) ─────────────────
# #         if len(agents) == 1:
# #             name, url = next(iter(agents.items()))
# #             client    = A2AClient(url)
# #             return client.ask(user_query)

# #         # ── Multi-domain routing via AIAgentRouter ─────────────────────────────
# #         try:
# #             result = self._get_router().route(user_query)
# #             return str(result)
# #         except Exception as e:
# #             # Fallback: direct call to books agent
# #             fallback_url = agents.get("books")
# #             if fallback_url:
# #                 return A2AClient(fallback_url).ask(user_query)
# #             return f"Routing error: {e}"
# import sys, os
# sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# from python_a2a import AgentNetwork, HTTPClient
# from config import settings


# class AdvisorRouter:

#     def __init__(self, network: AgentNetwork):
#         self.network = network

#     def route(self, user_query: str) -> str:
#         agents = self.network.agents

#         # ── Single domain (books only prototype) ─────────────────────────────
#         if len(agents) == 1:
#             url = f"http://localhost:{settings.BOOKS_AGENT_PORT}"
#             try:
#                 client   = HTTPClient(url)           # ✅ HTTPClient, not A2AClient
#                 response = client.send_message(user_query)  # ✅ send_message, not ask()
#                 return response.content              # ✅ .content, not str(response)
#             except Exception as e:
#                 return f"⚠️ Books Agent error: {e}"

#         # ── Multi-domain routing (future) ─────────────────────────────────────
#         try:
#             client   = HTTPClient(self.network)
#             response = client.send_message(user_query)
#             return response.content
#         except Exception as e:
#             try:
#                 fallback = HTTPClient(f"http://localhost:{settings.BOOKS_AGENT_PORT}")
#                 return fallback.send_message(user_query).content
#             except Exception as fe:
#                 return f"⚠️ Routing failed: {e} | Fallback: {fe}"



import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from python_a2a import A2AClient, AgentNetwork
from config import settings

DOMAIN_PORT_MAP = {
    "books"   : settings.BOOKS_AGENT_PORT,
    # "products": settings.PRODUCTS_AGENT_PORT,
    # "courses" : settings.COURSES_AGENT_PORT,
}


class AdvisorRouter:

    def __init__(self, network: AgentNetwork):
        self.network = network

    def _send_to(self, port: int, user_query: str) -> str:
        url      = f"http://localhost:{port}"
        client   = A2AClient(url)
        response = client.ask(user_query)   # ✅ returns plain string directly
        return response

    def route(self, user_query: str) -> str:
        active = list(DOMAIN_PORT_MAP.keys())

        # ── Single domain (books only prototype) ──────────────────────────────
        if len(active) == 1:
            try:
                return self._send_to(DOMAIN_PORT_MAP[active[0]], user_query)
            except Exception as e:
                return f"⚠️ Books Agent error: {e}"

        # ── Multi-domain keyword detection (future) ────────────────────────────
        q = user_query.lower()
        domain = "books"
        if any(w in q for w in ["product", "buy", "price", "purchase"]):
            domain = "products"
        elif any(w in q for w in ["course", "learn", "tutorial", "class"]):
            domain = "courses"

        try:
            return self._send_to(DOMAIN_PORT_MAP.get(domain, settings.BOOKS_AGENT_PORT), user_query)
        except Exception as e:
            try:
                return self._send_to(settings.BOOKS_AGENT_PORT, user_query)
            except Exception as fe:
                return f"⚠️ Failed: {e} | Fallback: {fe}"
