"""KAG retrieval tool: turn a natural-language question into a Cypher query
with Gemini, run it against Neo4j, and return the result.

Quick test:
  python -c "from graph_tool import query_graph; \
print(query_graph('Who teaches the prerequisite for the course that uses PixelKit?'))"
"""
import vertexai
from vertexai.generative_models import GenerativeModel
from neo4j import GraphDatabase
from config import (
    PROJECT, LOCATION, GEMINI_MODEL,
    NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD,
)

vertexai.init(project=PROJECT, location=LOCATION)
_model = GenerativeModel(GEMINI_MODEL)
_driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))

SCHEMA = """Nodes: (:Entity {name, type})
Relationships: TEACHES, LEADS, BUILT, USES, STUDIED_AT,
PREREQUISITE_FOR, SUPERVISES, ALUMNUS_OF (all directed source->target)"""

CYPHER_PROMPT = """Given this Neo4j schema:
{schema}
Write ONE Cypher query answering the question. Return ONLY the query, no markdown.
Question: {q}"""


def query_graph(question: str) -> str:
    """Answer relational questions by querying the Neo4j knowledge graph."""
    resp = _model.generate_content(CYPHER_PROMPT.format(schema=SCHEMA, q=question))
    cypher = (
        resp.text.strip()
        .removeprefix("```cypher")
        .removeprefix("```")
        .removesuffix("```")
        .strip()
    )
    with _driver.session() as s:
        rows = [r.data() for r in s.run(cypher)]
    return f"Cypher: {cypher}\nResult: {rows}"
