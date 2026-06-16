"""Headless runner for the KAG agent (no web UI needed).

Run:  python run_agent.py
Optionally pass your own question:
      python run_agent.py "Who leads the Vision Lab?"
"""
import sys
import asyncio
from google.adk.runners import InMemoryRunner
from agent import root_agent

DEFAULT_Q = "Who teaches the prerequisite for the course that uses PixelKit?"


async def main(question: str):
    runner = InMemoryRunner(agent=root_agent)
    async for event in runner.run_async(
        user_id="student", session_id="s1", new_message=question
    ):
        if event.content:
            print(event.content)


if __name__ == "__main__":
    q = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_Q
    print(f"Q: {q}\n")
    asyncio.run(main(q))
