# Ambiente e compatibilidade

Revisão pré-publicação em 08/11/2026: versões instaladas relidas via importlib.metadata, sem instalar/atualizar pacotes. Python 3.12.6, pip 24.2, FastAPI 0.162.2, Starlette 1.10.0, Uvicorn 0.54.0, Pydantic 2.14.3, pydantic-settings 2.16.2, SQLAlchemy 2.0.57, Alembic 1.20.1, psycopg 3.3.8, pytest 9.2.0, HTTPX 0.28.1 e Ruff 0.17.4. PowerShell em uso: 5.1.26100.9818. Não é nova execução da suíte. Fontes oficiais de instalação conferidas para os READMEs: [Python para Windows](https://www.python.org/downloads/windows/), [PostgreSQL para Windows](https://www.postgresql.org/download/windows/), [Git para Windows](https://git-scm.com/downloads/win) e Docker no link abaixo. Não foram executados instaladores ou prometida compatibilidade de outros patches/SOs.

Revisão US07/US09 em 08/11/2026: locks mantidos e reinstalados em venv nova, pip check aprovado. Docker novamente ausente; configuração Compose não executada. Workflow revisado com PostgreSQL de serviço em Ubuntu, modo simulado e mesmo pipeline local; timeout limitado a 20 minutos para instalação/regressão, sem inferir execução remota. Fontes oficiais consultadas nesta revisão: [Docker Desktop no Windows e requisitos](https://docs.docker.com/desktop/setup/install/windows-install/) e [GitHub Actions com PostgreSQL de serviço](https://docs.github.com/en/actions/tutorials/use-containerized-services/create-postgresql-service-containers). As versões de actions existentes foram preservadas; a execução em GitHub/Linux continua pendente.

Verificação em 07/11/2026, sem alterações de configurações globais.

| Componente | Encontrado / decisão |
|---|---|
| Python | 3.12.6, usado em .venv exclusiva; projeto requer 3.12.x |
| pip | 24.2; mantido sem atualização global |
| Git | 2.46.2.windows.1; pasta inicialmente sem repositório |
| Docker / Compose | Comando docker ausente; configuração criada, execução pendente |
| PostgreSQL | Binários 16.4 em C:\Program Files\PostgreSQL\16\bin; serviço instalado parado e preservado |
| Banco dos testes | Cluster separado em .local/pgdata, bind 127.0.0.1:55432; não usar para dados reais |

Base escolhida: FastAPI/Pydantic 2, SQLAlchemy 2.0, Alembic, driver psycopg 3 binário, PostgreSQL 16, pytest/HTTPX. SQLAlchemy foi mantido em 2.0 (<2.1) para reduzir mudança de API nesta fundação. Psycopg binário evita instalar compilador/libpq global. Metadados dos pacotes resolvidos aceitam Python 3.12 e o conjunto foi instalado na .venv. Versões diretas e transitivas estão em `requirements.lock` (execução) e `requirements-dev.lock` (execução + testes/lint).

Fontes oficiais consultadas antes da configuração:

- [FastAPI: versões e fixação de dependências](https://fastapi.tiangolo.com/deployment/versions/).
- [SQLAlchemy 2.0: instalação e plataformas](https://docs.sqlalchemy.org/en/20/intro.html).
- [SQLAlchemy: dialeto psycopg](https://docs.sqlalchemy.org/en/20/dialects/postgresql.html#module-sqlalchemy.dialects.postgresql.psycopg).
- [Psycopg: instalação e pacote binário](https://www.psycopg.org/psycopg3/docs/basic/install.html).
- [Pydantic: documentação e validação](https://docs.pydantic.dev/latest/).
- [Alembic: instalação em ambiente virtual](https://alembic.sqlalchemy.org/en/latest/front.html).
- [PostgreSQL 16: initdb](https://www.postgresql.org/docs/16/app-initdb.html).
- [pytest: instalação e execução](https://docs.pytest.org/en/stable/getting-started.html).
- [HTTPX: transports, ASGI e rede](https://www.python-httpx.org/advanced/transports/).

Compatibilidade não é inferida apenas dessas páginas: `pip check`, migrações e suítes locais fornecem evidência do conjunto efetivamente instalado. Os locks fixam versões sem hashes; não são uma garantia de segurança nem substituem atualização controlada. Docker/CI usam a mesma série PostgreSQL 16, mas o patch da imagem varia; registrar versão efetiva ao validar esses ambientes.

Limitação conhecida: Starlette 1.10.0 emite aviso de depreciação do uso de HTTPX pelo TestClient. Os testes continuam funcionais com HTTPX 0.28.1; manter o aviso visível e avaliar migração de transporte na próxima atualização técnica. Não instalar HTTPX2 automaticamente nem confundir aviso com falha de teste.

O sandbox impediu a inicialização normal do PostgreSQL (token restrito) e a instalação de pacotes ficou sem progresso. Foram solicitadas execuções autorizadas fora do sandbox para inicializar o cluster isolado e instalar apenas na .venv; nenhum serviço global foi iniciado ou alterado. O comando de preparação do cluster deve ser executado no PowerShell do mesmo usuário que o inicializou.


US04 (08/11/2026): nenhuma dependência adicionada/atualizada ou configuração de versão alterada. Reutilizados os locks e fontes oficiais acima; versão da aplicação passa a 0.3.0. Sem SDK, tokenizer ou provedor externo. Pip check e execução de testes são registrados no andamento; esta atualização não representa instalação limpa ou execução Docker/CI.

US05 (08/11/2026): aplicação 0.4.0, mesmos locks/versões/fontes oficiais; nenhuma dependência instalada/reconfigurada e nenhuma migração nova. Teste HTTP de interrupção usa binário nativo CPython com PYTHONPATH dos mesmos pacotes da .venv para controlar o processo exato no Windows; não é evidência de Docker/Linux/CI remota.

US06 (08/11/2026): aplicação 0.5.0 e migração aditiva 0004 (human_reviews e FK composta para tentativa/chamado/revisão). Mesmos locks/versões/fontes oficiais, nenhuma dependência adicionada ou reconfigurada. Testes nativos não comprovam ambiente Docker/Linux/CI remota; pendências preservadas.
