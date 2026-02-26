# 📚 Paige — Personal Book Advisor

An AI-powered conversational book advisor built with **A2A (Agent2Agent) Protocol**, **LangChain**, **ChromaDB**, and **HuggingFace Mistral**. Talk to Paige via text or voice — she remembers what you've read, learns your preferences, and recommends books tailored specifically to you.

---

## ✨ Features

- 🎙️ **Voice + Text input** — speak or type your queries
- 🔊 **Voice responses** — Paige reads her answers back to you
- 📖 **Personalised recommendations** — based on your reading history stored in ChromaDB
- 🔍 **Real-time book search** — live data from OpenLibrary API (free, no key needed)
- 🧠 **Memory across sessions** — ChromaDB persists your liked/disliked/wishlist data on disk
- 🔌 **Multi-domain ready** — add Products or Courses advisor with minimal changes
- 🤖 **A2A Protocol** — agents communicate via open Agent2Agent standard

---

## 🏗️ Architecture

```
User (Text / Voice)
       ↓
[Whisper STT]  ←  speech-to-text (runs locally, CPU)
       ↓
┌─────────────────────────────────────┐
│         Streamlit UI                │
│   (chat history + mic + audio)      │
└──────────────┬──────────────────────┘
               ↓
┌─────────────────────────────────────┐
│       Orchestrator / Router         │  ← A2A Client
│   Detects domain → routes query     │
└──────────────┬──────────────────────┘
               │  A2A Protocol (JSON-RPC over HTTP)
               ↓
┌─────────────────────────────────────┐
│     Books Agent  (port 8001)        │  ← A2A Remote Agent
│                                     │
│  LLM : Mistral-7B (HF Router API)  │
│  Tools:                             │
│  ├─ add_to_liked                    │──► ChromaDB
│  ├─ add_to_disliked                 │──► ChromaDB
│  ├─ add_to_wishlist                 │──► ChromaDB
│  ├─ mark_not_interested             │──► ChromaDB
│  ├─ search_preferences              │──► ChromaDB (vector search)
│  ├─ get_my_list                     │──► ChromaDB
│  └─ search_book_api                 │──► OpenLibrary API
└─────────────────────────────────────┘
               ↓
[pyttsx3 TTS]  ←  text-to-speech (runs locally)
       ↓
User hears response
```

---

## 🗂️ Project Structure

```
book_advisor/
├── main.py                    # Entry point — boots agent server + Streamlit
├── requirements.txt
├── .env.example
│
├── config/
│   └── settings.py            # All config: HF token, model names, ports, paths
│
├── core/
│   ├── embeddings.py          # all-MiniLM-L6-v2 (local, 384-dim vectors)
│   ├── vector_store.py        # ChromaDB: add / vector search / get all
│   └── base_domain.py         # Abstract interface all domains must implement
│
├── agents/
│   └── books/
│       ├── agent.py           # LangChain ReAct agent + HFRouterLLM
│       ├── server.py          # Wraps agent as A2A server (port 8001)
│       ├── tools.py           # 7 LangChain @tool functions
│       ├── api_client.py      # OpenLibrary API client
│       └── prompts.py         # Paige's system prompt + rules
│
├── orchestrator/
│   ├── network.py             # AgentNetwork — registers all domain agents
│   └── router.py              # AdvisorRouter — A2A client routing logic
│
├── voice/
│   ├── stt.py                 # Whisper tiny (local, CPU-friendly)
│   └── tts.py                 # pyttsx3 TTS (local, no internet)
│
├── ui/
│   └── app.py                 # Streamlit chat UI
│
└── data/
    └── chromadb/              # Persistent vector DB (auto-created on first run)
```

---

## 🛠️ Tech Stack

