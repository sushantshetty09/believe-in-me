from typing import List, Dict, Any, Optional
from .base import ModelClient, ModelResponse, ToolCall

class MockModelClient(ModelClient):
    def __init__(self, responses: Optional[List[ModelResponse]] = None):
        self.responses = responses or []
        self.calls = []

    def complete(
        self,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]] = None,
        num_ctx: int = 16384,
        temperature: float = 0.2,
    ) -> ModelResponse:
        self.calls.append({"messages": messages, "tools": tools})
        if self.responses:
            return self.responses.pop(0)
        return ModelResponse(content="Default mock response.", tool_calls=[])
