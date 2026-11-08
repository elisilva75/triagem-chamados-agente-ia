# Homologação US04 — triagem exclusivamente simulada

**M01a–M01c com homologação manual informada por Eliana; M02/no-op validados por automação isolada.** Alcance e limitações no complemento ao final. E01–E04 de US03 foram aceitos e não serão repetidos. Usar apenas dados fictícios em http://127.0.0.1:8000/docs (Ctrl+F5); API 0.3.0, PostgreSQL demo migrado para 0003 conforme evidências no andamento. Critérios independentes atendidos; demonstração manual adicional opcional, sem bloquear US05.

## M01 — sugestão e invalidação por edição (US04-CA1/CA4; pendências específicas US03)

1. GET `/api/v1/tickets/ad903cac-a750-48d3-b205-91da97d7adee`: esperado 200. Copiar title, description, version/content_revision, timestamps. Última versão técnica é 2, mas usar a resposta atual. O chamado deve estar aberto/pendente.
2. POST `/api/v1/tickets/{ticket_id}/triage` → Try it out, mesmo ID, corpo `{"expected_version":2}` (adaptar à versão consultada). Esperado **200**, ticket aberto/sugerida, suggestion.mode=simulated, category=defeito, priority=media provisória e impacto entre missing_fields para o texto atual sem alcance informado. final_classification=null; content_revision mantida; version avança duas vezes (2→4 se não houver alteração intermediária). attempt.status=sucesso, model_calls=3, tool_calls=2, versões de catálogo/política=1. GET do chamado deve confirmar a resposta. Usar sempre a versão retornada, não cálculo fixo.
3. Para cobrir a pendência específica de no-op **com sugestão não nula**, PATCH com a versão retornada e title exatamente igual ao GET, envolto em dois espaços. Esperado 200 com resposta integral preservada, inclusive sugestão, versões e timestamps. Esse caso classificado é novo; não repetir o antigo E03 sem classificação.
4. PATCH com a mesma versão atual e `description="Descrição corrigida após sugestão simulada: no ambiente fictício, três usuários ficam bloqueados ao salvar, sem alternativa."`. Esperado **200**, suggestion/final_classification=null, triage_status=pendente, version e content_revision +1; GET confirma. GET `/api/v1/tickets/{ticket_id}/triage-attempts`: esperado 200, tentativa anterior sucesso e sugestão preservada. Snapshot no evento pode ser conferido pelo agente em SQL somente leitura após seu relato (não existe endpoint de eventos).

Não há classificação final humana nesta história; sua invalidação depende de US06. Preservação após múltiplas edições permanece com evidência automatizada e pendência manual registrada; não repetir edições extras neste roteiro curto.

## M02 — saída inválida não vira sugestão (US04-CA2)

1. POST `/api/v1/tickets` com:

```json
{
  "title": "[SIMULADO:saida-invalida]",
  "description": "Dados fictícios para demonstrar a rejeição de saída inválida do simulador."
}
```

Esperado 201; guardar ID e version. O título exato seleciona uma fixture explícita de demonstração local; não é uma instrução enviada a um modelo real. Esta criação é necessária para produzir a falha, sem repetir a homologação geral de cadastro.

2. POST `/api/v1/tickets/{novo_id}/triage` com `{"expected_version":1}` (versão retornada). Esperado **502/invalid_ai_response**, request_id e contexto da tentativa em error.details.
3. GET do novo chamado: **200**, conteúdo preservado, triage_status=falha, suggestion/final_classification=null, content_revision mantida; version avança duas vezes. GET de triage-attempts: tentativa falha, error_code=invalid_ai_response, sem saída bruta nem sugestão. **Não testar retry nesta etapa:** recuperação de falha é US05, ainda não iniciada.

## Registro

| Cenário | Estado | Evidência e origem |
|---|---|---|
| M01a geração de sugestão | Homologação manual informada por Eliana em 08/11/2026 | POST 200; GET confirmou simulated/defeito/media, sugerida, versões 4/2 |
| M01b no-op com sugestão existente | Homologação manual informada no alcance do relato em 08/11/2026 | PATCH 200, sugestão e versões 4/2 preservadas; timestamp intermediário não informado nem recuperável após edição posterior. SQL sem evento extra |
| M01c edição invalida sugestão e preserva histórico | Homologação manual informada por Eliana em 08/11/2026, com conferência técnica adicional | PATCH 200, versões 5/3, pendente, classificações nulas. GET/SQL confirmam persistência; tentativa e snapshot íntegros |
| M02 saída inválida preserva chamado | Validação técnica automatizada em 08/11/2026; não é homologação manual | Teste existente do marcador ampliado e executado: 502/invalid_ai_response, chamado preservado, versão/revisão 3/1, tentativa falha, sem classificação inválida e só evento criado |

Informar HTTP, IDs, versões antes/depois, estado da sugestão e divergências. O agente não executará esses PATCH/POST no demo para presumir homologação manual. Testes automatizados usam bancos isolados e estão documentados no andamento.

Docker Compose e CI no GitHub continuam pendentes; US01 parcialmente validada. US03 mantém as pendências específicas não homologadas; revisão/resolução e classificação final dependem de US06. US05 não iniciada. AI_MODE=simulated, sem rede de IA, credenciais, custos, publicação ou deploy.

