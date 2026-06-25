"""KAG retrieval tool: NL question -> Cypher (Gemini) -> Neo4j -> result.
Generated Cypher is non-deterministic, so retry and keep the first non-empty query."""
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

CYPHER_PROMPT = """You write ONE Cypher query for this Neo4j graph, then stop.
__SCHEMA__

Rules:
- The graph has ONE node label: :Entity. Match nodes by their `name`, e.g.
  (c {name:'PixelKit'}). Never use a type as a label like (:Person); no type filters.
- Match relationships WITHOUT a direction arrow: write -[:REL]- , not -[:REL]-> .
  Names are unique, so this never hits the wrong node and it works no matter which
  way an edge is stored.
- The question may chain several hops ("who Xs the Y of the Z that Ws?"). Resolve
  EVERY hop and return only the entity finally asked for; never stop at an
  intermediate node.
- Return ONLY the Cypher query, no markdown.

Worked example:
  Q: Who teaches the prerequisite for the course that uses PixelKit?
  A: MATCH (t {name:'PixelKit'})-[:USES]-(course)-[:PREREQUISITE_FOR]-(prereq)-[:TEACHES]-(teacher) RETURN teacher.name

Question: __QUESTION__"""


def _live_schema() -> str:
    with _driver.session() as s:
        edges = [
            f"{r['a']} -[:{r['rel']}]- {r['b']}"
            for r in s.run(
                "MATCH (a)-[r]->(b) "
                "RETURN a.name AS a, type(r) AS rel, b.name AS b "
                "ORDER BY a, rel, b LIMIT 60"
            )
        ]
    return (
        "All nodes share one label, :Entity, with a `name` property.\n"
        "Relationships present (match by name, direction does not matter):\n"
        + "\n".join("  " + e for e in edges)
    )


def _gen_cypher(question, schema):
    resp = _model.generate_content(
        CYPHER_PROMPT.replace("__SCHEMA__", schema).replace("__QUESTION__", question)
    )
    return (
        resp.text.strip()
        .removeprefix("```cypher")
        .removeprefix("```")
        .removesuffix("```")
        .strip()
    )


def query_graph(question: str) -> str:
    """Answer relational questions via the graph; retry flaky Cypher up to 5x."""
    schema = _live_schema()
    cypher = ""
    for _ in range(5):
        cypher = _gen_cypher(question, schema)
        with _driver.session() as s:
            rows = [r.data() for r in s.run(cypher)]
        if rows:
            return f"Cypher: {cypher}\nResult: {rows}"
    return f"Cypher: {cypher}\nResult: []"
