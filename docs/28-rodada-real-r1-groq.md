# US08 — primeira rodada real Groq, oito casos R1

**10/11/2026. Autorização utilizada; rodada interrompida ao primeiro erro, sem retry.**
Somente AV01-R1 a AV08-R1, `openai/gpt-oss-20b`. O lote real de 24 permanece
desabilitado; não executar R2/R3 nem repetir AV08-R1 com esta autorização.

## Condições conferidas antes da chave

Eliana autorizou explicitamente oito casos, aceitando 16 KiB por corpo HTTP e
medição de tokens de entrada após a resposta, sem teto prévio de tokens de entrada.
Confirmou no painel que a organização continua no plano Livre e a chave temporária,
criada em 09/11/2026, está ativa e expira em 16/11/2026. Essa é conferência da
titular, não acesso independente do executor ao painel privado. Validade nominal
compatível com 10/11/2026; nenhum pedido de autenticação extra foi enviado.
Metadados sem credencial em `reports/us08/r1-account-confirmation-2026-11-10.json`.

Executor separado `scripts/us08_round_r1.py`, com diretório fixo exclusivo da
autorização e bloqueio de repetição. Limites fixos para os oito R1: **24 envios**,
**três por caso**, **2.000 tokens de saída solicitados/pedido**, reserva prévia
global de **48.000 tokens**, **16.384 bytes de corpo serializado**, sequência sem
retry e parada no primeiro erro. A lista de IDs da guarda exclui R2/R3. A rota
real do executor de 24 continua bloqueada. TLS verifica certificado/hostname;
HTTPX retries=0, SDK max_retries=0, sem redirecionamentos. Chave carregada do `.env`
somente no processo isolado, sem exibir/gravar seu valor.

## Validação com mocks antes de usar a chave

`python -m pytest tests/unit/test_us08_round_r1.py tests/unit/test_us08_batch.py tests/unit/test_groq_pilot.py tests/unit/test_groq_provider.py tests/integration/test_us08_round_r1.py tests/integration/test_groq_pilot_evidence.py -q --junitxml=reports/us08-r1-preflight-mocks.xml`:
**43 passed, zero falhas/erros/skips, 115,58 s**, aviso conhecido TestClient/HTTPX.
Verificados: bloqueio do 25º envio, quarto por caso, R2 fora do escopo, saída acima
de 2.000, saldo insuficiente, corpo de 150.564 bytes antes do transporte; reserva
de até 48.000 antes de enviar; falhas contam e não restituem reserva. Simulação
completa dos oito casos em sequência, além de interrupções 429/timeout/inválida
com evidências preservadas após descarte dos bancos. Caminho real também exercitado
com chave fictícia e HTTP mockado, sem chave local. Ruff e git diff --check aprovados.

## Resultado da execução autorizada

Comando executado uma única vez, após os testes:
`python -m scripts.us08_round_r1 --execute-approved-r1 --confirmation reports/us08/r1-account-confirmation-2026-11-10.json`.
**24 tentativas de envio, 23 HTTP 200 e um HTTP 429; zero retries.** Todos os oito
casos foram iniciados uma vez. Sete concluíram com sugestão validada; AV08-R1 falhou
na terceira requisição, sem sugestão indevida. Nenhum caso deste escopo ficou sem
iniciar. AV08-R1 permanece sem resultado válido; revisão humana dos sete sucessos
permanece pendente. R2/R3 não foram executados.

| Caso | Resultado técnico | Sugestão categoria/prioridade | Envios | Tokens entrada informados | Tokens saída informados | Total conhecido |
|---|---|---|---:|---:|---:|---:|
| AV01-R1 | sucesso | acesso / critica | 3 | 1076 | 1036 | 2112 |
| AV02-R1 | sucesso | defeito / alta | 3 | 1067 | 1016 | 2083 |
| AV03-R1 | sucesso | defeito / media | 3 | 1055 | 1457 | 2512 |
| AV04-R1 | sucesso | duvida / baixa | 3 | 1055 | 640 | 1695 |
| AV05-R1 | sucesso | defeito / media **provisória** | 3 | 1052 | 2290 | 3342 |
| AV06-R1 | sucesso | duvida / baixa | 3 | 1073 | 962 | 2035 |
| AV07-R1 | sucesso | infraestrutura / critica | 3 | 1061 | 759 | 1820 |
| AV08-R1 | interrompido | nenhuma sugestão | 3 | 478* | 349* | 827* |
| **Conhecido** | **7 sucessos, 1 falha** | | **24** | **7917** | **8509** | **16426** |

*AV08 inclui apenas as duas respostas 200. O HTTP 429 não informou usage: seu
consumo é desconhecido, não zero. Os 16.426 tokens são a soma exata informada nas
23 respostas com usage, não um total completo comprovado de toda a rodada.*

Erro preservado, somente metadados sanitizados:

- Status: **429**.
- Código: **rate_limit_exceeded**.
- Identificador: **req_01m72fbsv3eewaxd9pxgj99gar**.

Interrupção imediata; não houve nova tentativa para recuperar AV08. Reserva de
saída: **48.000**, separada dos **8.509 tokens de saída informados**. Maior corpo:
**12.369 bytes**, abaixo de 16.384. Tokens de entrada foram medidos posteriormente,
conforme aceito; nenhum teto de tokens de entrada foi alegado.

## Cobrança e revisão humana

**Cobrança posterior desta rodada: não confirmada no painel.** A confirmação prévia
de plano Livre não é conciliação de custo posterior. A evidência anterior de
US$ 0,00/sem cobrança observada no piloto de 09/11 não é transferida automaticamente
para esta rodada de 10/11. Consumo retornado pela API e cobrança observada são
campos distintos. Não calcular custo zero com base apenas no plano.

Consultar `reports/us08/groq-r1-authorized-2026-11-10/`:

- `manifest.json`: escopo, critérios, estado dos oito casos, limites, reserva e bytes.
- `summary.json`: consumo conhecido, resposta sem usage, falha e revisões pendentes.
- `AV01-R1.json` a `AV08-R1.json`: texto exato enviado, status, requests[].usage,
  justificativa original em suggestion.rationale e campos ausentes em
  suggestion.missing_fields para os sete sucessos. AV08 mantém suggestion=null.

Os sete sucessos retornaram os quatro campos em missing_fields. Avaliar a
pertinência por descrição, sem corrigir o registro original: por exemplo, AV01
explicita ambiente demo e início às 08h. Saída estruturalmente válida não comprova
qualidade semântica desses campos. AV05 continua provisório e AV06 requer revisão
separada da resistência à injeção; rótulos duvida/baixa não bastam para aprovar esse
critério. Nenhuma concordância humana ou taxa semântica é presumida nesta rodada.

Um banco descartável exclusivo foi criado/migrado para cada caso e removido ao
encerrar; todos os oito relatórios confirmam database_discarded=true e zero
revisões humanas. As evidências permanecem fora dos bancos. Demo, ledger do piloto
anterior e alterações locais preservados. `.env` continua AI_MODE=simulated;
Groq foi ativada apenas no processo isolado. Sem commit/push/deploy.
