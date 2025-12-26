#!/bin/bash
#=============================================================================
# GAC Waiter - Package Creation Script
# Creates a distributable archive for new installations
#
# Usage: ./scripts/package.sh [--with-images] [--with-data]
#   --with-images  Include all menu images (makes package larger)
#   --with-data    Include actual menu data (not just templates)
#=============================================================================

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Parse arguments
WITH_IMAGES=false
WITH_DATA=false

for arg in "$@"; do
    case $arg in
        --with-images)
            WITH_IMAGES=true
            shift
            ;;
        --with-data)
            WITH_DATA=true
            shift
            ;;
    esac
done

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}GAC Waiter - Creating Distribution Package${NC}"
echo -e "${BLUE}========================================${NC}"
if $WITH_IMAGES; then
    echo -e "${YELLOW}Including images (package will be larger)${NC}"
fi
if $WITH_DATA; then
    echo -e "${YELLOW}Including actual menu data${NC}"
fi

# Change to project root
cd "$(dirname "$0")/.."
PROJECT_DIR=$(pwd)
PROJECT_NAME="GAC_Waiter"
VERSION=$(date +%Y%m%d)
PACKAGE_NAME="${PROJECT_NAME}_v${VERSION}"
DIST_DIR="dist"
PACKAGE_DIR="${DIST_DIR}/${PACKAGE_NAME}"

# Clean previous builds
rm -rf "$DIST_DIR"
mkdir -p "$PACKAGE_DIR"

echo -e "\n${YELLOW}Creating package: ${PACKAGE_NAME}${NC}\n"

#=============================================================================
# Copy Core Files
#=============================================================================
echo "Copying core files..."

# Python files
cp app.py "$PACKAGE_DIR/"
cp config.py "$PACKAGE_DIR/"
cp menu_components.py "$PACKAGE_DIR/"
cp requirements.txt "$PACKAGE_DIR/"

# Installation script
cp install.sh "$PACKAGE_DIR/"
chmod +x "$PACKAGE_DIR/install.sh"

# Backend directory
mkdir -p "$PACKAGE_DIR/backend"
cp backend/__init__.py "$PACKAGE_DIR/backend/" 2>/dev/null || touch "$PACKAGE_DIR/backend/__init__.py"
cp backend/api.py "$PACKAGE_DIR/backend/"
cp backend/agent.py "$PACKAGE_DIR/backend/"
cp backend/rag_retriever.py "$PACKAGE_DIR/backend/"
cp backend/tts_client.py "$PACKAGE_DIR/backend/"
cp backend/menu_manager.py "$PACKAGE_DIR/backend/"
cp backend/llm_client.py "$PACKAGE_DIR/backend/" 2>/dev/null || true

echo -e "${GREEN}✓ Core files copied${NC}"

#=============================================================================
# Copy Scripts
#=============================================================================
echo "Copying scripts..."

mkdir -p "$PACKAGE_DIR/scripts"
cp scripts/start.sh "$PACKAGE_DIR/scripts/"
cp scripts/stop.sh "$PACKAGE_DIR/scripts/"
cp scripts/restart.sh "$PACKAGE_DIR/scripts/"
cp scripts/verify_llm.py "$PACKAGE_DIR/scripts/" 2>/dev/null || true

chmod +x "$PACKAGE_DIR/scripts/"*.sh

echo -e "${GREEN}✓ Scripts copied${NC}"

#=============================================================================
# Copy Documentation
#=============================================================================
echo "Copying documentation..."

