# US08 — campos a verificar e rastro mínimo de ferramentas

**10/11/2026. Alteração validada somente offline, sem nova avaliação real.**
Política de triagem versão **2** para distinguir as instruções futuras da versão
usada na rodada R1. Prioridades/categorias e o array expected_fields não mudaram.

## Critério explicitado

expected_fields é uma lista de **campos a verificar**, não uma lista de ausentes.
missing_fields contém somente campos **aplicáveis** cuja informação ainda falta:

- **Ausente:** incluir se o campo é aplicável à triagem.
- **Parcial:** reconhecer o que foi informado. Incluir somente se faltar complemento
  indispensável à triagem, explicando na justificativa qual parte falta; não tratar
  informação incompleta como ausência total.
- **Não aplicável:** não incluir. Uma dúvida de uso sem incidente não exige passos
  de reprodução de falha ou horário de início de incidente.
- A lista pode ser vazia. Sem bloqueio informa impacto, mas não prova que não há
  qualquer impacto no serviço.

A mesma orientação curta consta da mensagem de sistema em run_agent, da descrição
da ferramenta consultar_politica_prioridade enviada ao modelo e do retorno da
ferramenta em expected_fields_guidance. Usa uma constante compartilhada para evitar
divergência. O schema continua permitindo listas vazias, parciais e completas,
com os quatro nomes conhecidos, sem preenchimento automático. Não foi acrescentado
um detector determinístico que infira semanticamente quais dados faltam.

## Exemplos offline com as entradas existentes

Listas abaixo são referências de teste roteirizadas, não novas respostas da Groq
nem correção dos JSON históricos:

| Caso | Informação já disponível / aplicabilidade | Lista usada no mock |
|---|---|---|
| AV01 | Ambiente demo, início às 08h e impacto coletivo explícitos; faltam passos para reproduzir o incidente | passos_reproducao |
| AV04 | Dúvida de uso sem bloqueio; sem incidente que exija início/reprodução; não inventar necessidade técnica para preencher lista | vazia |
| AV05 | Demonstração é contexto genérico; ambiente técnico, passos, impacto e início insuficientes/ausentes | ambiente, passos_reproducao, impacto, inicio_ocorrencia |
| AV07 | Rede indisponível para todos em serviço essencial, sem alternativa já informa impacto; demais dados não explicitados | ambiente, passos_reproducao, inicio_ocorrencia |

Se detalhes adicionais de um campo parcial não forem indispensáveis à triagem,
não incluir o campo só porque seria possível perguntar mais. A pertinência dessas
escolhas continua sendo objeto de avaliação humana e do comportamento do modelo.
AV05 mantém prioridade media provisória; rótulos e critérios prévios preservados.

## O que os mocks verificam

`tests/unit/test_missing_fields_instructions.py` passa AV01/04/05/07 pelo
orquestrador, SDK, adaptador Groq e transporte em memória. Confere o conteúdo de
system, descrição da ferramenta e seu resultado efetivamente enviado na etapa
final. A lista retornada pelo mock é preservada em captura e validação. Os testes
de proveniência existentes não foram substituídos: listas vazia/parcial/completa
continuam aceitas e propriedade ausente continua rejeitada sem default.

Mocks comprovam montagem do payload, validação e preservação dos valores
roteirizados. **Não comprovam que o modelo entendeu ou melhorou missing_fields.**
Uma futura execução real autorizada teria de medir, por campo/caso, informação
presente indevidamente marcada ausente, lacuna aplicável omitida, inclusão de campo
não aplicável, pertinência de complementos em informação parcial e coerência da
justificativa. Comparar com a linha de base R1 sem sobrescrever evidências ou
presumir causalidade; registrar prompt/política versão 2, consumo e cobrança
separadamente. Não há autorização de nova chamada nesta entrega.

## AV06 — registro mínimo disponível para avaliações futuras

O adaptador admite observador opcional on_tool_decision. Para cada function_call,
na ordem em que é recebido, emite **somente name e decision (allow/block)**,
conforme validação do nome e do contrato de argumentos vazios. Rejeição de JSON
de argumentos também é block, sem registrar seu conteúdo. O executor salva a
sequência em tool_decisions no JSON externo ao banco, antes de prosseguir.

Por segurança, só nomes conhecidos das duas ferramentas e o marcador shell são
gravados literalmente. Outros nomes remotos viram [redacted], para não registrar
credenciais/texto arbitrário colocado no nome. Nunca gravar argumentos, cabeçalhos,
chaves, IDs de chamada ou corpo bruto nesse rastro.

**Escopo:** tool_decisions_scope=provider_function_contract_not_execution.
Allow significa contrato individual permitido, não prova execução: limites globais,
prazo, resposta mista ou outros problemas de protocolo podem impedir a execução
posterior. Contadores/erros do orquestrador e revisão da resposta final continuam
necessários. O rastro ajuda a distinguir solicitação hostil bloqueada de ausência
de solicitação hostil, mas não certifica sozinho resistência integral à injeção.

Mocks verificam sequência allow/block, shell bloqueado, argumentos proibidos ou
malformados bloqueados, nome desconhecido ocultado e ausência de valores privados.
Integração com PostgreSQL descartável verifica persistência do rastro depois da
remoção do banco. O callback é opcional e não altera o schema público da aplicação.

**Histórico preservado:** os dez JSON da rodada R1 permanecem idênticos por SHA-256.
Não lhes foram acrescentados rastros retrospectivos. A resistência integral do
AV06-R1 continua inconclusiva. Concordâncias humanas 7/7, 6/6 e 1/1 provisória
continuam como registradas; consumo parcial e cobrança não confirmada também.
Demo preservado, AI_MODE=simulated, lote pausado/desabilitado, sem commit/push.

## Verificações executadas

Regressão: `python -m pytest tests/unit tests/integration/test_groq_pilot_evidence.py -q --junitxml=reports/us08-field-instructions-offline.xml`:
**210 passed, zero falhas/erros/skips, 52,52 s**.

Verificação final: `python -m pytest tests/unit/test_missing_fields_instructions.py tests/unit/test_missing_fields_provenance.py tests/unit/test_openai_provider.py tests/unit/test_groq_provider.py tests/integration/test_groq_pilot_evidence.py -q --junitxml=reports/us08-field-instructions-final.xml`:
**47 passed, zero falhas/erros/skips, 28,95 s**. São casos reexecutados, não 47
novos além dos 210. Oito casos novos cobrem quatro exemplos e quatro decisões
bloqueadas/privacidade. Três integrações existentes foram fortalecidas para conferir
persistência da sequência e seu escopo depois do descarte do banco.
Aviso conhecido TestClient/HTTPX mantido nas duas execuções.

Chaves removidas do processo de teste, AI_MODE=simulated e TEST_DATABASE_URL
administrativo local de teste; apenas bancos exclusivos portfolio_test_* criados
e removidos. Ruff global, format dos seis arquivos Python tocados e
git diff --check aprovados. Dez JSON originais comparados por SHA-256, sem mudança.
