from typing import List, Dict, Any

def estimate_tokens(text: str) -> int:
    """Approximate token count: ~4 characters per token."""
    return max(1, len(text) // 4)

def trim_context(messages: List[Dict[str, Any]], max_tokens: int = 16384) -> List[Dict[str, Any]]:
    """Trim old tool execution contents if total estimated tokens exceeds threshold."""
    total_tokens = sum(estimate_tokens(str(m.get("content", ""))) for m in messages)
    if total_tokens <= max_tokens * 0.8:
        return messages

    # Keep system prompt (index 0) and user request (index 1 if present) intact
    result = [messages[0]]
    middle = messages[1:]

    # Truncate older tool response outputs
    trimmed_middle = []
    for msg in middle[:-4]:  # Keep last 4 messages intact
        if msg.get("role") == "tool" and len(str(msg.get("content", ""))) > 500:
            msg_copy = dict(msg)
            msg_copy["content"] = msg_copy["content"][:200] + "\n...[older output trimmed to preserve context window]"
            trimmed_middle.append(msg_copy)
        else:
            trimmed_middle.append(msg)

    trimmed_middle.extend(middle[-4:])
    return result + trimmed_middle
