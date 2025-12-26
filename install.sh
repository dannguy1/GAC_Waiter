#!/bin/bash
#=============================================================================
# GAC Waiter - Installation Script
# Digital Waiter for Garlic & Chives Restaurant
#=============================================================================

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_header() {
    echo -e "\n${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}\n"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

# Check if running from project root
if [ ! -f "app.py" ]; then
    print_error "Please run this script from the project root directory"
    exit 1
fi

PROJECT_DIR=$(pwd)

print_header "GAC Waiter Installation"
echo "Installing to: $PROJECT_DIR"

#=============================================================================
# Step 1: Check System Requirements
#=============================================================================
print_header "Step 1: Checking System Requirements"

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 10 ]); then
    print_error "Python 3.10+ required. Found: $PYTHON_VERSION"
    exit 1
fi
print_success "Python version: $PYTHON_VERSION"

# Check for required system commands
for cmd in curl wget tar; do
    if command -v $cmd &> /dev/null; then
        print_success "$cmd is installed"
    else
        print_warning "$cmd not found - may be needed for downloads"
    fi
done

#=============================================================================
# Step 2: Create Virtual Environment
#=============================================================================
print_header "Step 2: Setting Up Python Virtual Environment"

if [ -d "venv" ]; then
    print_warning "Virtual environment already exists"
    read -p "Recreate it? (y/N): " recreate
    if [[ $recreate =~ ^[Yy]$ ]]; then
        rm -rf venv
        python3 -m venv venv
        print_success "Virtual environment recreated"
    fi
else
    python3 -m venv venv
    print_success "Virtual environment created"
fi

# Activate venv
source venv/bin/activate
print_success "Virtual environment activated"

#=============================================================================
# Step 3: Install Python Dependencies
#=============================================================================
print_header "Step 3: Installing Python Dependencies"

pip install --upgrade pip wheel setuptools > /dev/null
print_success "pip upgraded"

pip install -r requirements.txt
print_success "Python dependencies installed"

#=============================================================================
# Step 4: Download Piper TTS
#=============================================================================
print_header "Step 4: Setting Up Piper TTS"

PIPER_DIR="piper"
PIPER_URL="https://github.com/rhasspy/piper/releases/download/v1.2.0/piper_linux_x86_64.tar.gz"

if [ -f "$PIPER_DIR/piper" ]; then
    print_warning "Piper already installed"
else
    echo "Downloading Piper TTS..."
    mkdir -p "$PIPER_DIR"
    
    if command -v wget &> /dev/null; then
        wget -q --show-progress -O piper.tar.gz "$PIPER_URL"
    else
        curl -L -o piper.tar.gz "$PIPER_URL"
    fi
    
    tar -xzf piper.tar.gz -C "$PIPER_DIR" --strip-components=1
    rm piper.tar.gz
    chmod +x "$PIPER_DIR/piper"
    print_success "Piper TTS installed"
fi

#=============================================================================
# Step 5: Download TTS Voice Models
#=============================================================================
print_header "Step 5: Downloading Voice Models"

MODELS_DIR="models/piper"
mkdir -p "$MODELS_DIR"

download_model() {
    local name=$1
    local url=$2
    
    if [ -f "$MODELS_DIR/$name" ]; then
        print_warning "$name already exists"
    else
        echo "Downloading $name..."
        if command -v wget &> /dev/null; then
            wget -q --show-progress -O "$MODELS_DIR/$name" "$url"
            wget -q -O "$MODELS_DIR/$name.json" "$url.json"
        else
            curl -L -o "$MODELS_DIR/$name" "$url"
            curl -L -o "$MODELS_DIR/$name.json" "$url.json"
        fi
        print_success "$name downloaded"
    fi
}

# Download voice models
download_model "en_US-amy-medium.onnx" \
    "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/amy/medium/en_US-amy-medium.onnx"

download_model "vi_VN-vais1000-medium.onnx" \
    "https://huggingface.co/rhasspy/piper-voices/resolve/main/vi/vi_VN/vais1000/medium/vi_VN-vais1000-medium.onnx"

download_model "zh_CN-huayan-medium.onnx" \
    "https://huggingface.co/rhasspy/piper-voices/resolve/main/zh/zh_CN/huayan/medium/zh_CN-huayan-medium.onnx"

