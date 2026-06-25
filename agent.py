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
        "You answer questions about a university using two retrieval tools. "
        "Decide by WHAT the question asks for, not by how it is phrased.\n\n"
        "Use query_graph when the question is about a RELATIONSHIP between named things: "
        "who LEADS / TEACHES / BUILT / SUPERVISES / STUDIED something, what is the "
        "PREREQUISITE for a course, who is an ALUMNUS of where, plus any counting or "
        "multi-hop 'the X of the Y that Z' question. If the question names a specific "
        "entity and asks who or what is connected to it, use query_graph — even when it "
        "sounds descriptive ('who leads the Vision Lab?' is a LEADS lookup, not a "
        "description).\n\n"
        "Use query_vectors ONLY for open-ended descriptive questions with no specific "
        "relationship to traverse: 'what does Coastal Tech specialize in?', "
        "'describe the robotics program', 'what is X about?'.\n\n"
        "Examples:\n"
        "  'Who leads the Vision Lab?' -> query_graph (LEADS relationship)\n"
        "  'Who teaches the prerequisite for the course that uses PixelKit?' "
        "-> query_graph (multi-hop)\n"
        "  'What does Coastal Tech specialize in?' -> query_vectors (descriptive)\n\n"
        "When both seem possible, prefer query_graph. State which tool you used and why, "
        "then give the answer."
    ),
    tools=[query_graph, query_vectors],
)
