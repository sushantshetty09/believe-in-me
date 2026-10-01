from typing import List, Dict, Any, Optional
import ollama
from .base import ModelClient, ModelResponse, ToolCall

class OllamaClient(ModelClient):
    def __init__(self, model: str = "qwen3-coder:30b", host: Optional[str] = None):
        self.model = model
        self.host = host
        if host:
            self.client = ollama.Client(host=host)
        else:
            self.client = ollama.Client()

    def complete(
        self,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]] = None,
        num_ctx: int = 16384,
        temperature: float = 0.2,
    ) -> ModelResponse:
        options = {
            "num_ctx": num_ctx,
            "temperature": temperature,
        }
        kwargs = {
            "model": self.model,
            "messages": messages,
            "options": options,
        }
        if tools:
            kwargs["tools"] = tools

        resp = self.client.chat(**kwargs)
        msg = resp.message

        content = msg.content or ""
        raw_calls = getattr(msg, "tool_calls", None) or []
        tool_calls = []

        for call in raw_calls:
            # handle dict or object access
            if isinstance(call, dict):
                fn = call.get("function", {})
                name = fn.get("name")
                args = fn.get("arguments", {})
            else:
                fn = getattr(call, "function", None)
                name = getattr(fn, "name", None) if fn else None
                args = getattr(fn, "arguments", {}) if fn else {}

            if isinstance(args, str):
                import json
                try:
                    args = json.loads(args)
                except Exception:
                    args = {}

            if name:
                tool_calls.append(ToolCall(name=name, arguments=args))

        return ModelResponse(content=content, tool_calls=tool_calls)
