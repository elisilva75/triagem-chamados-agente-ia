# Homologação de US03 — edição com controle de versão

**CA1–CA3/T1–T3 e integração com US06 atendidos no escopo funcional local.** Registros manuais históricos de Eliana preservados abaixo; a validação técnica automatizada encerrou as dependências de classificação final/resolvido sem exigir repetição manual. Infraestrutura US01/Compose e CI no GitHub continuam pendentes; detalhes no complemento US06 e no andamento.

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

| Cenário | Estado | Evidência e origem |
|---|---|---|
| E01 edição e consulta | Confirmado no alcance do relato de Eliana em 08/11/2026 | PATCH expected_version=1: HTTP 200, descrição alterada, título preservado; version/content_revision 1→2. GET posterior: HTTP 200, versões=2 e descrição da primeira edição preservada. Classificação/timestamps/histórico não confirmados por esse relato |
| E02 versão antiga | Homologação manual informada por Eliana em 08/11/2026 | Novo PATCH com expected_version=1 e outra descrição: HTTP 409/version_conflict. GET posterior confirmou que a alteração rejeitada não foi aplicada. Variante executada altera descrição, não title como no roteiro original |
| E03 no-op após trim | Homologação manual informada por Eliana em 08/11/2026; histórico conferido tecnicamente pelo agente | HTTP 200, título normalizado, version/content_revision mantidos em 2 e timestamps iguais ao GET anterior. Consulta SQL posterior confirmou somente criado/revisão 1 e editado/revisão 2, sem evento adicional |
| E04a sem title/description | Homologação manual informada por Eliana em 08/11/2026 | HTTP 422/validation_error; GET 200 com conteúdo, versões 2 e timestamps preservados. Histórico reconfirmado somente em leitura: dois eventos |
| E04b título nulo | Homologação manual informada por Eliana em 08/11/2026 | PATCH expected_version=2 e title=null: HTTP 422/validation_error; GET 200 preservou título, descrição, version=2, content_revision=2 e timestamps. Consulta técnica posterior: exatamente dois eventos |
| E04c título curto | Homologação manual informada por Eliana em 08/11/2026 | PATCH expected_version=2/title="abcd": 422/validation_error, body.title/string_too_short. GET 200 com conteúdo, versões 2 e timestamps preservados. Consulta somente leitura posterior: exatamente dois eventos |
| E04d descrição curta | Homologação manual informada por Eliana em 08/11/2026 | PATCH expected_version=2/description="curta": HTTP 422/validation_error, body.description/string_too_short. GET 200 manteve conteúdo, versões 2 e timestamps. Consulta somente leitura posterior confirmou dois eventos |
| Histórico básico via SQL | Conferido pelo agente em 08/11/2026, em consulta somente leitura; não atribuído a Eliana | Um evento criado/revisão 1 e um editado/revisão 2. Snapshot anterior da edição contém revisão 1 e classificações nulas. Não comprova preservação de classificação não nula |
| Invalidação de classificação existente | Validação técnica automatizada integrada com US06; não é novo relato manual | Sugestão e classificação final geradas pelas rotas reais; no-op, invalidação, snapshots e bloqueios executados no teste existente reaproveitado. Dependência funcional atendida; sem repetição manual obrigatória |

### Registro de 08/11/2026 e próximo cenário

Origem das evidências acima: execução manual no Swagger **informada por Eliana**, sem observação visual ou reexecução pelo agente nesta etapa. ID e texto exato da descrição não foram transcritos, por isso não foram inventados. O GET confirma persistência da primeira alteração e não aplicação da segunda; não comprova, por si só, eventos ou snapshots no banco.

Próximo cenário escolhido: **E03 — no-op após trim (US03-CA3)**. Consultar o mesmo chamado por GET, copiar title/versões/timestamps e enviar PATCH com a versão atual e exatamente o título atual envolto em dois espaços no começo/fim. Expected_version=2 apenas se o GET ainda mostrar 2. Esperado: HTTP 200 e resposta integral idêntica ao GET anterior, sem incrementar versões nem alterar timestamps. Reconsultar e informar o resultado; aguardar retorno antes de E04.

