from enum import Enum
import re
from typing import Tuple

class PermissionLevel(Enum):
    AUTO_ALLOW = "auto_allow"
    ASK = "ask"
    BLOCK = "block"

BLOCKED_COMMAND_PATTERNS = [
    r"rm\s+-rf\s+/",
    r"sudo\b",
    r"curl.*\|\s*sh",
    r"wget.*\|\s*sh",
    r"git\s+push.*--force",
    r">\s*/dev/sd",
]

ALWAYS_SAFE_COMMANDS = {
    "pytest", "git status", "git diff", "git log", "ls", "dir", "pwd", "npm test"
}

class PermissionManager:
    def __init__(self, auto_approve_all: bool = False):
        self.auto_approve_all = auto_approve_all

    def check_tool_permission(self, tool_name: str, args: dict) -> Tuple[PermissionLevel, str]:
        if tool_name in ("list_dir", "read_file", "search"):
            return PermissionLevel.AUTO_ALLOW, "Read-only tool."

        if tool_name in ("write_file", "edit_file"):
            if self.auto_approve_all:
                return PermissionLevel.AUTO_ALLOW, "Auto-approved session."
            return PermissionLevel.ASK, f"File modification via {tool_name}."

        if tool_name == "run_command":
            cmd = args.get("command", "").strip()
            for pattern in BLOCKED_COMMAND_PATTERNS:
                if re.search(pattern, cmd):
                    return PermissionLevel.BLOCK, f"Command matches blocked security pattern '{pattern}'."

            if cmd in ALWAYS_SAFE_COMMANDS:
                return PermissionLevel.AUTO_ALLOW, "Safe read-only command."

            if self.auto_approve_all:
                return PermissionLevel.AUTO_ALLOW, "Auto-approved session."

            return PermissionLevel.ASK, f"Execute shell command: '{cmd}'"

        return PermissionLevel.ASK, f"Unknown action for tool '{tool_name}'."
