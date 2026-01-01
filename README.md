# GAC Waiter - Voice-Enabled Digital Concierge

Welcome to the Garage & Chives (GAC) Digital Waiter project. This repository contains the source code for "Kristin", an AI-powered digital waiter that assists customers with ordering, menu exploration, and more.

## Quick Start

```bash
# Install
./install.sh

# Start System
./scripts/start.sh
```

## Documentation

The documentation has been reorganized to help you find what you need quickly.

### 🏗️ Architecture
Deep dive into how the system works.
- [System Design](docs/architecture/01_System_Design.md): High-level overview of Client-Server model, goals, and requirements.
- [Data Flow](docs/architecture/02_Data_Flow.md): How images and menu data move through the system.

### 📘 Guides
Step-by-step instructions for running and maintaining the system.
- [Installation Guide](docs/guides/01_Installation.md): Setup instructions for new deployments.
- [Waiter Workflow](docs/guides/02_Waiter_Workflow.md): Understanding the "Kristin" persona and interaction logic.

### 🧩 Components
Detailed specifications for core subsystems.
- [Agent Tools](docs/components/01_Agent_Tools.md): Capabilities of the AI agent.
- [RAG System](docs/components/02_RAG_System.md): Retrieval-Augmented Generation for accurate menu answers.
- [TTS System](docs/components/03_TTS_System.md): Text-to-Speech engine details (Piper).
- [UI Design](docs/components/04_UI_Design.md): Frontend design system and specifications.

---
*Developed for Garlic & Chives Restaurant*
