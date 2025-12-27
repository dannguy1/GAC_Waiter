# 🍽️ GAC Waiter - Digital Waiter System

A voice-enabled AI waiter for **Garlic & Chives** restaurant, featuring intelligent menu navigation, multi-language support, and text-to-speech capabilities.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.10%2B-green.svg)
![Next.js](https://img.shields.io/badge/Next.js-16%2B-black.svg)

---

## ✨ Features

- **🤖 AI-Powered Conversations** - Natural language ordering powered by LLM
- **🔍 Smart Menu Search** - Hybrid semantic + keyword search (RAG)
- **🌐 Multi-Language Support** - English, Vietnamese, Chinese, Spanish
- **🔊 Text-to-Speech** - Hear AI responses with one click
- **📱 Responsive UI** - Mobile-first design, works on all devices
- **⚠️ Allergy Tracking** - Safety-first order management
- **📝 Special Notes** - Captures dietary preferences and time constraints
- **🛒 Smart Cart** - Chat-to-cart integration with fuzzy item matching

---

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Node.js 20+ (auto-installed by setup script)
- 8GB RAM minimum
- Internet connection (for cloud LLM)

### Installation

```bash
# Clone repository
git clone https://github.com/dannguy1/GAC_Waiter.git
cd GAC_Waiter

# Run installer
./install.sh

# Setup Node.js (if not already installed)
./scripts/setup_node.sh

# Install frontend dependencies
npm install --prefix frontend

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

# Server Ports
APP_PORT=8501    # Frontend (Next.js)
API_PORT=8000    # Backend API
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
│   Next.js UI    │────▶│  FastAPI Backend│────▶│  LLM Provider   │
│   (Frontend)    │     │  (API Server)   │     │  (Groq/Ollama)  │
└─────────────────┘     └─────────────────┘     └─────────────────┘
        │                       │
        │               ┌───────┴───────┐
        │               ▼               ▼
        │       ┌─────────────┐   ┌─────────────┐
        │       │RAG Retriever│   │ Piper TTS   │
        │       │(FAISS+BM25) │   │(Voice Synth)│
        │       └─────────────┘   └─────────────┘
        │
   Zustand State Management
   (Cart, Chat History, UI)
```

---

## 📁 Project Structure

```
GAC_Waiter/
├── frontend/                 # Next.js Frontend
│   ├── src/
│   │   ├── app/             # App router pages
│   │   ├── components/      # React components
│   │   │   ├── chat/        # Chat interface
│   │   │   ├── cart/        # Shopping cart
│   │   │   ├── menu/        # Menu display
│   │   │   └── layout/      # App shell, sidebar
│   │   └── lib/             # Utilities, store, API
│   └── package.json
├── backend/
│   ├── api.py               # REST API endpoints
│   ├── agent.py             # LLM Agent with ReAct loop
│   ├── rag_retriever.py     # Hybrid search engine
│   └── tts_client.py        # Text-to-speech
├── data/
│   ├── menu.json            # Menu items
│   ├── facts.json           # Restaurant info
│   └── images/              # Food images
├── models/piper/            # TTS voice models
├── scripts/                 # Utility scripts
└── docs/                    # Documentation
```

---

## 🛠️ Scripts

| Script | Description |
|--------|-------------|
| `./install.sh` | Full installation |
| `./scripts/setup_node.sh` | Install Node.js |
| `./scripts/start.sh` | Start services |
| `./scripts/stop.sh` | Stop services |
| `./scripts/restart.sh` | Restart services |
| `./scripts/status.sh` | Check service status |
| `./scripts/refresh_menu.sh` | Hot-reload menu data |

---

## 📚 Documentation

- [Installation Guide](docs/INSTALLATION.md) - Complete setup instructions
- [System Design](docs/System_Design.md) - Architecture documentation
- [Waiter Workflow](docs/waiter_workflow.md) - Agent behavior spec
- [RAG Integration](docs/RAG_Integration.md) - Search system details
- [UI Design Guide](docs/UI_Design_Guide.md) - Frontend components

---

## 🧪 Testing

```bash
# Test LLM connection
python scripts/verify_llm.py

# Test RAG retrieval
python test_rag.py

# View logs
tail -f api.log frontend.log
```

---

## 🔧 Troubleshooting

**Services won't start?**
```bash
./scripts/stop.sh
rm -f *.pid frontend/.next/dev/lock
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

**Frontend issues?**
```bash
cd frontend
npm install
rm -rf .next
npm run dev
```

---

## 📄 License

MIT License - See [LICENSE](LICENSE) for details.

---

## 🙏 Credits

- **LLM**: [Groq](https://groq.com) / [Ollama](https://ollama.ai)
- **TTS**: [Piper](https://github.com/rhasspy/piper)
- **UI**: [Next.js](https://nextjs.org) + [TailwindCSS](https://tailwindcss.com)
- **State**: [Zustand](https://github.com/pmndrs/zustand)
- **Search**: [FAISS](https://faiss.ai) + [BM25](https://github.com/dorianbrown/rank_bm25)

---

*Made with ❤️ for Garlic & Chives Restaurant*