Histórico básico de criação/edição pode ser inspecionado agora por SQL somente leitura, conforme consulta acima; não depende de US04, embora não exista endpoint de eventos no Swagger. Histórico de **classificação existente** requer dados classificados, hoje disponíveis apenas como fixtures nos testes automatizados; produção pelo fluxo da API depende de US04/US06. Não semear classificação diretamente no banco demo nem antecipar histórias para contornar essa dependência. A ausência de evento extra no no-op deve ser conferida separadamente no banco, não inferida apenas do JSON de resposta.

### Complemento de 08/11/2026 — E03 e conferência do histórico

Eliana informou E03: HTTP 200, título normalizado, versões mantidas em 2 e timestamps iguais ao GET anterior. Registrado como homologação manual informada, sem reexecutar PATCH pelo agente.

O agente executou `psql` no banco demo com `BEGIN READ ONLY`, consultou tickets, agrupamento/contagem de eventos e eventos completos, finalizando com COMMIT. Único chamado encontrado: `ad903cac-a750-48d3-b205-91da97d7adee`, version=2/content_revision=2. Histórico: **exatamente 2 eventos**, um `criado` na revisão 1 e um `editado` na revisão 2; nenhum evento adicional para o no-op. Evento criado em 07/11/2026 18:23:24.789820−03:00; editado em 08/11/2026 10:01:30.957372−03:00. Snapshot da edição: `{"suggestion":null,"content_revision":1,"final_classification":null}`. Não houve alteração de dados. O ID foi obtido pela consulta técnica, não transcrito do relato de Eliana.

Essa evidência confirma a preservação do evento original e ausência de evento extra no estado observado. Não comprova invalidação/preservação de uma classificação existente não nula: esse cenário continua dependente de US04/US06 pelo Swagger e só possui evidência automatizada com fixtures até aqui.

**Próximo cenário: E04a — PATCH sem title/description.** No mesmo chamado, enviar somente `{"expected_version":2}` (consultar versão atual se houver alteração posterior). Esperado: HTTP 422, error.code=validation_error, sem alteração de conteúdo/versões/timestamps. Conferir por GET e aguardar retorno antes de apresentar outra rejeição de E04. Não registrar E04 inteiro como homologado após apenas esse subcaso.

Permanecem pendentes E04 e invalidação/histórico de classificação existente não nula. Homologação de US03 continua aberta. Docker Compose e execução do CI no GitHub permanecem pendentes; US01 não totalmente validada e US04 não iniciada.

Ao responder, informar ID escolhido, HTTP e versão antes/depois de cada cenário executado, além de divergências. Registrar somente os cenários efetivamente informados; aguardar validação antes da próxima história.


### Complemento de 08/11/2026 — E04a informado; conferência atual do histórico indisponível

Eliana confirmou manualmente no Swagger o PATCH contendo somente `expected_version=2`: HTTP 422, `validation_error`. O GET posterior retornou HTTP 200 e preservou título, descrição, version=2, content_revision=2 e timestamps anteriores. **Homologação manual informada por Eliana**; o agente não reexecutou a requisição nem observou sua execução visualmente. E04a homologado no alcance desse relato; E04 completo permanece aberto.

Conferência técnica tentada com `psql -X -v ON_ERROR_STOP=1 -h 127.0.0.1 -p 55432 -U portfolio_test -d portfolio_chamados_demo -c <SQL>`, com SQL preparado para `BEGIN READ ONLY; SHOW transaction_read_only; SELECT` de versões/timestamps, contagem e eventos do chamado `ad903cac-a750-48d3-b205-91da97d7adee`, seguido de `COMMIT`. **Resultado: conexão recusada, saída 1; nenhuma instrução SQL foi executada.** O servidor não foi iniciado nem dados alterados. A última consulta bem-sucedida, anterior a E04a, encontrou dois eventos; ela não comprova a ausência de evento adicional após esta rejeição. Repetir a consulta somente leitura quando o PostgreSQL estiver disponível; conferência atual pendente.

