from pathlib import Path
from typing import Set, Optional
import os

DEFAULT_WORKDIR = Path.cwd().resolve()

def safe_path(p: str, workdir: Optional[Path] = None) -> Path:
    """Resolve a path and ensure it remains strictly inside the workdir."""
    base = (workdir or DEFAULT_WORKDIR).resolve()
    target = (base / p).resolve()
    if not target.is_relative_to(base):
        raise ValueError(f"Security error: Path '{p}' resolves outside project folder '{base}'.")
    return target

def truncate_text(text: str, max_chars: int = 6000) -> str:
    """Truncate output if it exceeds max_chars."""
    if len(text) <= max_chars:
        return text
    return text[:max_chars] + f"\n...[truncated {len(text) - max_chars} characters]"
