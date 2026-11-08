# Andamento e continuidade

## 08/11/2026 — US01, US07 e US09: preparação local do MVP simulado

### Autorização e resultado atual

Eliana autorizou fechar qualidade/documentação e verificar ambiente, preservando o demo, sem publicação, deploy ou chamadas pagas. Branch local `chore/mvp-readiness`, baseada em `8049206`, sem reescrever histórico. Arquivo workspace preexistente continua intacto e não incluído. Evidências desta seção são **validação técnica automatizada executada pelo agente**, não novos relatos de homologação manual de Eliana. Registros manuais anteriores não foram duplicados.

**US01 continua parcial:** Docker ausente no PATH, no caminho Program Files e nos caminhos locais de instalação conferidos. Não houve build, Compose, teste de volume ou reinício de containers. Pré-requisito: Docker Desktop com mecanismo Linux ativo e Compose, conforme fontes no documento 09. Não instalado nem contratado nesta entrega. Guia identifica comandos Compose não executados e separa portas/projeto/volume para preservar demo. CA2/CA3 continuam cobertos pela regressão nativa; CA1 exige execução própria.

**US07: critérios/tasks no equivalente local executados; CI remoto permanece pendente.** Workflow usa Ubuntu, PostgreSQL 16 de serviço, Python 3.12, locks existentes, AI_MODE=simulated/APP_ENV=test e credenciais fictícias. Sem secrets de provedor ou adaptador real. Instalação pelo lock e permissões contents:read preservadas; job limitado a 20 minutos, upload JUnit com always. Runner compartilhado interrompe na primeira falha e rejeita suíte obrigatória vazia/com skips. Arquivo revisto não equivale à execução do GitHub Actions; nem valida o provisionamento Linux/container nesta máquina.

**US09: documentação e ensaio no escopo nativo isolado atendidos.** README PT/EN, arquitetura/modelo atual, contrato/exemplos, guia Windows consolidado (removidas instruções obsoletas de versões), roteiro curto/descrição de portfólio e declaração de uso de IA no desenvolvimento. Integração real permanece adiada em US08; não há SDK de modelo, avaliação de acurácia ou inferência paga. Publicação preparada para revisão futura, sem PR remoto/push/deploy.

### Rastreabilidade da entrega

| História / critérios / tasks | Arquivos e cobertura | Evidência executada |
|---|---|---|
| US01-CA1/T3 | compose.yaml, Dockerfile, guia 10, ambiente 09 | Diagnóstico Docker indisponível; execução Compose não aprovada |
| US01-CA2/CA3/T2 | Suíte existente de health/migração | Regressão real PostgreSQL e dois roundtrips simultâneos, sem limpar demo |
| US07-CA1/T1/T2/T3 | .github/workflows/ci.yml, scripts/check_quality.py, suites unit/integration/api/e2e | Pipeline local 177 passed, relatórios por camada; GitHub remoto pendente |
| US07-CA2/T1/T2 | tests/unit/test_quality_gate.py | 4 casos novos: primeira falha bloqueia sequência, config obrigatória, relatório vazio e com skip bloqueados; sem duplicar testes de produto |
| US07-CA3/T2 | tests/conftest.py e roundtrip existente reaproveitado | Nome isolado sem URL/senha registrado em JUnit; duas execuções concorrentes passaram com bancos distintos, migração do zero/duplo upgrade/downgrade/upgrade |
| US09-CA1/T1/T3 | README.md, README.en.md, docs 04/05/10/16, scripts/demo_flow.py | Roteiro cadastro→falha→retry→correção→sugestão→review→resolve executado por HTTP real em fontes isoladas |
| US09-CA2/T2 | Revisão de arquivos rastreados + 5 novos previstos, .gitignore/.dockerignore | 88 arquivos inspecionados; sem artefatos locais ou achados de segredo nos padrões conferidos; links locais verificados |
| US09-CA3/T2 | Exportação limpa em .local/rehearsal-source, venv nova, banco exclusivo gerado | Lock instalado, pip check, upgrade head duas vezes, health + consulta real, roteiro e reinício nativo da API com GET integral idêntico |

### Comandos e resultados realmente executados

Na raiz em PowerShell, definidos TEST_DATABASE_URL para banco administrativo `portfolio_test` em 127.0.0.1:55432, AI_MODE=simulated e APP_ENV=test. Executado `.venv/Scripts/python.exe scripts/check_quality.py`, saída 0:

- pip check aprovado; Ruff check aprovado e format aprovado. Rechecagem final inclui scripts novos.
- `pytest tests/unit -q --junitxml=reports/unit.xml`: **98 passed, 1 warning, 1,41 s**.
- `pytest tests/integration tests/api -q --junitxml=reports/postgres-api.xml`: **77 passed, 1 warning, 504,42 s** (53 API in-process + 24 integração, incluindo driver real com conexão recusada). Execução teve outros ensaios isolados concorrentes; não usar duração como benchmark da suíte.
- `pytest tests/e2e -q --junitxml=reports/http-real.xml`: **2 passed, 1 warning, 42,16 s**, Uvicorn/TCP/PostgreSQL reais, incluindo interrupção/reinício/recuperação por prazo.

**Total: 177 passed, nenhuma falha/erro/skip.** Um aviso conhecido se repete por camada: Starlette TestClient depreca HTTPX. Não instalado pacote para ocultá-lo. Relatórios ignorados pelo Git; nenhuma porcentagem de cobertura de linhas foi medida.

Isolamento: `.venv/Scripts/python.exe .local/check_isolation.py` iniciou em paralelo duas execuções do teste existente `test_us01_ca3_migrations_roundtrip_and_metadata`, cada uma com JUnit próprio (reports/isolation-0.xml e isolation-1.xml). Ambas saída 0, 1 passed cada (26,55 s e 26,88 s); bancos `portfolio_test_c10e936cd83a436ea996ad3133e79bba` e `portfolio_test_1ea251901d1940ca945e873047ea8e67`, distintos e removidos pela fixture. São reexecuções do mesmo teste, não dois casos novos somados aos 177.

Instalação/guia: `python -m venv .local/rehearsal-venv` e Python dessa venv com `-m pip install -r requirements-dev.lock` concluídos. A primeira tentativa restrita foi interrompida sem progresso; a execução autorizada com acesso aos pacotes terminou usando cache. Sem alteração de locks/versões ou instalação global. `.local/rehearse_readiness.py` copiou os 88 arquivos de fonte/documentação preparados para diretório sem .env/.git/.venv/dados locais; usou venv nova e banco gerado `portfolio_test_6986db906ad443e4b2fc5a0244231235`, com migrações 0001–0004 do zero e segundo upgrade sem alteração. Não foi clone remoto ou máquina Windows nova: reutilizou binários PostgreSQL 16.4 e cluster nativo existente, com banco separado.

Ensaio: `scripts/demo_flow.py --base-url <loopback:porta exclusiva>` na cópia isolada retornou 201 no cadastro, 502/invalid_ai_response nas duas tentativas, 200 na correção, 200 na triagem válida, 201 na review e 200 na resolução. Consultou GET antes de cada escrita. Final resolvido/revisada, version=10, content_revision=2, 3 tentativas e 1 review; reinício do processo da API manteve GET completo idêntico. Banco gerado removido no finally; demo não usado. Evidência local em .local/readiness-rehearsal.json. Esse reinício **não valida reinício Compose**.

Reutilização do cluster: `scripts/start-test-postgres.ps1` não conseguiu reconhecer processo/abrir log sob o token restrito do sandbox e falhou. pg_isready e consultas continuaram respondendo; não houve recriação nem perda de dados. Reexecução autorizada fora dessa restrição reconheceu PID 18284 e reutilizou o cluster existente, saída 0. A limitação foi incluída no guia.

### Medição informativa RNF03 e preservação de dados

`.venv/Scripts/python.exe .local/measure_readiness.py`: banco exclusivo com 1.000 chamados fictícios, Uvicorn/TCP loopback, HTTPX com conexão reutilizada, 100 requisições sequenciais por operação, sem IA. GET individual p95 **30,95 ms**, GET lista limit=20 p95 **43,25 ms**, POST p95 **45,99 ms**; máximos 104,03 / 51,95 / 173,77 ms. Leituras feitas com 1.000 registros; os 100 POSTs elevaram a base até 1.100. p95 calculado por ordem/nearest rank. Windows 11 build 26300, Intel64 Family 6 Model 142 Stepping 10, PostgreSQL 16.4 nativo, Python 3.12.6; evidência .local/readiness-performance.json. Abaixo da referência informativa de 500 ms neste ensaio, sem alegar SLA, carga concorrente ou desempenho Docker/produção.

Demo consultado em transações somente leitura antes/depois: comparação integral JSON por ID de tickets, ticket_events, triage_attempts e human_reviews **idêntica**, incluindo timestamps/snapshots. Permanece 1 chamado, 3 eventos, 1 tentativa, 0 reviews; chamado histórico ad903cac-a750-48d3-b205-91da97d7adee continua version=5/content_revision=3. Evidências .local/demo-readiness-before.json e after.json. Nenhum servidor demo encerrado/recarregado.

Revisão de preparação: `.local/audit_readiness.py` verificou os 88 arquivos rastreados/novos previstos, 80 links Markdown locais, caracteres Unicode inválidos, artefatos de venv/banco/.env e padrões de tokens/chaves privadas/URLs com credenciais. Nenhum achado final ou link quebrado; a credencial `segredo_demo` em teste de conexão recusada foi inspecionada e confirmada fictícia (o próprio teste exige que não vaze na resposta). Não é garantia de detecção universal de segredos. `git check-ignore` confirmou .env, .venv, .local e reports; .dockerignore reforçado para reports/cache/workspace. Sem dados de empregadores identificados. Diff revisado, `git diff --check` aprovado após corrigir linha vazia no fim do guia, sem incluir workspace preexistente ou dados locais. Qualidade registrada no commit local `6310986`; documentação preparada em commit separado, sem push.

### O que ainda impede a entrega final

