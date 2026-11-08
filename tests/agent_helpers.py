from app.agent.protocol import ModelReply, ToolCall
from app.agent.tools import TOOLS

VALID = {
    "category": "defeito",
    "priority": "alta",
    "rationale": "Justificativa fictícia para teste do contrato.",
    "missing_fields": [],
}
BOTH = ModelReply(calls=tuple(ToolCall(name) for name in TOOLS))


class ScriptProvider:
    def __init__(self, replies):
        self.replies = iter(replies)
        self.calls = []

    def respond(self, messages, tools, **budget):
        self.calls.append((list(messages), tools, budget))
        reply = next(self.replies)
        if isinstance(reply, Exception):
            raise reply
        return reply
