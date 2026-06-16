"""Use Gemini on Vertex AI to extract a knowledge graph (entities + relationships)
from a piece of unstructured text, returned as JSON."""
import json
import vertexai
from vertexai.generative_models import GenerativeModel
from config import PROJECT, LOCATION, GEMINI_MODEL

vertexai.init(project=PROJECT, location=LOCATION)
model = GenerativeModel(GEMINI_MODEL)

PROMPT = """Extract a knowledge graph from the text as JSON only (no markdown).
Shape:
{{"entities":[{{"name":"...","type":"Person|Course|Lab|Tool|University"}}],
 "relationships":[{{"source":"...","relation":"UPPER_SNAKE","target":"..."}}]}}

Rules:
- Canonical names (e.g. "Dr. Lina Cheong", never "she").
- Relations are short verbs: TEACHES, LEADS, BUILT, USES, STUDIED_AT,
  PREREQUISITE_FOR, SUPERVISES, ALUMNUS_OF.
- Only facts stated in the text.

TEXT:
{text}"""


def extract(text: str) -> dict:
    resp = model.generate_content(PROMPT.format(text=text))
    raw = (
        resp.text.strip()
        .removeprefix("```json")
        .removeprefix("```")
        .removesuffix("```")
        .strip()
    )
    return json.loads(raw)
