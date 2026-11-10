# Adaptador OpenAI — preparação local da US08

## Diagnóstico técnico sanitizado de HTTP 429

Atualização offline de 09/11/2026: `app/agent/diagnostics.py` extrai somente `http_status`, `error.code`, `error.type` e `x-request-id`. O adaptador captura `APIStatusError` e emite `openai_http_error` no logger `app.agent.openai_provider`; o transporte do piloto usa o mesmo sanitizador no evento JSONL `response_received`, **antes** de validar usage ou interromper por erro. O campo anterior `request_id` do ledger também recebe o valor sanitizado de `x-request-id`.

Códigos/tipos usam listas fechadas para cota, crédito, limites e throttling documentados; valores desconhecidos, não textuais ou contendo a chave são substituídos por `[redacted]`. Request IDs precisam ter prefixo `req_` e sufixo ASCII alfanumérico/underscore/hífen de 1–128 caracteres; quebras de linha, formatos inválidos, chaves e excesso de tamanho são ocultados. Campos ausentes/nulos são `null`. JSON ausente/inválido ou envelope inesperado não impede registrar o status e o request ID seguro. Nunca registrar `error.message`, param, corpo bruto, Authorization ou exceção remota completa. Novos códigos do provedor podem exigir expansão revisada da lista, sem liberar texto remoto arbitrário nos logs.

Exemplo inteiramente fictício:

```json
{"http_status":429,"error":{"code":"insufficient_quota","type":"insufficient_quota"},"x-request-id":"req_quota_test"}
```

A resposta pública permanece HTTP 503/`ai_unavailable`, com a mesma mensagem/envelope/detalhes, sem metadados remotos adicionais. Timeout, retries=0, modo padrão e persistência do chamado não mudaram; nenhuma migração ou dependência nova. A correção não recupera campos ausentes dos dois pilotos passados, cujos ledgers permanecem intactos.

