# MyAgent - Local Autonomous Coding Agent

An OpenCode-style local autonomous coding agent that runs 100% on your own machine using open-weights models (via Ollama or local LLM backends).

## Features
- **Local & Private**: Runs completely offline using local LLMs.
- **Full Toolset**: File exploration, reading, writing, exact search/grep, line editing, and shell command execution.
- **Safety First**: Path jail protection, permission controls, step limits, stuck detection, and git undo checkpoints.
- **Dual Entrypoint**: Run via installed CLI (`myagent`) or direct standalone script (`python agent.py`).

## Installation

```bash
pip install -e .
```

## Quick Start

### 1. Start Ollama with a coding model
```bash
ollama pull qwen3-coder:30b  # or qwen3:8b, devstral:24b, etc.
```

### 2. Run the agent

Via CLI:
```bash
myagent
```

Or direct standalone script:
```bash
python agent.py
```
