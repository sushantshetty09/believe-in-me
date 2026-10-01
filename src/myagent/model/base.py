from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field

@dataclass
class ToolCall:
    name: str
    arguments: Dict[str, Any]

@dataclass
class ModelResponse:
    content: str
    tool_calls: List[ToolCall] = field(default_factory=list)

class ModelClient(ABC):
    @abstractmethod
    def complete(
        self,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]] = None,
        num_ctx: int = 16384,
        temperature: float = 0.2,
    ) -> ModelResponse:
        """Send messages and tools to the model and return a standardized ModelResponse."""
        pass
