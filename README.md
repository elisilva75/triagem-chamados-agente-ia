# Triagem Inteligente de Chamados

Portfólio de **Eliana Gomes da Silva**, Analista de Sistemas Sênior com experiência em QA, automação e desenvolvimento.

**Escopo aprovado — US01–US03 implementadas.** Cadastro/consulta com homologação manual informada por Eliana; edição com controle de versão implementada e aguardando sua validação. PostgreSQL e migrações nativas verificados. Docker Compose e CI no GitHub permanecem pendentes; US01 não está totalmente validada.

O produto proposto registra chamados por API e usa um agente de IA para sugerir categoria, prioridade e informações ausentes. A pessoa revisora decide a classificação final. Falhas da IA preservam o chamado e permitem nova tentativa.

Nesta entrega estão disponíveis `/health`, criação/listagem em `/api/v1/tickets` e GET/PATCH `/api/v1/tickets/{ticket_id}`, além de `/docs` e `/openapi.json`. PATCH exige expected_version; edição efetiva invalida classificação e preserva seu snapshot no histórico. Triagem, revisão e resolução continuam planejadas. Cadastro/edição não chamam IA; `AI_MODE` aceita somente `simulated`.

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

## Base técnica proposta

Python 3.12, FastAPI, PostgreSQL 16, SQLAlchemy 2.0, Alembic, Pydantic 2, pytest, HTTPX, Docker Compose, GitHub Actions e OpenAPI/Swagger. Compatibilidade consultada em fontes oficiais antes da configuração; versões exatas fixadas em requirements.lock e requirements-dev.lock. Evidências e limitações em docs/andamento.md.

O modo simulado será padrão, reproduzível e sem credenciais de IA quando a triagem for implementada em US04. A integração real está adiada por decisão de Eliana; não há SDK de provedor nem chamada paga. O acesso ao Codex não fornece credenciais nem saldo à aplicação.

Somente dados fictícios. Não publicar, fazer deploy ou contratar serviços sem autorização. O MVP proposto será local, sem autenticação; não está previsto uso público nessa configuração.

## Próximo passo

Eliana valida US03 conforme o roteiro. Aguardar essa validação antes de US04. Pendências de US01/Compose e CI remota preservadas. US08 adiada; README em inglês e roteiro completo permanecem para US09.
