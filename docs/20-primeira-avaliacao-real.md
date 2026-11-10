# Proposta da primeira avaliação real — US08

**Estado posterior:** o único piloto autorizado foi executado e interrompido na conexão, sem retry ou usage. [Resultado e pendências](21-resultado-piloto-us08.md). Os comandos de execução abaixo são históricos; não repeti-los com base na autorização já utilizada. Conciliar consumo e obter nova autorização antes de outra tentativa. As 24 continuam não autorizadas.

## Autorização posterior — 09/11/2026

Eliana autorizou um único chamado fictício, uma tentativa de triagem no `gpt-6-luna`, até três requisições, com orçamento de referência de **USD 0,01**, sem teto de cobrança garantido. **As 24 execuções não foram autorizadas.** O texto abaixo preserva a proposta inicial, inclusive seus valores anteriores, como histórico; prevalece esta autorização. Executor ajustado para piloto sem orçamento de lote. Comando autorizado, a usar apenas quando a chave estiver configurada localmente:

```powershell
$env:AI_MODE = 'simulated'
$env:APP_ENV = 'test'
$env:TEST_DATABASE_URL = 'postgresql+psycopg://portfolio_test:senha_ficticia_teste@127.0.0.1:55432/portfolio_test'
.\.venv\Scripts\python.exe -m scripts.us08_pilot --execute-approved --model gpt-6-luna --pilot-budget-usd 0.01
```

A chave pode estar em `OPENAI_API_KEY` no ambiente do processo ou no `.env` local ignorado pelo Git. Não a enviar na conversa; manter `AI_MODE=simulated`. O runner lê a chave somente no caminho de execução explícita. Se faltar, nenhum banco ou request é criado. A revisão humana continua pendente de decisão explícita de Eliana; não registrar uma decisão automática como revisão humana.

Preparação em **09/11/2026**, branch local `feat/us08-avaliacao`, para revisão de Eliana Gomes da Silva. **Nenhuma chamada real autorizada ou executada nesta etapa.** Simulação permanece padrão; chave não solicitada, lida ou configurada. Banco de demonstração preservado. [Adaptador existente](19-adaptador-openai.md), [plano AV01–AV08](06-testes.md), [concordância](18-avaliacao-triagem.md).

## Modelo recomendado e fontes

