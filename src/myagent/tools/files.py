import os
from pathlib import Path
from typing import Optional
import re
import subprocess
from .utils import safe_path, truncate_text

# Skip directories for listing and searching
SKIP_DIRS = {".git", "node_modules", ".venv", "__pycache__", ".pytest_cache", ".myagent"}

def list_dir(path: str = ".", workdir: Optional[Path] = None) -> str:
    try:
        base = safe_path(path, workdir)
        if not base.is_dir():
            return f"Error: '{path}' is not a directory."
        items = sorted(p for p in base.iterdir() if p.name not in SKIP_DIRS)
        if not items:
            return "(empty directory)"
        return "\n".join(f"{p.name}{'/' if p.is_dir() else ''}" for p in items)
    except Exception as e:
        return f"Error: {e}"

def read_file(path: str, start_line: Optional[int] = None, end_line: Optional[int] = None, max_output: int = 6000, workdir: Optional[Path] = None) -> str:
    try:
        f = safe_path(path, workdir)
        if not f.is_file():
            return f"Error: file '{path}' not found."
        try:
            content = f.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            return f"Error: file '{path}' is binary or non-UTF-8 text."

        lines = content.splitlines()
        if start_line is not None or end_line is not None:
            s = (start_line - 1) if start_line and start_line > 0 else 0
            e = end_line if end_line is not None else len(lines)
            selected = lines[s:e]
            result = "\n".join(f"{i + s + 1}: {line}" for i, line in enumerate(selected))
            return truncate_text(result, max_output)

        return truncate_text(content, max_output)
    except Exception as e:
        return f"Error: {e}"

def write_file(path: str, content: str, workdir: Optional[Path] = None) -> str:
    try:
        f = safe_path(path, workdir)
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(content, encoding="utf-8")
        return f"Successfully wrote {len(content)} characters to '{path}'."
    except Exception as e:
        return f"Error writing file '{path}': {e}"

def edit_file(path: str, old: str, new: str, workdir: Optional[Path] = None) -> str:
    try:
        f = safe_path(path, workdir)
        if not f.is_file():
            return f"Error: file '{path}' not found."
        text = f.read_text(encoding="utf-8")
        count = text.count(old)
        if count == 0:
            return "Error: 'old' text not found in file. Read the file first and copy the text exact including whitespace."
        if count > 1:
            return f"Error: 'old' text appears {count} times in '{path}'. Please provide more surrounding lines to specify a unique match."

        updated = text.replace(old, new)
        f.write_text(updated, encoding="utf-8")
        return f"Successfully edited '{path}'."
    except Exception as e:
        return f"Error editing file '{path}': {e}"

def search(pattern: str, path: str = ".", workdir: Optional[Path] = None) -> str:
    try:
        base = safe_path(path, workdir)
        regex = re.compile(pattern)
        matches = []

        target_files = []
        if base.is_file():
            target_files.append(base)
        else:
            for root, dirs, files in os.walk(base):
                dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
                for file in files:
                    target_files.append(Path(root) / file)

        for f in target_files:
            try:
                rel = f.relative_to(workdir or Path.cwd())
            except ValueError:
                rel = f
            try:
                lines = f.read_text(encoding="utf-8", errors="ignore").splitlines()
                for idx, line in enumerate(lines, 1):
                    if regex.search(line):
                        matches.append(f"{rel}:{idx}:{line}")
                        if len(matches) >= 200:
                            break
            except Exception:
                continue
            if len(matches) >= 200:
                break

        if not matches:
            return f"No matches found for pattern '{pattern}'."
        return truncate_text("\n".join(matches))
    except Exception as e:
        return f"Error searching pattern '{pattern}': {e}"

def run_command(command: str, timeout: int = 120, workdir: Optional[Path] = None) -> str:
    try:
        cwd = (workdir or Path.cwd()).resolve()
        r = subprocess.run(
            command,
            shell=True,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        output = f"exit code: {r.returncode}\nstdout:\n{r.stdout}\nstderr:\n{r.stderr}"
        return truncate_text(output)
    except subprocess.TimeoutExpired:
        return f"Error: command timed out after {timeout} seconds."
    except Exception as e:
        return f"Error executing command '{command}': {e}"
