"""Responses API; sem estado de conversa compartilhado, retries ou ferramentas externas."""

import asyncio
import json
import logging
import ssl

import httpx
from openai import APIError, APIStatusError, APITimeoutError, AsyncOpenAI

from app.agent.diagnostics import sanitized_429
from app.agent.orchestrator import AgentOutput
from app.agent.protocol import ModelReply, ToolCall
from app.agent.tools import TOOL_DESCRIPTIONS, TOOLS

logger = logging.getLogger(__name__)


def verified_tls_context():
    """CAs do sistema, certificado e hostname obrigatórios; sem fallback inseguro."""
    context = ssl.create_default_context()
    context.keylog_filename = None
    return context


class OpenAIProvider:
    base_url = "https://api.openai.com/v1"
    mode = "openai"
    provider = "openai"

    def __init__(self, api_key, model, *, transport=None, on_tool_decision=None):
        self._api_key = api_key
        self.model = model
        self._transport = transport
        self._on_tool_decision = on_tool_decision

    def _record_tool_decision(self, name, allowed):
        if self._on_tool_decision is not None:
            # Nomes desconhecidos são dados remotos: nunca registrar texto arbitrário.
            safe = name if isinstance(name, str) and name in (*TOOLS, "shell") else "[redacted]"
            self._on_tool_decision({"name": safe, "decision": "allow" if allowed else "block"})

    def respond(self, messages, tools, *, remaining_seconds, max_output_tokens):
        if remaining_seconds <= 0:
            raise TimeoutError
        if tuple(tools) != TOOLS:
            raise ValueError("tool_protocol_error")
        try:
            return asyncio.run(
                self._respond(messages, remaining_seconds, min(max_output_tokens, 2000))
            )
        except APITimeoutError:
            raise TimeoutError from None
        except APIStatusError as exc:
            if exc.status_code == 429:
                details = sanitized_429(exc.response, secret=self._api_key.get_secret_value())
                logger.warning("%s_http_error %s", self.provider, json.dumps(details))
            raise ConnectionError from None
        except APIError:
            raise ConnectionError from None

    async def _respond(self, messages, seconds, tokens):
        inputs = []
        for message in messages:
            if message.get("role") == "tool":
                inputs.append(
                    {
                        "type": "function_call_output",
                        "call_id": message["call_id"],
                        "output": json.dumps(message["content"], ensure_ascii=False),
                    }
                )
            else:
                inputs.append(message)
        # asyncio impõe prazo total, além dos timeouts por fase do HTTPX.
        async with asyncio.timeout(seconds):
            async with httpx.AsyncClient(
                transport=self._transport,
                verify=verified_tls_context(),
                trust_env=False,
                follow_redirects=False,
            ) as http_client:
                async with AsyncOpenAI(
                    api_key=self._api_key.get_secret_value(),
                    base_url=self.base_url,
                    max_retries=0,
                    timeout=seconds,
                    http_client=http_client,
                ) as client:
                    response = await client.responses.create(
                        model=self.model,
                        input=inputs,
                        max_output_tokens=tokens,
                        **self.request_options(messages),
                    )
        if response.status != "completed" or response.usage is None:
            raise ValueError("invalid_ai_response")
        calls = []
        texts = []
        for item in response.output:
            if item.type == "function_call":
                try:
                    arguments = json.loads(item.arguments)
                except (ValueError, TypeError):
                    self._record_tool_decision(item.name, False)
                    raise ValueError("invalid_ai_response") from None
                allowed = item.name in TOOLS and type(arguments) is dict and not arguments
                self._record_tool_decision(item.name, bool(allowed))
                if not allowed:
                    raise ValueError("tool_protocol_error")
                calls.append(ToolCall(item.name, arguments, item.call_id))
            elif item.type == "message":
                for content in item.content:
                    if content.type != "output_text":
                        raise ValueError("invalid_ai_response")
                    texts.append(content.text)
            elif item.type != "reasoning":
                raise ValueError("tool_protocol_error")
        if calls and texts:
            raise ValueError("tool_protocol_error")
        if calls:
            if len({call.call_id for call in calls}) != len(calls):
                raise ValueError("tool_protocol_error")
            return ModelReply(
                calls=tuple(calls),
                output_tokens=response.usage.output_tokens,
                context=tuple(item.model_dump(exclude_none=True) for item in response.output),
            )
        if len(texts) != 1:
            raise ValueError("invalid_ai_response")
        return ModelReply(result=json.loads(texts[0]), output_tokens=response.usage.output_tokens)

    def request_options(self, messages):
        return dict(
            store=False,
            include=["reasoning.encrypted_content"],
            tools=[
                {
                    "type": "function",
                    "name": name,
                    "description": TOOL_DESCRIPTIONS[name],
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": [],
                        "additionalProperties": False,
                    },
                    "strict": True,
                }
                for name in TOOLS
            ],
            text={
                "format": {
                    "type": "json_schema",
                    "name": "triage_suggestion",
                    "schema": AgentOutput.model_json_schema(),
                    "strict": True,
                }
            },
        )