**Próximo cenário vigente: E04b — title nulo (US03-CA2/CA3).** No Swagger local, consultar o mesmo chamado por GET e guardar conteúdo, versões e timestamps. Se version continuar 2, enviar PATCH `{"expected_version":2,"title":null}`. Esperado: HTTP 422, `error.code=validation_error`. Executar GET posterior: esperado HTTP 200 e mesmos título, descrição, versões e timestamps. Se a versão tiver mudado, usar a versão consultada e registrar a diferença. Aguardar o relato de Eliana antes de E04c; não repetir E01–E03 nem E04a. Se o ambiente estiver indisponível, retomar pelo guia Windows antes da execução manual, sem considerar o cenário realizado.

US03 continua em homologação. Sugestão existente depende de US04 e classificação final humana de US06 para produção via Swagger; preservação/invalidação de classificação não nula permanece sem homologação manual, com evidência automatizada por fixtures já registrada. Não semear o demo nem iniciar essas histórias para contornar a dependência. Docker Compose e CI no GitHub continuam pendentes; US01 parcialmente validada. Sem novas execuções de testes de aplicação nesta etapa, sem publicação, deploy ou chamadas pagas; somente AI_MODE=simulated.

Nova tentativa nesta continuidade de 08/11/2026: mesmo relato de E04a reconhecido, sem duplicar homologação. Consulta `psql -X -v ON_ERROR_STOP=1` ao mesmo banco/porta, com `BEGIN READ ONLY`, verificação do modo, SELECT de versões, contagem e eventos e COMMIT: conexão novamente recusada, código de saída do psql=2. Nenhum SQL executado, nenhum processo iniciado e nenhum dado alterado. O código 1 da tentativa anterior correspondeu ao comando PowerShell que lançou erro após a falha do psql. Histórico após E04a continua pendente de reconferência; não afirmar dois eventos atuais. Próximo cenário continua E04b (title=null); não avançar sem seu relato. US04/US06, Compose e CI mantêm as dependências e pendências acima.


### 08/11/2026 — Ambiente restabelecido; histórico de E04a reconfirmado

Por solicitação de Eliana, consultado o guia de execução e confirmado `.local/pgdata/PG_VERSION=16`. `pg_ctl status` informou servidor parado. Iniciado **o cluster existente**, com `pg_ctl -D <projeto>/.local/pgdata -l <projeto>/.local/postgres.log -o "-h 127.0.0.1 -p 55432" -w start`, sem initdb, createdb, limpeza ou migração. Primeira tentativa na sandbox falhou com erro 87 de criação de token; execução com permissão ampliada iniciou com sucesso. Aviso de possível servidor existente foi emitido pelo pg_ctl; nenhum PID/arquivo foi removido manualmente.

Consulta real por `psql -X -v ON_ERROR_STOP=1` ao banco demo, com `BEGIN READ ONLY; SHOW transaction_read_only; SELECT ...; COMMIT`, executada com sucesso: modo somente leitura `on`, banco `portfolio_chamados_demo`, endereço 127.0.0.1, porta 55432, migração 0002. Chamado `ad903cac-a750-48d3-b205-91da97d7adee`: **version=2, content_revision=2**. Histórico reconfirmado após E04a: **exatamente dois eventos**, criado/revisão 1 e editado/revisão 2, sem evento adicional pela rejeição. Snapshot da edição permanece com content_revision=1, suggestion=null e final_classification=null. Essa consulta resolve a pendência de conferência antes impedida por conexão recusada; não é reexecução do PATCH nem homologação visual pelo agente.

API iniciada em segundo plano com Start-Process/WindowStyle Hidden, Python da .venv, Uvicorn factory, bind 127.0.0.1:8000, DATABASE_URL do demo e AI_MODE=simulated. Launcher PID 18120 (reconferir identidade antes de encerrar); logs `.local/api-restored.stdout.log` e `.local/api-restored.stderr.log`. GET /health, /docs e /openapi.json retornaram **200**; versão 0.2.0 e PATCH presente. **GET /api/v1/tickets/ad903cac-a750-48d3-b205-91da97d7adee retornou 200 com o registro persistido**, comprovando consulta pela API além do health: aberto/pendente, versões 2, suggestion/final_classification nulos, created_at=2026-11-07T21:23:24.789820Z e updated_at=2026-11-08T13:01:30.959837Z. Nenhuma escrita de chamado/evento. Inspeção complementar com Get-NetTCPConnection teve acesso negado; isso não invalida os retornos HTTP nem a conexão SQL confirmados. API e banco deixados ativos, sem garantia de sobrevivência ao encerramento da sessão do sistema.

