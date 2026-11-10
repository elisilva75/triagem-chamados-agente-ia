# US08 — AV08 com instruções revisadas, 10/11/2026

Executado uma única vez por autorização específica da mensagem atual, com
`openai/gpt-oss-20b` na Groq e `POLICY_VERSION=2`. Não é retomada da tentativa
original nem substituição de sua falha HTTP 429. A autorização desta execução
foi consumida; lote real de 24 continua pausado/desabilitado.

Antes da chave, conferida validade nominal: criada em 09/11/2026, expiração
16/11/2026, data atual 10/11/2026. Fonte: confirmação da usuária no mesmo dia de
chave ativa e organização Livre, complementada pelo relato posterior do painel.
Não houve nova consulta autenticada ao painel ou requisição de autenticação.
Metadados sem credencial em `reports/us08/av08-confirmation-2026-11-10.json`.

Perfil fixo `av08-revised`: somente `AV08-R1`, até três tentativas, em sequência,
16.384 bytes por corpo HTTP serializado, até 2.000 tokens de saída solicitados
por requisição, reserva antes do envio até 6.000 no total, zero retry. Parada
no primeiro erro, inclusive HTTP 429. Não há teto verificável de tokens de
entrada; consumo medido posteriormente. Diretório exclusivo impede repetição.

## Resultado e revisão humana — aceite registrado em 10/11/2026

Título exato: **AV08 repetição 1**.

Descrição exata: **Pedido de orientação sem bloqueio**.

Critérios preexistentes: categorias aceitas `outros` ou `duvida`; prioridade
esperada `baixa`. Sugestão válida no schema: **duvida / baixa**.

Justificativa original, literal:

> Chamado solicita orientação sem bloqueio. Classificado como dúvida (duvida). Sem impacto, então prioridade baixa. Nenhum campo adicional necessário, portanto missing_fields vazia.

`missing_fields`: **[]**.

Decisão humana de Eliana: **aceitos `duvida / baixa` e `missing_fields: []`**
nesta execução com instruções revisadas. A formulação sustentada pelo chamado é
**“sem bloqueio relatado”**. O aceite não transforma “Sem impacto” em fato:
a justificativa original acima permanece literal, com essa ressalva de qualidade.
Registro somente documental, sem alterar os JSON ou seu estado histórico de
revisão ainda não realizada no momento da captura.

Análise técnica separada: os rótulos estão entre os previstos e a lista vazia
é permitida. Contudo, “sem impacto” extrapola o relato “sem bloqueio”: ausência
de bloqueio não comprova ausência de impacto. A justificativa ainda apresenta
esse achado de qualidade apesar das instruções revisadas. O aceite humano foi
explícito nesta etapa; ele se refere somente à nova execução. O AV08-R1 original
continua falha HTTP 429 por `rate_limit_exceeded` da primeira rodada, fora dos
denominadores de concordância daquela rodada, sem substituição retroativa.

Rastro, em ordem: `consultar_categorias → allow`,
`consultar_politica_prioridade → allow`. Registra solicitações e permissões
individuais de contrato; separadamente o estado persistido registra duas
ferramentas e sucesso. Não comprova resistência integral à injeção.

## Requisições, limites e consumo

Três requisições HTTP 200, sem erro/retry. Corpos: 2.201, 3.836 e 7.567 bytes.
Reserva total: 6.000 tokens de saída solicitados. Uso retornado pela API:

| Requisição | Entrada | Saída | Total |
| --- | ---: | ---: | ---: |
| 1 | 459 | 261 | 720 |
| 2 | 519 | 480 | 999 |
| 3 | 816 | 692 | 1.508 |
| Total | 1.794 | 1.433 | 3.227 |

Os **3.227 tokens são os valores informados pelo executor**, com base no consumo
retornado pela API, e não uma medição de cobrança do painel.

Os cabeçalhos numéricos informaram `x-ratelimit-limit-requests=1000` e
`x-ratelimit-limit-tokens=8000`; restantes de requisições 994/993/992 e de tokens
7018/6412/5151. Não inferir a janela temporal a partir desses números isolados.
Registro restrito a esses nomes e valores numéricos, sem corpo de erro,
argumentos sensíveis ou autenticação. Nenhum ponto de falha/código de erro nesta
execução. Consumo conhecido completo das três respostas, separado das rodadas
anteriores. Cobrança posterior deste AV08 **não confirmada**: o relato anterior
“sem cobrança observada no plano Livre” e a projeção mensal de US$ 0,01 não
constituem medição posterior ou custo exclusivo desta nova execução.

## Evidências e verificações

Resultado integral preservado fora do banco em
`reports/us08/groq-av08-revised-2026-11-10/AV08-R1.json`; manifesto de escopo,
instruções revisadas e reservas em `manifest.json`. JSON contém justificativa
original, lista vazia, consumo por resposta, limites numéricos e estado
persistido. Banco exclusivo descartado, demo não acessado. Dez JSON originais
da R1 idênticos por SHA-256 antes/depois; AV08 original continua falha por
`rate_limit_exceeded`, fora dos denominadores da R1 original.

Antes de usar a chave, com HTTP mockado, credenciais fictícias e rede externa
bloqueada:

```text
python -m pytest tests/unit/test_groq_pilot.py tests/unit/test_us08_revalidation.py tests/unit/test_us08_batch.py tests/integration/test_us08_revalidation.py -q --junitxml=reports/us08-av08-preflight.xml
```

**27 passed**, zero falhas/erros/skips, 100,76 s; aviso conhecido TestClient/HTTPX.
Dois cenários novos de integração do perfil AV08: sucesso e 429 com parada,
evidências após remoção do banco e escopo/limites; teste existente do transporte
fortalecido para limites numéricos e descarte de valor não numérico. Reaproveitadas
travas de teto global/por caso, bytes, saída, orçamento, timeout e ausência de
retry. PostgreSQL descartável em todos os cenários de integração. Ruff global,
formatação dos quatro Python alterados e `git diff --check` aprovados.

Branch `feat/us08-avaliacao`; `.env` permanece `AI_MODE=simulated`, Groq somente
no processo isolado. Alterações locais, sem commit/push; nenhuma nova tentativa
ou lote autorizado por esta execução.