mkdir -p "$PACKAGE_DIR/docs"
cp docs/*.md "$PACKAGE_DIR/docs/" 2>/dev/null || true
cp README.md "$PACKAGE_DIR/" 2>/dev/null || true

echo -e "${GREEN}✓ Documentation copied${NC}"

#=============================================================================
# Copy Data (Sample/Template)
#=============================================================================
echo "Copying data templates..."

mkdir -p "$PACKAGE_DIR/data"
mkdir -p "$PACKAGE_DIR/data/images"
mkdir -p "$PACKAGE_DIR/data/downloaded_images"

# Copy menu.json if it exists, or create sample
if [ -f "data/menu.json" ]; then
    cp data/menu.json "$PACKAGE_DIR/data/"
    echo -e "${GREEN}✓ Menu data copied${NC}"
else
    cat > "$PACKAGE_DIR/data/menu.json" << 'EOF'
{
  "restaurant": {
    "name": "Your Restaurant Name",
    "address": "123 Main Street",
    "phone": "(555) 123-4567"
  },
  "items": [
    {
      "item_name": "Sample Dish",
      "item_viet": "Món Mẫu",
      "description": "A delicious sample dish",
      "description_viet": "Một món ăn mẫu ngon",
      "price": 15.99,
      "category": "Main Courses",
      "popular": true
    }
  ]
}
EOF
    echo -e "${YELLOW}⚠ Sample menu.json created${NC}"
fi

# Copy facts.json if it exists, or create sample
if [ -f "data/facts.json" ]; then
    cp data/facts.json "$PACKAGE_DIR/data/"
    echo -e "${GREEN}✓ Facts data copied${NC}"
else
    cat > "$PACKAGE_DIR/data/facts.json" << 'EOF'
{
  "info": [
    {
      "topic": "Hours",
      "content": "Open daily 11am-10pm"
    },
    {
      "topic": "Contact",
      "content": "Call us at (555) 123-4567"
    }
  ]
}
EOF
    echo -e "${YELLOW}⚠ Sample facts.json created${NC}"
fi

#=============================================================================
# Create Empty Directories
#=============================================================================
echo "Creating directory structure..."

mkdir -p "$PACKAGE_DIR/cache/tts"
mkdir -p "$PACKAGE_DIR/cache/rag"
mkdir -p "$PACKAGE_DIR/models/piper"
mkdir -p "$PACKAGE_DIR/piper"
mkdir -p "$PACKAGE_DIR/logs"

# Add .gitkeep to empty dirs
touch "$PACKAGE_DIR/cache/tts/.gitkeep"
touch "$PACKAGE_DIR/cache/rag/.gitkeep"
touch "$PACKAGE_DIR/models/piper/.gitkeep"
touch "$PACKAGE_DIR/piper/.gitkeep"
touch "$PACKAGE_DIR/logs/.gitkeep"
touch "$PACKAGE_DIR/data/images/.gitkeep"
touch "$PACKAGE_DIR/data/downloaded_images/.gitkeep"

echo -e "${GREEN}✓ Directory structure created${NC}"

#=============================================================================
# Create .env.example
#=============================================================================
echo "Creating configuration templates..."

cat > "$PACKAGE_DIR/.env.example" << 'EOF'
# =============================================================================
# GAC Waiter Configuration
# Copy this file to .env and edit with your settings
# =============================================================================

# LLM Configuration
# -----------------
# Option 1: Groq (Recommended - Fast cloud API)
LLM_BASE_URL=https://api.groq.com/openai/v1
LLM_API_KEY=your_groq_api_key_here
LLM_MODEL=llama-3.1-70b-versatile

# Option 2: Ollama (Local)
# LLM_BASE_URL=http://localhost:11434/v1
# LLM_API_KEY=ollama
# LLM_MODEL=llama3.2:latest

# Data Paths
# ----------
MENU_PATH=data/menu.json
FACTS_PATH=data/facts.json
IMAGES_DIR=data/images

# TTS Configuration
# -----------------
PIPER_BINARY=piper/piper
PIPER_MODEL=models/piper/en_US-amy-medium.onnx
PIPER_MODEL_EN=models/piper/en_US-amy-medium.onnx
PIPER_MODEL_VI=models/piper/vi_VN-vais1000-medium.onnx
PIPER_MODEL_ZH=models/piper/zh_CN-huayan-medium.onnx
PIPER_MODEL_ES=models/piper/es_ES-sharvard-medium.onnx

# Server Configuration
# --------------------
APP_PORT=8501
APP_HOST=0.0.0.0
API_PORT=8000
BACKEND_URL=http://127.0.0.1:8000
ENABLE_SERVER_AUDIO=false
EOF

echo -e "${GREEN}✓ Configuration templates created${NC}"

#=============================================================================
# Create .gitignore
#=============================================================================
cat > "$PACKAGE_DIR/.gitignore" << 'EOF'
# Environment
.env
.env.local

# Python
__pycache__/
*.py[cod]
venv/
.venv/

# Models (large files)
models/piper/*.onnx
models/piper/*.onnx.json

# Tools
piper/

# Cache and Logs
cache/
*.log
*.pid

# System
.DS_Store
EOF

echo -e "${GREEN}✓ .gitignore created${NC}"

#=============================================================================
# Copy Images (optional)
#=============================================================================
if $WITH_IMAGES; then
    echo "Copying images..."
    if [ -d "data/images" ] && [ "$(ls -A data/images 2>/dev/null)" ]; then
        cp -r data/images/* "$PACKAGE_DIR/data/images/" 2>/dev/null || true
        echo -e "${GREEN}✓ Images copied${NC}"
    fi
    if [ -d "data/downloaded_images" ] && [ "$(ls -A data/downloaded_images 2>/dev/null)" ]; then
        cp -r data/downloaded_images/* "$PACKAGE_DIR/data/downloaded_images/" 2>/dev/null || true
        echo -e "${GREEN}✓ Downloaded images copied${NC}"
    fi
fi

#=============================================================================
# Create Archive
#=============================================================================
echo -e "\n${YELLOW}Creating archive...${NC}"

cd "$DIST_DIR"
tar -czvf "${PACKAGE_NAME}.tar.gz" "$PACKAGE_NAME"
cd ..

# Create zip as well (if zip is available)
if command -v zip &> /dev/null; then
    cd "$DIST_DIR"
    zip -rq "${PACKAGE_NAME}.zip" "$PACKAGE_NAME"
    cd ..
    ZIP_CREATED=true
else
    ZIP_CREATED=false
fi

#=============================================================================
# Summary
#=============================================================================
TARBALL_SIZE=$(du -h "$DIST_DIR/${PACKAGE_NAME}.tar.gz" | cut -f1)

echo -e "\n${GREEN}========================================${NC}"
echo -e "${GREEN}Package Created Successfully!${NC}"
echo -e "${GREEN}========================================${NC}"
echo -e "
${BLUE}Package Contents:${NC}
  - Core application files
  - Backend API and agent
  - Installation script
  - Documentation
  - Configuration templates
  - Sample/actual data files"

if $WITH_IMAGES; then
    echo -e "  - Menu images"
fi

echo -e "
${BLUE}Outputs:${NC}
  - ${DIST_DIR}/${PACKAGE_NAME}.tar.gz (${TARBALL_SIZE})"

if $ZIP_CREATED; then
    ZIP_SIZE=$(du -h "$DIST_DIR/${PACKAGE_NAME}.zip" | cut -f1)
    echo -e "  - ${DIST_DIR}/${PACKAGE_NAME}.zip (${ZIP_SIZE})"
fi

echo -e "  - ${DIST_DIR}/${PACKAGE_NAME}/ (unpacked)

${YELLOW}To install on new host:${NC}
  1. Copy package to target machine
  2. Extract: tar -xzf ${PACKAGE_NAME}.tar.gz
  3. Enter dir: cd ${PACKAGE_NAME}
  4. Run: ./install.sh
  5. Configure: cp .env.example .env && nano .env
  6. Add your menu data to data/menu.json
  7. Start: ./scripts/start.sh
"

