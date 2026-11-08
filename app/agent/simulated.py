import json

from app.agent.protocol import ModelReply, ToolCall


class SimulatedProvider:
    """Roteiros reproduzíveis; marcadores de demonstração só no título exato."""

    def respond(self, messages, tools, *, remaining_seconds, max_output_tokens):
        data = json.loads(messages[1]["content"])["ticket_data"]
        results = [m for m in messages if m["role"] == "tool"]
        # O simulador escolhe a ordem; somente a allowlist externa pode executar.
        if not results:
            return ModelReply(calls=(ToolCall(tools[1]),), output_tokens=20)
        if len(results) == 1:
            return ModelReply(calls=(ToolCall(tools[0]),), output_tokens=20)
        if data["title"] == "[SIMULADO:saida-invalida]":
            return ModelReply(result={"category": "financeiro"}, output_tokens=10)
        # Regras de fixture, não inferência de modelo real. Instruções no texto
        # não mudam ferramenta, catálogo, política nem protocolo.
        text = (data["title"] + " " + data["description"]).lower().split("ignore")[0]
        category = "outros"
        if any(word in text for word in ("dúvida", "duvida", "pergunta")):
            category = "duvida"
        elif any(word in text for word in ("rede", "infraestrutura")):
            category = "infraestrutura"
        elif any(word in text for word in ("acesso", "permissão")):
            category = "acesso"
        elif any(word in text for word in ("erro", "falha", "salvar")):
            category = "defeito"
        missing = [
            field
            for field, hints in {
                "ambiente": ("ambiente",),
                "passos_reproducao": ("ao ", "passos", "gerar"),
                "impacto": ("usuário", "usuários", "pessoas", "bloque", "todos", "alternativa"),
                "inicio_ocorrencia": ("desde", "início"),
            }.items()
            if not any(hint in text for hint in hints)
        ]
        priority = "media"
        if "impacto" not in missing and (category == "duvida" or "orientação" in text):
            priority = "baixa"
        elif "sem alternativa" in text:
            priority = "critica" if "todos" in text and "essencial" in text else "alta"
        categories = next(m["content"]["categories"] for m in results if m["name"] == tools[0])
        priorities = next(m["content"]["priorities"] for m in results if m["name"] == tools[1])
        return ModelReply(
            result={
                "category": category,
                "priority": priority,
                "rationale": (
                    f"Simulação: {categories[category]}. "
                    f"Política consultada: {priorities[priority]} Requer revisão humana."
                ),
                "missing_fields": missing,
            },
            output_tokens=100,
        )
