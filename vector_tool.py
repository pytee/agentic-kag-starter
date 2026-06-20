"""RAG baseline: embed the same corpus with Vertex AI embeddings, store in
Chroma, and retrieve by semantic similarity. This is the thing KAG competes with.

Quick test:
  python -c "from vector_tool import query_vectors; \
print(query_vectors('Who teaches the prerequisite for the course that uses PixelKit?'))"
"""
import chromadb
from langchain_google_vertexai import VertexAIEmbeddings
from corpus import DOCUMENTS
from config import PROJECT, LOCATION

_embed = VertexAIEmbeddings(
    model_name="text-embedding-005", project=PROJECT, location=LOCATION
)
_client = chromadb.Client()
_collection = _client.get_or_create_collection("corpus")

# index once at import
_collection.upsert(
    ids=[d["id"] for d in DOCUMENTS],
    documents=[d["text"] for d in DOCUMENTS],
    embeddings=_embed.embed_documents([d["text"] for d in DOCUMENTS]),
)


def query_vectors(question: str) -> str:
    """Answer open-ended DESCRIPTIVE questions by semantic similarity search.

    Use only when there is no specific relationship to traverse, e.g. 'what does
    Coastal Tech specialize in?' or 'describe the robotics program'. For who/what
    is connected to a named entity, use query_graph instead.
    """
    qvec = _embed.embed_query(question)
    res = _collection.query(query_embeddings=[qvec], n_results=2)
    return "\n---\n".join(res["documents"][0])
