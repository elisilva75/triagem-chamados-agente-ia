# Contrato inicial da API

**Contrato do MVP com implementação parcial (US01–US04).** Prefixo `/api/v1`, JSON UTF-8, campos em inglês e valores de negócio conforme enums documentados. OpenAPI gerado pelo FastAPI descreve apenas os endpoints implementados; rotas futuras estão explicitamente identificadas abaixo.

**Estado da entrega US01–US04:** disponíveis GET `/health`, POST/GET `/api/v1/tickets`, GET/PATCH `/api/v1/tickets/{ticket_id}`, POST `/api/v1/tickets/{ticket_id}/triage` e GET `/api/v1/tickets/{ticket_id}/triage-attempts`. OpenAPI usa ticket_id. Revisão, resolução, reabertura e recuperação/retry de falha são futuros (US05/US06).

## PATCH implementado em US03

Exemplo: `{"expected_version":1,"description":"Descrição fictícia corrigida para demonstração."}`. expected_version é inteiro estrito ≥1; pelo menos title ou description deve ser informado. Não aceitar null, campos extras ou classificação pelo PATCH; limites/trim de RN01 valem igualmente. 200 devolve Ticket atualizado. Edição efetiva incrementa version e content_revision uma vez, volta triage_status a pendente, limpa suggestion/final_classification e arquiva classificação anterior no evento editado. No-op após trim preserva a resposta inteira e o histórico, exigindo versão atual e estado editável.

409 version_conflict: versão antiga; consultar GET e revisar o conteúdo antes de tentar novamente. 409 invalid_transition: chamado resolvido ou em_analise. UUID inexistente: 404/not_found; inválido: 422. O corpo é sempre o envelope error documentado. Datas retornadas em UTC com Z, normalizadas independentemente do fuso da sessão PostgreSQL. Sugestões simuladas agora são produzidas por US04; classificação final/revisão continuam futuras. Testes antigos de classificação final ainda usam fixtures sintéticas.

## Recursos

| Método e rota | Entrada | Sucesso | Falhas previstas |
|---|---|---|---|
| GET `/health` (sem prefixo) | nenhuma | 200 `{status:"ok"}` | 503 banco indisponível |
| POST `/tickets` | title, description | 201 Ticket + Location | 422, 503 |
| GET `/tickets` | limit=20, offset=0; status/triage_status opcionais | 200 `{items,total,limit,offset}` | 422, 503 |
| GET `/tickets/{id}` | UUID | 200 Ticket | 404, 422, 503 |
| PATCH `/tickets/{id}` | expected_version + title e/ou description | 200 Ticket | 404, 409, 422, 503 |
| POST `/tickets/{id}/triage` | expected_version | 200 `{ticket,attempt}` | 404, 409, 422, 502, 503, 504 |
| GET `/tickets/{id}/triage-attempts` | limit/offset | 200 lista paginada de Attempt | 404, 422, 503 |
| POST `/tickets/{id}/reviews` | expected_version, category, priority, reason, declared_reviewer | 201 `{ticket,review}` + Location | 404, 409, 422, 503 |
| GET `/tickets/{id}/reviews` | limit/offset | 200 lista paginada de Review | 404, 422, 503 |
| GET `/tickets/{id}/reviews/{review_id}` | UUIDs | 200 Review | 404, 422, 503 |
| POST `/tickets/{id}/resolve` | expected_version | 200 Ticket | 404, 409, 422, 503 |
| POST `/tickets/{id}/reopen` | expected_version | 200 Ticket | 404, 409, 422, 503 |

Listagens: limit inteiro 1–100, offset inteiro ≥ 0, ordenação `created_at ASC, id ASC` (tentativas por `attempt_number ASC, id ASC`). Filtros de estados inválidos: 422. Sem exclusão nem alteração direta de status/categoria pelo PATCH. Não aceitar `null` em campos fornecidos. `expected_version` inteiro ≥ 1, obrigatório em todas as escritas de chamado existente.

## Exemplo fictício

POST `/api/v1/tickets`:

```json
{"title":"Erro ao gerar relatório","description":"No ambiente de demonstração, gerar relatório retorna erro. Três usuários estão bloqueados desde 09h, sem alternativa."}
```

Resposta inicial (timestamps ilustrativos):

```json
{
  "id":"11111111-1111-4111-8111-111111111111",
  "title":"Erro ao gerar relatório",
  "description":"No ambiente de demonstração, gerar relatório retorna erro. Três usuários estão bloqueados desde 09h, sem alternativa.",
  "status":"aberto",
  "triage_status":"pendente",
  "content_revision":1,
  "version":1,
  "suggestion":null,
  "final_classification":null,
  "created_at":"2026-11-07T12:00:00Z",
  "updated_at":"2026-11-07T12:00:00Z"
}
```

