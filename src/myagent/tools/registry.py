from typing import Callable, Dict, Any, List, Optional
from pathlib import Path
from .files import list_dir, read_file, write_file, edit_file, search, run_command

TOOL_FUNCTIONS: Dict[str, Callable] = {
    "list_dir": list_dir,
    "read_file": read_file,
    "write_file": write_file,
    "edit_file": edit_file,
    "search": search,
    "run_command": run_command,
}

def schema(name: str, desc: str, props: Dict[str, Any], required: List[str]) -> Dict[str, Any]:
    return {
        "type": "function",
        "function": {
            "name": name,
            "description": desc,
            "parameters": {
                "type": "object",
                "properties": props,
                "required": required,
            },
        },
    }

S = {"type": "string"}
I = {"type": "integer"}

TOOL_SCHEMAS = [
    schema(
        "list_dir",
        "List files and folders in a directory of the project.",
        {"path": S},
        [],
    ),
    schema(
        "read_file",
        "Read a text file from the project. Always read before editing.",
        {
            "path": S,
            "start_line": I,
            "end_line": I,
        },
        ["path"],
    ),
    schema(
        "write_file",
        "Create a new file or fully overwrite one. Prefer edit_file for changes.",
        {"path": S, "content": S},
        ["path", "content"],
    ),
    schema(
        "edit_file",
        "Replace one exact occurrence of 'old' text with 'new' text in a file.",
        {"path": S, "old": S, "new": S},
        ["path", "old", "new"],
    ),
    schema(
        "search",
        "Search for a regex pattern in codebase files.",
        {"pattern": S, "path": S},
        ["pattern"],
    ),
    schema(
        "run_command",
        "Run a shell command in the project folder (tests, build, git).",
        {"command": S},
        ["command"],
    ),
]

def execute_tool(name: str, args: Dict[str, Any], workdir: Optional[Path] = None) -> str:
    func = TOOL_FUNCTIONS.get(name)
    if not func:
        return f"Error: unknown tool '{name}'. Available tools: {list(TOOL_FUNCTIONS.keys())}"

    import inspect
    sig = inspect.signature(func)
    if "workdir" in sig.parameters:
        args = dict(args)
        args["workdir"] = workdir

    try:
        return str(func(**args))
    except Exception as e:
        return f"Error executing {name}: {e}"
