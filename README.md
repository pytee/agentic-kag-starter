# Agentic KAG Starter — Vertex AI · Neo4j · ADK

Starter code for the **"Build an Agentic KAG System on Vertex AI"** codelab.

You'll go from plain paragraphs to an AI agent that reasons over a **knowledge graph**,
falls back to **vector search** when it makes sense, and shows its work — built on
**Gemini** (Vertex AI), **Neo4j AuraDB**, **ChromaDB**, and Google's **Agent Development Kit (ADK)**.

> **RAG vs KAG in one line:** RAG retrieves text by *similarity* ("sounds like the question");
> KAG retrieves facts by *traversing relationships* in a graph. RAG is great for lookups and
> summaries; KAG wins on multi-hop reasoning, counting, and explainability. This project builds
> **both** and lets an agent choose per question.

---

## What it costs

Effectively **free**. The only paid component is Vertex AI (Gemini calls + embeddings) —
Neo4j AuraDB Free, Chroma, and Cloud Shell are all free.

- The corpus is tiny (3 short paragraphs), so a full run — extraction, graph queries,
  embeddings, and a dozen-plus agent turns with re-runs — uses on the order of
  ~100K input / ~30K output tokens.
- At **Gemini 2.5 Flash-Lite** rates ($0.10 / $0.40 per 1M tokens) that's about
  **$0.02–0.04 per student**, or roughly **$1 for a class of 30**.
- New Google Cloud accounts get **$300 free credits (90 days)**, and Flash models have a
  free daily request quota — so in practice this codelab usually costs **$0**.

Cost would only grow with a much larger corpus, chatty agent loops, or escalating to a
Pro-tier model — none of which this codelab does.

---

## What's in here

| File | What it does |
|------|--------------|
| `config.py` | Reads project / model / Neo4j settings from `.env` |
| `corpus.py` | Tiny sample dataset with a hidden multi-hop chain |
| `extract.py` | Gemini extracts entities + relationships as JSON |
| `build_graph.py` | Loads the extracted triples into Neo4j AuraDB |
| `graph_tool.py` | **KAG** retrieval: natural language → Cypher → answer |
| `vector_tool.py` | **RAG** baseline: Chroma + Vertex AI embeddings |
| `agent.py` | The ADK agent that chooses between the two tools |
| `run_agent.py` | Run the agent headless (no web UI) |
| `main.py` | Full pipeline: build → index → demo questions |

---

## Prerequisites

- **Python 3.10+**
- A **Google Cloud project** with billing enabled (free credits are fine)
- A free **Neo4j AuraDB** instance — sign up at [console.neo4j.io](https://console.neo4j.io)

Easiest environment is **Google Cloud Shell** (everything pre-installed, runs in the browser).

---

## Setup

### 1. Enable Vertex AI

```bash
gcloud services enable aiplatform.googleapis.com
```

### 2. Create a Neo4j AuraDB Free instance

At [console.neo4j.io](https://console.neo4j.io), create an **AuraDB Free** instance and
**download the credentials file when prompted** (the URI and password are shown only once).

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure your secrets

```bash
cp .env.example .env
# then edit .env with your project ID, region, and Neo4j credentials
```

Sanity check:

```bash
python -c "import config; print(config.PROJECT)"
```

If it prints your project ID, you're ready.

---

## Run it

### Option A — the whole pipeline at once

```bash
python main.py
```

This builds the graph, indexes the vectors, and runs three demo questions through the
agent so you can watch it route between the graph and vector tools.

### Option B — step by step (recommended for the codelab)

```bash
# 1. Build the knowledge graph from the corpus
python build_graph.py

# 2. (optional) Inspect it: open the AuraDB console -> Query, run:
#    MATCH (n)-[r]->(m) RETURN n,r,m

# 3. Try the KAG tool directly (multi-hop traversal)
python -c "from graph_tool import query_graph; print(query_graph('Who teaches the prerequisite for the course that uses PixelKit?'))"

# 4. Try the RAG baseline on the SAME question — see the difference
python -c "from vector_tool import query_vectors; print(query_vectors('Who teaches the prerequisite for the course that uses PixelKit?'))"

# 5. Run the agent (headless)
python run_agent.py
python run_agent.py "Who leads the Vision Lab?"
```

### Option C — the ADK web UI (with built-in trace view)

ADK's web UI expects the agent inside its own package folder. Quick setup:

```bash
mkdir kag_agent
cp agent.py kag_agent/agent.py
echo "from .agent import root_agent" > kag_agent/__init__.py
adk web
```

In Cloud Shell, click the **Web Preview** link, pick `kag_agent`, and ask away.
Open the **Events / Trace** tab on any response to see the agent's reasoning, which
tool it picked, the exact query it ran, and the timing of each step.

---

## Questions to try

| Question | Expected tool | Why |
|----------|---------------|-----|
| "What does Coastal Tech specialize in?" | `query_vectors` | Descriptive — answer sits in a passage |
| "Who leads the Vision Lab?" | `query_graph` | Single relationship lookup |
| "Who teaches the prerequisite for the course that uses PixelKit?" | `query_graph` | Multi-hop: PixelKit → Robotics → (prereq) ML → Lina |

The last one is the headline demo: the **graph traverses the chain reliably**, while
vector search only *happens* to work because the corpus is tiny. Add more documents and
the vector approach degrades while the graph keeps winning.

---

## Make it yours (extensions)

1. **Add a document** to `corpus.py`, rebuild, and find a question only the graph can answer.
2. **Trick the agent** into picking the wrong tool, then fix its `instruction` in `agent.py`.
3. **Hybrid mode**: have the agent call *both* tools and compare — when do they disagree?
4. **Bigger graph**: load a public dataset (movies, companies) and watch vector search degrade.

---

## Troubleshooting

- **`PermissionDenied` on Vertex AI** — re-run `gcloud services enable aiplatform.googleapis.com`
  and confirm the region in `.env` matches where Gemini is available.
- **Neo4j connection timeout** — the URI must start with `neo4j+s://`, and AuraDB Free instances
  *pause when idle*; open the console to wake it.
- **Empty Cypher result** — the extractor may have used a slightly different relation name.
  Open the graph, check the actual relationship types, and adjust `SCHEMA` in `graph_tool.py`.
- **Model not found** — list what's available and swap the name in `config.py`:
  ```bash
  gcloud ai models list --region=$GOOGLE_CLOUD_LOCATION
  ```

---

## Notes

- `.env` holds secrets and is gitignored — never commit it.
- Chroma here is in-memory and re-indexes on each run. For persistence, switch to
  `chromadb.PersistentClient(path=".chroma")` in `vector_tool.py`.
