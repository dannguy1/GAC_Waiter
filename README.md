# 🍽️ GAC Waiter - Digital Waiter System

A voice-enabled AI waiter for **Garlic & Chives** restaurant, featuring intelligent menu navigation, multi-language support, and text-to-speech capabilities.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.10%2B-green.svg)
![Streamlit](https://img.shields.io/badge/streamlit-1.0%2B-red.svg)

---

## ✨ Features

- **🤖 AI-Powered Conversations** - Natural language ordering powered by LLM
- **🔍 Smart Menu Search** - Hybrid semantic + keyword search (RAG)
- **🌐 Multi-Language Support** - English, Vietnamese, Chinese, Spanish
- **🔊 Text-to-Speech** - Hear responses in natural voice
- **📱 Responsive UI** - Works on tablets and touchscreens
- **⚠️ Allergy Tracking** - Safety-first order management
- **📝 Special Notes** - Captures dietary preferences and time constraints

---

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- 8GB RAM minimum
- Internet connection (for cloud LLM)

### Installation

```bash
# Clone repository
git clone https://github.com/your-org/GAC_Waiter.git
cd GAC_Waiter

# Run installer
./install.sh

# Configure LLM (edit .env)
nano .env

# Start system
./scripts/start.sh
```

Access at: **http://localhost:8501**

---

## 📋 Configuration

Edit `.env` file:

```env
# LLM Configuration (Groq recommended)
LLM_BASE_URL=https://api.groq.com/openai/v1
LLM_API_KEY=your_api_key
LLM_MODEL=llama-3.1-70b-versatile

# Server
APP_PORT=8501
API_PORT=8000
```

See [docs/INSTALLATION.md](docs/INSTALLATION.md) for full configuration options.

---

## 🍽️ Managing the Menu

You can update the menu at any time without restarting the server:

1.  **Edit** the source menu file: `data-original/menu.json`
2.  **Run** the update script:
    ```bash
    ./scripts/refresh_menu.sh
    ```
    This will sync the changes and hot-reload the backend database.

---

## 🏗️ Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Streamlit UI  │────▶│  FastAPI Backend│────▶│  LLM Provider   │
│   (Frontend)    │     │  (API Server)   │     │  (Groq/Ollama)  │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                               │
                   ┌───────────┴───────────┐
                   ▼                       ▼
          ┌─────────────────┐     ┌─────────────────┐
          │   RAG Retriever │     │   Piper TTS     │
          │  (FAISS+BM25)   │     │  (Voice Synth)  │
          └─────────────────┘     └─────────────────┘
```

---

## 📁 Project Structure

```
GAC_Waiter/
├── app.py                 # Frontend (Streamlit)
├── backend/
│   ├── api.py            # REST API
│   ├── agent.py          # LLM Agent
│   └── rag_retriever.py  # Search engine
├── data/
│   ├── menu.json         # Menu items
│   └── facts.json        # Restaurant info
├── models/piper/         # TTS voice models
├── scripts/              # Utility scripts
└── docs/                 # Documentation
```

---

## 🛠️ Scripts

| Script | Description |
|--------|-------------|
| `./install.sh` | Full installation |
| `./scripts/start.sh` | Start services |
| `./scripts/stop.sh` | Stop services |
| `./scripts/restart.sh` | Restart services |
| `./scripts/status.sh` | Check service status |
| `./scripts/refresh_menu.sh` | Hot-reload menu data (no restart) |

---

## 📚 Documentation

- [Installation Guide](docs/INSTALLATION.md) - Complete setup instructions
- [System Design](docs/System_Design.md) - Architecture documentation
- [Waiter Workflow](docs/waiter_workflow.md) - Agent behavior spec
- [RAG Integration](docs/RAG_Integration.md) - Search system details

---

## 🧪 Testing

```bash
# Test LLM connection
python scripts/verify_llm.py

# Test RAG retrieval
python test_rag.py

# View logs
tail -f api.log app.log
```

---

## 🔧 Troubleshooting

**Services won't start?**
```bash
./scripts/stop.sh
rm -f *.pid
./scripts/start.sh
```

**LLM not responding?**
- Check `.env` configuration
- Verify API key is valid
- Run `python scripts/verify_llm.py`

**TTS not working?**
```bash
chmod +x piper/piper
./piper/piper --version
```

---

## 📄 License

MIT License - See [LICENSE](LICENSE) for details.

---

## 🙏 Credits

- **LLM**: [Groq](https://groq.com) / [Ollama](https://ollama.ai)
- **TTS**: [Piper](https://github.com/rhasspy/piper)
- **UI**: [Streamlit](https://streamlit.io)
- **Search**: [FAISS](https://faiss.ai) + [BM25](https://github.com/dorianbrown/rank_bm25)

---

*Made with ❤️ for Garlic & Chives Restaurant*
