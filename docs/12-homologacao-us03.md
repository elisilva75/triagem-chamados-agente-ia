# Homologação de US03 — edição com controle de versão

**Implementada e verificada automaticamente; aguardando validação de Eliana.** Nenhum cenário abaixo foi registrado como aprovado manualmente. US01/Compose e CI no GitHub continuam pendentes. Não iniciar US04.

## Ambiente preparado

API local versão 0.2.0 disponível em http://127.0.0.1:8000/docs. PATCH consta em `/openapi.json`, /docs retornou 200. PostgreSQL demo em 127.0.0.1:55432, migração 0002 (head). O único chamado existente e seu evento de criação foram comparados antes/depois da migração e preservados integralmente; o agente não editou o chamado demo. Consulta posterior confirmou total=1 e version=1. Reconsultar antes de testar, pois Eliana pode ter alterado os dados desde esse registro.

Atualizar a página com **Ctrl+F5**. Se a API não estiver ativa, seguir os comandos de retomada do [guia Windows](10-validacao-local.md), aplicando `alembic upgrade head` antes de iniciar. Usar somente dados fictícios.

## Passo inicial — obter ID e versão

Expandir **GET /api/v1/tickets** → **Try it out** → manter limit=20, offset=0, filtros vazios → **Execute**. Copiar `items[0].id`, `title`, `description`, `version` e `content_revision`. Esperado: 200. O ID do cadastro homologado não foi transcrito no relato de Eliana, por isso deve ser obtido da listagem atual, sem adivinhá-lo. Alternativa: criar um novo chamado fictício para manter o anterior intacto; registrar qual ID foi escolhido.

## E01 — editar descrição (US03-CA1)

Expandir **PATCH /api/v1/tickets/{ticket_id}** → **Try it out**. Preencher ticket_id com o ID escolhido. Substituir todo Request body pelo JSON abaixo, trocando 1 pela version consultada se necessário:

```json
{
  "expected_version": 1,
  "description": "Descrição corrigida: no ambiente fictício, ao salvar o cadastro de demonstração, a tela apresenta erro."
}
```

Clicar **Execute** uma vez. Esperado: **200**; description corrigida; title preservado; version e content_revision incrementados em 1; status=aberto, triage_status=pendente; suggestion/final_classification=null; created_at preservado e updated_at atualizado, ambos em UTC. Guardar versão anterior e versão nova. Reconsultar por GET `/api/v1/tickets/{ticket_id}`: **200**, mesmos dados do PATCH.

## E02 — impedir edição com versão antiga (US03-CA2)

No mesmo PATCH, informar a expected_version anterior a E01 e title="Título com versão antiga". Esperado: **409**, error.code=version_conflict e request_id. Repetir GET: título, descrição e versões continuam como após E01. Não ajustar automaticamente a versão e repetir sem revisar o conteúdo atual.

## E03 — alteração sem efeito após trim (US03-CA3)

Consultar versão/título atuais. Enviar PATCH com expected_version atual e title exatamente igual ao atual, acrescido de dois espaços no começo/fim. Esperado: **200**, retorno inteiro igual ao GET anterior, inclusive timestamps, versões e classificação. Não criar evento editado adicional.

## E04 — campos/limites inválidos (US03-CA2/CA3)

Usar expected_version atual. Executar uma entrada de cada vez:

- `{"expected_version":2}` (adaptar versão): sem title/description → **422**.
- `{"expected_version":2,"title":null}` → **422**.
- `{"expected_version":2,"title":"abcd"}` → **422**, título abaixo de 5 caracteres.
- `{"expected_version":2,"description":"curta"}` → **422**, descrição abaixo de 20 caracteres.

GET após cada rejeição deve permanecer inalterado. Não há avanço de versão por rejeição. Limites completos e tipos também foram executados em testes automatizados; não declarar que todos foram homologados manualmente a partir desses quatro exemplos.

## Histórico e estados que ainda não são produzidos pela API

Eventos persistem em `ticket_events`. Não há endpoint de eventos nesta história. Se desejar inspecionar manualmente, executar consulta somente leitura no PostgreSQL demo, substituindo o UUID pelo ID escolhido:

```sql
SELECT type, content_revision, previous_classification, created_at
FROM ticket_events
WHERE ticket_id = 'UUID_DO_CHAMADO'
ORDER BY content_revision, created_at, id;
```

Esperado após uma única edição efetiva: evento criado original e um editado na revisão seguinte, com snapshot da classificação anterior. No-op e rejeições não criam eventos. Não gravar diretamente no banco para simular resolução ou análise durante a homologação.

A invalidação de classificação existente, a preservação de snapshots após múltiplas edições, o bloqueio de resolvido/em_analise e a concorrência foram verificados em PostgreSQL real com **fixtures fictícias**. Não foram executadas triagens/revisões para produzir essas fixtures. Esses casos não são reproduzíveis só pelo Swagger até US04–US06 e permanecem identificados como evidência automatizada, não manual. Concorrência automatizada usa duas conexões e a mesma versão: exatamente uma edição confirma e a outra recebe 409.

## Registro manual

| Cenário | Estado | Evidência informada por Eliana |
|---|---|---|
| E01 edição e consulta | Aguardando homologação | — |
| E02 versão antiga | Aguardando homologação | — |
| E03 no-op após trim | Aguardando homologação | — |
| E04 rejeições | Aguardando homologação | — |
| Histórico via SQL opcional | Não executado manualmente | Coberto por automação PostgreSQL |

Ao responder, informar ID escolhido, HTTP e versão antes/depois de cada cenário executado, além de divergências. Registrar somente os cenários efetivamente informados; aguardar validação antes da próxima história.
