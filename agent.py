"""The ADK agent. Gemini is given BOTH retrieval tools and decides which to
use per question.

Run the dev UI:  adk web   (then pick "kag_agent" in the browser)
Or run headless:  python run_agent.py
"""
from google.adk.agents import Agent
from config import GEMINI_MODEL
from graph_tool import query_graph
from vector_tool import query_vectors

root_agent = Agent(
    name="kag_agent",
    model=GEMINI_MODEL,
    instruction=(
        "You answer questions about a university using two tools.\n"
        "- Use query_graph for questions about RELATIONSHIPS or chains: who "
        "teaches/leads/built what, prerequisites, multi-step connections, counting.\n"
        "- Use query_vectors for FUZZY or DESCRIPTIVE questions where the answer "
        "is likely written in a passage.\n"
        "Choose deliberately. State which tool you used and why, then give the answer."
    ),
    tools=[query_graph, query_vectors],
)