1. US01-CA1: disponibilizar Docker/Compose e executar build/start/migração/consulta/reinício com volume em projeto isolado. Não concluído.
2. Executar workflow no GitHub após autorização de publicação. US07 tem equivalente local aprovado; CI remoto/Linux não executado e permanece gate separado.

US02–US06 sem novo gate manual; US09 preparada/ensaiada no escopo nativo descrito. US08 adiada por decisão de produto, não bloqueia o MVP simulado. A próxima revisão de publicação deve partir destes arquivos concretos e não exigir nova homologação manual de regras já automatizadas. Não houve chamada paga, publicação, PR remoto ou deploy.

## 08/11/2026 — US06 e dependências funcionais de US03 verificadas automaticamente

### Escopo, implementação e DoD

Eliana autorizou US06 conforme backlog/regras, com automação isolada, demonstração opcional e preservação do demo. Criada branch local `feat/us06-human-review` a partir da entrega US05 `555b414`, sem reescrever histórico ou tocar no arquivo workspace preexistente. Sem iniciar US07/US09 ou US08 adiada. Origem das evidências abaixo: **validação técnica automatizada pelo agente**, não homologação manual informada por Eliana.

Entregues POST/GET reviews, GET review por ID/Location, POST resolve/reopen. Revisão exige categoria/prioridade válidas, motivo 10–500 e autor declarado 2–80 após trim. Classificação final aponta para HumanReview gerada; correção em revisada insere outra review, preserva a anterior e a sugestão da IA. Resolver exige aberto/revisada com classificação final vinculada ao próprio chamado/revisão; reabrir mantém classificação/conteúdo. Escritas com versão antiga ou transições repetidas são rejeitadas, sem histórico adicional. Revisão e transições não chamam provedor.

Migração 0004 cria human_reviews e unicidade de tentativa/chamado/content_revision para FK composta; nenhuma revisão fictícia é retroativamente criada. Referência final permanece em projeção JSON validada pelo serviço sob lock, conforme ADR10. Novo registro/referência final e transições/eventos são transacionais. Autor é declarado e sem autenticação; histórico imutável pelas rotas, sem promessa de auditoria legal. Mesmas dependências/locks/fontes oficiais, sem instalação/reconfiguração de bibliotecas; aplicação 0.5.0.

| História/critério/tasks | Código/teste | Evidência executada |
|---|---|---|
| US06-CA1/T1/T2 | application/reviews.py, schemas/rotas, HumanReview; test_us06_ca1_ca3_review_correct_resolve_reopen_and_preserve_history | Review inicial, correção com nova decisão final, autor/motivo persistidos, sugestão/primeira review intactas, resolução e reabertura com version+1 sem alterar content_revision |
| US06-CA2/T2 | Guardas/ReviewCreate; testes de estado e entrada inválida | Pendente/falha/sugerida sem review não resolvem; resolvido não revisa/edita nem aceita no-op; em_analise bloqueia review/resolve/reopen no teste de tentativa real reaproveitado. Enums/tipos/extras/limites inválidos retornam 422 sem escrita |
| US06-CA3/T2 | reason/declared_reviewer; testes unitários e HTTP | Motivo 10/500 e autor 2/80 aceitos após trim/Unicode, ±1 rejeitados. Revisão subsequente mantém registro anterior e Location consultável |
| US06-CA4/T1/T2 | SELECT FOR UPDATE + expected_version; testes de conflitos/escopo/concorrência | Versão antiga, transições repetidas e seis disputas de duas conexões: só uma escrita confirma, outra recebe version_conflict, sem duplicar reviews/eventos |
| US03-CA1/CA3 com US06 | Teste existente test_us03_ca1_archive_classification_and_preserve_history reaproveitado | Preparação agora via POST cadastro/triagem/review, sem fixture sintética nesse caso. No-op mantém resposta integral/timestamps/classificações e contagem imediata de eventos=1. Edição limpa sugestão/final e preserva reviews/tentativas; segunda edição e nova triagem/review mantêm snapshot não nulo antigo e vinculam novo conteúdo |
| US03-CA2 com US06 | Fluxo US06 + teste existente de tentativa ativa | Edição/no-op bloqueados em resolvido; edição bloqueada em_analise com tentativa real. Reabertura habilita escrita; resolve após invalidação é bloqueado até nova classificação |
| US06-T2 atomicidade/integridade | tests/integration/test_reviews.py | FK composta rejeita outro ticket/revisão; projeção final interna corrompida é rejeitada. CHECK real inválido após inserir review reverte também projeção/versão; evento inválido de resolve/reopen reverte estado/timestamp/histórico |
| US06-T2 migração/HTTP real | Teste de migração novo + roundtrip existente; tests/e2e/test_http.py ampliado | Upgrade preserva tentativas/snapshots; alembic check sem divergência; downgrade só em banco descartável. Uvicorn/TCP real percorre review→resolve→bloqueio→reopen→edição/invalidação, preservando review/tentativa |
| US06-T3 | README, ADR10, contrato, backlog, guia, docs/15-validacao-us06.md | Critérios/tasks/resultados, DoD local e pendências separados; demonstração opcional, sem repetição manual obrigatória |

### Comandos e resultados efetivos

Executados na raiz com Python da .venv, TEST_DATABASE_URL apontando para o banco administrativo isolado portfolio_test em 127.0.0.1:55432. Cada teste cria e remove somente seu portfolio_test_<uuid>; nenhum POST/PATCH de teste no demo:

```powershell
.\.venv\Scripts\python.exe -m ruff check .
.\.venv\Scripts\python.exe -m ruff format --check .
.\.venv\Scripts\python.exe -m pip check
.\.venv\Scripts\python.exe -m pytest tests/unit/test_reviews.py -q
$env:TEST_DATABASE_URL='postgresql+psycopg://portfolio_test:senha_ficticia_teste@127.0.0.1:55432/portfolio_test'
.\.venv\Scripts\python.exe -m pytest tests/api/test_reviews.py tests/integration/test_postgres.py::test_us01_ca3_migrations_roundtrip_and_metadata -q --junitxml=reports/us06-api-focused.xml
.\.venv\Scripts\python.exe -m pytest tests/integration/test_reviews.py tests/integration/test_editing.py::test_us03_ca1_archive_classification_and_preserve_history tests/api/test_triage.py::test_us04_attempt_committed_and_no_connection_held_during_provider tests/e2e/test_http.py -q --junitxml=reports/us06-integration-focused.xml
.\.venv\Scripts\python.exe -m pytest -q --junitxml=reports/us06-all.xml
```

**Resultados: 21 unitários passed (0,13 s); foco API/migração 7 passed (48,70 s); foco integração/HTTP reaproveitado 14 passed (79,25 s). Regressão final: 173 passed, 1 warning, 292,88 s; zero falhas, erros ou skips.** XML conferido: 94 unitários, 53 API dentro do processo com PostgreSQL real, 24 integração (23 com PostgreSQL ativo, um de conexão recusada com driver real), 2 HTTP/TCP com servidor Uvicorn e PostgreSQL real. Inclui regressão US01–US05, recuperação/reinício real e todos os testes novos. Sem SQLite ou modelo de IA externo. Não somar focos à suíte como se fossem casos distintos.

Nenhuma execução pytest desta entrega falhou. Primeiras passagens de Ruff apontaram formatação/linhas longas, corrigidas antes das verificações finais. Ruff check/format e pip check aprovados. Aviso conhecido Starlette/TestClient sobre HTTPX preservado, sem pacote novo para ocultá-lo. Relatórios locais reports/us06-*.xml ignorados pelo Git. Links locais conferidos sem referências quebradas.

### Demo e ambiente

Snapshot SQL somente leitura antes da entrega em `.local/demo-us06-before.json` e comparação antes/depois da migração `alembic upgrade head` e novamente após recarregar API: **todos os campos anteriores integralmente iguais**, 1 chamado, 3 eventos e 1 tentativa; human_reviews=0. Snapshot posterior `.local/demo-us06-after.json`, fora do Git. Esquema demo **0004**. Nenhum chamado/review/evento/tentativa inserido/alterado no demo pelo agente; somente DDL aditiva. Nenhum initdb, createdb, limpeza ou downgrade no demo.

API anterior identificada por executável absoluto da .venv, comando Uvicorn e parentesco (launcher 3524/servidor 3324) antes de encerrá-la. Recarregada somente a API deste projeto, mesma DATABASE_URL demo/AI_MODE=simulated/bind 127.0.0.1:8000. Novo launcher PID **22504**, sempre reconferir identidade antes de encerrar; logs `.local/api-us06.*`. /health, /docs, /openapi.json, GET do chamado e GET reviews retornaram 200; OpenAPI 0.5.0 com reviews/resolve/reopen; chamado mantém version=5/content_revision=3 e classificação final nula; histórico reviews vazio. API/banco deixados ativos sem garantia de sobreviver ao encerramento da sessão do sistema. Nenhuma configuração global ou .env alterado.

### Status das histórias e pendências segundo DoD

**US03: dependência funcional de US06 encerrada por automação integrada; CA1–CA3/T1–T3 locais atendidos. US06: CA1–CA4/T1–T3 implementados e verificados, DoD funcional local atendida.** US02/US04/US05 mantêm critérios/tasks locais atendidos com regressão atual. Não há gate manual obrigatório, nem atribuição dos testes a Eliana; demos opcionais. Limitação histórica do timestamp intermediário de um no-op manual não é reconstruída e não exige repetição da regra já automatizada.

**DoD global do MVP ainda incompleta:** US01 permanece parcial por CA1/Compose e persistência por reinício do Compose; US07 precisa completar/verificar pipeline do fluxo completo, isolamento/caminho de falha e execução remota conforme autorização; US09 precisa portfólio final, README PT/EN e ensaio completo de guias/roteiro. Medição informativa RNF03 e checkout limpo continuam trabalho de fechamento de qualidade/portfólio, não resultados presumidos da suíte funcional. Docker/Linux/CI não foram comprovados pelo ambiente nativo Windows. US08 adiada por D08, não bloqueia MVP exclusivamente simulado. Não iniciar outras histórias automaticamente nesta entrega.

