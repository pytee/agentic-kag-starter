"""RAG baseline: embed the same corpus with Vertex AI embeddings, store in
Chroma, and retrieve by semantic similarity. This is the thing KAG competes with.

Quick test:
  python -c "from vector_tool import query_vectors; \
print(query_vectors('Who teaches the prerequisite for the course that uses PixelKit?'))"
"""
import chromadb
import vertexai
from vertexai.language_models import TextEmbeddingModel
from corpus import DOCUMENTS
from config import PROJECT, LOCATION

# Use the same vertexai SDK as graph_tool — it authenticates cleanly in Cloud
# Shell. LangChain's VertexAIEmbeddings routes through the google.genai client,
# which fails here with "service account info is missing 'email' field".
vertexai.init(project=PROJECT, location=LOCATION)
_embed_model = TextEmbeddingModel.from_pretrained("text-embedding-005")


def _embed(texts):
    return [e.values for e in _embed_model.get_embeddings(texts)]


_client = chromadb.Client()
_collection = _client.get_or_create_collection("corpus")

# index once at import
_collection.upsert(
    ids=[d["id"] for d in DOCUMENTS],
    documents=[d["text"] for d in DOCUMENTS],
    embeddings=_embed([d["text"] for d in DOCUMENTS]),
)


def query_vectors(question: str) -> str:
    """Answer fuzzy/descriptive questions by semantic similarity search."""
    qvec = _embed([question])[0]
    res = _collection.query(query_embeddings=[qvec], n_results=2)
    return "\n---\n".join(res["documents"][0])
