# US05 — validação técnica automatizada e demonstração opcional

Eliana autorizou automação como caminho de validação; demonstração manual não é requisito para repetir cobertura. Resultados realmente executados estão no [andamento](andamento.md): foco M02/no-op 3 passed; US05 API 8 passed; recuperação/HTTP 3 passed; regressão completa **135 passed/1 warning, 224,88 s**, sem falhas ou skips. Ruff/formatação/pip check aprovados. Somente AI_MODE=simulated, bancos de teste exclusivos; nenhum POST/PATCH no demo.

| Critério | Teste/evidência |
|---|---|
| US05-CA1: timeout preserva chamado e retry pode obter sugestão | test_us05_ca1_retry_preserves_content_and_failed_attempt, parametrizado para timeout, indisponibilidade e saída inválida; conteúdo/revisão/criação preservados, versões 1→3→5 e primeira tentativa imutável |
| US05-CA2: no máximo um agente para requisições simultâneas | test_us05_ca2_two_simultaneous_retry_posts_run_one_agent: dois POSTs de retry com mesma versão, uma resposta 200 e outra 409; uma só nova tentativa. Validação de saída inválida reaproveita testes US04 |
| US05-CA3: prazo, reinício e resultado tardio | test_us05_ca3_finalization_deadline_boundary: 19,999/20/20,001 s; test_us05_ca3_late_result_cannot_overwrite_recovered_attempt: duas conexões, relógio controlado e resultado atrasado; test_us05_ca3_actual_process_interruption_restart_and_expiration: Uvicorn/TCP real, término real do processo, reinício e espera real do lease |
| US05-CA4: falha no banco ao finalizar, sem falso sucesso | test_us05_ca4_real_constraint_failure_rolls_back_finalization_then_recovers: violação real de CHECK, 503, em_analise preservado, bloqueio antes do prazo e recuperação após prazo |
| US05-T1/T2: recuperação e aquisição atômicas | test_us05_recovery_and_new_attempt_are_atomic: CHECK inválido na nova tentativa reverte também o encerramento da anterior; nova solicitação funciona após remover somente a injeção do teste |

Nenhum prazo é alterado diretamente no banco no ensaio HTTP de reinício. Nos testes de fronteira/atraso, o relógio é controlado no processo de teste; não há chave HTTP para modificar o relógio. Sem dependências ou migrações novas, esquema 0003.

## M02 e no-op de US04

Reaproveitados testes existentes, sem duplicação: test_us04_public_simulation_failure_marker cria ticket fictício, recebe 502/invalid_ai_response e confere conteúdo/versões/estado/ausência de classificação inválida/histórico. test_us04_ca1_real_suggestion_noop_edit_and_immutable_history confere igualdade integral antes/depois do no-op (incluindo timestamps), só evento criado, preservação de sugestão/tentativa e invalidação por edição. Integração test_us03_ca1_archive_classification_and_preserve_history também foi executada. É **validação técnica automatizada**, não homologação manual de Eliana.

O timestamp histórico do no-op manual anterior não é reconstruído por estes testes; essa limitação documental não exige repetir manualmente a regra funcional comprovada em banco isolado. Não solicitar a criação de outro chamado M02 no demo.

## Demonstração curta opcional

Se Eliana quiser demonstrar, usar Swagger local atualizado, consultar um chamado fictício em falha e sua versão, repetir POST triage e observar nova tentativa no histórico sem duplicar chamado. Uma saída determinística inválida pode falhar novamente; não prometer sucesso para a mesma fixture inválida. A recuperação após reinício já foi demonstrada automaticamente com processo real e banco isolado; não interromper o demo para repetir o ensaio.

## Lacunas preservadas

US03: integração pelo fluxo público com classificação final humana e estado resolvido depende de US06; regras já têm fixtures automatizadas. Sugestão, snapshots, no-op/timestamps e limites não exigem repetição manual. US04: critérios independentes atendidos por testes e relatos já registrados; M02 não é lacuna manual obrigatória. Sem avaliação de modelo real, pois US08 está adiada. Docker Compose e CI no GitHub seguem não executados; US01 parcialmente validada. US06 não iniciada. Sem custos, publicação ou deploy.