download_model "es_ES-sharvard-medium.onnx" \
    "https://huggingface.co/rhasspy/piper-voices/resolve/main/es/es_ES/sharvard/medium/es_ES-sharvard-medium.onnx"

#=============================================================================
# Step 6: Create Required Directories
#=============================================================================
print_header "Step 6: Creating Directory Structure"

for dir in "cache/tts" "cache/rag" "data/images" "data/downloaded_images" "logs"; do
    mkdir -p "$dir"
    print_success "Created $dir"
done

#=============================================================================
# Step 7: Configure Environment
#=============================================================================
print_header "Step 7: Configuring Environment"

if [ -f ".env" ]; then
    print_warning ".env file already exists"
    read -p "Overwrite with defaults? (y/N): " overwrite
    if [[ ! $overwrite =~ ^[Yy]$ ]]; then
        echo "Keeping existing .env"
    fi
fi

if [ ! -f ".env" ] || [[ $overwrite =~ ^[Yy]$ ]]; then
    cat > .env << 'EOF'
# =============================================================================
# GAC Waiter Configuration
# =============================================================================

# LLM Configuration
# For Ollama (local):
LLM_BASE_URL=http://localhost:11434/v1
LLM_API_KEY=ollama
LLM_MODEL=llama3.2:latest

# For Groq (cloud - faster):
# LLM_BASE_URL=https://api.groq.com/openai/v1
# LLM_API_KEY=your_groq_api_key_here
# LLM_MODEL=llama-3.1-70b-versatile

# Data Paths (relative to project root or absolute)
MENU_PATH=data/menu.json
FACTS_PATH=data/facts.json
IMAGES_DIR=data/images

# TTS Configuration
PIPER_BINARY=piper/piper
PIPER_MODEL=models/piper/en_US-amy-medium.onnx
PIPER_MODEL_EN=models/piper/en_US-amy-medium.onnx
PIPER_MODEL_VI=models/piper/vi_VN-vais1000-medium.onnx
PIPER_MODEL_ZH=models/piper/zh_CN-huayan-medium.onnx
PIPER_MODEL_ES=models/piper/es_ES-sharvard-medium.onnx

# Server Configuration
APP_PORT=8501
APP_HOST=0.0.0.0
API_PORT=8000
BACKEND_URL=http://127.0.0.1:8000
ENABLE_SERVER_AUDIO=false
EOF
    print_success ".env file created"
fi

#=============================================================================
# Step 8: Verify Installation
#=============================================================================
print_header "Step 8: Verifying Installation"

# Check if data files exist
if [ -f "data/menu.json" ]; then
    MENU_ITEMS=$(python3 -c "import json; print(len(json.load(open('data/menu.json')).get('items', [])))")
    print_success "Menu loaded: $MENU_ITEMS items"
else
    print_warning "data/menu.json not found - you'll need to create it"
fi

if [ -f "data/facts.json" ]; then
    print_success "facts.json found"
else
    print_warning "data/facts.json not found - you'll need to create it"
fi

# Check Piper
if [ -x "$PIPER_DIR/piper" ]; then
    print_success "Piper TTS executable"
else
    print_error "Piper TTS not executable"
fi

# Check models
for model in en_US-amy-medium vi_VN-vais1000-medium zh_CN-huayan-medium es_ES-sharvard-medium; do
    if [ -f "$MODELS_DIR/${model}.onnx" ]; then
        print_success "Voice model: $model"
    else
        print_warning "Missing voice model: $model"
    fi
done

#=============================================================================
# Step 9: Final Instructions
#=============================================================================
print_header "Installation Complete!"

echo -e "
${GREEN}GAC Waiter has been installed successfully!${NC}

${YELLOW}Before starting, ensure:${NC}
1. Edit .env file with your LLM API settings
2. data/menu.json contains your menu items
3. data/facts.json contains restaurant info (optional)

${YELLOW}To start the system:${NC}
    ./scripts/start.sh

${YELLOW}To stop the system:${NC}
    ./scripts/stop.sh

${YELLOW}Access the application:${NC}
    http://localhost:8501

${YELLOW}View logs:${NC}
    tail -f api.log      # Backend logs
    tail -f app.log      # Frontend logs

${BLUE}For more information, see:${NC}
    docs/INSTALLATION.md
    docs/System_Design.md
"
