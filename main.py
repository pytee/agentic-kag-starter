"""Full pipeline entrypoint: build the graph, index vectors, then run a few
demo questions through the agent so you can see it route between tools.

Run:  python main.py
"""
import asyncio
from google.adk.runners import InMemoryRunner
from build_graph import build
from vector_tool import _collection  # noqa: F401  (import triggers indexing)
from agent import root_agent

DEMO_QUESTIONS = [
    "What does Coastal Tech specialize in?",                 # -> vector
    "Who leads the Vision Lab?",                             # -> graph (1 hop)
    "Who teaches the prerequisite for the course that uses " # -> graph (multi-hop)
    "PixelKit?",
]


async def ask(runner, question, i):
    print(f"\nQ{i}: {question}")
    async for event in runner.run_async(
        user_id="student", session_id=f"demo{i}", new_message=question
    ):
        if event.content:
            print(event.content)


async def demo():
    runner = InMemoryRunner(agent=root_agent)
    for i, q in enumerate(DEMO_QUESTIONS, 1):
        await ask(runner, q, i)


if __name__ == "__main__":
    print("=== Building knowledge graph ===")
    build()
    print("=== Vectors indexed on import ===")
    print("=== Running demo questions ===")
    asyncio.run(demo())