**Próximo cenário: E04b — título nulo**, usando expected_version=2 consultada. Orientar pelo Swagger e aguardar resultado de Eliana; **não executado e não homologado nesta etapa**. E01–E03 e E04a não foram repetidos. US03 continua aberta. Homologação com sugestão existente depende de US04; classificação final depende de US06; fixtures automatizadas não equivalem a homologação manual. Docker Compose e CI no GitHub continuam pendentes, US01 parcialmente validada. Sem início de US04/US06, chamadas pagas, publicação ou deploy. Verificação operacional SQL/HTTP executada; sem nova execução da suíte de testes de aplicação.


### 08/11/2026 — E04b informado; histórico conferido somente em leitura

E04b/US03-CA2/CA3 registrado uma única vez como **homologação manual informada por Eliana**: PATCH com expected_version=2 e title=null retornou HTTP 422/validation_error; GET posterior HTTP 200 preservou título, descrição, version=2, content_revision=2 e timestamps anteriores. Sem observação visual nem reexecução do PATCH pelo agente.

Conferência técnica executada com `psql -X -v ON_ERROR_STOP=1 -h 127.0.0.1 -p 55432 -U portfolio_test -d portfolio_chamados_demo -c <SQL>`: `BEGIN READ ONLY; SHOW transaction_read_only; SELECT` de chamado, contagem e eventos, seguido de `COMMIT`. **Saída 0**, transaction_read_only=on. Chamado `ad903cac-a750-48d3-b205-91da97d7adee`: version=2/content_revision=2, created_at=2026-11-07T21:23:24.789820Z, updated_at=2026-11-08T13:01:30.959837Z. **Exatamente dois eventos**, criado/revisão 1 e editado/revisão 2; nenhum evento adicional após E04b. Snapshot anterior da edição mantém revisão 1 e classificações nulas. Nenhuma escrita de dados ou alteração de processo; nenhuma nova execução de testes de aplicação alegada.

**Próximo cenário vigente: E04c — título abaixo de 5 caracteres**, conforme roteiro: no mesmo chamado, PATCH `{"expected_version":2,"title":"abcd"}`. Esperado HTTP 422/validation_error; GET posterior HTTP 200 com título, descrição, versões e timestamps preservados. Usar versão atual caso outro GET indique mudança. **E04c não executado; aguardar relato de Eliana antes de E04d.** Não repetir E01–E03/E04a/E04b. E04 completo e US03 permanecem abertos.

Pendências preservadas: classificação existente não nula depende de US04 (sugestão) e US06 (classificação final) para produção pelo Swagger; evidência automatizada com fixtures não equivale à homologação manual. Docker Compose e CI no GitHub pendentes; US01 parcialmente validada. US04/US06 não iniciadas, US08 adiada; somente AI_MODE=simulated, sem chamadas pagas, publicação ou deploy.


### 08/11/2026 — E04c informado; histórico reconfirmado somente em leitura

E04c/US03-CA2/CA3: **homologação manual informada por Eliana**, sem duplicação. PATCH expected_version=2 e title="abcd": HTTP 422, validation_error, campo body.title, motivo string_too_short. GET posterior HTTP 200 preservou título, descrição, version=2, content_revision=2 e timestamps anteriores. O agente não observou visualmente nem reexecutou o PATCH.