Fontes oficiais consultadas: [erros e códigos da OpenAI](https://developers.openai.com/api/docs/guides/error-codes) e [SDK Python/APIStatusError e request IDs](https://developers.openai.com/api/reference/python), confrontadas com o SDK 2.54.0 instalado. Validação com transporte falso/rede externa bloqueada: `tests/unit/test_openai_diagnostics.py` (quota, requests, ausências, JSON inválido e conteúdo malicioso, tanto no logger quanto no ledger); teste de API/PostgreSQL isolado reaproveitado com três casos para verificar resposta pública e preservação do chamado. Evidências/comandos em andamento. Nenhuma chamada real autorizada ou realizada nesta atualização.

Estado posterior: [primeiro piloto interrompido por conexão](21-resultado-piloto-us08.md), sem resposta HTTP/usage e sem retry. Correção TLS preparada com CAs do sistema e verificação obrigatória de certificado/hostname, validada apenas com transporte falso. Integração remota e semântica continuam não aprovadas.

Proposta posterior para revisão, sem ativação: [modelo econômico, preços, estimativas, comandos e critérios do primeiro piloto](20-primeira-avaliacao-real.md). `scripts/us08_pilot.py` prepara a avaliação sem rede por padrão e oferece registro de usage/interrupção para execução futura explicitamente aprovada. Não altera o adaptador nem seu provedor padrão.

Em 09/11/2026, Eliana escolheu OpenAI como primeiro provedor e autorizou implementação e testes sem chamadas reais. Modelo definitivo, estimativa de custo e autorização para as 24 execuções reais continuam pendentes. `AI_MODE=simulated` permanece padrão e obrigatório na CI comum. O demo não foi acessado ou migrado nesta entrega. [Evidências executadas](andamento.md).

Rastreabilidade: US08-CA1/T1 → `factory.py`, `openai_provider.py`, protocolo e orquestrador → testes unitários de tradução e integração de persistência/revisão; US08-CA2/T1/T2 → Settings, SecretStr, `.env.example`, SDK sem retries e CI simulada → testes de configuração, falha sanitizada e seleção; US08-CA3/T2 → timeout total, limites do orquestrador e testes de excesso/timeout. CA3 permanece parcial quanto à compatibilidade do modelo definitivo, ainda não escolhido nem habilitado para uso real. T1 também permanece parcial quanto à decisão de modelo/custo; T2 remoto e avaliação real não executados. US08 não concluída.

## Contrato e validação

`app/agent/factory.py` seleciona o provedor a partir de Settings. O adaptador `OpenAIProvider` implementa `AIProvider.respond`, usando Responses API e SDK Python. Envia somente as duas funções de `app/agent/tools.py`, com argumentos vazios e schema estrito. Converte chamadas em `ToolCall` e devolve resultados locais com o mesmo `call_id`. O histórico de resposta necessário à continuação, inclusive reasoning criptografado quando fornecido pela API, fica somente em memória daquela execução, sem estado compartilhado entre chamados. Usa `store=False`, sem conversation ou previous_response_id.

O JSON Schema é derivado de `AgentOutput`, enviado por `text.format` com `strict=true`. Recusas, respostas incompletas, JSON inválido, funções não permitidas e argumentos extras são rejeitados. A validação Pydantic e as duas consultas obrigatórias permanecem fora do provedor; saída estruturada não dispensa a validação local. O modelo a escolher precisa suportar Responses, function calling e esse schema. HTTP 4xx/5xx, autenticação, limite de uso e conexão são falhas sanitizadas de indisponibilidade, sem fallback para simulação.

O orquestrador mantém 20 segundos totais, no máximo 3 chamadas de modelo, 4 execuções de ferramentas e 2.000 tokens de saída por chamada (até 6.000 na execução; não é teto monetário). O SDK recebe `max_retries=0`, timeout restante e `max_output_tokens`. O cliente assíncrono roda sob `asyncio.timeout` dentro da interface síncrona, impondo deadline total além dos timeouts por fase do HTTPX; a resposta tardia também é descartada pelo orquestrador/serviço. A API síncrona é executada pelo FastAPI em worker; não chamar `respond` diretamente de um event loop ativo.

A chave é `SecretStr`, não aparece em schemas, respostas ou logs da aplicação. O endpoint é fixo `https://api.openai.com/v1`, sem base URL configurável, redirects ou proxies herdados do ambiente. Não habilitar logs HTTP/SDK em DEBUG nem registrar prompts, corpos brutos ou headers. Somente dados fictícios e uso loopback sem autenticação. O envio real implica transmissão do texto e dos resultados das ferramentas à OpenAI; `store=False` não representa promessa de retenção zero pelo provedor.

Tentativas continuam confirmadas antes da chamada e sem conexão de banco mantida durante o provedor. A falha preserva título, descrição e chamado, persistindo tentativa/falha sanitizada. Sugestões OpenAI seguem os mesmos fluxos de revisão humana obrigatória, resolução e invalidação; não decidem classificação final autonomamente.

## Configuração futura, após autorização

1. Definir um modelo compatível, estimar custo de entrada/saída e até três chamadas por tentativa, registrar parâmetros e obter autorização para a rodada. Limites de tokens/tempo não garantem um orçamento monetário; avaliar preços, quotas e possíveis custos de requisições interrompidas antes de usar chave real.
2. Instalar `requirements-dev.lock` (ou `requirements.lock` para execução). Preparar banco de avaliação exclusivo, explicitamente selecionado por `DATABASE_URL`, e executar `python -m alembic upgrade head`. Não apontar a avaliação para o demo.
3. Configurar localmente `AI_MODE=openai`, `OPENAI_API_KEY` e `OPENAI_MODEL` em ambiente ou `.env` ignorado pelo Git. Nenhum segredo real deve ser incluído em documentação ou conversa. Sem chave/modelo não vazios, Settings falha antes de servir requisições, sem fallback. Sem `AI_MODE=openai`, continua simulação mesmo com chave/modelo configurados. Iniciar a API apenas em loopback; inicialização não chama a API externa.
4. Só executar POST de triagem com autorização real. Registrar as 24 execuções AV01–AV08 × 3 conforme [plano](06-testes.md), incluindo falhas e exclusões. Aplicar o [relatório de concordância](18-avaliacao-triagem.md) e os critérios semânticos independentes. Não tratar os testes com transporte falso como avaliação de modelo.

Não há modelo padrão. `modelo-ficticio` e `chave-ficticia-sem-validade` são exclusivamente fixtures, não instruções para uma chamada real.

## Persistência e compatibilidade

Migração `0005_openai_provider.py`, a partir de 0004: acrescenta `provider`/`model` nullable e amplia o CHECK de modo para `simulated`/`openai`. Tentativas simuladas existentes continuam com metadados nulos; tentativas OpenAI exigem provider=openai e modelo não vazio até 200 caracteres. Schemas de tentativa e sugestão aceitam o modo explícito. Downgrade com dados OpenAI é bloqueado pelo CHECK antigo; não apaga nem converte essas tentativas. Fazer backup e planejar reversão antes de qualquer migração de dados fora dos bancos descartáveis. Nenhum upgrade automático no demo.

Em 09/11/2026, fontes oficiais consultadas antes de atualizar dependências: [Responses API](https://developers.openai.com/api/reference/responses/overview), [function calling](https://developers.openai.com/api/docs/guides/function-calling), [Structured Outputs](https://developers.openai.com/api/docs/guides/structured-outputs) e [SDK Python, retries/timeouts](https://developers.openai.com/api/reference/python). A documentação atual exige Python 3.10+ e já descreve HTTPX2; ela não comprova a versão resolvida neste ambiente. O índice disponibilizou `openai==2.54.0`, cujos metadados instalados e testes locais usam HTTPX 0.28.1 e Pydantic 2.14.3, compatíveis com Python 3.12.6. Dry-run com os locks existentes aprovado antes da instalação; nenhuma dependência anterior atualizada. Novas transitivas: distro 1.9.0, jiter 0.19.0, sniffio 1.3.1 e tqdm 4.70.1. Locks regenerados pelo script do projeto. A CI permanece simulada; não foi executada remotamente nesta entrega.