Sem chamadas pagas, SDK de IA externo, publicação ou deploy. Uso somente loopback/AI_MODE=simulated. Evidências e demonstração opcional em [15-validacao-us06.md](15-validacao-us06.md).


## 08/11/2026 — US05 implementada e validada tecnicamente; demo preservado

### Autorização e rastreabilidade

Após executar M02/no-op por automação e verificar os critérios independentes de US04 (registro imediatamente abaixo), iniciada US05 na branch local `feat/us05-triage-recovery`, a partir do commit local `1d48ec4` da validação US04. Sem iniciar US06, sem publicar ou fazer deploy. Demonstrações manuais agora são opcionais; nenhum teste técnico foi atribuído a homologação manual de Eliana. Alterações anteriores e arquivo workspace preservados.

| Critério/task | Implementação e teste | Resultado executado |
|---|---|---|
| US05-CA1/T1/T2 | application/triage.py aceita retry em falha; test_us05_ca1_retry_preserves_content_and_failed_attempt | Timeout 504/ai_timeout, indisponibilidade 503/ai_unavailable e saída inválida 502/invalid_ai_response seguidos de retry com provedor simulado válido: mesmo chamado, conteúdo/revisão/criação preservados, versões 1→3→5, primeira tentativa imutável, sem eventos de conteúdo extras |
| US05-CA2/T2 | Lock de linha e índice parcial existentes; test_us05_ca2_two_simultaneous_retry_posts_run_one_agent | Dois POSTs simultâneos de retry com mesma versão: um 200, outro 409; só um agente executado e uma tentativa adicional. Barreira/Event determinísticos; PostgreSQL real |
| US05-CA3/T1/T2 | Recuperação de tentativa ativa vencida + finalização condicional; testes de fronteira/atraso | 19,999 s aceita resultado, 20/20,001 s rejeitam como ai_timeout; lease válido bloqueia com triage_in_progress sem escrita; resultado antigo após recuperação recebe 409/version_conflict e não altera vencedor/histórico |
| US05-CA3/T2 HTTP real | tests/e2e/test_recovery.py e factory exclusiva tests/interrupted_server.py | Servidor Uvicorn encerrou realmente com código 17 após confirmar aquisição; novo servidor no mesmo banco de teste leu em_analise/version=2, bloqueou retry dentro do prazo, aguardou lease real de 20 s e recuperou com tentativa 2/sucesso/version=5. Sem alterar deadline no banco |
| US05-CA4/T2 | test_us05_ca4_real_constraint_failure_rolls_back_finalization_then_recovers | CHECK real inválido durante finalização: 503/storage_unavailable, sem falso contexto de falha persistida; tentativa continuou ativa/version=2 sem sugestão. Após prazo, nova solicitação recuperou e concluiu; conteúdo preservado |
| US05-T1/T2 atomicidade | test_us05_recovery_and_new_attempt_are_atomic | CHECK real inválido ao inserir próxima tentativa reverte também encerramento da anterior e versões; após retirar somente a injeção de teste, nova solicitação conclui normalmente |
| Regressão US01–US04/T2 | Suíte completa existente + novos casos US05, sem duplicar M02/no-op | Cadastro/consulta/edição/limites/snapshots/migração/agente anteriores preservados; M02/no-op tiveram apenas asserções faltantes adicionadas aos testes existentes |
| US05-T3 | ADR09, contrato, README, backlog, guia e docs/14-validacao-us05.md | Códigos, retry explícito, prazo, versões, resultados e lacunas documentados; sem exigência de repetição manual |

Recuperação + nova aquisição são uma única transação sob lock; flush libera índice ativo antes de inserir a seguinte. Recuperação de em_analise→falha incrementa version uma vez, aquisição outra e finalização outra (exemplo 2→5). Retry de falha normal soma duas (3→5). Versão antiga falha antes de qualquer recuperação. Tentativas concluídas não são sobrescritas; eventos de conteúdo não são criados por retry. Sem nova migração: esquema continua 0003. Sem dependências adicionadas/atualizadas, mesmos locks/fontes oficiais; aplicação 0.4.0.

### Execuções reais

Comandos na raiz:

```powershell
.\.venv\Scripts\python.exe -m ruff check .
.\.venv\Scripts\python.exe -m ruff format --check .
.\.venv\Scripts\python.exe -m pip check
$env:TEST_DATABASE_URL='postgresql+psycopg://portfolio_test:senha_ficticia_teste@127.0.0.1:55432/portfolio_test'
.\.venv\Scripts\python.exe -m pytest tests/api/test_recovery.py -q --junitxml=reports/us05-api-focused.xml
.\.venv\Scripts\python.exe -m pytest tests/integration/test_recovery.py tests/e2e/test_recovery.py -q --junitxml=reports/us05-recovery-focused.xml
.\.venv\Scripts\python.exe -m pytest -q --junitxml=reports/us05-all.xml
```

**Foco API: 8 passed, 1 warning, 23,34 s. Foco integração/HTTP real: 3 passed, 1 warning, 30,62 s. Regressão completa final: 135 passed, 1 warning, 224,88 s; nenhuma falha, erro ou skip.** Relatório XML conferido: 73 unitários, 47 API dentro do processo com PostgreSQL real, 13 integração (12 com PostgreSQL ativo e um de conexão recusada com driver real), 2 HTTP/TCP com Uvicorn e PostgreSQL real. Cada caso com banco ativo criou/descartou somente seu portfolio_test_<uuid>. Não usou SQLite ou demo. Relatórios em reports/ ignorados pelo Git.

Ruff check/format e pip check aprovados. Falhas iniciais de lint por linhas longas/formatação foram corrigidas; nenhuma execução pytest desta etapa falhou. Aviso conhecido Starlette/TestClient sobre HTTPX continua registrado, sem pacote extra para escondê-lo. O teste HTTP de interrupção usa binário nativo CPython e PYTHONPATH dos mesmos pacotes da .venv para controlar o processo criado no Windows; não prova execução Linux/Docker/CI. Testes de fronteira e resposta tardia usam relógio controlado no serviço; o ensaio HTTP usa prazo real. Factory os._exit fica exclusivamente em tests/, não há opção de encerramento do servidor na API de produção. Nenhuma chamada de IA real, custo ou avaliação semântica de modelo externo.

### Preservação e ambiente local

Comparação SQL **somente leitura** antes/depois de todas as execuções e novamente após recarregar a API: todos os campos de tickets/ticket_events/triage_attempts **integralmente iguais**. Snapshots locais ignorados `.local/demo-us05-before.json` e `.local/demo-us05-after.json`: **1 chamado, 3 eventos, 1 tentativa**. Chamado ad903cac-a750-48d3-b205-91da97d7adee mantém version=5/content_revision=3, pendente/suggestion=null. Nenhum POST/PATCH, criação de chamado, alteração de prazo ou migração no demo nesta etapa; fixture inválida criada somente nos bancos de teste.

Somente a API do projeto foi recarregada: comandos/executável absoluto da .venv/parentesco reconferidos para launcher 17332 e servidor 3504 antes de encerrá-los. Novo launcher PID **3524** (reconferir identidade antes de encerrar); logs `.local/api-us05.*`. Mesmo DATABASE_URL demo, AI_MODE=simulated e bind 127.0.0.1:8000; não alterados .env/serviço global/configuração do PostgreSQL. /health, /docs, /openapi.json, GET do chamado e GET de tentativas retornaram 200; OpenAPI confirmou 0.4.0, chamado 5/3 e histórico total=1. API/banco deixados ativos, sem garantia de sobreviver a encerramento da sessão do sistema.

### Lacunas e próximo escopo

**US05-CA1–CA4 verificados localmente por automação; implementação e documentação entregues.** Nenhum aceite manual obrigatório criado. US04 sem lacuna independente de M02/no-op: validados tecnicamente, demos opcionais. US03 mantém lacunas de validação integrada com classificação final humana/resolvido pelas futuras rotas de US06; lógica já possui fixtures, e o timestamp histórico de um no-op manual específico não pode ser reconstruído depois de outra edição. Não exigir repetição manual para suprir evidência histórica ou regras já automatizadas. Não iniciar US06 sem nova instrução de continuidade.

**Docker Compose e CI no GitHub continuam pendentes; US01 parcialmente validada.** US07 não concluída, US08 adiada; sem modelo real/tokenizer real e sem garantia de preempção de provedor Python arbitrariamente bloqueante (simulador atual é imediato e sem I/O, interface exige respeito ao prazo). US06/revisão/resolução não implementadas. Nada publicado ou implantado; exclusivamente loopback e AI_MODE=simulated. Evidências e demonstração opcional em [14-validacao-us05.md](14-validacao-us05.md).


## 08/11/2026 — M02/no-op validados por automação; continuidade US05 autorizada

Eliana alterou explicitamente a estratégia de aceite: participação em decisões de produto e demonstrações curtas opcionais; não exigir repetição manual de verificações automatizadas. Autorizou iniciar US05 se critérios independentes atendidos. Não atribuir testes do agente a homologação manual da usuária. US06 continua fora desta implementação; Docker Compose/CI permanecem pendentes.

Revisados e **reaproveitados** os testes existentes `test_us04_public_simulation_failure_marker`, `test_us04_ca1_real_suggestion_noop_edit_and_immutable_history` e `test_us03_ca1_archive_classification_and_preserve_history`. Acrescentadas somente asserções faltantes ao teste do marcador (502/código, conteúdo, estado, versão/revisão 3/1, ausência de classificação inválida, tentativa falha e só evento criado) e ao no-op (200, GET integral idêntico incluindo timestamps/sugestão/versões, contagem de eventos imediatamente após no-op=1 e tentativa intacta), sem duplicar cenários.

