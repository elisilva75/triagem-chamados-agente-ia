from app.domain.catalog import CATALOG_VERSION, Category

POLICY_VERSION = "2"
TOOLS = ("consultar_categorias", "consultar_politica_prioridade")
FIELD_CHECK_GUIDANCE = (
    "expected_fields é uma lista de campos a verificar, não uma lista de campos ausentes. "
    "missing_fields contém apenas campos aplicáveis cuja informação ainda falta. "
    "Informação ausente: incluir o campo aplicável. Informação parcial: reconhecer o que "
    "já foi informado; incluir apenas se faltar complemento indispensável à triagem, "
    "explicando na justificativa o que falta. Campo não aplicável: não incluir. "
    "Não copiar expected_fields automaticamente; a lista pode ser vazia. "
    "Não exigir reprodução ou início de incidente para uma dúvida de uso sem incidente. "
    "Sem bloqueio é informação de impacto, mas não prova ausência de todo impacto."
)
TOOL_DESCRIPTIONS = {
    TOOLS[0]: "Consulta o catálogo local de categorias permitidas.",
    TOOLS[1]: "Consulta a política local de prioridade e os campos a verificar. "
    + FIELD_CHECK_GUIDANCE,
}


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
        "expected_fields_guidance": FIELD_CHECK_GUIDANCE,
    }
