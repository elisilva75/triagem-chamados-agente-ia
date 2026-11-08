# Triagem Inteligente de Chamados

[English](README.en.md) · API local de portfólio, versão 0.5.0.

Portfólio de **Eliana Gomes da Silva**, Analista de Sistemas Sênior com experiência em QA, automação e desenvolvimento.

**Escopo aprovado — US01–US06 implementadas; IA exclusivamente simulada.** Revisão humana, classificação final, resolução e reabertura disponíveis. Critérios independentes de US02–US06 e integração de edição/classificação são verificados localmente; resultados e limites no andamento. PostgreSQL e migrações nativas verificados. Docker Compose e CI no GitHub permanecem pendentes; US01 não está totalmente validada.

O produto proposto registra chamados por API e usa um agente de IA para sugerir categoria, prioridade e informações ausentes. A pessoa revisora decide a classificação final. Falhas da IA preservam o chamado e permitem nova tentativa.

Nesta entrega estão disponíveis `/health`, criação/listagem em `/api/v1/tickets` e GET/PATCH `/api/v1/tickets/{ticket_id}`, POST `/api/v1/tickets/{ticket_id}/triage` e GET `/api/v1/tickets/{ticket_id}/triage-attempts`, além de `/docs` e `/openapi.json`. PATCH exige expected_version; edição efetiva invalida classificação e preserva seu snapshot no histórico. Triagem simulada, retry explícito, recuperação por prazo, POST/GET de reviews e POST resolve/reopen disponíveis. Decisão final exige categoria/prioridade, motivo e autor declarado; sem autenticação. Cadastro/edição não chamam IA; `AI_MODE` aceita somente `simulated`.

Para executar e testar no Windows, seguir o [guia de validação local](docs/10-validacao-local.md), que oferece PostgreSQL nativo e a configuração Compose ainda não executada. Requisitos e versões em [ambiente](docs/09-ambiente-e-versoes.md). Usar exclusivamente dados fictícios em loopback; sem autenticação, não disponibilizar publicamente.

## Documentação

- [Visão, escopo e decisões para revisão](docs/01-produto.md)
- [Fluxos, regras e requisitos não funcionais](docs/02-regras-e-fluxos.md)
- [Backlog, critérios de aceite e tasks](docs/03-backlog.md)
- [Arquitetura e modelo de dados](docs/04-arquitetura.md)
- [Contrato inicial da API](docs/05-api.md)
- [Testes e avaliação do agente](docs/06-testes.md)
- [Entregas, riscos e definições de qualidade](docs/07-entregas.md)
- [Andamento e continuidade](docs/andamento.md)
- [Decisões aprovadas D01–D08](docs/08-decisoes-aprovadas.md)
- [Ambiente e compatibilidade](docs/09-ambiente-e-versoes.md)
- [Execução, testes e validação no Windows](docs/10-validacao-local.md)
- [Homologação informada de US01/US02](docs/11-homologacao-us01-us02.md)
- [Roteiro e resultados de homologação de US03](docs/12-homologacao-us03.md)
- [Registro US04: relatos manuais e validação técnica automatizada](docs/13-homologacao-us04.md)
- [Validação técnica de US05 e demonstração opcional](docs/14-validacao-us05.md)
- [Validação integrada US06/US03, DoD e demonstração opcional](docs/15-validacao-us06.md)

## Base técnica proposta

Python 3.12, FastAPI, PostgreSQL 16, SQLAlchemy 2.0, Alembic, Pydantic 2, pytest, HTTPX, Docker Compose, GitHub Actions e OpenAPI/Swagger. Compatibilidade consultada em fontes oficiais antes da configuração; versões exatas fixadas em requirements.lock e requirements-dev.lock. Evidências e limitações em docs/andamento.md.

O agente simulado usa roteiros reproduzíveis, duas ferramentas locais somente leitura e validação estrita; não interpreta texto com um modelo real. Sem credenciais de IA. A integração real está adiada por decisão de Eliana; não há SDK de provedor nem chamada paga. O acesso ao Codex não fornece credenciais nem saldo à aplicação.

Somente dados fictícios. Não publicar, fazer deploy ou contratar serviços sem autorização. O MVP proposto será local, sem autenticação; não está previsto uso público nessa configuração.

## Instalação e testes

Requisitos: Python 3.12.x, PostgreSQL 16 e Git. Na raiz, em PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.lock
.\scripts\start-test-postgres.ps1
$env:AI_MODE = 'simulated'
$env:APP_ENV = 'test'
.\.venv\Scripts\python.exe scripts/check_quality.py
```

O script PostgreSQL define TEST_DATABASE_URL na sessão. O pipeline cria bancos exclusivos, não limpa o banco recebido e bloqueia falhas/skips obrigatórios. Relatórios JUnit ficam em reports/, ignorado pelo Git. Para iniciar API, criar banco de demonstração **somente se ainda não existir**, definir DATABASE_URL, aplicar `alembic upgrade head` e iniciar Uvicorn em loopback: comandos completos no [guia Windows](docs/10-validacao-local.md). Health deve ser complementado por GET real. Não executar downgrade nem limpar o demo.

## Demonstração e portfólio

[Roteiro curto, corpos das requisições e descrição do projeto](docs/16-demonstracao-e-portfolio.md). A demonstração é opcional; verificações automatizadas não são homologação manual de Eliana. O desenvolvimento teve assistência de IA para implementação, testes e documentação, sob decisões de produto e revisão de Eliana. Essa assistência é distinta do simulador da aplicação.

## Pendências de entrega

Não repetir E01–E04, M02 ou no-op já cobertos. Integração de US03 com classificação final/resolvido coberta por US06; sem gate manual obrigatório. US01 continua dependente de execução Compose (Docker indisponível). A revisão e execução locais de US07 e o ensaio/documentação de US09 têm evidências em [andamento](docs/andamento.md); CI remota permanece pendente e não é inferida dos testes locais. US08 adiada não bloqueia o MVP simulado. Nenhuma publicação ou deploy autorizado nesta entrega.
