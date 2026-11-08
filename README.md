# Triagem Inteligente de Chamados

[English](README.en.md) · Portfólio de **Eliana Gomes da Silva** · versão 0.5.0.

API local para registrar chamados, sugerir classificação e apoiar uma decisão humana rastreável. **O agente é inteiramente simulado:** roteiros reproduzíveis consultam duas ferramentas locais (catálogo de categorias e política de prioridade). Não há LLM, SDK de provedor, chave de IA nem inferência paga. Integração com modelo real permanece adiada em **US08**; não alegamos acurácia de modelo real.

Funcionalidades: cadastro/consulta paginada, edição com versionamento otimista, sugestão validada, retry explícito, recuperação de tentativas expiradas, revisão humana, classificação final, resolução e reabertura. Edição efetiva invalida a classificação atual e preserva tentativas, revisões e snapshots anteriores. Cadastro funciona sem triagem; a pessoa revisora decide a classificação final.

Arquitetura: monólito modular FastAPI/Pydantic → serviços de aplicação e regras de domínio → repositórios SQLAlchemy/PostgreSQL; migrações Alembic. Orquestrador separado por interface AIProvider usa somente o simulador. A tentativa é persistida antes da execução; não há transação de banco aberta durante a chamada ao provedor. Saídas/ferramentas são validadas fora dele. [Arquitetura e decisões](docs/04-arquitetura.md).

## Obter o projeto

