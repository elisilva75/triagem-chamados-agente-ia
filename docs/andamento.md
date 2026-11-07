# Andamento e continuidade

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
