# US08 — evidências fora do banco descartável

Atualização de 10/11/2026: o [executor sequencial do lote](../scripts/us08_batch.py)
grava manifesto e um JSON por AVxx-Rn, somente com mocks. Limites de bytes,
reservas/contadores globais e exemplos após interrupção estão no
[plano atualizado](26-plano-24-avaliacoes-us08.md#travas-implementadas-no-executor-de-lote-somente-mocks).
O estado persistido exportado agora inclui também attempt_id e error_code nas falhas.
Consumo informado pelo provedor permanece no JSON do caso, separado de orçamento
reservado, bytes e estimativa de entrada não disponível. Execução real desabilitada.

O executor `scripts/us08_groq_pilot.py` agora salva, por chamado fictício, um
relatório JSON UTF-8 em `reports/us08/`, fora do PostgreSQL. O descarte do banco
não remove o relatório. A pasta é local e ignorada pelo Git.

## O que consultar para revisão humana

| Campo do relatório | Conteúdo e origem |
|---|---|
| `ticket_id`, `ticket.title`, `ticket.description` | Identificação e texto do chamado persistido antes da triagem |
| `suggestion.category`, `suggestion.priority` | Rótulos do JSON retornado pelo modelo, exportados após sucesso da validação existente |
| `suggestion.rationale`, `suggestion.missing_fields` | Valores originais do JSON, antes da normalização do domínio, sem reescrita pelo assistente |
| `result`, `persisted_state`, `attempt_id` quando há sucesso | Resultado e estado conferido antes do descarte |
| `requests[].usage` | Tokens de entrada, saída e total informados por cada resposta HTTP, inclusive quando uma saída posterior é inválida |
| `usage_totals` | Soma do consumo informado no sucesso; em falhas consultar as respostas disponíveis, sem assumir consumo ausente como zero |
| `database_discarded` | Confirmação do descarte do banco exclusivo |
| `evidence_kind` | Distingue `ensaio_automatizado_com_mocks` de `piloto_real` |

Somente quatro campos de sugestão são exportados; respostas inválidas não são
publicadas como sugestão (`suggestion=null`). Não são gravados credenciais, URLs
de conexão, cabeçalhos de autenticação, corpo HTTP completo ou mensagem de erro
remota. Metadados de erro continuam restritos a status/código/identificador
sanitizados. Não há retry nem mudança dos limites de requisições.

## Ensaio offline executado em 09/11/2026

Com `AI_MODE=simulated`, credencial fictícia e MockTransport, três casos chamaram
o próprio executor em PostgreSQL local exclusivo: sucesso, saída inválida e 429.
Os testes bloquearam HTTP externo e leitura da chave pelo executor. Após cada
execução, reabriram o JSON no disco e consultaram `pg_database` para confirmar
que o banco exclusivo já não existia. A fixture também removeu seu banco de
teste administrativo; o demo não foi acessado.

Arquivos locais produzidos e preservados:

- Sucesso: `reports/us08/mock-evidence-success-1194c9b62e20479c95176c602ae87f1a.json`.
- Inválida: `reports/us08/mock-evidence-invalid-b89ecf8b88ca448c96ae85eb3ffca3d5.json`.
- 429: `reports/us08/mock-evidence-quota-1240bbcbab7b4b1086d71888d128947c.json`.

No sucesso, a justificativa fictícia com acentos e espaços originais e a lista
`missing_fields=["ambiente","impacto"]` foram preservadas exatamente. Duas
respostas HTTP mockadas informaram 20 tokens entrada + 40 saída = 60 total.
Esses números são fixtures, não consumo real ou medição de qualidade de modelo.

Reproduzir somente o ensaio, com `TEST_DATABASE_URL` administrativo de testes
local `portfolio_test*` configurado e `AI_MODE=simulated`:

```powershell
.\.venv\Scripts\python.exe -m pytest tests/integration/test_groq_pilot_evidence.py -q
```

Cada ensaio gera nomes exclusivos de arquivos e bancos. O JUnit
`reports/us08-groq-evidence-retention.xml` registra os caminhos desta execução.
Não usar `--execute-approved` para reproduzir mocks: essa flag é de execução real,
e a autorização anterior continua consumida e bloqueada pelo ledger original.

Atualização da revisão do PR #1: o piloto avulso exige também `--confirmation`
atual com escopo `groq_single_pilot_once`, validada antes da leitura da chave ou
criação de recursos. Falha no DROP preserva sugestão/evidências e retorna erro
operacional 2, interrompendo a rodada. Detalhes e regressões offline em
[correções do PR #1](34-correcoes-revisao-pr1.md). Isso não autoriza novas chamadas.

## Limite histórico

O ledger real `reports/us08/groq-authorized-single-pilot.json` não foi alterado.
Sua justificativa e `missing_fields` não foram preservados antes do descarte e
continuam indisponíveis. O ajuste vale para execuções futuras autorizadas e para
o ensaio offline; não completa retrospectivamente a evidência do modelo real.
Revisão humana histórica em [24-revisao-humana-piloto-groq.md](24-revisao-humana-piloto-groq.md).
Lote real de 24 pausado, simulador local ativo, sem nova chamada real/commit/push.
