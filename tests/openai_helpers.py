"""Transporte falso: o SDK serializa requests reais, sem rede ou credenciais reais."""

import json

import httpx
from pydantic import SecretStr

from app.agent.openai_provider import OpenAIProvider
from app.agent.tools import TOOLS

OUTPUT = {
    "category": "defeito",
    "priority": "alta",
    "rationale": "Bloqueio fictício confirmado pelos dados informados.",
    "missing_fields": [],
}


def response(output, *, status="completed", tokens=20):
    return httpx.Response(
        200,
        json={
            "id": "resp_fake",
            "object": "response",
            "created_at": 0,
            "model": "modelo-ficticio",
            "status": status,
            "output": output,
            "usage": {"input_tokens": 10, "output_tokens": tokens, "total_tokens": 10 + tokens},
        },
    )


def calls():
    return [
        {
            "type": "function_call",
            "id": f"fc_{index}",
            "call_id": f"call_{index}",
            "name": name,
            "arguments": "{}",
            "status": "completed",
        }
        for index, name in enumerate(TOOLS)
    ]


def message(value):
    return [
        {
            "type": "message",
            "id": "msg_fake",
            "role": "assistant",
            "status": "completed",
            "content": [{"type": "output_text", "text": json.dumps(value), "annotations": []}],
        }
    ]


def fake_provider(handler):
    return OpenAIProvider(
        SecretStr("chave-ficticia-sem-validade"),
        "modelo-ficticio",
        transport=httpx.MockTransport(handler),
    )
