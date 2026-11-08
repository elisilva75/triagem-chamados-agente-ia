# Execução e validação local no Windows

US01–US06: cadastro, consulta, edição, triagem exclusivamente simulada, recuperação de falhas, revisão humana e resolução/reabertura. Sem autenticação ou chamadas de IA externas. Usar dados fictícios e manter bind em 127.0.0.1. Executar os comandos na raiz do projeto em PowerShell. Não alterar a política de execução global; se scripts estiverem bloqueados por política da máquina, usar os comandos manuais equivalentes ou informar o impedimento.

## Ambiente Python

Python 3.12.x e PostgreSQL 16 são os requisitos nativos. Git é necessário para versionar. Docker Desktop com Compose é alternativa; não está instalado no ambiente desta entrega.

```powershell
python --version
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.lock
.\.venv\Scripts\python.exe -m pip check
```

Se .venv já existe desta entrega, pode reutilizá-la. Não é necessário ativar o ambiente nem instalar pacotes globalmente. O lock de produção é `requirements.lock`; o de desenvolvimento inclui ferramentas de teste e lint.

## Alternativa nativa com PostgreSQL já instalado

O serviço PostgreSQL existente não precisa ser iniciado. O script abaixo usa os binários instalados, cria cluster exclusivo em `.local/pgdata`, senha fictícia e acesso somente por loopback. Esse diretório é ignorado pelo Git e não deve ser sincronizado como artefato do projeto nem usado em produção. Idealmente manter o checkout executável fora de pastas sincronizadas pelo OneDrive.

```powershell
.\scripts\start-test-postgres.ps1
# Se os binários estiverem em outro lugar:
# .\scripts\start-test-postgres.ps1 -PgBin 'C:\caminho\PostgreSQL\16\bin'
```

O script define TEST_DATABASE_URL apenas na sessão atual. Os testes criam/removem bancos próprios `portfolio_test_<uuid>`; não removem o banco informado. O usuário desse cluster tem permissão para CREATE DATABASE exclusivamente para suportar testes. Não usar credenciais reais nem apontar para banco de trabalho.

Para experimentar a API com dados que sobrevivam aos testes, criar **outro banco** uma única vez:

```powershell
$env:PGPASSWORD = 'senha_ficticia_teste'
& 'C:\Program Files\PostgreSQL\16\bin\createdb.exe' -h 127.0.0.1 -p 55432 -U portfolio_test portfolio_chamados_demo
Remove-Item Env:PGPASSWORD
$env:DATABASE_URL = 'postgresql+psycopg://portfolio_test:senha_ficticia_teste@127.0.0.1:55432/portfolio_chamados_demo'
$env:AI_MODE = 'simulated'
.\.venv\Scripts\python.exe -m alembic upgrade head
.\.venv\Scripts\python.exe -m uvicorn app.main:create_app --factory --host 127.0.0.1 --port 8000 --no-access-log
```

