"""Central configuration. Reads from environment / .env file."""
import os
from dotenv import load_dotenv

load_dotenv()

PROJECT = os.environ["GOOGLE_CLOUD_PROJECT"]
LOCATION = os.environ["GOOGLE_CLOUD_LOCATION"]
GEMINI_MODEL = "gemini-2.5-flash-lite"   # cheapest current model, ideal for a workshop
# Note: gemini-2.0-flash was deprecated 2026-06-01. If a model string ever fails,
# list what's live in your project/region:
#   gcloud ai models list --region=$GOOGLE_CLOUD_LOCATION

NEO4J_URI = os.environ["NEO4J_URI"]
NEO4J_USERNAME = os.environ["NEO4J_USERNAME"]
NEO4J_PASSWORD = os.environ["NEO4J_PASSWORD"]
