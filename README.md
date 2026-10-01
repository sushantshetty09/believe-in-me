# MyAgent - Local Autonomous Coding Agent

**MyAgent** is an OpenCode-style local autonomous coding agent that runs 100% on your own machine using open-weights language models (such as `qwen3-coder:30b`, `devstral:24b`, `gpt-oss:20b`, or `qwen3:8b` via Ollama or local backends). No cloud APIs, no data leaving your machine, and no external servers required.

---

## Table of Contents
1. [Capabilities (Can it perform any task?)](#capabilities-can-it-perform-any-task)
2. [Tech Stack](#tech-stack)
3. [Architecture & How It Works](#architecture--how-it-works)
4. [Installation & Setup](#installation--setup)
5. [Usage](#usage)
   - [CLI Executable](#cli-executable)
   - [Standalone Single-File Script](#standalone-single-file-script)
6. [Safety & Permission Guardrails](#safety--permission-guardrails)

---

## Capabilities: Can it perform any task?

Yes! **MyAgent** is an **autonomous coding agent**. Once given a high-level goal in natural language (e.g. *"Fix the failing unit tests"*, *"Add dark mode toggle to navbar"*, or *"Refactor user authentication to use JWT"*), the agent operates autonomously in an iterative loop:

1. **Explores Your Project**: Lists files, reads source code, and searches for regex patterns across the repository using `list_dir`, `read_file`, and `search`.
2. **Plans & Decides**: Uses its LLM "brain" to determine what files need modification.
3. **Edits Code Safely**: Performs precise line-by-line text replacements with `edit_file` or writes new files with `write_file`.
4. **Verifies Changes**: Automatically runs unit tests, linter commands, or build scripts using `run_command`.
5. **Self-Corrects**: Reads error outputs/stack traces if a test or build fails, fixes the bug, and re-runs tests until the goal is achieved.
6. **Git Safety & Undo**: Automatically creates a git checkpoint before modifying files. You can type `/undo` at any point to instantly roll back all agent changes.

---

## Tech Stack

| Component | Choice | Purpose |
|---|---|---|
| **Language** | Python 3.11+ | High performance, cross-platform compatibility, rich ecosystem. |
| **Model Engine** | Ollama | Loads and runs open-weights models (Qwen3-Coder, Devstral, GPT-OSS) locally on CPU/GPU. |
| **LLM Client Interface** | Custom `ModelClient` (`OllamaClient` / `MockModelClient`) | Swappable abstraction for sending messages + tool schemas to local LLMs. |
| **Terminal UI** | `rich` + `prompt_toolkit` | Colorful panels, interactive prompts, formatted tool call outputs, diffs, and command history. |
| **Testing** | `pytest` | Comprehensive unit test suite covering tool operations, path security, permissions, and mock agent loops. |

---

## Architecture & How It Works

### Architectural Diagram

```
+-------------------------------------------------------------------------------+
|                                USER TERMINAL                                  |
|               ( CLI: myagent  OR  Standalone: python agent.py )                |
+-------------------------------------------------------------------------------+
                                        |
                                        v
+-------------------------------------------------------------------------------+
|                            UI LAYER (rich / cli.py)                            |
|        Reads user prompt, streams progress, displays formatted tool calls     |
+-------------------------------------------------------------------------------+
                                        |
                                        v
+-------------------------------------------------------------------------------+
|                             AGENT CORE (agent.py)                             |
|  - Manages Autonomous Loop (Max Steps, Stuck Detection: 3x repeat rule)        |
|  - Trims Context Window (context.py) & Saves Sessions (session.py)             |
|  - Enforces Git Safety Checkpoints & Undo (/undo) (git_utils.py)               |
+-------------------------------------------------------------------------------+
       |                                   |                                |
       | (Prompt + Tools)                  | (Check Action)                 | (Execute Tool)
       v                                   v                                v
+----------------------+        +-----------------------+       +------------------------+
|     MODEL CLIENT     |        |  PERMISSION MANAGER   |       |     TOOL REGISTRY      |
| (OllamaClient / LLM) |        |   (permissions.py)    |       |      (registry.py)     |
+----------------------+        +-----------------------+       +------------------------+
       |                         | Auto-Allow / Ask /   |        | - list_dir             |
       v                         | Always Block Rules   |        | - read_file            |
+----------------------+        +-----------------------+        | - write_file           |
| OLLAMA (localhost)   |                                         | - edit_file            |
| Local Model Weights  |                                         | - search (regex)       |
+----------------------+                                         | - run_command (shell)  |
                                                                 +------------------------+
                                                                             |
                                                                             v
                                                                 +------------------------+
                                                                 |     PATH JAIL          |
                                                                 |     (safe_path)        |
                                                                 |  Restricts execution   |
                                                                 |  to project directory  |
                                                                 +------------------------+
```

---

## Installation & Setup

### Prerequisites
1. Install [Ollama](https://ollama.com).
2. Pull your choice of open-weights coding model:
   ```bash
   ollama pull qwen3-coder:30b   # Recommended standard
   # OR
   ollama pull qwen3:8b         # Fast lightweight option
   ```

### Package Installation
```bash
# Clone repository and install editable package
pip install -e .[dev]
```

---

## Usage

### CLI Executable
Run `myagent` directly from any project folder:

```bash
myagent --model qwen3-coder:30b --auto-approve
```

Options:
- `--model MODEL`: Specify local LLM tag (default: `qwen3-coder:30b`).
- `--host HOST`: Specify Ollama server URL (default: `http://localhost:11434`).
- `--auto-approve`: Automatically approve file edits and command executions.
- `--workdir WORKDIR`: Set working directory.

### Standalone Single-File Script
You can also run the agent as a standalone script without installing:

```bash
python agent.py
```

---

## Safety & Permission Guardrails

1. **Path Jail (`safe_path`)**: Prevents reading, writing, or listing files outside the root project folder.
2. **Command Blocklist**: Automatically blocks dangerous commands such as `rm -rf /`, `sudo`, `curl | sh`, etc.
3. **Stuck Detection**: If the model invokes the exact same tool with identical parameters 3 times sequentially, the agent halts to prevent infinite loops.
4. **Git Undo (`/undo`)**: Creates a git checkpoint before executing modifications. Enter `/undo` at any prompt to revert state.
