# Execução e validação local no Windows

Executar na raiz em PowerShell. Requisitos: Python 3.12.x, PostgreSQL 16 com ferramentas de linha de comando e Git. [Versões e fontes](09-ambiente-e-versoes.md). Somente dados fictícios, AI_MODE=simulated e loopback; não há autenticação.

## Instalação

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.lock
.\.venv\Scripts\python.exe -m pip check
.\scripts\start-test-postgres.ps1
```

Não é necessário ativar a venv nem alterar a política de execução global. O script reutiliza o cluster .local/pgdata se existir; inicializa somente diretório novo. Usa 127.0.0.1:55432 e banco administrativo portfolio_test, com credencial fictícia. Para outro caminho de instalação, passar -PgBin 'C:\caminho\PostgreSQL\16\bin'. Não inicia o serviço global nem limpa dados. Prefira checkout fora de pasta sincronizada.

O script deve ser executado pelo mesmo usuário que iniciou o cluster. No ensaio pelo Codex, o sandbox não conseguiu reconhecer o processo existente; a reexecução autorizada fora dessa restrição confirmou reutilização sem recriar dados. Uma falha de permissão não significa que o cluster esteja parado: conferir pg_isready/consulta real antes de tentar outra inicialização.

## Demonstração em banco separado

Em instalação nova, criar o banco abaixo **uma única vez**; se já existir, omitir createdb. Nunca apagar o demo para repetir o guia. Testes não devem apontar para ele.

```powershell
$env:PGPASSWORD = 'senha_ficticia_teste'
& 'C:\Program Files\PostgreSQL\16\bin\createdb.exe' -h 127.0.0.1 -p 55432 -U portfolio_test portfolio_chamados_demo
Remove-Item Env:PGPASSWORD
$env:DATABASE_URL = 'postgresql+psycopg://portfolio_test:senha_ficticia_teste@127.0.0.1:55432/portfolio_chamados_demo'
$env:AI_MODE = 'simulated'
.\.venv\Scripts\python.exe -m alembic upgrade head
.\.venv\Scripts\python.exe -m uvicorn app.main:create_app --factory --host 127.0.0.1 --port 8000 --no-access-log
```

Para ensaio independente, usar outro nome novo (exemplo portfolio_test_ensaio) em createdb e DATABASE_URL, e outra porta da API (18000). Preservar o servidor e o banco demo existentes. Head atual 0004, aplicação 0.5.0. Migração explícita, nunca por requisição; não aplicar downgrade no demo. Não encerrar processos pelo nome genérico Python.

Em outra janela, consultar /health e GET /api/v1/tickets em http://127.0.0.1:8000. Uma consulta real complementa health. Swagger /docs e OpenAPI /openapi.json. [Exemplos completos](16-demonstracao-e-portfolio.md), [contrato](05-api.md). Consultar GET antes de toda escrita em chamado existente para obter expected_version. Demonstração opcional; não repetir homologações antigas.

Ctrl+C encerra a API. Somente quando não houver API/testes usando o cluster, executar scripts/stop-test-postgres.ps1, que preserva os dados.

## Pipeline obrigatório local

```powershell
$env:TEST_DATABASE_URL = 'postgresql+psycopg://portfolio_test:senha_ficticia_teste@127.0.0.1:55432/portfolio_test'
$env:AI_MODE = 'simulated'
$env:APP_ENV = 'test'
.\.venv\Scripts\python.exe scripts/check_quality.py
```

Executa pip check, Ruff check/format, unitários, integração/API e HTTP real. Interrompe na primeira falha e rejeita suítes obrigatórias vazias/com skips. JUnit por camada em reports/, ignorado. Fixtures criam bancos únicos portfolio_test_<uuid>, migram do zero e removem somente o banco gerado. A URL administrativa é validada para loopback/prefixo de teste, nunca é limpa. Sem SQLite.

Execução parcial: Python da venv com -m pytest tests/unit -q. Fora do pipeline, sem TEST_DATABASE_URL os testes PostgreSQL são pulados: isso não comprova persistência. TestClient é HTTP dentro do processo; tests/e2e inicia Uvicorn separado e usa TCP e PostgreSQL reais, com espera limitada. CI usa o mesmo runner, PostgreSQL de serviço e modo simulado, sem chave de IA. Verificação local não equivale à execução de Actions no GitHub.

## Docker Compose — execução pendente

Docker não encontrado nesta máquina em 08/11/2026. Pré-requisito: Docker Desktop com mecanismo Linux ativo e Compose. Verificar docker version e docker compose version antes de continuar. Os comandos desta seção **não foram executados**.

O Compose usa volume próprio. A configuração padrão publica 127.0.0.1:5432 e 127.0.0.1:8000. Antes do ensaio, copiar compose.yaml para .local/compose-isolated.yaml, ajustar build para a raiz absoluta do projeto e trocar somente as portas publicadas para 15432 e 18000. Usar projeto exclusivo:

```powershell
docker compose -p portfolio-isolated -f .local/compose-isolated.yaml config --quiet
docker compose -p portfolio-isolated -f .local/compose-isolated.yaml up --build -d
docker compose -p portfolio-isolated -f .local/compose-isolated.yaml ps -a
```

Exigir migrate exited(0), health 200 e consulta real em 18000. Criar chamado fictício, guardar resposta, executar restart db api com os mesmos argumentos de projeto/arquivo, aguardar health e comparar GET completo. Depois down com os mesmos argumentos, **sem -v**. Não usar projeto/volume demo nem remover volumes. US01-CA1 e persistência Compose continuam pendentes até execução; ensaio nativo não os substitui.
