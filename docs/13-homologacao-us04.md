# Homologação US04 — triagem exclusivamente simulada

**Aguardando execução/relato de Eliana.** Roteiro preparado, sem registrar aprovação manual. E01–E04 de US03 foram aceitos e não serão repetidos. Usar apenas dados fictícios em http://127.0.0.1:8000/docs (Ctrl+F5); API 0.3.0, PostgreSQL demo migrado para 0003 conforme evidências no andamento. US04 ainda não encerrada.

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

| Cenário | Estado | Evidência manual |
|---|---|---|
| M01 sugestão + no-op classificado + edição invalida sugestão e preserva tentativa | Aguardando Eliana | — |
| M02 saída inválida preserva chamado | Aguardando Eliana | — |

Informar HTTP, IDs, versões antes/depois, estado da sugestão e divergências. O agente não executará esses PATCH/POST no demo para presumir homologação manual. Testes automatizados usam bancos isolados e estão documentados no andamento.

Docker Compose e CI no GitHub continuam pendentes; US01 parcialmente validada. US03 mantém as pendências específicas não homologadas; revisão/resolução e classificação final dependem de US06. US05 não iniciada. AI_MODE=simulated, sem rede de IA, credenciais, custos, publicação ou deploy.

Preparação técnica concluída em 08/11/2026: API 0.3.0 e endpoints de leitura verificados, demo em 0003; chamado version/content_revision=2, 0 tentativas e 2 eventos preservados. Regressão automatizada final: 124 passed/1 warning, sem falhas ou skips; não é homologação manual.
