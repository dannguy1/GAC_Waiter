# GAC Waiter - Installation Guide

A comprehensive guide for installing the Digital Waiter system at a new location.

---

## Table of Contents

1. [System Requirements](#system-requirements)
2. [Quick Installation](#quick-installation)
3. [Manual Installation](#manual-installation)
4. [Configuration](#configuration)
5. [LLM Setup Options](#llm-setup-options)
6. [Data Setup](#data-setup)
7. [Running the System](#running-the-system)
8. [Production Deployment](#production-deployment)
9. [Troubleshooting](#troubleshooting)

---

## System Requirements

### Minimum Hardware
- **CPU**: 4 cores
- **RAM**: 8 GB
- **Storage**: 5 GB free space

### Recommended Hardware
- **CPU**: 8+ cores
- **RAM**: 16 GB
- **Storage**: 20 GB SSD
- **GPU**: Optional (for local LLM inference)

### Software Requirements
- **OS**: Ubuntu 20.04+ / Debian 11+ / macOS 12+
- **Python**: 3.10 or higher
- **Network**: Internet access for initial setup

---

## Quick Installation

### 1. Clone the Repository

```bash
git clone https://github.com/your-org/GAC_Waiter.git
cd GAC_Waiter
```

### 2. Run Installation Script

```bash
./install.sh
```

The script will:
- Create Python virtual environment
- Install dependencies
- Download Piper TTS and voice models
- Create required directories
- Generate default configuration

### 3. Configure LLM

Edit `.env` and set your LLM provider:

```bash
# For Groq (recommended - fast cloud API)
LLM_BASE_URL=https://api.groq.com/openai/v1
LLM_API_KEY=your_groq_api_key
LLM_MODEL=llama-3.1-70b-versatile
```

### 4. Start the System

```bash
./scripts/start.sh
```

Access at: **http://localhost:8501**

---

## Manual Installation

### Step 1: Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 2: Install Python Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 3: Download Piper TTS

```bash
# Linux x86_64
wget https://github.com/rhasspy/piper/releases/download/v1.2.0/piper_linux_x86_64.tar.gz
mkdir -p piper
tar -xzf piper_linux_x86_64.tar.gz -C piper --strip-components=1
chmod +x piper/piper
rm piper_linux_x86_64.tar.gz
```

### Step 4: Download Voice Models

```bash
mkdir -p models/piper

# English (required)
wget -O models/piper/en_US-amy-medium.onnx \
  "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/amy/medium/en_US-amy-medium.onnx"

# Vietnamese
wget -O models/piper/vi_VN-vais1000-medium.onnx \
  "https://huggingface.co/rhasspy/piper-voices/resolve/main/vi/vi_VN/vais1000/medium/vi_VN-vais1000-medium.onnx"

# Chinese
wget -O models/piper/zh_CN-huayan-medium.onnx \
  "https://huggingface.co/rhasspy/piper-voices/resolve/main/zh/zh_CN/huayan/medium/zh_CN-huayan-medium.onnx"

# Spanish
wget -O models/piper/es_ES-sharvard-medium.onnx \
  "https://huggingface.co/rhasspy/piper-voices/resolve/main/es/es_ES/sharvard/medium/es_ES-sharvard-medium.onnx"
```

### Step 5: Create Directories

```bash
mkdir -p cache/tts cache/rag data/images data/downloaded_images logs
```

### Step 6: Configure Environment

```bash
cp .env.example .env
# Edit .env with your settings
```

---

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `LLM_BASE_URL` | LLM API endpoint | `http://localhost:11434/v1` |
| `LLM_API_KEY` | API key for LLM | `ollama` |
| `LLM_MODEL` | Model name | `llama3.2:latest` |
| `MENU_PATH` | Path to menu.json | `data/menu.json` |
| `FACTS_PATH` | Path to facts.json | `data/facts.json` |
| `APP_PORT` | Frontend port | `8501` |
| `API_PORT` | Backend API port | `8000` |
| `APP_HOST` | Listen address | `0.0.0.0` |

### Sample .env File

```env
# LLM Configuration
LLM_BASE_URL=https://api.groq.com/openai/v1
LLM_API_KEY=gsk_xxxxxxxxxxxxx
LLM_MODEL=llama-3.1-70b-versatile

# Data Paths
MENU_PATH=data/menu.json
FACTS_PATH=data/facts.json
IMAGES_DIR=data/images

# TTS Configuration
PIPER_BINARY=piper/piper
PIPER_MODEL_EN=models/piper/en_US-amy-medium.onnx
PIPER_MODEL_VI=models/piper/vi_VN-vais1000-medium.onnx
PIPER_MODEL_ZH=models/piper/zh_CN-huayan-medium.onnx
PIPER_MODEL_ES=models/piper/es_ES-sharvard-medium.onnx

# Server
APP_PORT=8501
API_PORT=8000
BACKEND_URL=http://127.0.0.1:8000
```

---

## LLM Setup Options

### Option 1: Groq (Recommended)

Fast cloud API with free tier.

1. Sign up at [console.groq.com](https://console.groq.com)
2. Create an API key
3. Configure `.env`:

```env
LLM_BASE_URL=https://api.groq.com/openai/v1
LLM_API_KEY=gsk_your_key_here
LLM_MODEL=llama-3.1-70b-versatile
```

**Recommended models:**
- `llama-3.1-70b-versatile` - Best quality
- `llama-3.1-8b-instant` - Faster, good quality

### Option 2: Ollama (Local)

Run LLM locally on your machine.

1. Install Ollama: [ollama.ai](https://ollama.ai)
2. Pull a model:
   ```bash
   ollama pull llama3.2
   ```
3. Configure `.env`:
   ```env
   LLM_BASE_URL=http://localhost:11434/v1
   LLM_API_KEY=ollama
   LLM_MODEL=llama3.2:latest
   ```

### Option 3: OpenAI Compatible

Any OpenAI-compatible API:

```env
LLM_BASE_URL=https://api.your-provider.com/v1
LLM_API_KEY=your_api_key
LLM_MODEL=model-name
```

---

## Data Setup

### Menu Data (menu.json)

```json
{
  "restaurant": {
    "name": "Your Restaurant Name",
    "address": "123 Main St",
    "phone": "(555) 123-4567"
  },
  "items": [
    {
      "item_name": "Signature Dish",
      "item_viet": "Món Đặc Biệt",
      "description": "Our famous signature dish...",
      "description_viet": "Món ăn đặc trưng của nhà hàng...",
      "price": 15.99,
      "category": "Main Courses",
      "popular": true,
      "image_path": "data/images/signature_dish.jpg"
    }
  ]
}
```

### Restaurant Facts (facts.json)

```json
{
  "info": [
    {
      "topic": "Owner",
      "content": "The restaurant is owned by Chef John Doe..."
    },
    {
      "topic": "History",
      "content": "Founded in 2010, our restaurant..."
    },
    {
      "topic": "Hours",
      "content": "Open daily 11am-10pm"
    }
  ]
}
```

### Menu Images

Place menu item images in `data/images/` or `data/downloaded_images/`.

---

## Running the System

### Start Services

```bash
./scripts/start.sh
```

### Stop Services

```bash
./scripts/stop.sh
```

### Restart Services

```bash
./scripts/restart.sh
```

### View Logs

```bash
# Backend API logs
tail -f api.log

# Frontend logs
tail -f app.log
```

---

## Production Deployment

### Using systemd

Create `/etc/systemd/system/gac-waiter.service`:

```ini
[Unit]
Description=GAC Waiter Digital Menu
After=network.target

[Service]
Type=forking
User=www-data
WorkingDirectory=/opt/GAC_Waiter
ExecStart=/opt/GAC_Waiter/scripts/start.sh
ExecStop=/opt/GAC_Waiter/scripts/stop.sh
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl enable gac-waiter
sudo systemctl start gac-waiter
```

### Using Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY . /app

RUN apt-get update && apt-get install -y wget
RUN pip install -r requirements.txt
RUN ./install.sh

EXPOSE 8501 8000

CMD ["./scripts/start.sh"]
```

### Nginx Reverse Proxy

```nginx
server {
    listen 80;
    server_name menu.yourrestaurant.com;

    location / {
        proxy_pass http://127.0.0.1:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }
}
```

---

## Troubleshooting

### Common Issues

**1. "Module not found" errors**
```bash
source venv/bin/activate
pip install -r requirements.txt
```

**2. TTS not working**
```bash
# Check Piper is executable
chmod +x piper/piper

# Test Piper
echo "Hello" | ./piper/piper --model models/piper/en_US-amy-medium.onnx --output_file test.wav
```

**3. LLM not responding**
```bash
# Test connection
curl -X POST $LLM_BASE_URL/chat/completions \
  -H "Authorization: Bearer $LLM_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"'$LLM_MODEL'","messages":[{"role":"user","content":"Hi"}]}'
```

**4. Port already in use**
```bash
# Find and kill existing process
lsof -i :8501
kill -9 <PID>
```

### Getting Help

- Check logs: `tail -f api.log app.log`
- Review docs: `docs/System_Design.md`
- Test LLM: `python scripts/verify_llm.py`

---

## Directory Structure

```
GAC_Waiter/
├── app.py                 # Frontend (Streamlit)
├── config.py              # Configuration loader
├── requirements.txt       # Python dependencies
├── install.sh             # Installation script
├── .env                   # Environment config (create from .env.example)
├── backend/
│   ├── api.py            # FastAPI backend
│   ├── agent.py          # LLM agent
│   ├── rag_retriever.py  # Hybrid search
│   ├── tts_client.py     # Text-to-speech
│   └── menu_manager.py   # Menu data handler
├── data/
│   ├── menu.json         # Menu items
│   ├── facts.json        # Restaurant info
│   ├── images/           # Original images
│   └── downloaded_images/# Downloaded images
├── models/piper/         # TTS voice models
├── piper/                # Piper TTS binary
├── scripts/
│   ├── start.sh          # Start services
│   ├── stop.sh           # Stop services
│   └── restart.sh        # Restart services
├── cache/
│   ├── tts/              # Audio cache
│   └── rag/              # FAISS index cache
└── docs/                 # Documentation
```

---

*Last updated: December 26, 2024*
