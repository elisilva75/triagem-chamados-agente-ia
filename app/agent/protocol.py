from dataclasses import dataclass, field
from typing import Protocol


@dataclass(frozen=True)
class ToolCall:
    name: str
    arguments: dict = field(default_factory=dict)
    call_id: str | None = None


@dataclass(frozen=True)
class ModelReply:
    calls: tuple[ToolCall, ...] = ()
    result: dict | None = None
    output_tokens: int = 0
    context: tuple[dict, ...] = ()


class AIProvider(Protocol):
    def respond(
        self,
        messages: list[dict],
        tools: tuple[str, ...],
        *,
        remaining_seconds: float,
        max_output_tokens: int,
    ) -> ModelReply: ...
