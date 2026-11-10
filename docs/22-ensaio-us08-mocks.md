# US08 — ensaio automatizado com mocks

Validação local de 09/11/2026, branch `feat/us08-avaliacao`. **Não é avaliação de modelo real.** O SDK OpenAI e o adaptador Responses são reais; as respostas HTTP são produzidas por `httpx.MockTransport` em memória. Nenhuma requisição externa, chave válida ou custo é necessário. O SDK recebe somente um placeholder fictício já usado pelos testes. A chave local não é carregada para a avaliação; `AI_MODE=simulated` permanece no ambiente, e `.env` não é alterado. Demo e bancos dos dois pilotos reais são preservados.

## Cobertura reaproveitada

| Arquivo/casos existentes | O que verificam |
|---|---|
| `tests/unit/test_openai_provider.py` | SDK/adaptador com funções, correlação de call_id, saída estruturada, saída inválida/recusa/incompleta, timeout, HTTP 429, limites, configuração e TLS |
| `tests/unit/test_openai_diagnostics.py` | Registro técnico e ledger para insuficiência de cota, rate limit, campos ausentes/nulos, JSON inválido e sanitização; nenhuma retentativa |
| `tests/unit/test_us08_pilot.py` | Preparação sem chave/conexão, consumo fictício, budgets e interrupções; integração do transporte medido com o adaptador |
| Oito casos AV existentes em `tests/unit/test_agent.py` | Fixtures reproduzíveis AV01–AV08 do simulador; entradas/rótulos movidos sem alteração para `tests/agent_helpers.py` e compartilhados |
| `tests/integration/test_openai.py` | API da aplicação dentro do processo/PostgreSQL isolado: sucesso/revisão/resolução, inválido, timeout e 429 quota/rate/missing; chamado preservado, sem sugestão nas falhas, mesmo erro público sanitizado e ausência de retry; migração/histórico |
| `tests/integration/test_review_agreement.py` | SQL existente: amostra vazia, última correção por data/ID, prioridade divergente e exclusões de falhas/sem revisão/sugestão incompleta |

Os códigos `insufficient_quota` e `rate_limit_exceeded` usados nessa validação são **cenários simulados**. Não confirmam a causa do HTTP 429 do piloto real, que não preservou code/type. Os ledgers históricos não foram alterados.

## Único teste acrescentado

`tests/integration/test_mock_evaluation.py::test_24_fixture_evaluation_with_existing_sql` usa a fixture existente de banco descartável e o cliente de API, os oito casos AV compartilhados, helpers HTTP existentes e `scripts/triage_review_agreement.sql` **sem modificar a consulta**. São três repetições por AV01–AV08, totalizando 24 tentativas de triagem e 24 chamados fictícios rastreados.

O teste usa o adaptador OpenAI atrás da mesma interface; por isso os registros têm mode=openai. Esse valor identifica o adaptador, **não prova tráfego real**. O transporte HTTP real é bloqueado; cada sucesso é roteirizado como duas funções na primeira resposta e JSON estruturado na segunda. Todas as decisões gravadas na tabela human_reviews são fixtures identificadas como automação, sem representar revisão/aceite de Eliana.

| Controle roteirizado | Efeito esperado |
|---|---|
| AV08, repetições 1–3 | HTTP 429: insufficient_quota, rate_limit_exceeded e campos ausentes, respectivamente; três falhas, uma chamada por tentativa e nenhuma ferramenta/sugestão/revisão |
| AV07, repetição 3 | Sucesso sem revisão; excluído da concordância |
| AV01, repetição 1 | Categoria concordante, prioridade divergente |
| AV01, repetição 2 | Categoria divergente, prioridade concordante |
| AV01, repetição 3 | Categoria e prioridade divergentes |
| AV02, repetição 1 | Revisão inicialmente divergente nas duas dimensões, depois corrigida para concordar; ambos os registros preservados |
| Demais sucessos revisados | Concordância nas duas dimensões, conforme respostas/revisões fictícias |

## Resultado numérico controlado

24 tentativas = 21 sucessos + 3 falhas. Das 21 bem-sucedidas, uma não recebe revisão: **20 tentativas elegíveis**. São 45 requisições **mockadas** (21 × 2 + 3 × 1), 42 execuções de ferramentas locais e 21 registros de revisão para 20 tentativas revisadas, por causa da correção append-only.

| Consulta existente | Tentativas elegíveis | Categoria | Prioridade | Ambas |
|---|---:|---:|---:|---:|
| Antes da correção | 20 | 17 / 85,00% | 17 / 85,00% | 16 |
| Depois da correção | 20 | 18 / 90,00% | 18 / 90,00% | 17 |

A correção altera o numerador, mantendo denominador 20, e o histórico anterior permanece. A concordância simultânea final é 17/20; o SQL retorna sua contagem, não percentual. **Nenhum desses percentuais mede acurácia ou qualidade semântica de um LLM:** todas as sugestões e divergências foram construídas para verificar o cálculo. Não usar esse 90% como atendimento da meta de adequação semântica real.

JUnit em `reports/us08-24-mock-rehearsal.xml` inclui nome do banco exclusivo, identificação explícita de ensaio com mocks e manifesto com AV/repetição/ticket/attempt/status de cada uma das 24 execuções. O banco é removido pela fixture após o teste, sem limpar o banco administrativo. Relatórios ficam ignorados pelo Git. Resultados efetivamente executados, comandos, tempos e limites em [andamento](andamento.md).

## Pendências reais

Piloto e lote de 24 reais continuam pausados. Ainda dependem de autorização própria e condição de acesso/faturamento/limites da conta, geração real válida pelo modelo, consumo informado e custo medido, avaliação semântica dos casos e decisão humana registrada. Não há nova tentativa real nesta entrega; as falhas anteriores e seus custos desconhecidos não foram reinterpretados. Nenhuma mudança em código de produção, dependências, migrações ou CI para habilitar OpenAI. Tudo local, sem commit/push/deploy.
