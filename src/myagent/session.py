import json
import time
from pathlib import Path
from typing import List, Dict, Any, Optional

class SessionStore:
    def __init__(self, workdir: Path):
        self.session_dir = workdir / ".myagent" / "sessions"
        self.session_dir.mkdir(parents=True, exist_ok=True)

    def save_session(self, messages: List[Dict[str, Any]], session_id: Optional[str] = None) -> str:
        if not session_id:
            session_id = f"session_{int(time.time())}"
        filepath = self.session_dir / f"{session_id}.json"
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(messages, f, indent=2)
        return session_id

    def load_session(self, session_id: str) -> List[Dict[str, Any]]:
        filepath = self.session_dir / f"{session_id}.json"
        if not filepath.exists():
            raise FileNotFoundError(f"Session file '{filepath}' not found.")
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)

    def list_sessions(self) -> List[str]:
        return [f.stem for f in self.session_dir.glob("*.json")]
