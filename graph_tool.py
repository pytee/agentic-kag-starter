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

CYPHER_PROMPT = """Given this Neo4j schema:
{schema}
Write ONE Cypher query answering the question. Return ONLY the query, no markdown.
Question: {q}"""


def _live_schema() -> str:
    """Ground the Cypher prompt in the REAL graph. LLM extraction is
    non-deterministic — it may emit USED_IN instead of USES, or flip a
    direction — so a hardcoded schema quickly drifts from what was built.
    Reading the live relationship names and edges keeps them in sync."""
    with _driver.session() as s:
        rels = [r["relationshipType"] for r in s.run("CALL db.relationshipTypes()")]
        edges = [
            f'{r["a"]} -[:{r["rel"]}]-> {r["b"]}'
            for r in s.run(
                "MATCH (a)-[r]->(b) "
                "RETURN a.name AS a, type(r) AS rel, b.name AS b LIMIT 40"
            )
        ]
    return (
        "Nodes are (:Entity {name, type}); match nodes by their name.\n"
        f"Relationship types: {', '.join(rels)}\n"
        "Actual edges (use these exact names AND directions):\n"
        + "\n".join(edges)
    )


def query_graph(question: str) -> str:
    """Answer relational questions by querying the Neo4j knowledge graph."""
    resp = _model.generate_content(CYPHER_PROMPT.format(schema=_live_schema(), q=question))
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
