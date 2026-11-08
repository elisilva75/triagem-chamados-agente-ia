# US06 — revisão humana, classificação final e ciclo operacional

Implementação autorizada por Eliana, com validação técnica automatizada em bancos isolados e demo preservado. Não há requisito de repetição manual; demonstração curta é opcional. Evidências e comandos realmente executados no [andamento](andamento.md). **Regressão: 173 passed, 1 warning, 292,88 s; zero falhas ou skips.** 94 unitários, 53 API/PostgreSQL, 24 integração e 2 HTTP/TCP. Ruff, formatação e dependências aprovados. IA exclusivamente simulada; a decisão final é informada pela pessoa na requisição, sem chamar provedor.

## Critérios e rastreabilidade

| História / critério / task | Código | Teste/evidência |
|---|---|---|
| US06-CA1/T1/T2 | application/reviews.py, rotas/schemas, models.HumanReview e migração 0004 | test_us06_ca1_ca3_review_correct_resolve_reopen_and_preserve_history: confirmar/corrigir categoria e prioridade, autor/motivo, GET por Location, resolver/reabrir preservando classificações e conteúdo |
| US06-CA2/T2 | ReviewCreate e guardas de estado | test_us06_ca2_pending_failure_suggested_cannot_resolve_without_review e test_us06_ca2_ca3_invalid_review_leaves_all_data_unchanged; estados em_analise reaproveitam test_us04_attempt_committed_and_no_connection_held_during_provider |
| US06-CA3/T2 | reason 10–500 e declared_reviewer 2–80 após trim; revisões append-only | test_us06_ca3_http_boundaries e testes unitários de schema, Unicode/trim, limites exatos e ±1; revisão subsequente cria outro ID e mantém anterior consultável |
| US06-CA4/T1/T2 | Lock de linha, expected_version e evento de estado na mesma transação | test_us06_ca4_version_guards_and_scoped_review_reads; test_us06_ca4_two_connections_one_version_wins com seis disputas, revisão/revisão, revisão/edição, resolver/resolver, resolver/edição, resolver/revisão, reabrir/reabrir |
| US03-CA1/CA3 integrado com US06 | edição preserva HumanReview/TriageAttempt e snapshot antes de limpar projeções | test_us03_ca1_archive_classification_and_preserve_history existente foi reaproveitado, substituindo só sua preparação sintética por POST cadastro/triagem/review reais; no-op com resposta inteira/timestamps preservados, edição invalida ambas as classificações, duas edições mantêm snapshot antigo e nova triagem/revisão usa nova revisão de conteúdo |
| US03-CA2 integrado com US06 | bloqueio de edição em resolvido/em_analise | teste de fluxo US06 verifica edição/no-op resolvido; teste existente de tentativa ativa verifica em_analise por fluxo real; fixtures anteriores mantidas para outros testes de rollback/concorrência |
| US06-T2 atomicidade/integridade | FK composta tentativa/chamado/revisão; validação da projeção final antes de resolver/revisar | test_us06_review_fk_and_current_projection_belong_to_same_content, rollback de review/projeção e de eventos resolve/reopen com CHECK real inválido em PostgreSQL |
| US06-T2 migração | 0004 aditiva | test_us06_migration_preserves_attempts_and_classification_snapshots; roundtrip e alembic check existentes reaproveitados; downgrade só em banco descartável |
| US06-T2 HTTP real | endpoints reais em Uvicorn/TCP | tests/e2e/test_http.py existente ampliado com revisão, resolução, bloqueio, reabertura e edição que invalida classificação final, mantendo review/tentativa |
| US06-T3 | README, contrato, ADR10, backlog e este documento | Regras, resultados, DoD local e pendências separados, sem nova exigência manual |

## Comportamento entregue

POST `/api/v1/tickets/{ticket_id}/reviews` recebe expected_version, category, priority, reason e declared_reviewer, sem extras. Exige aberto/sugerida ou aberto/revisada com sugestão válida da mesma tentativa bem-sucedida e revisão do conteúdo. Retorna 201 `{ticket,review}` e Location para GET da review. Uma correção é outra decisão explícita, com nova versão/ID e motivo, mesmo sem mudar todos os campos; repetir a requisição antiga recebe 409. A sugestão é preservada para comparação e classificação final aponta para a nova review.

GET reviews é paginado por created_at/id. GET de review pertencente a outro chamado retorna 404; isso valida o escopo do recurso, **não é autenticação**. declared_reviewer é texto declarado, sem prova de identidade. Motivo e autor são dados fictícios nos testes/demos.

POST resolve exige aberto/revisada e classificação final vinculada à HumanReview do próprio chamado/revisão. POST reopen exige resolvido/revisada e mantém classificação/sugestão/conteúdo. Cada operação válida incrementa version uma vez, sem mudar content_revision; escreve evento resolvido/reaberto junto com a alteração do chamado. Transição repetida ou versão antiga retorna 409, sem evento extra. Não há PATCH/DELETE de review nem atribuição direta de classificação pelo PATCH do chamado.

Edição efetiva de chamado aberto revisado invalida sugestão/final, volta a pendente, preserva review/tentativa e arquiva snapshot no evento editado. No-op revisado mantém tudo, inclusive timestamps e eventos. Resolvido não admite edição nem no-op; precisa reabrir primeiro. Recuperação/retry continuam conforme US05; revisão não aciona provedor.

## DoD e lacunas

Com a regressão executada e registrada no andamento, CA1–CA4/T1–T3 de US06 e CA1–CA3/T1–T3 de US03 estão atendidos no escopo funcional local; dependência de US06 encerrada por integração automatizada. Nenhuma captura histórica de resposta manual foi inventada. Infraestrutura não é aceite funcional presumido: US01/Compose e execução remota do CI continuam pendentes; não declarar Docker/Linux/CI aprovados por testes nativos.

Para encerrar o MVP simulado faltam a parcela de ambiente de US01 (Compose/persistência por reinício), completar/verificar US07 (pipeline completo, isolamento/falhas e evidências locais/remotas conforme autorização) e US09 (portfólio final, README PT/EN e ensaio completo do guia). US08 está adiada por D08 e não bloqueia o MVP exclusivamente simulado. Não iniciar essas histórias automaticamente nesta entrega de US06.

## Demonstração opcional

Se desejado, criar um chamado fictício separado, solicitar triagem, consultar a versão atual, revisar concordando ou corrigindo a sugestão, resolver, reabrir e editar. Consultar GET antes de cada escrita que exige expected_version e usar o valor efetivamente retornado. Observar review antiga no histórico após invalidação. Esses comportamentos já foram automatizados; não é tarefa pendente de Eliana nem motivo para repetir o demo existente.
