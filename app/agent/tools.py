from app.domain.catalog import CATALOG_VERSION, Category

POLICY_VERSION = "1"
TOOLS = ("consultar_categorias", "consultar_politica_prioridade")


def execute_tool(name: str, arguments: dict) -> dict:
    if name not in TOOLS or arguments != {}:
        raise ValueError("tool_protocol_error")
    if name == TOOLS[0]:
        return {
            "version": CATALOG_VERSION,
            "categories": {
                Category.ACESSO: "Acesso e permissões",
                Category.DEFEITO: "Erro no comportamento da aplicação",
                Category.INFRAESTRUTURA: "Rede e infraestrutura",
                Category.DUVIDA: "Dúvidas de uso",
                Category.OUTROS: "Demais solicitações",
            },
        }
    return {
        "version": POLICY_VERSION,
        "priorities": {
            "critica": "Serviço essencial indisponível para todos, sem alternativa.",
            "alta": "Vários usuários afetados ou bloqueio essencial sem alternativa.",
            "media": "Falha parcial com alternativa; provisória quando impacto ausente.",
            "baixa": "Dúvida ou melhoria sem bloqueio.",
        },
        "expected_fields": ["ambiente", "passos_reproducao", "impacto", "inicio_ocorrencia"],
    }