Repositório: [elisilva75/triagem-chamados-agente-ia](https://github.com/elisilva75/triagem-chamados-agente-ia), branch principal **main**. Para contribuir, faça fork no GitHub e clone a URL do seu fork. Para apenas executar, clone o original:

```powershell
git clone "https://github.com/elisilva75/triagem-chamados-agente-ia.git"
Set-Location triagem-chamados-agente-ia
```

Não é necessário configurar remoto ou publicar para executar uma cópia local.

## Pré-requisitos e instalação nativa (Windows/PowerShell)

Instale Python **3.12.x** pelas [distribuições oficiais para Windows](https://www.python.org/downloads/windows/), PostgreSQL **16** com ferramentas de linha de comando pelo [site oficial](https://www.postgresql.org/download/windows/) e [Git para Windows](https://git-scm.com/downloads/win). Inclua Python no PATH; localize os binários PostgreSQL. As versões efetivamente ensaiadas estão abaixo; outros patches/SOs não foram certificados. Não é necessário ativar o serviço PostgreSQL global nem instalar pgAdmin para usar este guia.

Na raiz do projeto, em checkout preferencialmente fora de pasta sincronizada:

```powershell
python --version
git --version
& 'C:\Program Files\PostgreSQL\16\bin\pg_ctl.exe' --version
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.lock
.\.venv\Scripts\python.exe -m pip check
if (-not (Test-Path .env)) { Copy-Item .env.example .env }
notepad .env
```

No .env, mantenha APP_ENV=local e AI_MODE=simulated. Para o caminho nativo, **troque DATABASE_URL do exemplo** pelo valor da tabela. O .env.example usa porta/usuário do Compose; não são os mesmos do cluster nativo.

| Variável | Valor local nativo |
|---|---|
| APP_ENV | local |
| AI_MODE | simulated |
| DATABASE_URL | postgresql+psycopg://portfolio_test:senha_ficticia_teste@127.0.0.1:55432/portfolio_chamados_demo |

São credenciais fictícias de desenvolvimento, não segredos de produção. .env é ignorado pelo Git; não inclua chaves reais. Variáveis da sessão PowerShell prevalecem sobre .env. Os comandos abaixo as definem explicitamente para evitar usar outra conexão. Não altere a política de execução global nem ative a venv: use seu Python diretamente.

## Iniciar pelo caminho nativo ensaiado

```powershell
.\scripts\start-test-postgres.ps1
# Somente na primeira execução: omita createdb se o banco já existir.
$env:PGPASSWORD = 'senha_ficticia_teste'
& 'C:\Program Files\PostgreSQL\16\bin\createdb.exe' -h 127.0.0.1 -p 55432 -U portfolio_test portfolio_chamados_demo
Remove-Item Env:PGPASSWORD
$env:APP_ENV = 'local'
$env:AI_MODE = 'simulated'
$env:DATABASE_URL = 'postgresql+psycopg://portfolio_test:senha_ficticia_teste@127.0.0.1:55432/portfolio_chamados_demo'
.\.venv\Scripts\python.exe -m alembic upgrade head
.\.venv\Scripts\python.exe -m uvicorn app.main:create_app --factory --host 127.0.0.1 --port 8000 --no-access-log
```

O script inicia/reutiliza .local/pgdata em **127.0.0.1:55432**, preserva dados e define TEST_DATABASE_URL na sessão. Para outro caminho de binários, use `-PgBin 'C:\caminho\PostgreSQL\16\bin'`. O usuário desse cluster local pode criar bancos para os testes. Não apontar para banco de empregador ou produção. Se createdb/migração falhar, resolva o erro antes de iniciar API; não apague o banco.

Em outro terminal:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health
Invoke-RestMethod http://127.0.0.1:8000/api/v1/tickets
```

Health 200 deve ser complementado pela consulta real. Swagger: **http://127.0.0.1:8000/docs**; OpenAPI: /openapi.json. Migração deve estar em 0004; não ocorre por requisição.

## Parar e reiniciar sem apagar dados

Primeiro Ctrl+C no terminal da API. Pare o cluster somente quando nenhuma API ou suíte estiver usando-o. Para reiniciar apenas a API, mantenha PostgreSQL ativo e repita somente as variáveis e o comando Uvicorn.

```powershell
# API: Ctrl+C
.\scripts\stop-test-postgres.ps1
# Reinício completo: reutiliza cluster e banco; não repetir createdb.
.\scripts\start-test-postgres.ps1
$env:APP_ENV = 'local'
$env:AI_MODE = 'simulated'
$env:DATABASE_URL = 'postgresql+psycopg://portfolio_test:senha_ficticia_teste@127.0.0.1:55432/portfolio_chamados_demo'
.\.venv\Scripts\python.exe -m uvicorn app.main:create_app --factory --host 127.0.0.1 --port 8000 --no-access-log
```

Ao atualizar código, encerre a API, mantenha o cluster ativo, execute `alembic upgrade head` pelo Python da venv com a conexão correta e reinicie Uvicorn. Não executar initdb de novo, downgrade, exclusão de .local/pgdata ou limpeza do demo.

## Docker Compose — alternativa ainda não validada

Docker não estava disponível no ambiente local. Build, início e persistência por reinício do **Compose não foram executados**. Instale/inicie [Docker Desktop com mecanismo Linux e Compose](https://docs.docker.com/desktop/setup/install/windows-install/) conforme os requisitos oficiais. A CI verifica a aplicação no runner Linux com PostgreSQL de serviço; isso não valida a imagem da API nem o fluxo Compose.

Portas padrão: **127.0.0.1:5432** (banco) e **127.0.0.1:8000** (API). Antes de usar, encerre sua API nativa ou siga o [guia de projeto isolado/portas alternativas](docs/10-validacao-local.md). Não encerre outros serviços para liberar portas. O Compose define sua própria DATABASE_URL interna para db:5432 e credenciais fictícias no YAML; não usa o banco nativo nem o DATABASE_URL do .env.

```powershell
docker version
docker compose version
docker compose -p portfolio-local config --quiet
docker compose -p portfolio-local up --build -d
docker compose -p portfolio-local ps -a
docker compose -p portfolio-local logs --tail 50 migrate api
```

Exigir db saudável e migrate encerrado com código 0 antes da API. Depois repetir health, consulta real e exemplo Swagger. Use sempre o mesmo nome de projeto e o mesmo checkout para reencontrar o volume.

```powershell
docker compose -p portfolio-local stop
docker compose -p portfolio-local up -d
docker compose -p portfolio-local restart db api
docker compose -p portfolio-local down
```

Comandos alternativos: stop pausa; up -d retoma; restart reinicia serviços existentes; down remove containers/rede e **preserva o volume nomeado**. Aguarde health novamente e compare GET do mesmo ID após reiniciar. **Nunca adicionar -v a down**, remover volumes ou trocar de projeto esperando os mesmos dados. Para atualização de imagem/código, usar novamente up --build -d. Estes comandos permanecem não ensaiados.

## Exemplo completo pelo Swagger

Use dados fictícios em um chamado novo. Em /docs, execute POST **/api/v1/tickets**:

```json
{"title":"Erro ao salvar cadastro fictício","description":"No ambiente fictício, salvar o cadastro retorna erro para todos os usuários."}
```

Esperado: 201, ID, aberto/pendente, version=1, content_revision=1. Guarde o ID. GET /api/v1/tickets/{ticket_id}; copie version para POST /api/v1/tickets/{ticket_id}/triage:

```json
{"expected_version":1}
```

Esperado: 200, {ticket,attempt}, sugestão mode=simulated, triagem sugerida, version=3/content_revision=1. GET novamente e use a versão atual em POST /api/v1/tickets/{ticket_id}/reviews:

```json
{"expected_version":3,"category":"defeito","priority":"alta","reason":"Confirmei o bloqueio no ambiente fictício.","declared_reviewer":"Pessoa Revisora Demo"}
```

Esperado: 201, {ticket,review}, version=4, triagem revisada, classificação final registrada. GET e POST /api/v1/tickets/{ticket_id}/resolve:

```json
{"expected_version":4}
```

Esperado: 200, resolvido, version=5/content_revision=1. GET confirma persistência; GET triage-attempts e GET reviews preservam os registros. As versões acima pressupõem apenas essa sequência: **consultar GET antes de toda escrita em chamado existente**, inclusive no-op. [Contrato de API](docs/05-api.md); [roteiro de falha/retry e portfólio](docs/16-demonstracao-e-portfolio.md). Demonstração opcional, sem nova homologação manual obrigatória.

## Testes automatizados em banco isolado

Inicie o cluster pelo script, sem parar o demo. Na raiz:

```powershell
$env:TEST_DATABASE_URL = 'postgresql+psycopg://portfolio_test:senha_ficticia_teste@127.0.0.1:55432/portfolio_test'
$env:AI_MODE = 'simulated'
$env:APP_ENV = 'test'
.\.venv\Scripts\python.exe scripts/check_quality.py
```

Pipeline: pip check, Ruff check/format, unitários, integração PostgreSQL/API dentro do processo e HTTP/TCP contra Uvicorn separado. Fixtures criam/migram/removem somente bancos únicos portfolio_test_<uuid>; não limpam o banco administrativo recebido. Não usar DATABASE_URL do demo como TEST_DATABASE_URL. URL administrativa deve ser local com prefixo portfolio_test e permissão de criar bancos.

Interrompe na primeira falha e rejeita suites vazias/com skips obrigatórios. JUnit em reports/, ignorado pelo Git. Para teste parcial: `.\.venv\Scripts\python.exe -m pytest tests/unit -q`. Fora do pipeline, ausência de TEST_DATABASE_URL causa skips de PostgreSQL, não aprovação. Actions usa esse mesmo runner em Ubuntu com PostgreSQL de serviço, sem chave paga; [CI remota aprovada: 177 testes](https://github.com/elisilva75/triagem-chamados-agente-ia/actions/runs/42507831040).

## Problemas comuns

| Sintoma | Verificação / solução sem apagar dados |
|---|---|
| Python errado ou não encontrado | Conferir python --version: este projeto requer 3.12.x. Corrigir PATH/selecionar instalação antes de criar venv; não substituir pacotes globais. |
| Porta 8000/5432 ocupada | `Get-NetTCPConnection -State Listen -LocalPort 8000,5432,55432 -ErrorAction SilentlyContinue`; identificar o serviço. Usar --port 18000 no Uvicorn ou guia de Compose isolado. Não encerrar processos pelo nome genérico Python. |
| PostgreSQL recusando conexão / health 503 | `& 'C:\Program Files\PostgreSQL\16\bin\pg_isready.exe' -h 127.0.0.1 -p 55432`; iniciar/reutilizar cluster pelo script. Conferir nome do banco, porta e variáveis da sessão/.env. Não imprimir credenciais em relatórios. |
| Relação não existe / migração atrasada | Com a conexão correta, `.\.venv\Scripts\python.exe -m alembic current`, `-m alembic heads` e `-m alembic upgrade head`. Não usar downgrade/reset no demo. Banco não existe exige createdb uma vez; alembic não cria o banco. |
| pg_ctl sem permissão / script bloqueado | Usar mesmo usuário que iniciou o cluster; conferir binários e política da máquina. No Codex, token restrito não reconheceu processo existente; execução autorizada fora da restrição funcionou. Não apagar postmaster.pid nem alterar política global como atalho. |
| 409 version_conflict / triage_in_progress | Consultar GET e revisar versão/estado. Tentativa em análise dentro do prazo bloqueia nova triagem; recuperação é explícita após prazo. Não limpar dados para destravar. |
| Falha no serviço migrate do Compose | Conferir ps -a e logs migrate. Corrigir conexão/migração antes de reiniciar; não remover volume. Compose permanece não validado. |

## Versões e última validação executada

| Componente | Versão |
|---|---|
| Aplicação / migração head | 0.5.0 / 0004 |
| Python / pip / Git | 3.12.6 / 24.2 / 2.46.2.windows.1 |
| PowerShell | 5.1.26100.9818 |
| PostgreSQL nativo | 16.4 |
| FastAPI / Starlette / Uvicorn | 0.162.2 / 1.10.0 / 0.54.0 |
| Pydantic / pydantic-settings | 2.14.3 / 2.16.2 |
| SQLAlchemy / Alembic / psycopg | 2.0.57 / 1.20.1 / 3.3.8 |
| pytest / HTTPX / Ruff | 9.2.0 / 0.28.1 / 0.17.4 |

Windows 11 build 26300, PowerShell, PostgreSQL nativo. Locks completos: requirements.lock e requirements-dev.lock. Conjunto efetivamente utilizado, **sem prometer outros patches/SOs**. Imagem da API python:3.12-slim ainda sem build validado; o serviço postgres:16 da CI executou PostgreSQL 16.15 conforme os logs. [Fontes/compatibilidade](docs/09-ambiente-e-versoes.md).

Validação local anterior em **08/11/2026**: Python da venv com `scripts/check_quality.py` e variáveis acima, **177 passed**, sem falha/erro/skip (98 unitários, 77 integração/API, 2 HTTP real). pip check e Ruff aprovados. Aviso conhecido TestClient/HTTPX mantido visível. Instalação isolada e reinício nativo da API aprovados, demo preservado.

**CI GitHub aprovada em 08/11/2026**, commit `c7c3331`: `python scripts/check_quality.py`, mesmos **177 testes**, zero falhas/erros/skips nos três relatórios JUnit. Ambiente observado nos logs: Ubuntu 26.04, Python 3.12.16, PostgreSQL 16.15, mesmos locks. A atualização documental posterior usa `[skip ci]` para não repetir a suíte sem mudança funcional; não atribui uma nova execução ao commit de documentação. Compose/imagem da API continuam não validados. [Evidências e limites](docs/andamento.md).

## Limitações, licença e publicação

Uso exclusivo em **loopback, com dados fictícios e sem autenticação**. Não expor publicamente nem usar com dados de empregadores. Autor da revisão é declarado, não autenticado. Não há reconstrução integral de textos antigos, auditoria legal, worker distribuído ou evidência de qualidade de modelo real.

Licença [MIT](LICENSE), copyright 2026 Eliana Gomes da Silva. Publicação pública de main autorizada pela autora, com endereço GitHub noreply confirmado nos commits. Auditoria e resultado da publicação/CI na revisão vinculada abaixo e no andamento. Docker Compose permanece pendente de validação. Sem deploy ou chamadas pagas.

Desenvolvimento com assistência de IA (Codex) em implementação, revisão, testes e documentação, sob decisões de produto e revisão de Eliana. Isso é distinto do simulador da aplicação.

[Produto](docs/01-produto.md) · [Regras](docs/02-regras-e-fluxos.md) · [Backlog/rastreabilidade](docs/03-backlog.md) · [Testes](docs/06-testes.md) · [DoD/entregas](docs/07-entregas.md) · [Guia Windows](docs/10-validacao-local.md) · [Revisão para publicação](docs/17-revisao-publicacao.md)