Conferência técnica executada com `psql -X -v ON_ERROR_STOP=1 -h 127.0.0.1 -p 55432 -U portfolio_test -d portfolio_chamados_demo -c <SQL>`: `BEGIN READ ONLY; SHOW transaction_read_only; SELECT` de versões/timestamps, contagem e eventos do chamado `ad903cac-a750-48d3-b205-91da97d7adee`; `COMMIT`. **Saída 0, transaction_read_only=on; exatamente dois eventos**, criado/revisão 1 e editado/revisão 2, sem evento adicional após E04c. Version/content_revision=2; created_at=2026-11-07T21:23:24.789820Z e updated_at=2026-11-08T13:01:30.959837Z. Nenhuma escrita de dados ou alteração de processo; nenhuma nova execução de testes de aplicação.

**Próximo cenário vigente: E04d — descrição abaixo de 20 caracteres.** No mesmo chamado, PATCH `{"expected_version":2,"description":"curta"}` (usar versão atual se houver mudança posterior). Esperado HTTP 422/validation_error; GET posterior HTTP 200 preservando título, descrição, versões e timestamps. **E04d não executado; aguardar relato de Eliana.** Não repetir E01–E03/E04a–E04c. E04 completo e US03 continuam abertos.

Pendências preservadas: sugestão existente depende de US04 e classificação final de US06 para homologação via Swagger; fixtures automatizadas não equivalem a homologação manual de classificação não nula. Docker Compose e CI no GitHub pendentes, US01 parcialmente validada. Sem início de US04/US06, US08 adiada; AI_MODE=simulated, sem chamadas pagas, publicação ou deploy.


### 08/11/2026 — E04d informado; roteiro E01–E04 coberto no alcance dos relatos

E04d/US03-CA2/CA3 registrado sem duplicação como **homologação manual informada por Eliana**: PATCH expected_version=2/description="curta" retornou HTTP 422, validation_error, body.description/string_too_short. GET posterior HTTP 200 manteve título, descrição, version=2, content_revision=2 e timestamps anteriores. Sem observação visual ou reexecução do PATCH pelo agente.

Conferência técnica: `psql -X -v ON_ERROR_STOP=1 -h 127.0.0.1 -p 55432 -U portfolio_test -d portfolio_chamados_demo -c <SQL>`, com `BEGIN READ ONLY; SHOW transaction_read_only; SELECT` de chamado/contagem/eventos e `COMMIT`: **saída 0**, modo somente leitura on, **exatamente dois eventos**, criado/revisão 1 e editado/revisão 2; nenhum evento adicional após E04d. Chamado ad903cac-a750-48d3-b205-91da97d7adee com version/content_revision=2, created_at=2026-11-07T21:23:24.789820Z, updated_at=2026-11-08T13:01:30.959837Z; snapshot anterior mantém revisão 1 e classificações nulas. Nenhuma escrita de dados ou mudança operacional.

E01–E03 e os quatro exemplos E04a–E04d estão registrados no alcance dos relatos, com histórico básico conferido tecnicamente. Não solicitar repetição desses exemplos nem confundir E04 com homologação de todos os limites/tipos. A matriz atual de cenários restantes está em [homologação US03](12-homologacao-us03.md): testes automatizados já executados na entrega de 07/11/2026 cobrem os demais limites, entradas inválidas, UUID ausente no PATCH, estados bloqueados, concorrência, rollback, migração e classificação com fixtures. Revisão dos arquivos de teste nesta etapa; **suíte não reexecutada**. Evidência histórica: 72 passed/1 warning, registrada abaixo; não atribuir esse resultado a nova execução.

**US03 não encerrada e US04 não iniciada.** Homologação manual pendente de classificação não nula e seus snapshots preservada; produção pelo Swagger depende de US04 (sugestão) e US06 (classificação final). Estados em_analise/resolvido dependem dos respectivos fluxos futuros para eventual homologação manual, mas já têm testes com fixtures. Não semear o demo nem antecipar histórias. Não há próximo exemplo E05 definido no roteiro atual. Não criar exigência de repetir manualmente toda a suíte: revisão/aceite de Eliana deve considerar a matriz de evidências e as pendências sem convertê-las em aprovação automática. Docker Compose e CI no GitHub pendentes, US01 parcialmente validada; US08 adiada, AI_MODE=simulated, sem chamadas pagas, publicação ou deploy.


### Cenários restantes e tipo de evidência — situação após E04d