Recomendo **`gpt-6-luna`** como candidato econômico para o piloto. A [página oficial do modelo](https://developers.openai.com/api/docs/models/gpt-6-luna) confirma Responses (`v1/responses`), function calling e Structured Outputs. Isso corresponde ao endpoint, funções com argumentos vazios e `text.format/json_schema/strict` do adaptador. Compatibilidade documental não comprova qualidade semântica, acesso da conta ou funcionamento remoto do SDK instalado; o piloto verificará esses pontos sem aumentar limites automaticamente. A escolha definitiva ainda depende da revisão e dos resultados.

Preço Standard para texto/contexto curto na [tabela oficial](https://developers.openai.com/api/docs/pricing), confirmado também na página do modelo: **USD 0,10/1 milhão de tokens de entrada**, **USD 0,50/1 milhão de saída**, cache lido USD 0,01/1 milhão e escrita de cache USD 0,125/1 milhão. Premissas: endpoint padrão da OpenAI, processamento Standard, sem Batch/Flex/Fast/Ultrafast, região especial, imagens ou ferramentas hospedadas. As funções locais não são web search/file search/code interpreter; seus argumentos e resultados entram nos tokens das requisições. Nenhum desconto de cache é necessário para as estimativas abaixo. Preços precisam ser reconferidos antes de executar.

## Custo de um chamado e das 24 execuções

Limites efetivos em `app/agent/orchestrator.py` e `openai_provider.py`: 20 s totais, até **3 requisições Responses**, no máximo **4 execuções de ferramentas locais**, **2.000 tokens gerados por requisição**, sem retry do SDK. Cadastro, GET, revisão humana e SQL não geram chamadas OpenAI. Um retry manual de triagem seria outra execução com novo custo, fora da rodada planejada.

Fluxo comum pode fazer duas requisições se ambas as funções forem pedidas juntas; o orçamento proposto considera **três**, incluindo as etapas com ferramentas. Não multiplicar quatro ferramentas por três requisições: ferramentas são executadas localmente dentro dessas etapas.

| Requisição | Conteúdo considerado na entrada (premissa, não medição) | Tokens de entrada | Tokens de saída reservados |
|---|---|---:|---:|
| 1 | Instruções, chamado fictício, definições das duas ferramentas e JSON Schema | 1.500 | 2.000 |
| 2 | Tudo reapresentado, chamadas anteriores e resultado(s) local(is), contexto de continuação | 2.500 | 2.000 |
| 3 | Histórico acumulado, resultados restantes/repetidos e contexto de continuação | 3.500 | 2.000 |
| Total de uma triagem | Todas as requisições, incluindo etapas de ferramentas | **7.500** | **6.000** |
| AV01–AV08 × 3 | Até **72 requisições**, até 96 execuções locais de ferramentas | **180.000** | **144.000** |

São premissas explícitas para chamados curtos, não contagens de tokenizer nem médias observadas. A [documentação de reasoning](https://developers.openai.com/api/docs/guides/reasoning) informa que `max_output_tokens` inclui saída visível, reasoning e formatação não visível; o consumo de reasoning é cobrado como saída e não deve ser somado uma segunda vez a `output_tokens`. O adaptador não define `reasoning.effort`; o padrão documentado do candidato é medium. Os 2.000 tokens podem resultar em resposta incompleta, com cobrança mesmo sem JSON final. Nesse caso, parar e revisar; não aumentar tokens/prazo ou trocar parâmetros para tentar de novo sem reestimar e obter autorização.

Fórmula nominal (sem cache): `USD = entrada × 0,10 / 1.000.000 + saída × 0,50 / 1.000.000`.

| Escopo | Estimativa nominal Standard | Reserva se toda entrada não cacheada for escrita de cache a 1,25× |
|---|---:|---:|
| Um chamado fictício, até 3 requisições | **USD 0,00375** | **USD 0,0039375** |
| 24 execuções completas, até 72 requisições | **USD 0,09000** | **USD 0,09450** |

A reserva usa entrada a USD 0,125/milhão e saída a USD 0,50/milhão. Valores em USD, sem conversão cambial, impostos, recarga mínima ou outros custos de conta. Não há garantia de consumir todo esse volume nem de atingir qualidade suficiente.

**Estas estimativas não são teto de cobrança.** A API local limita título/descrição em caracteres (120/5.000), mas não há limite de tokens de entrada verificado pelo tokenizer no adaptador. Schemas, histórico reencaminhado, resultados e contexto de reasoning também compõem a entrada. O runner verifica o consumo somente depois de receber cada resposta; uma requisição já enviada pode ultrapassar as premissas ou continuar sendo cobrada após interrupção/timeout. Preços/tier/acesso podem mudar. Limite de contexto do modelo não substitui limite financeiro local.

Proposta para revisão, **ainda não aprovada**: USD **0,004** para o piloto e USD **0,10** para o conjunto de 24, incluindo o piloto como AV02/repetição 1 caso ele passe com o mesmo modelo/parâmetros. Não são autorizações de cobrança. Se o piloto precisar ser repetido, seus custos continuam contabilizados; não reiniciar o contador nem alegar que ainda são apenas 24. Se for um piloto extra às 24, reestimar pelo menos 25 execuções: USD 0,09375 nominal / USD 0,0984375 com reserva, antes de solicitar aprovação de nova rodada.

## Preparação executável, sem chave nem banco

Na raiz, PowerShell:

```powershell
$env:AI_MODE = 'simulated'
.\.venv\Scripts\python.exe -m scripts.us08_pilot
```

Esse é o caminho padrão e o único executado nesta entrega. Exibe proposta e reserva; não lê chave, conecta banco ou faz HTTP. `scripts/us08_pilot.py` é separado do serviço/CI e não muda Settings, `.env` nem o provedor padrão. A flag futura indica intenção explícita no terminal, mas não substitui aprovação de Eliana.

## Primeiro teste, somente depois da aprovação

Antes de executar: confirmar modelo, acesso da conta, preços Standard, verba do piloto e da rodada; obter autorização explícita do teste. Garantir cluster local disponível, sem parar o demo. O banco administrativo deve ser `portfolio_test*` em loopback, com permissão de criar bancos; nunca usar a URL do demo. Desabilitar DEBUG do SDK/HTTP. Somente este processo deve usar o orçamento durante o piloto, sem requisições concorrentes.

Comandos futuros (não executados). Os valores abaixo são os propostos, utilizáveis somente se forem aprovados:

```powershell
$env:AI_MODE = 'simulated' # aplicação/ambiente continuam simulados
$env:APP_ENV = 'test'
$env:TEST_DATABASE_URL = 'postgresql+psycopg://portfolio_test:senha_ficticia_teste@127.0.0.1:55432/portfolio_test'
# Após aprovação: inserir chave no terminal privado, sem histórico de comando literal.
$us08Key = Read-Host 'Chave da API para o piloto autorizado' -AsSecureString
$us08KeyPointer = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($us08Key)
try {
    $env:OPENAI_API_KEY = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($us08KeyPointer)
    .\.venv\Scripts\python.exe -m scripts.us08_pilot --execute-approved --model gpt-6-luna --pilot-budget-usd 0.004 --round-budget-usd 0.10
    if ($LASTEXITCODE -ne 0) { throw 'Piloto interrompido; revisar evidência antes de continuar.' }
} finally {
    [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($us08KeyPointer)
    Remove-Item Env:OPENAI_API_KEY -ErrorAction SilentlyContinue
    Remove-Variable us08Key -ErrorAction SilentlyContinue
    $env:AI_MODE = 'simulated'
}
```

O runner exige flag, modelo proposto, os dois orçamentos e chave não vazia; cria **um novo banco** `portfolio_test_us08_<uuid>`, aplica head com migração em simulated, persiste chamado fictício AV02 e usa o adaptador explicitamente somente nessa triagem. Não inicia servidor nem altera o demo. Guarda banco e ledger para revisão, inclusive após falha; não faz limpeza ou retry automático. Cada nova invocação seria um novo gasto: não repetir sem conciliar gasto anterior e autorização. O script foi preparado para um único piloto; não é executor das 24 avaliações nem mantém orçamento acumulado entre invocações.

## Consumo e interrupção

O transporte do piloto registra **cada requisição** em `reports/us08/<run_id>.jsonl` (ignorado pelo Git), antes de o adaptador validar a resposta: parâmetros/orçamentos da rodada, nome do banco, ticket/attempt IDs, request ID, response ID, modelo devolvido, tier, status HTTP, `usage.input_tokens`, `input_tokens_details.cached_tokens`, `usage.output_tokens`, `output_tokens_details.reasoning_tokens` e `total_tokens`. Não grava chave, header Authorization, título/descrição, prompt, output bruto ou reasoning em texto. Também captura usage de respostas incompletas/invalidáveis quando disponível. O adaptador normal não persiste todo esse usage; o ledger é necessário na avaliação.

`cost_nominal_usd` aplica preços de entrada/cache lido/saída aos tokens informados; `cost_reserve_usd` aplica 1,25× aos tokens de entrada não cacheados para reservar escrita de cache. São cálculos locais, não valores de fatura devolvidos pela API. Conferir painel/fatura da conta depois, principalmente se faltarem detalhes de cache/tier ou houver timeout. Não considerar consumo desconhecido como zero.

O runner bloqueia antes da primeira requisição se a reserva projetada não cabe em um dos orçamentos. Antes e depois de cada resposta, calcula `consumo reservado acumulado do piloto + reserva das requisições restantes` e, para a rodada, soma `23 × USD 0,0039375`. Interrompe se exceder uma verba, se tokens excederem as premissas por etapa, tier retornar diferente de Standard/default, houver status não concluído, HTTP de erro, ausência de usage, JSON/protocolo inválido ou timeout. O serviço existente interrompe a triagem em saída inválida e preserva chamado/tentativa. Os 23 restantes são somente projeção: **não são disparados** pelo script.

Ao primeiro erro, **não iniciar outro chamado/retry**. Ctrl+C no terminal do runner cancela a operação local; não garante cancelamento da cobrança remota. Preservar ledger/banco, conferir consumo conhecido e marcar a requisição pendente como custo desconhecido, conciliar no painel antes de continuar. Se a projeção ultrapassar o aprovado, parar e apresentar nova estimativa; não aumentar budget/limites nem consumir a diferença sem nova aprovação. Não executar scripts de parar o PostgreSQL, limpar demo ou matar processos genéricos para interromper a avaliação.

## Critérios do piloto e passagem para as 24

- Migração 0005 no banco novo; demo sem acesso. Chamado persistido antes de qualquer requisição; mesma identidade/conteúdo após a execução.
- Sucesso técnico: tentativa `mode/provider=openai`, modelo registrado, status sucesso, ambas as ferramentas consultadas, até 3 requisições/4 ferramentas/2.000 tokens por resposta e prazo de 20 s. Ledger íntegro para todas as requisições, tier Standard/default e valores reconciliados; nenhum segredo nas evidências.
- Sucesso semântico AV02: categoria defeito, prioridade alta; justificativa baseada no bloqueio fictício de três pessoas, sem inventar causa raiz, sem ausentes injustificados. Validar humanamente; saída do runner com código 0 significa apenas conclusão técnica.
- Revisão humana registrada explicitamente pela API existente, incluindo eventual correção. Não marcar revisão aceita nem avaliar qualidade real antes desse relato/registro. No banco isolado, a consulta de concordância deve contar essa tentativa uma única vez após revisão.
- Qualquer erro/violação/consumo desconhecido ou inadequação semântica interrompe a passagem para a rodada. Se tudo passar, conferir projeção atualizada das 23 execuções restantes e aprovação vigente; seguir AV01–AV08 × 3, sem substituir resultados ruins. Meta de adequação semântica ≥90% e zero violação de catálogo/ferramentas conforme plano; métricas humanas e concordância são distintas.

Para revisar os dados depois do piloto, selecionar explicitamente o banco e o ticket registrados no ledger. Exemplo futuro, com campos a substituir pelos IDs reais dessa execução:

```powershell
$events = Get-Content -Encoding UTF8 'reports/us08/SUBSTITUIR_RUN_ID.jsonl' | ForEach-Object { $_ | ConvertFrom-Json }
$us08Database = ($events | Where-Object event -eq 'database_created').database
if ($us08Database -notmatch '^portfolio_test_us08_[0-9a-f]{32}$') { throw 'Banco de avaliação inválido.' }
$env:DATABASE_URL = "postgresql+psycopg://portfolio_test:senha_ficticia_teste@127.0.0.1:55432/$us08Database"
$env:AI_MODE = 'simulated' # revisão/consulta não precisam de provedor real ou chave
.\.venv\Scripts\python.exe -m uvicorn app.main:create_app --factory --host 127.0.0.1 --port 18008 --no-access-log
```

Em outro terminal, consultar GET `/api/v1/tickets/{ticket_id}`, GET `triage-attempts`, e POST `reviews` com `expected_version` lido no GET, classificação decidida pela pessoa, motivo e autor declarados conforme [contrato](05-api.md). Não fazer novo POST triage. Executar o SQL de concordância usando a conexão desse mesmo banco. Conservar esse banco para revisão; a rodada completa deve usar um banco exclusivo e rastrear todos os 24 IDs, sem misturar outros chamados. O runner do piloto não automatiza a revisão nem a agregação de múltiplos bancos.