Preparação técnica concluída em 08/11/2026: API 0.3.0 e endpoints de leitura verificados, demo em 0003; chamado version/content_revision=2, 0 tentativas e 2 eventos preservados. Regressão automatizada final: 124 passed/1 warning, sem falhas ou skips; não é homologação manual.

Condução guiada iniciada: apresentar somente M01a, com expected_version=2 obtida em GET real nesta etapa. POST não executado pelo agente. Aguardar resultado informado por Eliana; consultar versão atual novamente antes de orientar cada próximo PATCH/POST com expected_version.


### 08/11/2026 — M01a–M01c informados; edição e histórico conferidos

Homologação manual informada por Eliana, registrada sem duplicação: M01a POST triage expected_version=2 retornou 200 e GET confirmou simulated/defeito/media, sugerida, version=4/content_revision=2. M01b PATCH com título idêntico e espaços retornou 200 preservando sugestão e versões 4/2. M01c PATCH de descrição expected_version=4 retornou 200, version=5/content_revision=3, pendente, suggestion/final_classification=null. O agente não observou visualmente nem reexecutou essas ações.

Verificação técnica somente leitura via HTTPX: GET do chamado e de triage-attempts retornaram 200. Descrição persistida: “No ambiente fictício, o erro ao salvar o cadastro afeta todos os usuários e começou nesta manhã.” Texto obtido pelo agente, não atribuído ao relato integral de Eliana. PostgreSQL via psycopg, `SET TRANSACTION READ ONLY; SHOW transaction_read_only` (on), SELECT de tickets/triage_attempts/ticket_events, confirmação transacional sem escrita: **saída 0**. Chamado ad903cac-a750-48d3-b205-91da97d7adee version=5/revisão=3, aberto/pendente, classificações atuais nulas. Uma tentativa, b7b11f7f-1565-4ac4-b39a-6bf77a3669cf, sucesso/simulated, revisão 2, defeito/media, 3 chamadas de modelo/2 ferramentas, sugestão preservada.

**Exatamente três eventos:** criado/revisão 1, editado/revisão 2, editado/revisão 3. Os dois primeiros foram comparados integralmente com `.local/demo-us04-preservation.json` e estão idênticos, incluindo timestamps e snapshot antigo. O novo snapshot tem content_revision=2, final_classification=null e suggestion **integralmente igual** à tentativa anterior. Não há evento adicional para o no-op no estado observado. Nenhum dado alterado ou processo reconfigurado pelo agente; nenhuma nova suíte de aplicação executada.

Timestamps conferidos (UTC): created_at do chamado 2026-11-07T21:23:24.789820Z; updated_at atual 2026-11-08T15:35:04.358424Z; novo evento 2026-11-08T15:35:04.357654Z. Finalização da tentativa 2026-11-08T15:31:17.781295Z, valor que a implementação usa para updated_at da finalização. **Não há captura persistida de resposta imediatamente antes/depois do no-op**: após a edição seguinte, o timestamp intermediário não pode ser comprovado retrospectivamente pelo estado atual. Eliana não informou esse campo no relato do no-op; não registrá-lo como homologado nem inferir igualdade a partir de finished_at. A preservação de timestamp no no-op tem evidência automatizada anterior; não repetir o cenário para criar evidência histórica artificial.

Próximo: M02 saída simulada inválida. **Somente orientar criação de chamado fictício separado**, título exato `[SIMULADO:saida-invalida]`, conforme roteiro; preservar chamado existente. AI_MODE continua simulated: seleção por título é local à requisição, não muda configuração global/arquivo/serviço e não requer restauração posterior. Chamados com títulos comuns continuam no roteiro normal; manter o registro de falha como evidência, sem apagar/renomear. Aguardar ID/resultado da criação; consultar GET para obter versão antes de orientar POST de triagem do novo chamado. M02 não executado pelo agente nem homologado.

US03: no-op com sugestão e invalidação/preservação de sugestão agora informados manualmente e conferidos tecnicamente no alcance descrito; classificação final/resolvido continuam dependentes de US06. Não encerrar a história nem presumir os demais campos/snapshots não homologados. US04 mantém M02 pendente; US05 não iniciada. Docker Compose e CI no GitHub pendentes, US01 parcialmente validada. Sem chamadas pagas, publicação ou deploy.


### Estratégia atual de aceite — automação, 08/11/2026

Por instrução de Eliana, M02 e o no-op classificado foram executados nos testes existentes em bancos isolados: 3 passed/1 warning, incluindo integração de snapshots. Timestamp/versões/sugestão preservados pelo no-op e ausência de evento extra verificados automaticamente. Não solicitar repetição manual; demonstração de M02 é opcional. M01 mantém a origem manual de seus relatos; M02 é exclusivamente validação técnica automatizada. Critérios independentes de US04 atendidos, continuidade para US05 autorizada; dependências de US06 e pendências Compose/CI mantidas.


US06 implementada e validada automaticamente: classificação final/revisão/resolução agora disponíveis; dependência funcional da edição com esses dados coberta pelo teste existente de US03 reaproveitado. US04 não exige repetição manual de M01/M02/no-op. Consultar [DoD e validação US06](15-validacao-us06.md); Compose/CI continuam pendentes.
