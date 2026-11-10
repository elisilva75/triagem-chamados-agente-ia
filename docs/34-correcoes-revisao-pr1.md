# Correções da revisão do PR #1 — US08

10/11/2026. Escopo: dois achados da revisão, apenas na branch
`feat/us08-avaliacao`. Sem chamadas reais, merge, deploy ou lote real de 24.
Simulador continua padrão; Groq permanece experimental e opcional.

## 1. DROP DATABASE após triagem bem-sucedida

`scripts/us08_groq_pilot.py` não confunde mais sucesso de triagem com sucesso
operacional. Se o descarte falhar, mantém `result=sucesso`, sugestão, uso,
requisições e estado persistido já coletado. Grava `database_discarded=false`,
`operational_status=cleanup_error` e `cleanup_error` sanitizado (tipo/errno/winerror,
sem mensagem ou credenciais). Retorna **2**, distinto da falha de triagem (1).
Não repete DROP, triagem ou envio. A evidência continua fora do banco descartável.

Rodada e batch copiam o estado operacional/erro de limpeza para o manifesto,
preservam o resultado da triagem e param com `database_cleanup_error` antes do
próximo caso. O CLI da rodada também retorna 2 nessa situação. Um caso pode ter
sugestão bem-sucedida e falha operacional: não interpretar só `status=sucesso`
como autorização para prosseguir. O nome do banco gerado permanece no relatório
para diagnóstico; não limpar bancos por prefixo nem excluir o demo.

Regressão `tests/integration/test_us08_pr_regressions.py`, parametrizada para
rodada e batch: PostgreSQL real exclusivo e HTTP mockado, falha injetada somente
no DROP do banco gerado pelo piloto. Confere três envios do primeiro caso, retorno
2, sugestão/evidência preservadas, manifesto interrompido e **zero envios dos
casos seguintes ao transporte**. Após retirar a injeção, o teste descarta apenas
o nome UUID que criou, validado por regex; nenhum banco demo é usado.

## 2. Confirmação no piloto avulso

`--execute-approved` exige `--confirmation CAMINHO_JSON`. O validador compartilhado
`scripts/us08_confirmation.py` é reutilizado pela rodada. No piloto avulso exige:

- `plan` exatamente `Livre`;
- `active` booleano true (não string nem número);
- `checked_on` igual ao dia da execução;
- `expires_on` posterior ao dia da execução (não aceitar o próprio dia);
- `scope` exatamente `groq_single_pilot_once`.

São declarações da conferência humana do painel e da validade nominal, não uma
consulta de autenticação feita usando a chave. Dados malformados/ausentes são
rejeitados. CLI e função de piloto avulso validam antes de criar relatório,
ler chave, criar banco ou instanciar provedor/transporte. O relatório conserva
somente campos normalizados de confirmação, sem copiar campos livres do arquivo.
O caminho interno da rodada com `approved_key` já passou pelo seu próprio
preflight antes de ler a chave; não usa a confirmação do piloto para ampliar
o escopo da rodada. Limites existentes e bloqueio do lote real de 24 preservados.

Estrutura ilustrativa **sem autorização real nesta entrega**:

```json
{
  "plan": "Livre",
  "active": true,
  "checked_on": "AAAA-MM-DD",
  "expires_on": "AAAA-MM-DD",
  "scope": "groq_single_pilot_once"
}
```

Não executar o comando real para validar a correção. Regressões unitárias
exercitam ausência de confirmação/arquivo, conferência desatualizada, validade
vencida/hoje, plano pago, chave inativa/tipo incorreto, datas inválidas e escopo
incorreto. O caminho válido chama o CLI com confirmação fictícia atual, chave
fictícia, PostgreSQL isolado e transporte HTTP mockado, sem leitura de chave real.

## Verificação

Regressões novas executadas: **14 passed**, um aviso conhecido TestClient/HTTPX,
28,14 s. Após estabilizar o código, pipeline completo offline: **348 passed**,
exit 0, sem falhas/erros/skips: 230 unitários (16,80 s), 116 PostgreSQL/API
(908,52 s) e 2 HTTP loopback (39,48 s). Pip check, Ruff check/format e
git diff --check aprovados. Aviso conhecido TestClient/HTTPX preservado.
Sem novas dependências, sem leitura/migração do demo ou chamadas reais.
Publicação e CI deste commit serão acompanhadas e registradas no andamento;
checks do commit anterior não equivalem aos desta correção. Docker Compose
continua sem validação.
