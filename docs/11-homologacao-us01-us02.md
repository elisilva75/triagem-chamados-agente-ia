# Homologação local de US01 e US02

Sessão iniciada em 07/11/2026. Responsável pela homologação: Eliana Gomes da Silva. Resultado funcional depende do retorno de Eliana; preparação técnica não equivale a aceite humano.

## Preparação executada

- PostgreSQL isolado existente iniciado pelo script `scripts/start-test-postgres.ps1`, em 127.0.0.1:55432. Serviço global preservado, sem exclusão ou reinicialização de dados.
- Banco `portfolio_chamados_demo` não existia e foi criado. Migrações aplicadas com `python -m alembic upgrade head`; `alembic current` retornou `0001 (head)`.
- Contagem inicial confirmada: **0 chamados**. Nenhum cadastro foi feito pelo agente nesta preparação; os registros da homologação serão criados por Eliana com dados fictícios.
- API iniciada em segundo plano com bind 127.0.0.1:8000, AI_MODE=simulated e DATABASE_URL apontando para o banco demo. Processo lançador: PID 13276; log do servidor informa PID 22348. Logs e PID em `.local/api-homologacao.*`, fora do Git. Não encerrar processos usando esses números sem reconferir sua identidade, pois PIDs podem ser reutilizados.
- Verificação por HTTP após o comando de inicialização ter terminado: GET `/docs` retornou **200**, HTML contém `SwaggerUIBundle`; GET `/health` retornou **200**, `status=ok`; `/openapi.json` respondeu com o contrato da aplicação; GET `/api/v1/tickets?limit=1&offset=0` retornou total=0.
- Essa checagem confirma a entrega do HTML, não comprova interação no navegador nem carregamento dos recursos JavaScript/CSS externos do Swagger. Eliana confirmará que a interface abriu.
- Inspeção complementar de sockets via Get-NetTCPConnection no sandbox retornou acesso negado; a acessibilidade HTTP foi confirmada e o log informa bind local. Isso não foi interpretado como falha da API.

Processos deixados em execução para homologação. Caso a sessão do sistema os encerre, usar os comandos de retomada abaixo. Apenas GETs de preparação foram executados; não antecipar os cenários como aprovados.

## Cenários e registro de resultados

| ID | Cenário | Rastreabilidade | Situação | Resultado observado por Eliana |
|---|---|---|---|---|
| H01 | Cadastro válido e UUID | US02-CA1; RN01/RN02/RN13 | Homologação manual informada por Eliana | HTTP 201, campos iniciais e header location conforme esperado; UUID do cadastro não foi transcrito no retorno |
| H02 | Consultar chamado de H01 | US02-CA1 | Homologação manual informada por Eliana | HTTP 200, mesmos dados do cadastro |
| H03 | Listagem e paginação | US02-CA4 | Homologação manual informada por Eliana | HTTP 200, um chamado, total=1, limit=20, offset=0; limit=1/offset=1: items=[], total=1 |
| H04 | Title obrigatório ausente | US02-CA2; RN01 | Resposta homologada por Eliana; não persistência verificada tecnicamente pelo agente | HTTP 422, validation_error, body.title/missing; contagens SQL antes/depois: tickets 1→1, ticket_events 1→1 |
| H05 | UUID válido inexistente | US02-CA2 | Homologação manual informada por Eliana | UUID 11111111-1111-4111-8111-111111111111; HTTP 404 e not_found |

### Origem das evidências e complemento de H04

Eliana informou ter executado e conferido os resultados acima manualmente no Swagger. Não se trata de execução visual feita pelo agente. H04 foi executado por ela sem title, não com ambos os campos ausentes como no roteiro original; não registrar ausência de description como homologada manualmente. A paginação manual confirma a página vazia após o único registro; não equivale a navegar duas páginas não vazias. Limites e demais variações continuam cobertos pelos testes automatizados, sem atribuí-los à homologação humana.

Para encerrar a parte de não persistência de H04, o agente repetiu POST sem title com descrição fictícia válida e consultou diretamente o PostgreSQL demo antes/depois da requisição. Resultado: HTTP 422, validation_error, body.title/missing; **1 chamado e 1 evento antes, 1 chamado e 1 evento depois**. Request ID: `81295f21-37d8-4464-8cac-88371face1ee`. Essa reprodução confirma o comportamento atual; não reconstrói retroativamente a requisição manual. Nenhum dado existente foi editado/apagado. Evidência operacional local em `.local/rejected-registration-evidence.json` (fora do Git); resumo persistido neste documento.

