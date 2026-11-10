# Resultado do primeiro piloto US08 — 09/11/2026

Atualização posterior, somente offline: [registro sanitizado de HTTP 429](19-adaptador-openai.md#diagnóstico-técnico-sanitizado-de-http-429) implementado para futuras respostas. Nos registros da segunda tentativa, `error.code` e `error.type` **não foram registrados**; a mudança não preenche retrospectivamente esses campos e não altera a conclusão de custo desconhecido. Ledgers originais preservados; nenhuma nova chamada foi feita.

## Segunda tentativa, com nova autorização explícita

Em 09/11/2026, Eliana autorizou uma única nova tentativa, gpt-6-luna, até três requisições no total, orçamento de referência USD 0,01 e TLS com certificado/hostname verificados. Executada uma única vez, sem retry automático ou manual. **Resultado: HTTP 429 na primeira requisição; piloto interrompido.** A conexão real com TLS verificado foi estabelecida, mas não houve resposta válida do modelo, execução de ferramentas ou sugestão. O ledger não registra código/tipo específico do erro remoto; não atribuímos o 429 a crédito, quota ou taxa como causa confirmada.

| Evidência da segunda tentativa | Resultado |
|---|---|
| Run ID | `dba4d17ac5464fc5b23e48e163b0ad45` |
| Banco novo, exclusivo e preservado | `portfolio_test_us08_dba4d17ac5464fc5b23e48e163b0ad45` |
| Ticket | `a4955d63-5e88-4639-b3ac-2f6a27cc1c0c` |
| Attempt | `3b696a5c-1502-4e48-b5fe-cd85f884f6b1` |
| Início/fim, America/Sao_Paulo | 09/11/2026 18:44:04 / 18:44:07 (-03:00) |
| Requisições iniciadas / respostas HTTP | **1 / 1**, status **429** |
| Request ID | `req_7b52e8cf20d74ab9bf45f9e1badc8899` |
| Tentativas / chamadas de modelo / ferramentas | 1 / 1 / 0 |
| Estado / erro persistido | falha / `ai_unavailable` |
| Usage informado / custo calculado | Não informado / **desconhecido**, não zero |
| Classificação sugerida / revisão humana | Nenhuma / não registrada, pois não existe sugestão válida |
| Conteúdo/estado do chamado | Preservado, aberto/falha, version=3/content_revision=1; suggestion/final_classification nulos |
| Concordância no banco dessa tentativa | Zero linhas; tentativa falha e sem revisão excluída |

Ledger intacto em `reports/us08/dba4d17ac5464fc5b23e48e163b0ad45.jsonl`, SHA-256 `a61552d5f40e7125211596ea858e394e411d85a8bb46596dc0bc42a1189e1ea0`. Chave não exibida nem registrada; `.env` confirmado com `AI_MODE=simulated` ao encerrar. Banco demo e banco da primeira tentativa não acessados/alterados por essa execução; somente o novo banco do piloto foi criado/migrado e conferido. Sem terceira chamada/triagem, testes repetidos, mudanças de código, commit/push/deploy. Nova autorização foi utilizada; as 24 continuam pausadas. Sem consumo informado, não há base medida para atualizar o orçamento do lote. Histórico da primeira tentativa mantido abaixo.

## Conferência do CSV fornecido por Eliana

Recebido `completions_usage_2026-10-10_2026-11-09.csv`, lido integralmente sem modificar o original. SHA-256 `71cc6b52aa8732791affcb423e590cd9f7926172e16d6d99db05b6910ca335ff`. São 31 linhas de intervalos diários e somente quatro colunas: start_time, end_time, start_time_iso, end_time_iso. Não há colunas de requisições, tokens, modelo, projeto ou valores monetários.

O último intervalo é 09/11/2026 00:00 UTC a 10/11/2026 00:00 UTC e inclui o piloto, cuja tentativa no banco isolado começou em **09/11/2026 18:22:52 -03:00 (21:22:52 UTC)** e terminou às 18:22:54 -03:00. Comparação dos timestamps confirmou a inclusão na janela exportada.

Registro: **sem consumo visível no CSV fornecido; valor não informado**. Isso não comprova custo zero, nem identifica quais filtros de projeto foram usados na exportação. O custo faturado permanece não confirmado; o usage da tentativa continua indisponível. A conferência não autoriza outra chamada. Piloto e lote de 24 permanecem pausados; nenhuma tentativa adicional executada. O relato de falha abaixo e o ledger original são preservados.

Eliana autorizou um chamado fictício, uma tentativa, até três requisições no `gpt-6-luna`, orçamento de referência USD 0,01. Chave configurada e utilizada somente localmente, sem exibição ou inclusão no Git. **Piloto interrompido por falha de conexão, sem retry. Não aprovado como integração remota nem avaliação semântica.**

| Evidência | Resultado |
|---|---|
| Run ID | `8ee2f97c20d644f7b0f70fb134e638a5` |
| Banco exclusivo preservado | `portfolio_test_us08_8ee2f97c20d644f7b0f70fb134e638a5` |
| Migração | 0005 |
| Chamado AV02 fictício | `74f4841d-f116-4a99-ad35-9f966be99266` |
| Tentativa | `f28a746f-b5d9-4509-8ac1-e5cf47487e8a` |
| Tentativas / envios iniciados / respostas HTTP recebidas | 1 / 1 / 0 |
| Estado e erro | falha / `ai_unavailable` |
| Chamadas de modelo / ferramentas executadas | 1 / 0 |
| Sugestão / classificação final / revisões | nula / nula / 0 |
| Conteúdo e identidade do chamado | Preservados, aberto/falha, version=3, content_revision=1 |
| Consulta de concordância no banco do piloto | Zero linhas, conforme exclusão de falhas e tentativas sem revisão |
| Usage e custo medido | Não disponíveis; custo desconhecido, não tratado como zero |

Ledger original em `reports/us08/8ee2f97c20d644f7b0f70fb134e638a5.jsonl`, ignorado pelo Git, preservado sem edição. Resumo sanitizado com SHA-256 do ledger em arquivo de mesmo prefixo `-summary.json`. Nenhum corpo de requisição, chave, Authorization ou saída bruta registrado. Sem request/response ID da API, pois nenhuma resposta HTTP foi recebida. O evento request_started indica início local do transporte, não comprova recebimento pelo provedor.

## Diagnóstico e correção preparada

Após interromper o piloto, foram feitos somente resolução DNS e handshakes TLS, **sem HTTP, chave ou chamada de modelo**. DNS funcionou. TLS com CAs do sistema funcionou em TLSv1.3; TLS com o bundle certifi usado por padrão pelo HTTPX falhou com `SSLCertVerificationError`, verify_code=20. Proxy e CA customizada de ambiente ausentes (somente presença conferida, sem valores exibidos). HTTPX 0.28.1/certifi 2026.10.23.

Esse diagnóstico é compatível com a falha inicial, mas o ledger original não preservava o tipo da exceção do transporte; não atribuímos retrospectivamente um erro TLS específico àquela execução como fato provado. A partir desta correção, registra-se somente o nome da classe da exceção, sem sua mensagem ou detalhes sensíveis.

Conforme a [documentação HTTPX sobre contextos SSL](https://www.python-httpx.org/advanced/ssl/) e [Python 3.12 sobre CAs do sistema](https://docs.python.org/3.12/library/ssl.html#ssl.create_default_context), adaptador e transporte do piloto agora usam `ssl.create_default_context()`, com certificado obrigatório e verificação de hostname. Não há `verify=False`, instalação de CA, fallback sem verificação ou mudança de certificados da máquina. Key logging TLS desabilitado no contexto. Endpoint fixo, sem proxies herdados, sem redirects e retries=0 mantidos. Nenhuma dependência nova.

Validação da correção **somente com transporte falso**: 39 testes passaram (3,75 s), incluindo os dois novos de certificado/hostname obrigatórios e contexto do transporte do piloto, sem retry. Ruff/format e git diff --check aprovados. Não houve segunda chamada real para testar a correção. Banco demo não acessado; banco isolado e registros originais preservados para revisão.

## Próximos passos e limites

Antes de repetir: conferir consumo/cobrança no painel privado da OpenAI para essa janela de execução. Sem usage, não é possível recalcular as 24 com consumo medido nem afirmar custo zero. A projeção anterior permanece apenas hipotética. Nova tentativa paga requer nova autorização de Eliana; a autorização de um piloto já foi usada. As 24 execuções continuam sem autorização.

Não existe sugestão válida para decisão humana neste piloto; não criar review fictícia nem declarar ferramenta/classificação aprovada. Após uma futura tentativa válida e autorizada, apresentar saída e consumo para revisão humana explícita, registrar a decisão e só então recalcular o lote. A aplicação continua com `simulated` como padrão. Alterações locais, sem commit/push/deploy.