Se o banco demo já existir, omitir createdb; não apagar dados para repetir o guia. O servidor fica no terminal até Ctrl+C. Em outra janela, abrir `http://127.0.0.1:8000/docs`, ou executar:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health
$body = @{title='Erro na tela de demonstração'; description='Ao salvar dados fictícios, a tela retorna uma mensagem de erro.'} | ConvertTo-Json
$ticket = Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/api/v1/tickets -ContentType 'application/json; charset=utf-8' -Body ([System.Text.Encoding]::UTF8.GetBytes($body))
$ticket
Invoke-RestMethod "http://127.0.0.1:8000/api/v1/tickets/$($ticket.id)"
Invoke-RestMethod 'http://127.0.0.1:8000/api/v1/tickets?limit=20&offset=0'
```

Esperado: health ok; cadastro 201 (visível no Swagger/cliente com status), aberto/pendente, version=1, suggestion/final_classification nulos; consulta devolve o mesmo chamado. Entradas com título de 4 caracteres, descrição menor que 20, campo extra ou status no cadastro geram 422. ID UUID inexistente gera 404. Listagem limita 1–100. PATCH já disponível; seguir [homologação de US03](12-homologacao-us03.md). Triagem simulada implementada; revisão e resolução continuam futuras.

Após atualizar o código para US03, aplicar `alembic upgrade head` (migração 0002 aditiva, sem apagar chamados) e reiniciar apenas a API deste projeto para carregar as novas rotas. Não aplicar downgrade ao banco demo; snapshots seriam removidos. Abrir `/openapi.json` e confirmar info.version=0.2.0, ou atualizar `/docs` com Ctrl+F5 para ver PATCH.

Para parar o cluster, primeiro encerrar servidores da API e testes, depois:

```powershell
.\scripts\stop-test-postgres.ps1
```

Não usar `down -v` nem apagar .local para repetir uma validação; dados persistentes devem ser preservados.

## Testes e verificações

```powershell
.\.venv\Scripts\python.exe -m ruff check .
.\.venv\Scripts\python.exe -m ruff format --check .
.\.venv\Scripts\python.exe -m pytest tests/unit -q
# PostgreSQL real, banco administrativo de teste em cluster separado:
$env:TEST_DATABASE_URL = 'postgresql+psycopg://portfolio_test:senha_ficticia_teste@127.0.0.1:55432/portfolio_test'
.\.venv\Scripts\python.exe -m pytest tests/integration tests/api -q
.\.venv\Scripts\python.exe -m pytest tests/e2e -q
# Suíte completa e relatório:
.\.venv\Scripts\python.exe -m pytest -q --junitxml=reports/all.xml
```

Sem TEST_DATABASE_URL, casos que exigem PostgreSQL são **pulados**, não aprovados; o teste de conexão recusada ainda usa o driver real sem servidor ativo. Banco informado inacessível ou inválido produz falha, não skip. Testes não usam SQLite. `tests/unit/test_errors.py` usa mock de sessão e não comprova persistência. `tests/api` usa TestClient dentro do processo **com PostgreSQL real**; `tests/e2e` inicia processo Uvicorn e faz HTTPX por TCP **com PostgreSQL real**.

## Docker Compose — configuração ainda não executada nesta máquina

Após disponibilizar Docker/Compose, verificar `docker version` e `docker compose version`. Porta 5432 deve estar livre. O Compose usa seu próprio volume PostgreSQL e não lê o cluster .local.

```powershell
docker compose config --quiet
docker compose up --build -d
docker compose ps -a
Invoke-RestMethod http://127.0.0.1:8000/health
docker compose down
```

`migrate` é um serviço de execução única: sucesso deve aparecer como exited (0), antes de a API iniciar. Os binds publicados são 127.0.0.1:5432 e 127.0.0.1:8000. `down` preserva o volume. O critério US01-CA1 só será integralmente validado após esse caminho funcionar; não foi executado nesta entrega.

## CI

Workflow em `.github/workflows/ci.yml`: Python 3.12, PostgreSQL 16, instalação pelo lock, pip check, Ruff, unitários, integração/API e HTTP real, com relatórios JUnit. Não inclui IA externa, chaves ou serviços pagos. O arquivo foi preparado localmente, sem publicar nem executar no GitHub. Eventuais custos/limites de execução da conta GitHub devem ser revistos quando houver autorização para publicar; não há contratação nesta etapa.


## Atualização US04 — cluster e dados existentes

Reutilizar `.local/pgdata` e banco demo existentes; não executar initdb/createdb novamente, não limpar dados. Aplicar apenas `alembic upgrade head` (0003 aditiva) e reiniciar somente a API identificada deste projeto, mantendo DATABASE_URL do demo, AI_MODE=simulated e bind 127.0.0.1:8000. Confirmar OpenAPI info.version=0.3.0 e rotas triage/triage-attempts. O health deve ser complementado por GET real do chamado para conferir o destino persistido. A migração não acontece por requisição.

Homologação curta em [13-homologacao-us04.md](13-homologacao-us04.md); não repetir E01–E04 já aceitos. Retry e recuperação de tentativas expiradas são US05; não prometer que a API já recupera em_analise após interrupção. Docker Compose e CI remota permanecem pendentes.


## Atualização US05 — recuperação disponível, demonstração opcional

Sem nova migração, manter esquema 0003 e banco existente. Recarregar somente a API identificada deste projeto com a mesma DATABASE_URL demo, AI_MODE=simulated e bind 127.0.0.1:8000; OpenAPI info.version=0.4.0. Não criar banco novamente nem repetir POST/PATCH para validar a atualização. GET do chamado/histórico complementa health. Critérios de US05 e M02/no-op foram exercitados por automação em bancos isolados; não pedir repetição manual.

Para uso normal após falha, consultar GET para obter versão e decidir se solicita novamente POST triage. Em análise ainda no prazo: 409/triage_in_progress. Após prazo, POST com versão atual encerra anterior como execucao_expirada e adquire a seguinte atomicamente. Não há retry automático; não reiniciar nem limpar banco para destravar tentativa. Detalhes e limites em [validação US05](14-validacao-us05.md). US06 futura; Compose e CI remota pendentes.


## Atualização US06 — revisão e ciclo operacional

Reutilizar o cluster/banco existentes, aplicar somente `alembic upgrade head` (0004 aditiva: human_reviews e FK composta), comparar dados preexistentes e recarregar apenas a API identificada do projeto. Não executar initdb, createdb ou downgrade no demo. Mesmas variáveis DATABASE_URL e AI_MODE=simulated, bind 127.0.0.1:8000. Confirmar OpenAPI info.version=0.5.0 e reviews/resolve/reopen, health e GET real do chamado; GET reviews deve estar disponível sem criar revisão. Não alterar chamados para validar a atualização.

Critérios de US06 e pendências funcionais de US03 foram exercitados por automação em bancos isolados. [Demonstração opcional e rastreabilidade](15-validacao-us06.md); não é aceite manual obrigatório. Autor de revisão é declarado, sem autenticação. Docker Compose e CI no GitHub permanecem não executados até evidência própria; não inferir cobertura pelo caminho nativo.