| Component        | Technology                              | Notes                          |
|------------------|-----------------------------------------|--------------------------------|
| A2A Framework    | `python-a2a` 0.5.0                      | Agent discovery + routing      |
| Agent Framework  | LangChain 0.3.x                         | ReAct pattern + tools          |
| LLM              | Mistral-7B-Instruct via HF Router API   | Free HuggingFace inference     |
| Embeddings       | `all-MiniLM-L6-v2` (sentence-transformers) | Runs 100% locally           |
| Vector DB        | ChromaDB (persistent)                   | Cosine similarity search       |
| Book Data        | OpenLibrary API                         | Free, no API key required      |
| Speech-to-Text   | OpenAI Whisper `tiny` (local)           | CPU-friendly                   |
| Text-to-Speech   | pyttsx3                                 | Local, no internet needed      |
| UI               | Streamlit                               | Chat interface + mic button    |

---

## ⚙️ Setup & Installation

### Prerequisites
- Python 3.11.x (3.12+ not recommended — AI/ML library compatibility)
- HuggingFace account with API token

### 1. Clone / download the project
```bash
cd book_advisor
```

### 2. Create virtual environment with Python 3.11
```bash
py -3.11 -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate      # Linux / macOS
```

### 3. Install dependencies
```bash
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

> **Linux only:** `sudo apt install espeak-ng` (required for pyttsx3 TTS)

### 4. Configure environment
```bash
copy .env.example .env        # Windows
cp .env.example .env          # Linux / macOS
```
Open `.env` and add your HuggingFace API token:
```
HF_API_TOKEN=hf_xxxxxxxxxxxxxxxxxxxx
```

### 5. Run
```bash
python main.py
```

Open your browser at **http://localhost:8501**

---

## 💬 Example Conversations

```
You:   I just finished Atomic Habits and loved it
Paige: Great! I've added Atomic Habits to your liked list. It's
       a fantastic book on habit formation!

You:   Recommend something similar
Paige: Based on your love of Atomic Habits, I think you'd enjoy
       "The Power of Habit" by Charles Duhigg — it covers the
       neuroscience behind why habits form and how to change them.

You:   Show me my wishlist
Paige: Your wishlist (1 book):
         • The Lean Startup

You:   What is the capital of France?
Paige: I'm Paige, your personal book advisor! I can only help
       with book recommendations and your reading list. 📚
```

---

## 🔌 Adding a New Domain (e.g. Products)

The architecture is designed for zero-friction expansion:

```bash
cp -r agents/books/ agents/products/
```

Then change **4 things** inside `agents/products/`:
1. `prompts.py` → update personality to product advisor
2. `api_client.py` → call a products API
3. `tools.py` → change `DOMAIN = "products"`, rename `search_book_api`
4. `server.py` → change port to `settings.PRODUCTS_AGENT_PORT`

Then in `orchestrator/network.py`, **uncomment one line**:
```python
network.add("products", f"http://localhost:{settings.PRODUCTS_AGENT_PORT}")
```

**That's it.** All other files remain untouched.

---

## 🧠 How the A2A Protocol Works Here

1. **Startup** — Books Agent starts on port 8001 and serves its Agent Card at `/.well-known/agent.json`
2. **Discovery** — Orchestrator fetches the Agent Card and learns what the Books Agent can do
3. **Routing** — Every user query goes through `AdvisorRouter` which selects the correct domain agent
4. **Communication** — Orchestrator sends the query via `A2AClient.ask()` (JSON-RPC over HTTP)
5. **Execution** — Books Agent runs the LangChain ReAct loop: Thought → Tool Call → Observation → Answer
6. **Response** — Answer streams back to the Orchestrator → Streamlit renders it → pyttsx3 speaks it

---

## 📝 Known Limitations (Prototype)

- Voice input requires `audio-recorder-streamlit` browser microphone permission
- Whisper `tiny` model has lower accuracy for non-English or heavily accented speech — upgrade to `base` for better results
- HuggingFace free inference tier has rate limits (~30 req/min) — sufficient for personal use
- ChromaDB cold start — recommendations improve as you add more books to your history

---

## 📄 License

MIT — free to use, modify, and extend.