E01–E03 e E04a–E04d já informados manualmente; não repetir. E04 cobre os quatro exemplos do roteiro, não todos os limites possíveis. Não há E05 definido. US03 permanece aberta para revisão/aceite de Eliana e pendências explicitadas abaixo.

| Cenário / rastreabilidade | Evidência disponível | Homologação manual restante / encaminhamento |
|---|---|---|
| Edição, conflito, no-op e quatro rejeições E04; CA1–CA3 | Relatos de Eliana e conferências técnicas do histórico | Nenhum novo exemplo do roteiro pendente; preservar o alcance de cada relato, sem presumir campos não informados em E01 |
| Invalidação de sugestão/classificação final não nula e retorno a pendente; CA1/T2 | `test_us03_ca1_archive_classification_and_preserve_history`, PostgreSQL real com fixture sintética | Homologação manual permanece pendente conforme registro anterior; sugestão via Swagger depende de US04, classificação final de US06. Não antecipar histórias |
| No-op com classificação não nula e snapshot preservado após múltiplas edições; CA1/CA3/T2 | Mesmo teste de integração, com fixture; snapshot anterior preservado | Homologação manual desse fluxo permanece dependente de US04/US06; histórico atual com null não comprova esse caso |
| Bloqueio em_analise e resolvido; CA2 | `test_us03_ca2_blocks_state_without_changes` e guardas unitárias; fixtures de estado | Sem homologação manual desses estados; eventual execução pelo Swagger depende de US04 (em_analise) e US06 (resolvido). Não repetir fixture no demo nem criar obrigação adicional de repetição manual |
| Duas edições concorrentes na mesma versão; T2/RN16 | `test_us03_ca2_two_connections_only_one_version_wins`: duas conexões reais, um sucesso e um conflito | Coberto automaticamente; não requer repetir manualmente para o roteiro atual. E02 não equivale a disputa simultânea |
| Demais limites: título 5/120 e descrição 20/5000, trim/Unicode; rejeições 4/121 e 19/5001; CA3 | `test_us03_ca3_http_boundary_values`, teste de entradas inválidas da API e testes unitários de schema | Cobertos automaticamente; sem nova exigência manual. E04c/d são exemplos abaixo do mínimo, não todos os limites |
| description=null, versão ausente/inválida, tipos e campos extras; CA2/CA3 | `test_us03_ca2_ca3_invalid_patch_does_not_change_database` e `test_us03_ca2_ca3_patch_rejects_invalid` | Cobertos automaticamente nas camadas correspondentes; sem repetir no Swagger. Não alegar teste HTTP para todas as variantes unitárias |
| PATCH para UUID inexistente; CA2/contrato | `test_us03_ca2_stale_version_and_not_found` | Coberto automaticamente; GET inexistente homologado em US02 não é homologação manual de PATCH inexistente. Sem novo passo obrigatório no roteiro |
| Falha de gravação do evento reverte edição e classificação; T2 | `test_us03_edit_event_failure_rolls_back_everything`, falha real de constraint em banco isolado | Coberto automaticamente; não provocar falha no demo |
| Migração preserva chamado e roundtrip; T2 | `test_us03_migration_preserves_existing_ticket`; preservação demo já conferida no upgrade | Coberto tecnicamente; sem downgrade/repetição manual no demo |
| Fluxo HTTP contra servidor real; T2 | `tests/e2e/test_http.py`, Uvicorn/TCP e PostgreSQL real | Execução histórica registrada; sem nova exigência manual |

Os testes acima foram inspecionados, não reexecutados nesta atualização. Resultado executado da entrega original em andamento: 72 passed, 1 warning, em 07/11/2026. Evidência automatizada não é homologação manual. Docker Compose e CI remota continuam pendentes; não constituem cenários E04 nem foram aprovados pela execução nativa. US01 segue parcialmente validada. Não iniciar US04 sem validação/autorização de continuidade de Eliana, nem encerrar US03 com aceite obrigatório pendente.


### Aceite de Eliana e continuidade autorizada — 08/11/2026

