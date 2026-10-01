from dataclasses import dataclass, field
from pathlib import Path
import os

@dataclass
class Config:
    model: str = "qwen3-coder:30b"
    host: str = os.getenv("OLLAMA_HOST", "http://localhost:11434")
    num_ctx: int = 16384
    temperature: float = 0.2
    max_steps: int = 25
    max_output: int = 6000
    workdir: Path = field(default_factory=lambda: Path.cwd().resolve())

DEFAULT_CONFIG = Config()
