# """
# Books LangChain agent — wires Mistral (via HuggingFace API) + 7 tools.
# Uses ReAct pattern which works reliably with any text-generation LLM.
# """
# import sys, os
# sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))

# from langchain_huggingface import HuggingFaceEndpoint
# from langchain.agents import create_react_agent, AgentExecutor
# from langchain.prompts import PromptTemplate
# from agents.books.tools import get_all_tools
# from agents.books.prompts import BOOKS_SYSTEM_PROMPT
# from config import settings

# # ── ReAct prompt template (Thought → Action → Observation loop) ───────────────
# REACT_TEMPLATE = """{system_prompt}

# You have access to the following tools:
# {tools}

# Use EXACTLY this format for every response:

# Question: the input question you must answer
# Thought: think about what to do
# Action: the action to take, must be one of [{tool_names}]
# Action Input: the input to the action
# Observation: the result of the action
# ... (repeat Thought/Action/Action Input/Observation as needed)
# Thought: I now know the final answer
# Final Answer: the final answer to the original input question

# IMPORTANT: Always start with a Thought. Never skip to Final Answer without using a tool first.

# Begin!

# Question: {input}
# Thought:{agent_scratchpad}"""


# def create_books_agent() -> AgentExecutor:
#     """
#     Build and return a LangChain AgentExecutor for the Books domain.
#     This is the object wrapped by python-a2a's to_a2a_server().
#     """
#     llm = HuggingFaceEndpoint(
#     endpoint_url = f"{settings.HF_ROUTER_BASE}/{settings.LLM_MODEL}",
#     huggingfacehub_api_token = settings.HF_API_TOKEN,
#     max_new_tokens = 512,
#     temperature    = 0.4,
#     task           = "text-generation",
#     )

#     tools  = get_all_tools()
#     prompt = PromptTemplate(
#         template          = REACT_TEMPLATE,
#         input_variables   = ["input", "agent_scratchpad", "tools", "tool_names"],
#         partial_variables = {"system_prompt": BOOKS_SYSTEM_PROMPT},
#     )

#     agent = create_react_agent(llm=llm, tools=tools, prompt=prompt)

#     return AgentExecutor(
#         agent              = agent,
#         tools              = tools,
#         verbose            = True,        # shows Thought/Action in terminal
#         handle_parsing_errors = True,     # gracefully handles LLM formatting mistakes
#         max_iterations     = 6,           # max tool calls per query
#         return_intermediate_steps = False,
#     )

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))

from typing import Any, List, Optional
from langchain_core.language_models.llms import LLM
from langchain_core.callbacks.manager import CallbackManagerForLLMRun
from langchain.agents import create_react_agent, AgentExecutor
from langchain.prompts import PromptTemplate
from agents.books.tools import get_all_tools
from agents.books.prompts import BOOKS_SYSTEM_PROMPT
from config import settings


class HFRouterLLM(LLM):
    """
    Custom LangChain LLM using InferenceClient with provider='hf-inference'.
    Replaces HuggingFaceEndpoint entirely — no manual URL construction.
    InferenceClient handles routing to router.huggingface.co automatically.
    """
    model_id      : str
    api_key       : str
    max_new_tokens: int   = 512
    temperature   : float = 0.4

    @property
    def _llm_type(self) -> str:
        return "hf_router"

    def _call(
        self,
        prompt     : str,
        stop       : Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs   : Any,
    ) -> str:
        from huggingface_hub import InferenceClient

        client = InferenceClient(
            provider = "hf-inference",
            api_key  = self.api_key,
        )
        return client.text_generation(
            prompt,
            model          = self.model_id,
            max_new_tokens = self.max_new_tokens,
            temperature    = self.temperature,
            stop_sequences = stop or [],
        )


REACT_TEMPLATE = """{system_prompt}

You have access to the following tools:
{tools}

Use EXACTLY this format for every response:

Question: the input question you must answer
Thought: think about what to do
Action: the action to take, must be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (repeat Thought/Action/Action Input/Observation as needed)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

IMPORTANT: Always start with a Thought. Never skip to Final Answer without using at least one tool first.

Begin!

Question: {input}
Thought:{agent_scratchpad}"""


def create_books_agent() -> AgentExecutor:
    llm = HFRouterLLM(
        model_id       = settings.LLM_MODEL,
        api_key        = settings.HF_API_TOKEN,
        max_new_tokens = 512,
        temperature    = 0.4,
    )

    tools  = get_all_tools()
    prompt = PromptTemplate(
        template          = REACT_TEMPLATE,
        input_variables   = ["input", "agent_scratchpad", "tools", "tool_names"],
        partial_variables = {"system_prompt": BOOKS_SYSTEM_PROMPT},
    )

    agent = create_react_agent(llm=llm, tools=tools, prompt=prompt)

    return AgentExecutor(
        agent                 = agent,
        tools                 = tools,
        verbose               = True,
        handle_parsing_errors = True,
        max_iterations        = 6,
        return_intermediate_steps = False,
    )
