# US08 — Groq opcional e evidências de validação

Atualização de 09/11/2026: após confirmação do plano Livre do Projeto padrão por
Eliana, foi executado **um único piloto real autorizado** com `openai/gpt-oss-20b`.
Três requisições HTTP 200, duas ferramentas, saída validada defeito/alta; 1.145
tokens entrada e 1.029 saída. Revisão humana pendente; custo posterior no painel
não confirmado. Banco descartável removido, simulador local ativo. Autorização
utilizada, sem nova tentativa; lote de 24 real pausado. [Evidências](andamento.md).
O texto abaixo preserva o preparo offline que precedeu esse piloto.

Candidato escolhido por Eliana para o futuro piloto: `openai/gpt-oss-20b`.
A documentação oficial de Structured Outputs lista suporte a JSON Schema estrito,
e a página Responses usa esse modelo nos exemplos. A escolha não ativa o provedor
nem autoriza chamadas. Modelo continua configurável e sem padrão no código.
Após aprovação futura, usar `GROQ_MODEL=openai/gpt-oss-20b`; agora manter simulador.

Payloads capturados e conferidos nos mocks: etapa de ferramentas contém somente
`model`, `input`, `max_output_tokens`, `tools`, `tool_choice`; etapa final contém
somente `model`, `input`, `max_output_tokens`, `text`, com `format.type=json_schema`
e `strict=true`. Nenhuma requisição envia `previous_response_id`, `store`,
`truncation`, `include`, `safety_identifier`, `prompt_cache_key` ou `prompt`.
Testados dois pedidos quando as ferramentas vêm juntas e três quando separadas.
Não foi necessária mudança de produção: as novas asserções protegem o caminho Groq.

O simulador continua padrão. `GroqProvider` reutiliza o SDK OpenAI 2.54.0 e HTTPX
0.28.1 já instalados, parsing, TLS com certificado/hostname, prazo global de 20 s,
até três requisições, quatro ferramentas e 2.000 tokens de saída por requisição.
Não houve alteração de dependências nem chamada real. Sem retry, redirecionamento
ou fallback. A chave usa SecretStr e não integra o contrato público.

A [Responses API da Groq](https://console.groq.com/docs/responses-api) é beta e
documenta o uso do SDK OpenAI com `https://api.groq.com/openai/v1`. O adaptador não
envia `store`, `include` ou IDs de conversa mantidos pelo servidor. O histórico
fica local à triagem. A [referência da API](https://console.groq.com/docs/api-reference)
documenta ferramentas locais, `tool_choice=required`, `text` estruturado e limite
de saída incluindo raciocínio.

Como [Structured Outputs](https://console.groq.com/docs/structured-outputs) não
suporta ferramentas simultâneas, o adaptador primeiro solicita as ferramentas
permitidas; após ambas, solicita JSON Schema estrito sem ferramentas. São duas
requisições quando ambas vêm juntas ou três quando vêm separadas. A validação
determinística e a revisão humana existentes continuam obrigatórias. Modelo é
configurável, sem padrão: sua compatibilidade precisa ser confirmada antes do piloto.

Configuração futura, somente após aprovação específica de modelo/custo/chamada:
`AI_MODE=groq`, `GROQ_MODEL` e `GROQ_API_KEY` localmente, fora do Git. Configuração
incompleta falha claramente. Agora manter `AI_MODE=simulated`. Antes de usar um
banco existente, revisar backup e aplicar explicitamente `python -m alembic upgrade head`.
A migração 0006 amplia CHECKs sem converter/apagar registros; o demo não foi migrado.
Downgrade para 0005 é bloqueado se houver tentativas Groq.

Os testes offline usam credenciais fictícias e MockTransport no adaptador/SDK reais,
com rede externa bloqueada. Cobrem ferramentas juntas/separadas, JSON estruturado,
saída inválida, timeout, 429 com cota/limite/campos ausentes, sanitização, ausência
de retry e preservação do chamado sem sugestão na falha. São cenários simulados;
não explicam o 429 anterior da OpenAI. Integração usa bancos PostgreSQL descartáveis,
incluindo revisão humana e consulta de concordância. Resultados em [andamento](andamento.md).

Pendentes: conexão/TLS reais, aceitação do schema e histórico pelo modelo escolhido,
consumo, preço, latência e qualidade com revisão humana real. Piloto e lote real
de 24 continuam pausados. O script de piloto OpenAI não foi habilitado para Groq.
