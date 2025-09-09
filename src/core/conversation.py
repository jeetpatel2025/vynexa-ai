from dataclasses import dataclass
from typing import List, Optional, Dict, Any

@dataclass
class Message:
    role: str  # 'user', 'assistant', 'system', 'tool'
    content: str
    metadata: Optional[Dict[str, Any]] = None

class Conversation:
    def __init__(self):
        self.messages: List[Message] = []

    def add(self, role: str, content: str, metadata: Optional[Dict[str, Any]] = None):
        self.messages.append(Message(role=role, content=content, metadata=metadata))

    def last_n(self, n: int) -> List[Message]:
        return self.messages[-n:]

    def to_dict(self) -> List[Dict[str, Any]]:
        return [m.__dict__ for m in self.messages]