Eliana autorizou explicitamente iniciar US03 após esse retorno. Os cenários informados foram aceitos conforme o relato e a verificação complementar; US01 segue parcialmente validada por falta de Compose e CI remota permanece pendente.

Apresentar um cenário por vez no chat e aguardar o retorno antes do seguinte. Ao receber evidência, registrar status HTTP, resultado, UUID quando pertinente e eventuais divergências; não concluir por silêncio. Falha abre registro de problema e interrompe avanço dependente até esclarecer/corrigir.

## H01 — instrução apresentada

Abrir http://127.0.0.1:8000/docs → expandir **POST /api/v1/tickets** → **Try it out** → substituir todo o Request body por:

```json
{
  "title": "Erro ao salvar cadastro fictício",
  "description": "No ambiente de demonstração, ao salvar um cadastro fictício, a tela apresenta uma mensagem de erro."
}
```

Clicar **Execute**, observar **Server response** (não apenas a tabela de respostas documentadas). Esperado: HTTP **201**, id UUID gerado, mesmo title/description, status=aberto, triage_status=pendente, version=1, content_revision=1, suggestion=null, final_classification=null, created_at/updated_at preenchidos. Header Location deve ser `/api/v1/tickets/<id>`. Copiar o id para H02 e informar status/resultado no chat. Evitar repetir Execute após sucesso, pois o cadastro não possui chave de idempotência e criará outro chamado.

## Roteiro original de referência (execuções efetivas registradas acima)

- H02: GET `/api/v1/tickets/{ticket_id}` com ID de H01; 200 e mesmos campos do chamado criado.
- H03: GET `/api/v1/tickets`, limit=1, offset=0, sem filtros; 200, items com no máximo 1 registro, total refletindo o banco, limit/offset iguais aos pedidos. Preparar segundo registro fictício se necessário para demonstrar páginas distintas, sem apagar existentes; offset além do total deve devolver items=[] e manter total. Valores permitidos: limit 1–100, offset ≥ 0; inválidos geram 422.
- H04: POST `/api/v1/tickets` com `{}`; 422, error.code=validation_error, details para body.title e body.description com code=missing; nenhum chamado deve ser criado (comparar total antes/depois). Isso verifica campos ausentes, não texto em branco, que tem casos próprios automatizados.
- H05: GET com UUID sintaticamente válido confirmado como ausente no banco demo no momento do cenário; 404, error.code=not_found e request_id UUID. UUID malformado geraria 422 e não satisfaz esse cenário.

## Retomada, se os processos forem encerrados

PowerShell na raiz do projeto; reutilizar .venv e banco existentes. Não executar initdb de novo nem remover volumes/diretórios. Se a API já responder, não iniciar outra na mesma porta.

```powershell
Set-Location 'C:\Users\Cliente\OneDrive\Documentos\projeto-agente-ia'
.\scripts\start-test-postgres.ps1
$env:DATABASE_URL = 'postgresql+psycopg://portfolio_test:senha_ficticia_teste@127.0.0.1:55432/portfolio_chamados_demo'
$env:AI_MODE = 'simulated'
.\.venv\Scripts\python.exe -m alembic upgrade head
.\.venv\Scripts\python.exe -m uvicorn app.main:create_app --factory --host 127.0.0.1 --port 8000 --no-access-log
```

Manter esse terminal aberto e acessar /docs no navegador. O banco demo já foi criado nesta sessão; não repetir createdb. Migração upgrade head não exclui os chamados existentes. Se ocorrer falha, registrar o erro antes de alterar dados ou encerrar processos desconhecidos.

## Pendências preservadas

- Docker Compose não executado; US01 **não totalmente validada**, mesmo se H01–H05 passarem.
- Workflow CI não executado no GitHub; publicação não autorizada.
- US03 autorizada explicitamente por Eliana; sua implementação e homologação terão registro próprio. US04 não autorizada nesta entrega.
- Sem autenticação, apenas uso local e dados fictícios. Nenhuma integração real de IA, chamada paga, publicação ou deploy.
