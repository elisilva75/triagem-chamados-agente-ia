# Ambiente e compatibilidade

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