POST `/api/v1/tickets/{id}/triage` com `{"expected_version":1}` inicia tentativa e finaliza, incrementando version nas duas mudanças; no caminho normal o Ticket passa a version 3, sugerida. Exemplo do campo suggestion:

```json
{
  "attempt_id":"22222222-2222-4222-8222-222222222222",
  "mode":"simulated",
  "category":"defeito",
  "priority":"alta",
  "rationale":"Vários usuários estão bloqueados sem alternativa informada.",
  "missing_fields":["passos_reproducao"]
}
```

POST `/api/v1/tickets/{id}/reviews`:

```json
{"expected_version":3,"category":"defeito","priority":"alta","reason":"Confirmei o bloqueio com os usuários fictícios.","declared_reviewer":"Pessoa Revisora Demo"}
```

Resposta 201 com ticket revisada/version 4 e review criado. `final_classification` contém review_id, category e priority; suggestion permanece para comparação. Resolver com expected_version 4 produz resolvido/version 5. Clientes devem usar a versão retornada, sem calcular incrementos a partir desses exemplos.

## Schemas de leitura

- Ticket: campos do exemplo, suggestion nullable e final_classification nullable. Nunca expor chave, URL do banco ou saída bruta do modelo.
- Attempt: id, ticket_id, attempt_number, content_revision, status, mode, provider/model (nullable), catalog_version, policy_version, started_at, deadline_at, finished_at, suggestion nullable, error_code nullable, model_calls, tool_calls. Datas em UTC ISO 8601; nenhuma credencial ou raciocínio interno.
- Review: id, ticket_id, attempt_id, content_revision, category, priority, reason, declared_reviewer, created_at.
- Listagens de histórico usam `{items,total,limit,offset}`. ID de chamado inexistente: 404, ainda que coleção esteja vazia.

## Erros e recuperação

Envelope uniforme proposto, inclusive para erros de validação (handler próprio):

```json
{"error":{"code":"invalid_transition","message":"O chamado não permite essa operação.","details":[],"request_id":"33333333-3333-4333-8333-333333333333"}}
```

422 contém details com `field` e `code`, sem ecoar valores de entrada. 404 = recurso inexistente; 409 = `version_conflict`, `invalid_transition` ou `triage_in_progress`. 502 = `invalid_ai_response`, `tool_protocol_error` ou `execution_limit`; 504 = `ai_timeout`; 503 = `ai_unavailable` ou `storage_unavailable`. Mensagens sanitizadas, sem stack trace. Erro inesperado: 500 genérico com request_id.

Quando a tentativa falha e o banco está acessível, adicionar um objeto com `ticket_id`, `attempt_id` e `triage_status:"falha"` à lista details. Assim, details permanece sempre uma lista: objetos de campo/código para validação ou objeto de contexto para falha de triagem. Consultar GET do chamado para obter a nova versão antes do retry. Quando o banco falha ao finalizar, não prometer que estado falha foi persistido: pode continuar em_analise até recuperação pelo prazo (RN15).

POST de criação não é idempotente: repetir após perda de resposta pode duplicar chamado. Isso é limitação do MVP; chave de idempotência fica para evolução. Repetir triagem com versão antiga dá 409 e evita execução duplicada. Timeout/desconexão do cliente não equivale a cancelamento garantido no servidor: consultar estado antes de repetir.


## Contrato implementado de US04

POST triage recebe somente expected_version inteiro estrito ≥1, sem extras, e exige aberto/pendente. Chamado já persistido, duas transações de estado, sem alterar conteúdo/content_revision nem final_classification. Retorna 200 `{ticket,attempt}` ou erro sanitizado; saída inválida=502, timeout simulado=504 e indisponibilidade simulada=503. Falha persistida tem contexto ticket_id/attempt_id/triage_status em error.details. GET de tentativas devolve `{items,total,limit,offset}`, ordenado started_at/id, limit 1–100 e offset≥0; 404 para chamado inexistente. Campos provider/model são null porque não existe provedor real. Não expõe mensagens nem saída bruta.

Restrição incremental explícita: repetir em sugerida/revisada/resolvido/em_analise ou falha retorna 409; versão antiga retorna 409/version_conflict. Retry após falha e recuperação por prazo do contrato planejado ficam em US05. O título exato `[SIMULADO:saida-invalida]` seleciona fixture inválida no simulador de demonstração; nenhuma chave scenario é aceita na API. Invalidação de sugestão por edição pode ser homologada agora conforme [roteiro US04](13-homologacao-us04.md).
