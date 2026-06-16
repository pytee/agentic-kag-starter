"""Extract triples from every document and MERGE them into Neo4j AuraDB.

Run:  python build_graph.py
Then in the Neo4j console:  MATCH (n)-[r]->(m) RETURN n,r,m
"""
from neo4j import GraphDatabase
from config import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD
from corpus import DOCUMENTS
from extract import extract

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))


def build():
    with driver.session() as s:
        s.run("MATCH (n) DETACH DELETE n")            # start clean
        for doc in DOCUMENTS:
            g = extract(doc["text"])
            for e in g["entities"]:
                s.run(
                    "MERGE (n:Entity {name:$n}) SET n.type=$t",
                    n=e["name"], t=e["type"],
                )
            for r in g["relationships"]:
                rel = "".join(c for c in r["relation"] if c.isalnum() or c == "_").upper()
                s.run(
                    f"MATCH (a:Entity {{name:$s}}),(b:Entity {{name:$t}}) "
                    f"MERGE (a)-[:{rel}]->(b)",
                    s=r["source"], t=r["target"],
                )
            print(f"  loaded {doc['id']}")


if __name__ == "__main__":
    build()
    print("Done. In the Neo4j console run: MATCH (n)-[r]->(m) RETURN n,r,m")