Comando executado com TEST_DATABASE_URL do cluster local portfolio_test: `.\.venv\Scripts\python.exe -m pytest tests/api/test_triage.py::test_us04_public_simulation_failure_marker tests/api/test_triage.py::test_us04_ca1_real_suggestion_noop_edit_and_immutable_history tests/integration/test_editing.py::test_us03_ca1_archive_classification_and_preserve_history -q --junitxml=reports/us04-m02-noop-technical.xml`. **3 passed, 1 warning, 9,30 s; sem skips/falhas.** Cada caso usou banco exclusivo descartável, nenhum POST/PATCH no demo. Snapshot somente leitura do demo salvo em `.local/demo-us05-before.json`: 1 chamado, 3 eventos e 1 tentativa. Comparar novamente ao fim de US05.

M02 e timestamps do no-op estão **validados tecnicamente por automação**, sem homologação manual presumida e sem nova tarefa para Eliana no Swagger. Isso não reconstrói o timestamp histórico intermediário de seu no-op já seguido de edição; limitações históricas mantidas sem bloquear critério funcional automatizado. US04-CA1–CA4 independentes verificados (regressão prévia 124 testes e foco atual); pode avançar a US05. US03 mantém lacunas de fluxo com classificação final/resolvido dependentes de US06; fixtures existentes cobrem as regras, futura validação integrada automatizada deve usar as rotas de US06 quando existirem. Não iniciar US06 nesta autorização.


## 08/11/2026 — M01a–M01c informados; edição e histórico conferidos

Homologação manual informada por Eliana, registrada sem duplicação: M01a POST triage expected_version=2 retornou 200 e GET confirmou simulated/defeito/media, sugerida, version=4/content_revision=2. M01b PATCH com título idêntico e espaços retornou 200 preservando sugestão e versões 4/2. M01c PATCH de descrição expected_version=4 retornou 200, version=5/content_revision=3, pendente, suggestion/final_classification=null. O agente não observou visualmente nem reexecutou essas ações.

Verificação técnica somente leitura via HTTPX: GET do chamado e de triage-attempts retornaram 200. Descrição persistida: “No ambiente fictício, o erro ao salvar o cadastro afeta todos os usuários e começou nesta manhã.” Texto obtido pelo agente, não atribuído ao relato integral de Eliana. PostgreSQL via psycopg, `SET TRANSACTION READ ONLY; SHOW transaction_read_only` (on), SELECT de tickets/triage_attempts/ticket_events, confirmação transacional sem escrita: **saída 0**. Chamado ad903cac-a750-48d3-b205-91da97d7adee version=5/revisão=3, aberto/pendente, classificações atuais nulas. Uma tentativa, b7b11f7f-1565-4ac4-b39a-6bf77a3669cf, sucesso/simulated, revisão 2, defeito/media, 3 chamadas de modelo/2 ferramentas, sugestão preservada.

**Exatamente três eventos:** criado/revisão 1, editado/revisão 2, editado/revisão 3. Os dois primeiros foram comparados integralmente com `.local/demo-us04-preservation.json` e estão idênticos, incluindo timestamps e snapshot antigo. O novo snapshot tem content_revision=2, final_classification=null e suggestion **integralmente igual** à tentativa anterior. Não há evento adicional para o no-op no estado observado. Nenhum dado alterado ou processo reconfigurado pelo agente; nenhuma nova suíte de aplicação executada.

Timestamps conferidos (UTC): created_at do chamado 2026-11-07T21:23:24.789820Z; updated_at atual 2026-11-08T15:35:04.358424Z; novo evento 2026-11-08T15:35:04.357654Z. Finalização da tentativa 2026-11-08T15:31:17.781295Z, valor que a implementação usa para updated_at da finalização. **Não há captura persistida de resposta imediatamente antes/depois do no-op**: após a edição seguinte, o timestamp intermediário não pode ser comprovado retrospectivamente pelo estado atual. Eliana não informou esse campo no relato do no-op; não registrá-lo como homologado nem inferir igualdade a partir de finished_at. A preservação de timestamp no no-op tem evidência automatizada anterior; não repetir o cenário para criar evidência histórica artificial.

Próximo: M02 saída simulada inválida. **Somente orientar criação de chamado fictício separado**, título exato `[SIMULADO:saida-invalida]`, conforme roteiro; preservar chamado existente. AI_MODE continua simulated: seleção por título é local à requisição, não muda configuração global/arquivo/serviço e não requer restauração posterior. Chamados com títulos comuns continuam no roteiro normal; manter o registro de falha como evidência, sem apagar/renomear. Aguardar ID/resultado da criação; consultar GET para obter versão antes de orientar POST de triagem do novo chamado. M02 não executado pelo agente nem homologado.

US03: no-op com sugestão e invalidação/preservação de sugestão agora informados manualmente e conferidos tecnicamente no alcance descrito; classificação final/resolvido continuam dependentes de US06. Não encerrar a história nem presumir os demais campos/snapshots não homologados. US04 mantém M02 pendente; US05 não iniciada. Docker Compose e CI no GitHub pendentes, US01 parcialmente validada. Sem chamadas pagas, publicação ou deploy.


## 08/11/2026 — Início guiado de US04: somente geração de sugestão

A pedido de Eliana, conduzir um cenário por vez e aguardar seu relato antes do seguinte. Verificação técnica do agente, somente leitura via HTTPX/TCP: GET `/api/v1/tickets/ad903cac-a750-48d3-b205-91da97d7adee` retornou 200, version=2/content_revision=2, aberto/pendente, suggestion/final_classification=null. GET `/openapi.json` retornou 200, API 0.3.0 e POST triage disponível. Nenhum POST/PATCH executado, nenhum dado alterado e nenhuma nova suíte executada.

Orientação atual: POST `/api/v1/tickets/ad903cac-a750-48d3-b205-91da97d7adee/triage`, corpo completo `{"expected_version":2}`. Esperado 200, ticket aberto/sugerida, version=4/content_revision=2, sugestão simulated/defeito/media, ausentes impacto e inicio_ocorrencia para o texto atual, classificação final nula; tentativa sucesso, 3 chamadas de modelo e 2 ferramentas. **Geração ainda aguarda execução/relato de Eliana; não homologada.** Próximos passos separados: no-op com sugestão, edição que invalida e preserva histórico, saída simulada inválida. Consultar a versão novamente antes de orientar cada operação com expected_version. Não repetir limites/campos já conferidos.

US03 mantém pendências específicas; classificação final/resolução dependem de US06. US04 aguarda homologação; US05 não iniciada. Docker Compose e CI remota pendentes; US01 parcialmente validada. Somente modo simulado, sem custos, publicação ou deploy.


## 08/11/2026 — US04 simulada implementada; aguardando homologação de Eliana

### Autorização e escopo

Eliana aceitou E01–E04 de US03 e autorizou US04 exclusivamente simulada. Aceite registrado sem repetir cenários. US03 permanece aberta com pendências específicas de sugestão/classificação/snapshots; sugestão passa a estar disponível pelo Swagger nesta entrega, classificação final/resolução continuam dependentes de US06. US05/US06 não iniciadas, US08 adiada. Docker Compose e CI remota continuam pendentes; US01 parcialmente validada. Não houve chamada paga, SDK de IA, publicação ou deploy.

Git inspecionado: branch anterior feat/us03-ticket-edit, com alterações documentais e arquivo workspace preexistentes preservados. Criada branch local feat/us04-simulated-triage (primeira tentativa bloqueada pela restrição de escrita em .git, repetida com permissão ampliada). Não houve rebase, reset ou sobrescrita do histórico. Arquivo projeto-agente-ia.code-workspace mantido fora da entrega. Nenhuma dependência adicionada/atualizada; locks e fontes oficiais anteriores mantidos. Aplicação 0.3.0.

### Rastreabilidade e comportamento entregue

| Critérios/tasks | Código | Evidências |
|---|---|---|
| US04-CA1/T1/T2 | agent/protocol.py, simulated.py, tools.py, orchestrator.py; application/triage.py; rotas/schemas | Ferramentas locais consultadas, sugestão validada e modo simulated; tentativa confirmada antes do provedor, conexão liberada, sucesso sem classificação final |
| US04-CA2/T2 | AgentOutput, allowlist e erros sanitizados; modelos/migração 0003 | Enums, extras, justificativa curta, ferramenta desconhecida/argumentos inválidos/consulta ausente rejeitados; nenhuma sugestão inválida publicada, conteúdo preservado e tentativa falha consultável |
| US04-CA3/T2 | Laço e orçamento externos ao provedor; validação de ausentes | Exatos 3 modelos/4 ferramentas/2.000 tokens aceitos, chamada adicional rejeitada; ausentes 0/4 aceitos, 5/duplicatas rejeitados; relógio controlado inclui tempo de ferramenta/modelo |
| US04-CA4/T2 | Dados JSON separados do sistema; fixtures simuladas | Sem impacto informado, inclusive dúvida: média provisória e impacto ausente; prompt injection não habilita shell ou categoria externa; AV01–AV08 com roteiros, sem avaliação de modelo real |
| Base transacional US04/T2 | models.TriageAttempt, application/triage.py, migração 0003 | Uma tentativa ativa/numeração única, finalização condicional, duas conexões concorrentes com só um agente; migração preserva conteúdo/eventos/snapshots e roundtrip só em banco descartável |
| Regressão US01–US03/T2 | Suítes anteriores + tests/api/test_triage.py e tests/e2e/test_http.py | Cadastro, consulta, edição, conflitos, no-op com sugestão real do simulador, invalidação/snapshot e histórico de tentativas; teste TCP/Uvicorn inclui sucesso e falha relevante |
| US04-T3 | README, arquitetura ADR08, contrato, backlog, ambiente/guia e docs/13-homologacao-us04.md | Homologação curta preparada; nenhum resultado manual de US04 presumido |

Entidade normalizada TriageAttempt adicionada por migração somente aditiva. FK ticket_id e índice único parcial identificam a tentativa ativa sem referência circular nova em Ticket; sugestão guarda attempt_id gerado internamente. Finalização confere tentativa/status, revisão e versão capturada sob lock. Edição mantém tentativa imutável e snapshot anterior no evento. Rationale simulado usa descrições/ política retornadas pelas ferramentas; regras de fixture não são inferência de modelo real. Detalhes e limites em ADR08.

