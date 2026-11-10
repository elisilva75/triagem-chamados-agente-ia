"""Groq Responses beta: ferramentas e saída estruturada em etapas separadas."""

from app.agent.openai_provider import OpenAIProvider
from app.agent.tools import TOOLS


class GroqProvider(OpenAIProvider):
    base_url = "https://api.groq.com/openai/v1"
    mode = "groq"
    provider = "groq"

    def request_options(self, messages):
        options = super().request_options(messages)
        completed = {m.get("name") for m in messages if m.get("role") == "tool"}
        if set(TOOLS) <= completed:
            return {"text": options["text"]}
        return {
            "tools": [tool for tool in options["tools"] if tool["name"] not in completed],
            "tool_choice": "required",
        }
