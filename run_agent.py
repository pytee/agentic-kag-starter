"""Headless runner for the KAG agent (no web UI needed).

Run:  python run_agent.py
Optionally pass your own question:
      python run_agent.py "Who leads the Vision Lab?"
"""
import sys
import asyncio
from google.adk.runners import InMemoryRunner
from google.genai import types

try:
    from kag_agent.agent import root_agent   # after step 4.1 (agent wrapped in a package)
except ModuleNotFoundError:
    from agent import root_agent              # before step 4.1 (agent.py at repo root)

DEFAULT_Q = "Who teaches the prerequisite for the course that uses PixelKit?"


async def main(question: str):
    runner = InMemoryRunner(agent=root_agent)
    # ADK needs the session to exist before you send a message to it
    await runner.session_service.create_session(
        app_name=runner.app_name, user_id="student", session_id="s1"
    )
    # run_async expects a Content object, not a bare string
    message = types.Content(role="user", parts=[types.Part(text=question)])
    async for event in runner.run_async(
        user_id="student", session_id="s1", new_message=message
    ):
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.text:
                    print(part.text)


if __name__ == "__main__":
    q = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_Q
    print(f"Q: {q}\n")
    asyncio.run(main(q))