### Testes realmente executados

Comandos na raiz com Python da .venv, PostgreSQL 16 local e bancos exclusivos portfolio_test_<uuid>, sem limpar o demo:

```powershell
.\.venv\Scripts\python.exe -m ruff check .
.\.venv\Scripts\python.exe -m ruff format --check .
.\.venv\Scripts\python.exe -m pip check
$env:TEST_DATABASE_URL='postgresql+psycopg://portfolio_test:senha_ficticia_teste@127.0.0.1:55432/portfolio_test'
.\.venv\Scripts\python.exe -m pytest -q --junitxml=reports/us04-complete-final.xml
```

**Resultado final: 124 passed, 1 warning, 181,43 s; zero falhas, erros ou skips.** São 73 unitários, 39 API dentro do processo com PostgreSQL real, 11 de integração (10 com PostgreSQL ativo e um de conexão recusada por driver real) e 1 HTTP/TCP com Uvicorn e PostgreSQL real. A execução final cobre o código entregue, incluindo as justificativas e a regra de impacto refinadas. Não há SQLite, chamada de IA externa ou teste no banco demo.

Evidências intermediárias: unitários iniciais 73 passed/1 warning; API/migração focados 15 passed/1 warning. Primeira suíte completa: 122 passed/2 failed, 174,36 s; corrigidos teste antigo que enumerava só as rotas US01–US03 e fixture SQL de migração cujo JSON literal era interpretado como bind parameters. Segunda suíte completa: 124 passed/1 warning, 199,19 s. Verificação do limite de modelo refinada para isolar quarta chamada sem exceder ferramentas: 36 testes de agente aprovados. Após separar validação de domínio da serialização API, foco agente/API/integração/HTTP: 53 passed/1 warning, 69,57 s. Ajuste final de justificativa a partir das respostas das ferramentas e regra de dúvida sem impacto motivou a suíte final acima. Falhas intermediárias de Ruff (formatação/linhas longas) corrigidas; Ruff e pip check aprovados ao final. Aviso conhecido Starlette/TestClient sobre HTTPX permanece, sem pacote adicional para ocultá-lo. Relatórios locais em reports/, ignorados pelo Git.

### Demo e Swagger preparados

Executado snapshot somente leitura de todos os campos de tickets/ticket_events, `alembic upgrade head` no demo e novo snapshot: **preservação integral True, 1 chamado, 2 eventos, 0 tentativas**, migração 0003. Evidência operacional local `.local/demo-us04-preservation.json`, ignorada pelo Git. Nenhum POST/PATCH executado no demo pelo agente. Downgrade somente em testes descartáveis.

Primeira tentativa de reinício da API foi interrompida antes de encerrar processos porque Get-NetTCPConnection não encontrou listener, embora HTTP respondesse; Get-CimInstance/netstat na sandbox também tinham limitações de acesso/visibilidade. Identificação por comando Uvicorn, executável absoluto da .venv deste projeto e parentesco confirmou launcher 18120/servidor 18256; só esses processos foram encerrados. API iniciada em modo hidden/loopback com AI_MODE=simulated e DATABASE_URL do demo. Verificação: /health, /docs, /openapi.json e GET do chamado retornaram 200; API 0.3.0, rota triage presente, chamado ad903cac-a750-48d3-b205-91da97d7adee version/content_revision=2, aberto/pendente, suggestion=null; GET triage-attempts retornou 200/total=0. Após os últimos ajustes, API recarregada novamente identificando launcher 20720 e seu único filho pelo comando/parentesco. Launcher final PID **17332**, logs `.local/api-us04-final.*`, fora do Git. Nova conferência HTTP de health/docs/OpenAPI/chamado/tentativas retornou 200 e SQL somente leitura confirmou novamente igualdade integral com o snapshot anterior e dois eventos. API e banco deixados ativos; PIDs devem ser reconferidos antes de qualquer encerramento.

### Homologação e limites preservados

**US04 implementada e verificada automaticamente, aguardando homologação de Eliana; não encerrada.** Roteiro curto em [13-homologacao-us04.md](13-homologacao-us04.md): M01 sugestão → no-op classificado → edição invalida sugestão e mantém tentativa; M02 saída inválida → falha sanitizada, chamado preservado. Ambos aguardam relato. Não repetir E01–E04 de US03. Pendências de US03 com sugestão tornam-se verificáveis agora, sem marcá-las aprovadas antes do relato; classificação final/resolvido dependem de US06. Snapshot após múltiplas edições segue com evidência automatizada e pendência manual registrada.

Retry em falha, recuperação por prazo e ensaios completos de interrupção/finalização ficam em US05. Nesta entrega triage exige aberto/pendente; falha pode retornar a pendente por edição efetiva, sem oferecer retry direto ainda. Prazo verificado nas fronteiras das chamadas e na finalização; simulador imediato/sem I/O. Preempção de provedor Python arbitrariamente bloqueante não está implementada; a interface exige respeito ao orçamento para futuros adaptadores. Tokens do simulador são metadados roteirizados, não medição real de tokenizer. Nenhuma qualidade de IA externa alegada. Docker Compose e CI no GitHub permanecem não executados; não declarar cobertura Docker/Linux/CI por testes nativos. Somente AI_MODE=simulated e uso em loopback.


## 08/11/2026 — E04d informado; roteiro E01–E04 coberto no alcance dos relatos

E04d/US03-CA2/CA3 registrado sem duplicação como **homologação manual informada por Eliana**: PATCH expected_version=2/description="curta" retornou HTTP 422, validation_error, body.description/string_too_short. GET posterior HTTP 200 manteve título, descrição, version=2, content_revision=2 e timestamps anteriores. Sem observação visual ou reexecução do PATCH pelo agente.

Conferência técnica: `psql -X -v ON_ERROR_STOP=1 -h 127.0.0.1 -p 55432 -U portfolio_test -d portfolio_chamados_demo -c <SQL>`, com `BEGIN READ ONLY; SHOW transaction_read_only; SELECT` de chamado/contagem/eventos e `COMMIT`: **saída 0**, modo somente leitura on, **exatamente dois eventos**, criado/revisão 1 e editado/revisão 2; nenhum evento adicional após E04d. Chamado ad903cac-a750-48d3-b205-91da97d7adee com version/content_revision=2, created_at=2026-11-07T21:23:24.789820Z, updated_at=2026-11-08T13:01:30.959837Z; snapshot anterior mantém revisão 1 e classificações nulas. Nenhuma escrita de dados ou mudança operacional.

E01–E03 e os quatro exemplos E04a–E04d estão registrados no alcance dos relatos, com histórico básico conferido tecnicamente. Não solicitar repetição desses exemplos nem confundir E04 com homologação de todos os limites/tipos. A matriz atual de cenários restantes está em [homologação US03](12-homologacao-us03.md): testes automatizados já executados na entrega de 07/11/2026 cobrem os demais limites, entradas inválidas, UUID ausente no PATCH, estados bloqueados, concorrência, rollback, migração e classificação com fixtures. Revisão dos arquivos de teste nesta etapa; **suíte não reexecutada**. Evidência histórica: 72 passed/1 warning, registrada abaixo; não atribuir esse resultado a nova execução.

**US03 não encerrada e US04 não iniciada.** Homologação manual pendente de classificação não nula e seus snapshots preservada; produção pelo Swagger depende de US04 (sugestão) e US06 (classificação final). Estados em_analise/resolvido dependem dos respectivos fluxos futuros para eventual homologação manual, mas já têm testes com fixtures. Não semear o demo nem antecipar histórias. Não há próximo exemplo E05 definido no roteiro atual. Não criar exigência de repetir manualmente toda a suíte: revisão/aceite de Eliana deve considerar a matriz de evidências e as pendências sem convertê-las em aprovação automática. Docker Compose e CI no GitHub pendentes, US01 parcialmente validada; US08 adiada, AI_MODE=simulated, sem chamadas pagas, publicação ou deploy.


## 08/11/2026 — E04c informado; histórico reconfirmado somente em leitura

E04c/US03-CA2/CA3: **homologação manual informada por Eliana**, sem duplicação. PATCH expected_version=2 e title="abcd": HTTP 422, validation_error, campo body.title, motivo string_too_short. GET posterior HTTP 200 preservou título, descrição, version=2, content_revision=2 e timestamps anteriores. O agente não observou visualmente nem reexecutou o PATCH.

Conferência técnica executada com `psql -X -v ON_ERROR_STOP=1 -h 127.0.0.1 -p 55432 -U portfolio_test -d portfolio_chamados_demo -c <SQL>`: `BEGIN READ ONLY; SHOW transaction_read_only; SELECT` de versões/timestamps, contagem e eventos do chamado `ad903cac-a750-48d3-b205-91da97d7adee`; `COMMIT`. **Saída 0, transaction_read_only=on; exatamente dois eventos**, criado/revisão 1 e editado/revisão 2, sem evento adicional após E04c. Version/content_revision=2; created_at=2026-11-07T21:23:24.789820Z e updated_at=2026-11-08T13:01:30.959837Z. Nenhuma escrita de dados ou alteração de processo; nenhuma nova execução de testes de aplicação.

**Próximo cenário vigente: E04d — descrição abaixo de 20 caracteres.** No mesmo chamado, PATCH `{"expected_version":2,"description":"curta"}` (usar versão atual se houver mudança posterior). Esperado HTTP 422/validation_error; GET posterior HTTP 200 preservando título, descrição, versões e timestamps. **E04d não executado; aguardar relato de Eliana.** Não repetir E01–E03/E04a–E04c. E04 completo e US03 continuam abertos.