Eliana **aceitou os resultados manuais E01–E04 de US03** e autorizou US04 exclusivamente simulada, mantendo esta história aberta com as pendências específicas. Não repetir esses cenários. O novo roteiro em [homologação US04](13-homologacao-us04.md) permite verificar pela primeira vez no Swagger no-op com sugestão não nula, edição que a invalida e preservação da tentativa. Esses passos ainda aguardam execução/relato de Eliana; não estão aprovados pela implementação de US04. Snapshot no evento pode ser reconferido tecnicamente por SQL após o relato.

Classificação final humana e estado resolvido continuam dependentes de US06. Bloqueio em_analise possui teste automatizado com tentativa real de US04, sem exigir uma corrida manual de cliques num simulador imediato. Preservação de snapshot após múltiplas edições continua com evidência automatizada e pendência manual registrada, sem acrescentar repetição ao roteiro curto. Nenhuma pendência foi encerrada automaticamente. Compose e CI remota permanecem pendentes.


### Complemento US04 — sugestão existente, no-op e invalidação (08/11/2026)

Eliana informou M01a–M01c: sugestão simulada obtida (versões 4/2), no-op preservou sugestão e versões e edição seguinte invalidou a sugestão (versões 5/3). Conferência GET/SQL somente leitura confirmou conteúdo editado, tentativa anterior íntegra e snapshot no novo evento exatamente igual à sugestão anterior, mantendo os dois eventos/snapshot antigos. Três eventos totais, sem evento adicional no no-op. Registros detalhados e timestamps em [US04](13-homologacao-us04.md). Timestamp intermediário do no-op não foi informado nem capturado pelo agente; não inferir preservação desse campo após a edição posterior, nem repetir o cenário já conferido. Dependência de US04 para produzir e invalidar sugestão agora exercitada no alcance do relato. Classificação final e resolvido dependem de US06; demais pendências específicas não são encerradas automaticamente. Compose e CI permanecem pendentes.


### Estratégia vigente: lacunas de integração, sem repetição manual obrigatória

Eliana autorizou validar M02/no-op por automação e iniciar US05 após critérios independentes atendidos. Testes reaproveitados executados: 3 passed/1 warning, incluindo no-op classificado com timestamps/sugestão/versões e contagem imediata de eventos, M02 e snapshots de classificação. A lacuna histórica do timestamp de uma resposta manual específica não é reconstruível e não bloqueia a regra funcional automatizada. Demonstrações curtas são opcionais, não pedir repetição de limites/campos/snapshots já automatizados. Restam para US06 os testes integrados produzindo classificação final humana/resolvido pelas rotas públicas; fixtures já cobrem a lógica de edição nesses estados. US03 não é declarada integralmente integrada com US06 antes dessa implementação. Docker Compose e CI permanecem pendentes.


### US06 — dependências funcionais encerradas por validação técnica automatizada

Eliana autorizou US06 e testes integrados, com demonstrações opcionais. O teste existente `test_us03_ca1_archive_classification_and_preserve_history` foi reaproveitado: criação/triagem/revisão produzidas pelas rotas reais, no-op revisado com resposta inteira/timestamps preservados e sem evento extra, edição invalida sugestão e classificação final e mantém review/tentativa, segunda edição preserva o snapshot não nulo anterior, nova triagem/revisão referencia a nova revisão sem alterar histórico antigo. O fluxo US06 cobre edição/no-op bloqueados em resolvido, reabertura, correção de revisão e preservação de classificação/histórico; o teste de tentativa ativa real foi ampliado para bloqueios em_analise sem duplicar cenário. Evidência em [validação US06](15-validacao-us06.md) e andamento.

Isso encerra a dependência **funcional de US03 com US06**, por automação isolada, sem atribuir nova homologação manual a Eliana. Captura histórica do timestamp do no-op manual específico continua indisponível; não é lacuna funcional a repetir, pois a regra foi verificada por automação. Critérios locais CA1–CA3/T1–T3 atendidos após a regressão documentada. Não converter Compose/CI em aprovado: US01 permanece parcialmente validada e o MVP global ainda tem pendências de infraestrutura/qualidade/portfólio.
