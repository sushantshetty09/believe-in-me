from typing import List, Dict, Any, Optional, Callable
from pathlib import Path

from .config import Config, DEFAULT_CONFIG
from .model import ModelClient, OllamaClient
from .tools import TOOL_SCHEMAS, execute_tool
from .permissions import PermissionManager, PermissionLevel
from .context import trim_context
from .session import SessionStore
from .git_utils import create_checkpoint

SYSTEM_PROMPT = """You are a coding agent working inside the user's project directory.

Rules:
- Explore before editing: list files and read relevant code first.
- Make small, focused changes. Prefer edit_file over write_file.
- After changing code, run the project's tests or build to verify.
- If a command fails, read the error, fix the cause, and retry.
- Never guess file contents; read them.
- When the task is complete, reply with a short summary and NO tool calls.
- If you are unsure what the user wants, ask one clarifying question.
"""

class Agent:
    def __init__(
        self,
        config: Optional[Config] = None,
        model_client: Optional[ModelClient] = None,
        permission_manager: Optional[PermissionManager] = None,
        confirm_callback: Optional[Callable[[str], bool]] = None,
    ):
        self.config = config or DEFAULT_CONFIG
        self.client = model_client or OllamaClient(model=self.config.model, host=self.config.host)
        self.permissions = permission_manager or PermissionManager()
        self.confirm_callback = confirm_callback or (lambda msg: True)
        self.session_store = SessionStore(self.config.workdir)

    def run(
        self,
        user_request: str,
        messages: Optional[List[Dict[str, Any]]] = None,
        on_thought: Optional[Callable[[], None]] = None,
        on_tool_call: Optional[Callable[[str, Dict[str, Any]], None]] = None,
        on_tool_result: Optional[Callable[[str, str], None]] = None,
        on_message: Optional[Callable[[str], None]] = None,
    ) -> List[Dict[str, Any]]:
        if messages is None:
            messages = [{"role": "system", "content": SYSTEM_PROMPT}]

        messages.append({"role": "user", "content": user_request})

        # Create git safety checkpoint before starting execution
        create_checkpoint(self.config.workdir)

        last_call_signature = None
        repeat_count = 0

        for step in range(self.config.max_steps):
            if on_thought:
                on_thought()

            trimmed_messages = trim_context(messages, max_tokens=self.config.num_ctx)
            resp = self.client.complete(
                messages=trimmed_messages,
                tools=TOOL_SCHEMAS,
                num_ctx=self.config.num_ctx,
                temperature=self.config.temperature,
            )

            assistant_msg = {
                "role": "assistant",
                "content": resp.content,
            }
            if resp.tool_calls:
                assistant_msg["tool_calls"] = [
                    {
                        "function": {
                            "name": tc.name,
                            "arguments": tc.arguments,
                        }
                    }
                    for tc in resp.tool_calls
                ]

            messages.append(assistant_msg)

            if not resp.tool_calls:
                if on_message:
                    on_message(resp.content)
                self.session_store.save_session(messages)
                return messages

            for call in resp.tool_calls:
                name, args = call.name, call.arguments
                if on_tool_call:
                    on_tool_call(name, args)

                # Stuck detection: same tool and arguments 3 times in a row
                sig = (name, str(sorted(args.items())))
                if sig == last_call_signature:
                    repeat_count += 1
                else:
                    repeat_count = 1
                    last_call_signature = sig

                if repeat_count >= 3:
                    msg = "Error: Agent got stuck in a loop calling the exact same tool repeatedly. Stopping execution."
                    messages.append({"role": "tool", "tool_name": name, "content": msg})
                    if on_message:
                        on_message(msg)
                    self.session_store.save_session(messages)
                    return messages

                perm_level, reason = self.permissions.check_tool_permission(name, args)
                if perm_level == PermissionLevel.BLOCK:
                    result = f"Security Error: Action blocked by permissions manager ({reason})."
                elif perm_level == PermissionLevel.ASK:
                    prompt = f"[Permission Required] {reason} Allow?"
                    if not self.confirm_callback(prompt):
                        result = "User denied permission to run this action."
                    else:
                        result = execute_tool(name, args, workdir=self.config.workdir)
                else:
                    result = execute_tool(name, args, workdir=self.config.workdir)

                if on_tool_result:
                    on_tool_result(name, result)

                messages.append({"role": "tool", "tool_name": name, "content": result})

        msg = "Reached max execution steps without completing the task."
        if on_message:
            on_message(msg)
        self.session_store.save_session(messages)
        return messages