Pendências preservadas: sugestão existente depende de US04 e classificação final de US06 para homologação via Swagger; fixtures automatizadas não equivalem a homologação manual de classificação não nula. Docker Compose e CI no GitHub pendentes, US01 parcialmente validada. Sem início de US04/US06, US08 adiada; AI_MODE=simulated, sem chamadas pagas, publicação ou deploy.


## 08/11/2026 — E04b informado; histórico conferido somente em leitura

E04b/US03-CA2/CA3 registrado uma única vez como **homologação manual informada por Eliana**: PATCH com expected_version=2 e title=null retornou HTTP 422/validation_error; GET posterior HTTP 200 preservou título, descrição, version=2, content_revision=2 e timestamps anteriores. Sem observação visual nem reexecução do PATCH pelo agente.

Conferência técnica executada com `psql -X -v ON_ERROR_STOP=1 -h 127.0.0.1 -p 55432 -U portfolio_test -d portfolio_chamados_demo -c <SQL>`: `BEGIN READ ONLY; SHOW transaction_read_only; SELECT` de chamado, contagem e eventos, seguido de `COMMIT`. **Saída 0**, transaction_read_only=on. Chamado `ad903cac-a750-48d3-b205-91da97d7adee`: version=2/content_revision=2, created_at=2026-11-07T21:23:24.789820Z, updated_at=2026-11-08T13:01:30.959837Z. **Exatamente dois eventos**, criado/revisão 1 e editado/revisão 2; nenhum evento adicional após E04b. Snapshot anterior da edição mantém revisão 1 e classificações nulas. Nenhuma escrita de dados ou alteração de processo; nenhuma nova execução de testes de aplicação alegada.

**Próximo cenário vigente: E04c — título abaixo de 5 caracteres**, conforme roteiro: no mesmo chamado, PATCH `{"expected_version":2,"title":"abcd"}`. Esperado HTTP 422/validation_error; GET posterior HTTP 200 com título, descrição, versões e timestamps preservados. Usar versão atual caso outro GET indique mudança. **E04c não executado; aguardar relato de Eliana antes de E04d.** Não repetir E01–E03/E04a/E04b. E04 completo e US03 permanecem abertos.

Pendências preservadas: classificação existente não nula depende de US04 (sugestão) e US06 (classificação final) para produção pelo Swagger; evidência automatizada com fixtures não equivale à homologação manual. Docker Compose e CI no GitHub pendentes; US01 parcialmente validada. US04/US06 não iniciadas, US08 adiada; somente AI_MODE=simulated, sem chamadas pagas, publicação ou deploy.


## 08/11/2026 — Ambiente restabelecido; histórico de E04a reconfirmado

Por solicitação de Eliana, consultado o guia de execução e confirmado `.local/pgdata/PG_VERSION=16`. `pg_ctl status` informou servidor parado. Iniciado **o cluster existente**, com `pg_ctl -D <projeto>/.local/pgdata -l <projeto>/.local/postgres.log -o "-h 127.0.0.1 -p 55432" -w start`, sem initdb, createdb, limpeza ou migração. Primeira tentativa na sandbox falhou com erro 87 de criação de token; execução com permissão ampliada iniciou com sucesso. Aviso de possível servidor existente foi emitido pelo pg_ctl; nenhum PID/arquivo foi removido manualmente.

Consulta real por `psql -X -v ON_ERROR_STOP=1` ao banco demo, com `BEGIN READ ONLY; SHOW transaction_read_only; SELECT ...; COMMIT`, executada com sucesso: modo somente leitura `on`, banco `portfolio_chamados_demo`, endereço 127.0.0.1, porta 55432, migração 0002. Chamado `ad903cac-a750-48d3-b205-91da97d7adee`: **version=2, content_revision=2**. Histórico reconfirmado após E04a: **exatamente dois eventos**, criado/revisão 1 e editado/revisão 2, sem evento adicional pela rejeição. Snapshot da edição permanece com content_revision=1, suggestion=null e final_classification=null. Essa consulta resolve a pendência de conferência antes impedida por conexão recusada; não é reexecução do PATCH nem homologação visual pelo agente.

API iniciada em segundo plano com Start-Process/WindowStyle Hidden, Python da .venv, Uvicorn factory, bind 127.0.0.1:8000, DATABASE_URL do demo e AI_MODE=simulated. Launcher PID 18120 (reconferir identidade antes de encerrar); logs `.local/api-restored.stdout.log` e `.local/api-restored.stderr.log`. GET /health, /docs e /openapi.json retornaram **200**; versão 0.2.0 e PATCH presente. **GET /api/v1/tickets/ad903cac-a750-48d3-b205-91da97d7adee retornou 200 com o registro persistido**, comprovando consulta pela API além do health: aberto/pendente, versões 2, suggestion/final_classification nulos, created_at=2026-11-07T21:23:24.789820Z e updated_at=2026-11-08T13:01:30.959837Z. Nenhuma escrita de chamado/evento. Inspeção complementar com Get-NetTCPConnection teve acesso negado; isso não invalida os retornos HTTP nem a conexão SQL confirmados. API e banco deixados ativos, sem garantia de sobrevivência ao encerramento da sessão do sistema.

**Próximo cenário: E04b — título nulo**, usando expected_version=2 consultada. Orientar pelo Swagger e aguardar resultado de Eliana; **não executado e não homologado nesta etapa**. E01–E03 e E04a não foram repetidos. US03 continua aberta. Homologação com sugestão existente depende de US04; classificação final depende de US06; fixtures automatizadas não equivalem a homologação manual. Docker Compose e CI no GitHub continuam pendentes, US01 parcialmente validada. Sem início de US04/US06, chamadas pagas, publicação ou deploy. Verificação operacional SQL/HTTP executada; sem nova execução da suíte de testes de aplicação.


## 08/11/2026 — E04a informado; nova consulta do histórico sem conexão

Registrada em [homologação US03](12-homologacao-us03.md) a **homologação manual informada por Eliana**: PATCH somente com expected_version=2 retornou 422/validation_error; GET posterior 200 com título, descrição, version=2, content_revision=2 e timestamps anteriores preservados. E04a confirmado no alcance do relato, sem reexecução pelo agente; E04 completo e US03 continuam abertos.

Conferência somente leitura tentada com `psql -X -v ON_ERROR_STOP=1 -h 127.0.0.1 -p 55432 -U portfolio_test -d portfolio_chamados_demo -c <SQL>`: transação preparada com `BEGIN READ ONLY`, `SHOW transaction_read_only`, SELECT de chamado/contagem/eventos e COMMIT. Resultado: **conexão recusada, saída 1; SQL não executado**. Nenhum dado ou processo alterado. Os dois eventos foram confirmados na consulta anterior a E04a, mas **não reconfirmados após a rejeição atual**. Pendente repetir consulta quando PostgreSQL estiver disponível; não inferir histórico apenas do GET.

Próximo cenário vigente: **E04b, title=null**, com versão atual conferida por GET; esperado 422/validation_error e GET posterior integralmente inalterado. Aguardar retorno antes de E04c, sem repetir cenários homologados. Dependências de US04 (sugestão) e US06 (classificação final) para homologação de classificação não nula via Swagger preservadas; sem semear dados ou antecipar histórias. Docker Compose e CI no GitHub pendentes; US01 parcialmente validada. US04 não iniciada. Nenhum teste de aplicação novo executado ou alegado; somente tentativa de consulta operacional e atualização documental. Sem chamadas pagas, publicação ou deploy; AI_MODE=simulated.


Nova tentativa nesta continuidade de 08/11/2026: mesmo relato de E04a reconhecido, sem duplicar homologação. Consulta `psql -X -v ON_ERROR_STOP=1` ao mesmo banco/porta, com `BEGIN READ ONLY`, verificação do modo, SELECT de versões, contagem e eventos e COMMIT: conexão novamente recusada, código de saída do psql=2. Nenhum SQL executado, nenhum processo iniciado e nenhum dado alterado. O código 1 da tentativa anterior correspondeu ao comando PowerShell que lançou erro após a falha do psql. Histórico após E04a continua pendente de reconferência; não afirmar dois eventos atuais. Próximo cenário continua E04b (title=null); não avançar sem seu relato. US04/US06, Compose e CI mantêm as dependências e pendências acima.

## 08/11/2026 — E03 informado e histórico conferido no PostgreSQL

Eliana informou E03/US03-CA3: HTTP 200, título normalizado, version/content_revision mantidos em 2 e timestamps iguais ao GET anterior. Registrado como homologação manual informada em [homologação US03](12-homologacao-us03.md).

Conferência técnica do agente: `psql` em 127.0.0.1:55432/portfolio_chamados_demo, transação `BEGIN READ ONLY`, SELECT de versões e de eventos/contagens, COMMIT; execução com sucesso. Único chamado ad903cac-a750-48d3-b205-91da97d7adee na versão/revisão 2. Exatamente **dois eventos**: criado/revisão 1 e editado/revisão 2, um de cada, sem evento extra para o no-op. Snapshot de edição preserva revisão anterior 1, suggestion=null e final_classification=null. Não houve escrita nem nova execução de PATCH pelo agente. Essa consulta não comprova preservação de classificação não nula; dependência de US04/US06 para geração via Swagger continua registrada.

Próximo cenário guiado: **E04a — PATCH apenas com expected_version=2, sem title/description**; esperado 422/validation_error e GET inalterado. Aguardar retorno antes de outro subcaso. E04 não encerrado; homologação de US03 permanece aberta. Docker Compose e CI no GitHub pendentes; US01 não totalmente validada. Sem início de US04, publicação, deploy ou chamadas pagas. Apenas consulta operacional/documentação nesta etapa; nenhum teste de aplicação novo alegado.

## 08/11/2026 — Homologação manual parcial de US03 informada por Eliana

Eliana informou: PATCH com expected_version=1 retornou 200, descrição alterada e título preservado, version/content_revision 1→2; novo PATCH com versão 1 e outra descrição retornou 409/version_conflict; GET posterior retornou 200, versões=2 e descrição da primeira edição preservada, sem aplicar a rejeitada. Registro atualizado em [homologação US03](12-homologacao-us03.md), distinguindo relato humano de automação. ID, texto integral, timestamps e estado da classificação não foram informados, portanto não foram presumidos.

