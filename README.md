# BIS Standards Recommendation Engine
### Accelerating MSE Compliance — Automating BIS Standard Discovery for Building Materials

An AI-powered RAG (Retrieval-Augmented Generation) system that maps product descriptions to the most applicable Bureau of Indian Standards (BIS) for building materials — in seconds, across 11 Indian languages with full voice support.

---

## Live Demo

Demo video and PPT — [View here](https://drive.google.com/drive/folders/11oLCd4YqHXkvmGSgFwzhUwG3VnDWESpZ?usp=drive_link)

Live App — [hackathongit-5sbttvasahsfw3nkthdf2y.streamlit.app](https://hackathongit-5sbttvasahsfw3nkthdf2y.streamlit.app/)

Deploy on [Streamlit Cloud](https://streamlit.io/cloud) (free):
1. Fork this repo
2. Go to share.streamlit.io → New app → point to `app.py`
3. Add secrets: `DATABRICKS_TOKEN` and `SARVAM_API_KEY`

---

## Features

| Feature | Description |
|---------|-------------|
| RAG Pipeline | FAISS vector search + Llama-3.1-8B-Instruct rationale generation |
| 441 BIS Standards | 25+ categories from the full BIS building materials dataset |
| Multilingual | 11 Indian languages via Sarvam AI — Hindi, Tamil, Telugu, Kannada, Malayalam, Bengali, Marathi, Gujarati, Punjabi, Odia, English |
| Voice Input | Speech-to-text via Sarvam AI Saarika ASR (saarika:v2.5) |
| Voice Output | Text-to-speech via Sarvam AI Bulbul TTS (bulbul:v2) with WAV chunking |
| Sidebar API Keys | Enter Databricks and Sarvam keys at runtime — no config files needed |
| Top 3–5 Standards | With AI rationale and key compliance requirements |
| Download | Export results as JSON |

---

## Complete RAG Architecture

```
                         USER INPUT
                      (text or voice)
                             │
             ┌───────────────┴───────────────┐
             │                               │
        ✍️ Text Input                  🎙️ Voice Input
             │                               │
             │                    ┌──────────▼──────────┐
             │                    │   Sarvam ASR         │
             │                    │   saarika:v2.5       │
             │                    │  (audio → text)      │
             │                    └──────────┬──────────┘
             │                               │
             └───────────────┬───────────────┘
                             │
                    Non-English input?
                       Yes │       No
                           │        │
              ┌────────────▼──────┐ │
              │  Sarvam Translate  │ │
              │   mayura:v1       │ │
              │  (lang → English) │ │
              └────────────┬──────┘ │
                           └────────┘
                                │
                          English Query
                                │
                    ┌───────────▼───────────┐
                    │   Embedding Encoder    │
                    │  all-MiniLM-L6-v2     │
                    │  (text → 384-dim vec) │
                    └───────────┬───────────┘
                                │
                    ┌───────────▼───────────┐
                    │    FAISS Vector DB     │
                    │   IndexFlatIP          │
                    │  441 BIS standards     │
                    │  Cosine similarity     │
                    │  Top-K retrieval       │
                    └───────────┬───────────┘
                                │
                    Top-K candidate standards
                    (standard_number, title,
                     scope, key_requirements)
                                │
                    ┌───────────▼───────────┐
                    │    Databricks LLM      │
                    │  Llama-3.1-8B-Instruct │
                    │  OpenAI-compatible API │
                    │  Generates rationale   │
                    │  for each standard     │
                    └───────────┬───────────┘
                                │
                      Ranked Results with
                      Rationale + Key Req.
                                │
                    Non-English output?
                       Yes │       No
                           │        │
              ┌────────────▼──────┐ │
              │  Sarvam Translate  │ │
              │   mayura:v1       │ │
              │  (English → lang) │ │
              └────────────┬──────┘ │
                           └────────┘
                                │
                     Final Ranked Results
                                │
              ┌─────────────────┴──────────────────┐
              │                                    │
         📄 Display                        🔊 Voice Output
         (Streamlit UI)              ┌─────────────▼──────────┐
                                     │   Sarvam TTS            │
                                     │   bulbul:v2             │
                                     │  Text split ≤480 chars  │
                                     │  WAV chunks concatenated│
                                     └────────────────────────┘
```

### Pipeline Component Breakdown

| Stage | Component | Model / Tool | Notes |
|-------|-----------|--------------|-------|
| Voice Input | Sarvam ASR | saarika:v2.5 | Converts recorded audio to text |
| Translation IN | Sarvam Translate | mayura:v1 | Any Indian language → English |
| Embedding | sentence-transformers | all-MiniLM-L6-v2 | 384-dim dense vectors |
| Vector Search | FAISS | IndexFlatIP | L2-normalised cosine similarity |
| LLM Rationale | Databricks | Llama-3.1-8B-Instruct | OpenAI-compatible endpoint |
| Translation OUT | Sarvam Translate | mayura:v1 | English → selected language |
| Voice Output | Sarvam TTS | bulbul:v2 | WAV chunks joined with `wave` module |

---

## Repository Structure

```
hackathon/
├── src/
│   ├── __init__.py
│   ├── data_loader.py      # Loads bis_standards.json, builds embedding texts
│   ├── embeddings.py       # sentence-transformers encoder (all-MiniLM-L6-v2)
│   ├── retriever.py        # FAISS IndexFlatIP vector retriever
│   ├── llm_client.py       # Databricks/Llama rationale generator
│   ├── translator.py       # Sarvam AI: translate, STT (saarika:v2.5), TTS (bulbul:v2)
│   └── rag_pipeline.py     # End-to-end RAG pipeline
├── data/
│   ├── bis_standards.json          # 441 BIS standards (generated from CSV)
│   ├── indian_standards_dataset.csv # Source dataset
│   └── public_test_set.json        # Sample test queries (hackathon format)
├── faiss_index/
│   ├── index.faiss         # Pre-built FAISS index (441 standards)
│   └── metadata.json       # Standard metadata for retrieval
├── .streamlit/
│   └── secrets.toml        # API key template (not committed)
├── app.py                  # Streamlit web application
├── build_index.py          # Pre-build FAISS index (run after updating data)
├── convert_csv.py          # One-time: converts CSV → bis_standards.json
├── inference.py            # Judge entry-point: --input / --output
├── eval_script.py          # Evaluation: Hit Rate @3, MRR @5, Avg Latency
├── requirements.txt
└── README.md
```

---

## Quick Start

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Set API keys

**Option A — Streamlit secrets** (for deployment):
```toml
# .streamlit/secrets.toml
DATABRICKS_TOKEN = "dapi..."
SARVAM_API_KEY   = "sk-..."
```

**Option B — Environment variables**:
```bash
export DATABRICKS_TOKEN=your_databricks_token
export SARVAM_API_KEY=your_sarvam_key
```

**Option C — Sidebar at runtime**: Enter keys directly in the app sidebar. No files needed.

> Both keys are optional for basic operation. Without them the system uses rule-based rationale and skips translation/voice.

### 3. (Optional) Pre-build FAISS index
```bash
python build_index.py
```
The index is built automatically on first run if not present.

### 4. Run the app
```bash
streamlit run app.py
```

---

## Judge Evaluation

### Running inference
```bash
python inference.py --input public_test_set.json --output team_results.json --top_k 5
```

**Input format:**
```json
[
  {
    "id": "PUB-01",
    "query": "OPC 43 grade cement for multi-storey RCC building",
    "expected_standards": ["IS 8112:2013"]
  }
]
```

**Output format:**
```json
[
  {
    "id": "PUB-01",
    "query": "OPC 43 grade cement for multi-storey RCC building",
    "expected_standards": ["IS 8112:2013"],
    "retrieved_standards": ["IS 8112:2013", "IS 269:2015", "IS 12269:2013"],
    "latency_seconds": 0.84
  }
]
```

### Running evaluation
```bash
python eval_script.py --results team_results.json
```

**Metrics reported:**
- **Hit Rate @3** — fraction of queries where a ground-truth standard appears in top-3
- **MRR @5** — Mean Reciprocal Rank of the first relevant result in top-5
- **Avg Latency** — average `latency_seconds` across all queries

### Results on Public Test Set (10 queries)

| Metric | Score | Threshold |
|--------|-------|-----------|
| Hit Rate @3 | 100% | >80% |
| MRR @5 | 1.000 | >0.7 |
| Avg Latency | 1.42s (warm: 0.011s) | <5s |

---

## BIS Standards Covered (441 total)

| Category | Examples |
|----------|---------|
| Cement and Concrete | IS 269, IS 8112, IS 12269, IS 1489, IS 456 |
| Structural Steels | IS 1786, IS 2062, IS 432, IS 808 |
| Concrete Reinforcement | IS 1139, IS 1566 |
| Stones | IS 1121, IS 3620 |
| Wood Products for Building | IS 303, IS 710, IS 1328 |
| Timber | IS 287, IS 883 |
| Bitumen and Tar Products | IS 73, IS 217 |
| Floor, Wall, Roof Coverings | IS 777, IS 1237, IS 13006 |
| Water Proofing Materials | IS 1322, IS 1580 |
| Sanitary Appliances & Water Fittings | IS 771, IS 1795, IS 2326 |
| Glass | IS 2553, IS 5437 |
| Plastics | IS 4985, IS 12235 |
| Thermal Insulation | IS 3677, IS 8183 |
| Conductors and Cables | IS 694, IS 1554 |
| Doors, Windows and Shutters | IS 1038, IS 4021 |
| Builder's Hardware | IS 205, IS 729 |
| + 10 more categories | ... |

---

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Frontend | Streamlit |
| Embeddings | sentence-transformers / all-MiniLM-L6-v2 |
| Vector Store | FAISS IndexFlatIP (cosine similarity) |
| LLM | Databricks / Llama-3.1-8B-Instruct |
| Translation | Sarvam AI mayura:v1 (11 Indian languages) |
| ASR (Voice Input) | Sarvam AI saarika:v2.5 |
| TTS (Voice Output) | Sarvam AI bulbul:v2 |
| Deployment | Streamlit Cloud |

---

## Supported Languages

| Language | Code |
|----------|------|
| English | en-IN |
| Hindi | hi-IN |
| Tamil | ta-IN |
| Telugu | te-IN |
| Kannada | kn-IN |
| Malayalam | ml-IN |
| Bengali | bn-IN |
| Marathi | mr-IN |
| Gujarati | gu-IN |
| Punjabi | pa-IN |
| Odia | od-IN |

---

## Theme
**Accelerating MSE Compliance — Automating BIS Standard Discovery**

Indian Micro and Small Enterprises (MSEs) in the construction materials sector must comply with BIS standards under the BIS Act, 2016. This system removes the manual effort of identifying applicable standards — enter a product description in any Indian language and get the top BIS standards with rationale in seconds.
