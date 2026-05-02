# BIS Standards Recommendation Engine
### Accelerating MSE Compliance — Automating BIS Standard Discovery for Building Materials

An AI-powered RAG (Retrieval-Augmented Generation) system that maps product descriptions to the most applicable Bureau of Indian Standards (BIS) for building materials — in seconds, across 10 Indian languages.

---

## Live Demo

Deploy on [Streamlit Cloud](https://streamlit.io/cloud) (free):
1. Fork this repo
2. Go to share.streamlit.io → New app → point to `app.py`
3. Add secrets: `GROQ_API_KEY` and `SARVAM_API_KEY`

---

## Features

| Feature | Description |
|---------|-------------|
| RAG Pipeline | FAISS vector search + Llama-3.1-8B rationale generation |
| 39 BIS Standards | Cement, Steel, Concrete, Aggregates, Masonry, Structural |
| Multilingual | 10 Indian languages via Sarvam AI (Hindi, Tamil, Telugu, Kannada, Malayalam, Bengali, Marathi, Gujarati, Punjabi, Odia) |
| Voice Input | Speech-to-text via Sarvam AI Saarika ASR |
| Voice Output | Text-to-speech via Sarvam AI Bulbul TTS |
| Top 3–5 Standards | With rationale and key compliance requirements |
| Download | Export results as JSON |

---

## Repository Structure

```
hackathon/
├── src/                    # Main application logic
│   ├── __init__.py
│   ├── data_loader.py      # Loads BIS standards JSON
│   ├── embeddings.py       # sentence-transformers encoder
│   ├── retriever.py        # FAISS vector retriever
│   ├── llm_client.py       # Groq/LLM rationale generator
│   ├── translator.py       # Sarvam AI translation + voice
│   └── rag_pipeline.py     # End-to-end RAG pipeline
├── data/
│   ├── bis_standards.json  # 39 BIS standards dataset
│   └── sample_queries.json # Sample test queries
├── faiss_index/            # Auto-generated on first run
├── .streamlit/
│   └── config.toml         # Streamlit dark theme
├── app.py                  # Streamlit web application
├── build_index.py          # Pre-build FAISS index (optional)
├── inference.py            # Judge entry-point script
├── eval_script.py          # Evaluation metrics script
├── requirements.txt
├── .env.example
└── README.md
```

---

## Quick Start

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Set up API keys
```bash
cp .env.example .env
# Edit .env and add your keys
```

Or set environment variables:
```bash
export GROQ_API_KEY=your_groq_key      # https://console.groq.com (free)
export SARVAM_API_KEY=your_sarvam_key  # https://dashboard.sarvam.ai
```

> **Note:** Both keys are optional for basic operation. Without them the system uses rule-based rationale and skips translation/voice.

### 3. (Optional) Pre-build FAISS index
```bash
python build_index.py
```
The index is built automatically on first run if not present.

### 4. Run the Streamlit app
```bash
streamlit run app.py
```

---

## Judge Evaluation

### Running inference
```bash
python inference.py --input hidden_private_dataset.json --output team_results.json
```

**Input format:**
```json
[{"id": "q1", "query": "OPC 43 cement for multi-storey building"}, ...]
```

**Output format:**
```json
[{"id": "q1", "retrieved_standards": ["IS 8112:2013", "IS 456:2000"], "latency_seconds": 0.123}, ...]
```

### Running evaluation
```bash
python eval_script.py --results team_results.json --ground_truth ground_truth.json
```

**Metrics reported:**
- **Hit Rate @3** — fraction of queries with a correct standard in top-3
- **MRR @5** — Mean Reciprocal Rank in top-5
- **Avg Latency** — average response time in seconds

---

## BIS Standards Covered

### Cement (8 standards)
IS 269, IS 8112, IS 12269, IS 1489 (P1 & P2), IS 455, IS 6452, IS 12600

### Steel (5 standards)
IS 1786, IS 432, IS 2062, IS 808, IS 3502

### Concrete (7 standards)
IS 456, IS 10262, IS 516, IS 9103, IS 3812, IS 13311 (P1 & P2)

### Aggregates (5 standards)
IS 383, IS 2386 (P1, P3, P4), IS 515

### Masonry (6 standards)
IS 1077, IS 3952, IS 2185, IS 4139, IS 2212, IS 12894

### Structural/General (8 standards)
IS 875 (P1, P2, P3), IS 1893, IS 13920, IS 2950, IS 4082

---

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Frontend | Streamlit |
| Embeddings | sentence-transformers/all-MiniLM-L6-v2 |
| Vector Store | FAISS IndexFlatIP (cosine similarity) |
| LLM | Groq API / Llama-3.1-8B-Instant |
| Translation | Sarvam AI mayura:v1 |
| ASR (Voice Input) | Sarvam AI saarika:v1 |
| TTS (Voice Output) | Sarvam AI bulbul:v1 |

---

## Theme
**Accelerating MSE Compliance — Automating BIS Standard Discovery**

Hackathon focus: Building Materials (Cement · Steel · Concrete · Aggregates · Masonry)