**US03 continua em homologação, não encerrada.** Próximo cenário: E03/no-op após trim, RN01/RN11 e US03-CA3; orientar somente esse cenário e aguardar retorno antes de E04. Comparar resposta com GET anterior, inclusive timestamps e versões. Histórico básico pode ser conferido agora por SQL somente leitura, mas não há endpoint de eventos no Swagger. Invalidação/snapshot de classificação existente dependem, para geração pelo fluxo público local da API, de US04 (sugestão) e US06 (classificação final). Evidência automatizada com fixtures já existe, mas não é homologação manual; não semear dados diretamente no demo nem iniciar essas histórias para contornar o limite.

Docker Compose e execução do CI no GitHub continuam pendentes; US01 não totalmente validada. Nenhum código, dado de chamado ou estado operacional alterado nesta etapa; nenhuma nova execução de testes de aplicação declarada. Mudança documental para registrar resultados e conduzir o próximo cenário. US04 não iniciada, nenhuma publicação ou chamada paga.

## 07/11/2026 — Homologação informada de US02 e implementação de US03

### Retorno de Eliana e verificação complementar

Eliana informou execução manual no Swagger e conferência de: cadastro 201 com campos/location esperados; consulta 200; lista 200/total=1/limit=20/offset=0; página limit=1/offset=1 com items=[] e total=1; POST sem title 422/validation_error/body.title/missing; UUID inexistente 11111111-1111-4111-8111-111111111111 com 404/not_found. Resultados registrados como **homologação manual informada pela usuária**, não execução visual do agente, em [registro US01/US02](11-homologacao-us01-us02.md).

Não persistência de H04 foi verificada adicionalmente pelo agente antes de encerrar o cenário: SQL direto no PostgreSQL demo antes/depois de repetir POST sem title válido estruturalmente nos demais campos. HTTP 422; tickets **1→1**, ticket_events **1→1**; request_id 81295f21-37d8-4464-8cac-88371face1ee. Dados preservados. Isso reproduz o comportamento, não reconstrói a requisição histórica da usuária. Ausência de description não foi homologada manualmente; não atribuir esse caso ao relato.

Eliana autorizou iniciar US03 explicitamente. A fundação nativa estava verificada, mas Docker Compose permanece pendente e **US01 não está totalmente validada**. Execução do CI no GitHub continua pendente. Autorização não inclui US04, chamadas pagas, publicação ou deploy.

### Implementação de US03 e rastreabilidade

| Critério/task | Arquivos | Evidência executada |
|---|---|---|
| US03-CA1/T1 | routes.py, schemas.py, application/tickets.py, domain/editing.py | PATCH altera só campos fornecidos, incrementa versões, volta a pendente e registra evento na mesma transação |
| US03-CA1/T1 | models.py, domain/classification.py, migração 0002 | Projeções JSONB nullable e snapshot da classificação anterior no evento; não há rota para definir classificações |
| US03-CA1/T2 | tests/api/test_editing.py::test_us03_ca1_patch_content_and_history | HTTP 200, persistência confirmada por GET, versões/timestamps e eventos conferidos no PostgreSQL |
| US03-CA1/T2 | tests/integration/test_editing.py::test_us03_ca1_archive_classification_and_preserve_history | Fixture sintética classificada: no-op preserva, edição limpa dados atuais e arquiva snapshot; segunda edição preserva o snapshot anterior |
| US03-CA2/T2 | testes unitários e API de edição | 409 para versão antiga/resolvido/em_analise; 404 para UUID ausente; 422 sem campos de conteúdo, null, extras e versões inválidas |
| US03-CA2/T2 | test_us03_ca2_two_connections_only_one_version_wins | Duas conexões PostgreSQL adquiridas antes da disputa: uma confirma, outra recebe 409/version_conflict; apenas um evento editado |
| US03-CA1/CA2/T2 | test_us03_edit_event_failure_rolls_back_everything | Constraint de evento inválido reverte texto, versões, classificação e estado; não insere evento parcial |
| US03-CA3/T2 | testes unitários e API | Trim, no-op com resposta/timestamps/eventos intactos, limites exatos e ±1, null/tipos/extra rejeitados |
| US03-T2 | test_us03_migration_preserves_existing_ticket; migração roundtrip existente | Upgrade 0001→0002 preserva chamado; downgrade/upgrade só em banco descartável; alembic check sem divergência |
| US03-T2 | tests/e2e/test_http.py | TCP/Uvicorn real: cadastrar, editar, consultar e rejeitar versão antiga; PostgreSQL real exclusivo |
| US03-T3 | arquitetura ADR07, contrato API, README, guia Windows e registro de homologação | Decisão técnica, exemplos de conflito e roteiro manual atualizados |

Implementação usa SELECT FOR UPDATE dentro de transação: obter linha, verificar versão/estado, arquivar classificação, alterar e registrar evento sem liberar o bloqueio entre comparação e escrita. No-op ainda exige versão e estado válidos. Sem dependência de IA. ADR07 explica projeções/snapshots antes de existirem entidades de tentativas/revisões; estas seguem futuras. Não guardar texto antigo completo nem alegar auditoria legal.

### Testes e correções reais

Comandos na raiz, com Python da .venv e TEST_DATABASE_URL apontando para banco administrativo isolado portfolio_test em 127.0.0.1:55432:

```powershell
.\.venv\Scripts\python.exe -m ruff check .
.\.venv\Scripts\python.exe -m ruff format --check .
.\.venv\Scripts\python.exe -m pip check
$env:TEST_DATABASE_URL = 'postgresql+psycopg://portfolio_test:senha_ficticia_teste@127.0.0.1:55432/portfolio_test'
.\.venv\Scripts\python.exe -m pytest -q --junitxml=reports/us03-all.xml
```

**Resultado final: 72 passed, 1 warning, 185,82 s, nenhuma falha ou skip.** São 37 unitários, 9 integração (8 com PostgreSQL ativo + 1 de conexão recusada com driver real), 25 API dentro do processo com PostgreSQL real e 1 HTTP/TCP com Uvicorn real e PostgreSQL. Unitários usam objetos simples/mocks quando apropriado; não representam persistência. Não há SQLite. Cada teste de banco ativo usa banco exclusivo, sem limpar o demo. Relatório local ignorado pelo Git em reports/us03-all.xml. Ruff check/format e pip check aprovados; sem novas dependências.

Falhas intermediárias registradas e resolvidas: coleta pytest conflitou com módulos homônimos de testes, resolvido por --import-mode=importlib (sem apagar arquivos); integração inicial teve 34 passados/1 falha por PATCH/GET representarem o mesmo timestamp em fusos diferentes. Corrigida normalização de created_at/updated_at em UTC no schema de resposta e incluída regressão unitária; suíte final integral aprovada. Aviso conhecido de depreciação HTTPX/TestClient continua visível, sem falha. Formatação corrigida antes do resultado final.

### Banco demo e API prontos para homologação

Aplicada apenas migração upgrade head no demo: **0002 (head)**. Comparação de todos os campos preexistentes antes/depois confirmou **1 chamado e 1 evento preservados integralmente**; nenhuma edição de chamado demo pelo agente. Snapshots operacionais em .local/demo-us03-preservation.json, fora do Git. Downgrade não foi executado no demo.

API antiga identificada pelo comando Uvicorn e pelo processo lançador da .venv deste projeto antes de encerrá-la. Houve uma tentativa de inicialização sem sucesso por porta ocupada, sem modificar dados. Inspeção via Get-NetTCPConnection não foi suficiente; identificação final usou Win32_Process com comando/parent verificados. A API foi atualizada sem encerrar processos desconhecidos. Versão **0.2.0**, PATCH presente no OpenAPI, `/docs` HTTP 200, total demo=1 e version do chamado=1 confirmados após inicialização. API e PostgreSQL deixados ativos em loopback. Logs atuais .local/api-us03-current.*; launcher PID 16780, servidor PID 23448 (sempre reconferir identidade antes de encerrar; PIDs podem ser reutilizados).

### Próximo passo e limites

**US03 implementada, CA1–CA3 verificados automaticamente; aguardando homologação de Eliana**, roteiro em [12-homologacao-us03.md](12-homologacao-us03.md). Não marcar homologação manual antes do relato. Invalidação de classificação existente, estados resolvido/em_analise e concorrência têm evidência automatizada com fixtures fictícias: não há rotas de triagem/revisão/resolução para criá-los pelo Swagger ainda. Não antecipar US04–US06 para a homologação.

Docker Compose e CI no GitHub permanecem pendentes; US01 não totalmente validada. US04 não iniciada. Somente AI_MODE=simulated, sem chamadas de IA reais, custos, publicação ou deploy. Em nova conversa, ler esta seção e o registro de homologação antes dos registros históricos abaixo.

## 07/11/2026 — Ambiente iniciado para homologação guiada

PostgreSQL isolado iniciado em 127.0.0.1:55432; banco `portfolio_chamados_demo` criado sem excluir dados, migração `0001 (head)` aplicada. Total inicial=0. API iniciada em segundo plano em 127.0.0.1:8000; `/docs` HTTP 200, health ok e contrato OpenAPI conferidos após a inicialização. Processos deixados ativos para Eliana, sem garantia de sobrevivência a encerramento da sessão do sistema; comandos exatos de retomada documentados.

Homologação própria em [11-homologacao-us01-us02.md](11-homologacao-us01-us02.md). **H01 aguardando retorno de Eliana; H02–H05 não iniciados.** Não registrar aprovação sem retorno. Usar o UUID recebido em H01 nas próximas etapas. Docker Compose e execução remota de CI continuam pendentes, US01 não totalmente validada e US03 não iniciada. Nenhuma publicação ou chamada paga.

## 07/11/2026 — US01/US02 implementadas; aguardando validação de Eliana

### Aprovação e escopo

Eliana aprovou o MVP; [D01–D08 consolidadas](08-decisoes-aprovadas.md), sem conflitos. Somente uso local sem autenticação, categorias/prioridades centrais, triagem separada e retry manual, invalidação após edição, revisão obrigatória antes de resolução e histórico de transições. Provedor real e orçamento adiados; nenhuma chamada paga. Esta entrega se limita à fundação, cadastro/consulta e CI pertinente; não iniciar US03 sem validação de Eliana.

### Ambiente e implementação

- Python 3.12.6, pip 24.2 e Git 2.46.2 disponíveis. Docker/Compose ausentes. PostgreSQL 16.4 instalado, serviço existente parado e preservado.
- `.venv` local criada. Compatibilidade consultada em fontes oficiais antes da instalação; [fontes e versões](09-ambiente-e-versoes.md). Locks fixam dependências diretas/transitivas, sem hashes. Instalação pelo lock conferida com `--no-index` no ambiente já instalado; não representa ensaio de instalação limpa em Linux.
- Cluster de teste separado em `.local/pgdata`, loopback 127.0.0.1:55432, credenciais fictícias. Cada caso cria banco próprio `portfolio_test_<uuid>` e remove apenas esse banco; desenvolvimento não é usado. Serviço global não alterado. Scripts de iniciar/parar em `scripts/`.
- API FastAPI por factory; sessões SQLAlchemy, Alembic 0001, tabelas Ticket/TicketEvent, cadastro transacional com evento, consulta por UUID, listagem/paginação/filtros, trim e limites Unicode, campos extras rejeitados e erros uniformes sanitizados.
- Rotas disponíveis: GET `/health`, POST/GET `/api/v1/tickets`, GET `/api/v1/tickets/{ticket_id}`; Swagger e OpenAPI. Sem PATCH, triagem ou revisão nesta entrega. Cadastro não importa/instancia provedor algum e não depende de IA. AI_MODE diferente de simulated é rejeitado.
- Dockerfile/Compose com portas publicadas somente em loopback; migração como serviço separado. Workflow GitHub Actions com PostgreSQL 16 e etapas separadas de lint, unitários, integração/API e HTTP real. Preparados, mas Docker e CI remota não executados.
- Git local inicializado na branch `feat/foundation-tickets`, sem remoto; nenhuma publicação ou deploy.

### Rastreabilidade e evidências reais

| Critérios/tasks | Código/documentação | Evidência executada |
|---|---|---|
| US01-CA1/T1/T3 | pyproject, locks, database, main, Dockerfile, compose, migrations; guia Windows | Migração e health aprovados nativamente; inicialização Compose **não executada** por Docker ausente |
| US01-CA2/T2 | handlers, health e configuração | `test_us01_ca2_us02_storage_error_sanitized` (mock) e `test_us01_ca2_real_driver_connection_refused` (driver real sem servidor) aprovados |
| US01-CA3/T2 | Alembic 0001 e metadados | `test_us01_ca3_migrations_roundtrip_and_metadata`: upgrade duas vezes, alembic check, downgrade/base e novo upgrade, PostgreSQL real |
| US02-CA1/T1/T2 | rotas, schemas, serviço, repositório, modelos | `test_us01_ca1_us02_ca1_create_read_list`, `test_us02_atomic_event_and_reconnect` e `test_us02_http_real_process` aprovados |
| US02-CA2/T2 | validação e erros | Casos unitários e `test_us02_ca2_ca3_invalid_not_persisted`; 404/UUID inválido; rollback de evento com falha real de constraint |
| US02-CA3/T2 | schemas e constraints | Limites 5/120, 20/5000, ±1, trim/Unicode no unitário e por HTTP dentro do processo, com PostgreSQL real |
| US02-CA4/T2 | paginação/filtros/ordenação | Listagem vazia, limit 1/100 e inválidos 0/101, offset negativo, filtros inválidos e páginas estáveis aprovados |
| US02-T3 | README, contrato atualizado, guia Windows e decisões | Links locais conferidos e separação explícita entre rotas ativas e futuras |
| Base de US07 | `.github/workflows/ci.yml` e suítes por camada | Comandos locais equivalentes executados; workflow remoto não executado; US07 não concluída |

Comandos executados na raiz (Python local: `.\.venv\Scripts\python.exe`):

```powershell
.\.venv\Scripts\python.exe -m pip check
.\.venv\Scripts\python.exe scripts/lock_dependencies.py
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.lock --no-index
.\.venv\Scripts\python.exe -m ruff check .
.\.venv\Scripts\python.exe -m ruff format --check .
$env:TEST_DATABASE_URL = 'postgresql+psycopg://portfolio_test:senha_ficticia_teste@127.0.0.1:55432/portfolio_test'
.\.venv\Scripts\python.exe -m pytest -q --junitxml=reports/all.xml
# Após ajuste de sanitização da configuração e header de erro:
.\.venv\Scripts\python.exe -m pytest tests/unit tests/integration/test_unavailable.py -q --junitxml=reports/final-focused.xml
git diff --check
```

**Resultado completo: 40 passed, 1 warning, 133,84 s; nenhuma falha ou skip.** Divisão: 16 unitários, 5 integração, 18 API, 1 e2e. Integração: 4 casos com PostgreSQL ativo + 1 de conexão recusada com driver real. API: TestClient/HTTPX dentro do processo e PostgreSQL real. E2E: Uvicorn em processo separado, HTTPX por TCP e PostgreSQL real. **Reexecução focada final: 17 passed, 1 warning, 3,70 s**, sem novos casos além dos 40. Pip check sem dependências quebradas; Ruff check e format aprovados. Uma execução anterior de PostgreSQL/API/e2e havia obtido 22 passed antes dos dois casos adicionais. Relatórios JUnit locais em `reports/`, ignorados pelo Git.

Aviso preservado: Starlette TestClient depreca uso de HTTPX e sugere HTTPX2. Não houve falha; nenhum pacote extra foi instalado para esconder o aviso. Limitação técnica registrada em ambiente/versões. Primeira passagem de Ruff identificou formatação/linhas longas, corrigidas antes das verificações finais.

Conferência documental: 23 links locais verificados, zero quebrados; .env, .venv, .local e reports confirmados como ignorados por `git check-ignore`. Nenhum segredo real usado; apenas credenciais fictícias de desenvolvimento/teste.

### Estado e pendências

- **US01: não concluída**. CA2/CA3 aprovados; falta executar caminho Compose de CA1, imagem Docker e persistência por reinício do Compose. Não declarar cobertura de ambiente Docker/Linux ou de CI remota.
- **US02: implementada, CA1–CA4 verificados localmente, aguardando validação de Eliana.** Dependência US01 tem pendência de ambiente explicitada.
- **US07: somente base adiantada** para as verificações disponíveis; sem fluxo de triagem/revisão ainda.
- **US03–US06 e US09: não iniciadas; US08 adiada.** Não há simulador de triagem implementado ainda (US04); a aplicação atual apenas não utiliza IA.
- Nenhuma avaliação de modelo, chamada paga, publicação ou deploy. Guia de validação em [10-validacao-local.md](10-validacao-local.md).

Próximo passo: Eliana valida os endpoints e o guia local. Se Docker se tornar disponível, executar CA1/Compose e registrar resultado. Somente depois da validação solicitada, seguir para US03, mantendo a dependência de US01 visível. Nas próximas conversas ler esta seção antes do histórico documental abaixo.

## 07/11/2026 — Primeira entrega documental

**Estado: proposta inicial, aguardando revisão do escopo por Eliana.** Aplicação não implementada; nenhuma história US01–US09 iniciada ou concluída. Não configurar dependências nem iniciar código antes da revisão solicitada.

### Pedido e inspeção

Pedido recebido por arquivo anexado e lido em UTF-8. Pasta de trabalho inspecionada com `Get-Location`, `Get-ChildItem -Force` e busca `rg --files -g AGENTS.md -g '!node_modules' -g '!.git'`. A pasta estava vazia, inclusive sem `.git` ou instruções locais preexistentes. Busca sem resultados retornou código 1; não é falha de teste. Nenhum conteúdo existente foi alterado.

### Produzido

README inicial, AGENTS.md, .gitignore e .env.example fictício; documentos 01–07 cobrindo produto, regras, estados, requisitos não funcionais, backlog, critérios/tasks, arquitetura, dados, contrato de API, testes, avaliação do agente, plano, riscos, DoR e DoD.

### Validação desta entrega

Conferência documental executada em PowerShell: enumeração por `Get-ChildItem -Recurse -File`, leitura UTF-8, extração de links Markdown com regex e resolução por `Test-Path`; conferência de seções US01–US09 e marcadores CA1/CA2/CA3/T1/T2/T3 em cada história. Resultado: **12 arquivos, 12 links locais, zero links quebrados, 9 histórias com os marcadores esperados; saída 0**. Nenhum caractere de substituição Unicode encontrado nos documentos. Revisão manual cruzou estados, regras, versões, contrato e dependências; isso não equivale a validação executável do contrato.

Não há aplicação, dependências, testes ou workflow para executar. Nenhuma versão de biblioteca foi validada: essa verificação pertence a US01, antes de configurar dependências. Nenhuma chamada paga, publicação, deploy ou configuração de Git foi realizada.

### Pendências de revisão

Revisar D01–D08 em [produto](01-produto.md): MVP local sem autenticação; catálogo; prioridade sugerida; triagem explícita síncrona e retry; edição/invalidação; revisão humana; resolução/reabertura; escolha de provedor real e orçamento.

### Próxima conversa

1. Ler AGENTS.md, README e este documento.
2. Conferir se Eliana revisou o escopo; incorporar decisões nos documentos e registrar alterações.
3. Após revisão, iniciar US01: inspecionar ferramentas instaladas e Git, verificar versões em fontes oficiais, configurar ambiente/migrações e executar seus critérios.
4. Implementar uma história por vez; registrar IDs de aceite, comandos, resultados e limitações. Manter modo simulado padrão e aguardar autorização específica para publicação/deploy/chamadas pagas.
