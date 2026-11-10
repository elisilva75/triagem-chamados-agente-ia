# Andamento e continuidade

## 10/11/2026 — US08: retomada autorizada da publicação da branch

Eliana autorizou retomar commit/push exclusivamente de feat/us08-avaliacao e
PR em rascunho para main, sem merge. Conferidos repositório/conta autenticada
elisilva75/triagem-chamados-agente-ia e igualdade da main remota com a base local.
Seleção final corresponde aos **71 arquivos** de docs/33, incluindo escritor
atômico compartilhado, diagnóstico sanitizado e novas regressões.

Evidência reutilizada com autorização: pipeline final exit 0, **334 passed**
(219 unitários, 113 PostgreSQL/API, 2 HTTP loopback), sem falhas/erros/skips,
conforme registro abaixo. Conferência de datas de modificação dos candidatos
não documentais contra o início desse pipeline não encontrou alteração posterior
de código/configuração; nesta retomada somente registros documentais atualizados.
Pip check, Ruff check/format e git diff --check reexecutados e aprovados.

Auditoria final da seleção/índice exclui credenciais reais, .env local, reports/,
.local/ e diagnósticos temporários; apenas .env.example com valores fictícios.
Nenhum dado do demo foi acessado ou migrado. Estado de envio, URL do PR, commit
e conclusão da CI serão informados após as operações remotas autorizadas;
este é o registro da verificação anterior ao commit. PR deve permanecer draft,
Groq experimental, simulador padrão, lote real de 24 pausado/desabilitado e
consistência das 24 execuções pendente. Sem chamadas à Groq ou deploy.

## 10/11/2026 — US08: diagnóstico offline e correção da escrita atômica

Na branch feat/us08-avaliacao, reproduzidos antes de alterar o código os testes
batch invalid e R1 success: primeiro isoladamente (**1 passou em cada execução**),
depois juntos (**2 passaram**). R1 manteve 24 envios mockados no sucesso. Logs
do diagnóstico: 36/137/173 substituições, sem handle Python aberto em fonte ou
destino, um escritor observado por execução, caminhos UUID exclusivos e rodadas
sequenciais. Não identificado compartilhamento de caminho entre esses escritores;
isso não exclui handles transitórios de processos externos. Consulta CIM de
processos negada; não houve atribuição de causa a OneDrive ou antivírus.

Estresse do escritor original reproduziu **PermissionError/WinError 5 após
4.833 gravações** no caminho de relatórios. Zero handles Python abertos, um
escritor observado, atributos 32 (sem somente leitura) em fonte/destino. A mesma
substituição funcionou depois, sem mudar permissões: **negação transitória do
Windows confirmada; processo externo responsável não identificado**. Traceback
completo, eventos e cópias de manifesto/temporário preservados fora do checkout.

Correção mínima: escritor compartilhado em scripts/us08_groq_pilot.py, usado
também por scripts/us08_batch.py. Temporário continua fechado antes do replace
atômico; só esse replace local admite até cinco tentativas em PermissionError
Windows 5/32/33, com esperas configuradas 10/20/40/80 ms. Persistindo a falha,
propaga o erro e mantém manifesto anterior/temporário pendente. Nenhum retry HTTP,
retriagem, mudança de limites, devolução de orçamento ou escrita parcial no
destino. Estresse corrigido: **10.000 gravações concluídas**, quatro negações
transitórias recuperadas em 10.004 tentativas de replace, nenhum handle próprio
aberto. Cinco testes unitários novos verificam limite, propagação e atomicidade.

O R1 histórico parou no **AV04-R1 após 12 envios**, mas a exceção inicial não
foi preservada: **sua causa histórica continua não confirmada**. A reprodução
natural não falhou. Piloto e executor agora preservam tipo/errno/winerror
sanitizados, sem mensagem/corpo/credencial. Injeção explícita de erro persistente
após terceira resposta do AV04 captura PermissionError/13/5, interrompe aos 12
envios e não inicia AV05. Traceback offline identifica a primeira falha em save.
É regressão controlada, não evidência retrospectiva da mesma causa do WinError.
A expectativa de sucesso continua **24**, e a parada no primeiro erro persistente
ou erro de API continua obrigatória. Primeiro rascunho do teste de injeção falhou
por ocorrer antes do envio (11 respostas); corrigido apenas o ponto da injeção
para depois da resposta. Testes originais + regressão após ajuste: **3 passed**,
65,72 s; injeção instrumentada isolada também passou.

**Execução final única**, após o código estabilizado:
`python scripts/check_quality.py`, com APP_ENV=test, AI_MODE=simulated,
DATABASE_URL e TEST_DATABASE_URL no PostgreSQL administrativo fictício local
55432/portfolio_test, sem chaves no ambiente do processo. Saída completa e JUnit
preservados na etapa 09-final-pipeline do diagnóstico temporário:

| Etapa da mesma execução final | Resultado | Tempo dos testes |
| --- | --- | ---: |
| pip check | aprovado | — |
| Ruff check / format --check | aprovados | — |
| Unitários | 219 passed, zero falhas/erros/skips | 21,42 s |
| PostgreSQL/API | 113 passed, zero falhas/erros/skips | 548,67 s |
| HTTP/TCP loopback | 2 passed, zero falhas/erros/skips | 31,74 s |

**334 testes aprovados nesta mesma execução completa**, pipeline exit 0,
sem compensar falhas com resultados anteriores. Aviso conhecido TestClient/HTTPX
permanece. `git diff --check` final aprovado. Bancos de testes exclusivos nas
fixtures; demo não acessado/migrado. Sem chamadas Groq ou GitHub nesta etapa.

Arquivos alterados nesta correção: scripts/us08_groq_pilot.py,
scripts/us08_batch.py, scripts/us08_round_r1.py,
tests/integration/test_us08_round_r1.py, novo tests/unit/test_us08_atomic_evidence.py,
docs/33-revisao-local-us08-e-pr.md e docs/andamento.md. Lista candidata atualizada
para 71 arquivos, com o novo teste; documentação histórica preservada.
Tracebacks, stdout/stderr, JUnit e cópias de evidências em
TEMP/us08-diagnostics-*; caminho exato em .local/us08-diagnostics-location.txt,
ambos fora dos candidatos ao GitHub. Lote real de 24 pausado, AI_MODE=simulated
local mantido, sem commit/push. Resultado anterior de publicação suspensa abaixo
é histórico; nenhuma publicação foi realizada nesta correção.

## 10/11/2026 — US08: publicação autorizada, suspensa por falhas na verificação

Eliana autorizou publicar somente feat/us08-avaliacao e abrir PR em rascunho
para main, condicionado à nova suíte completa aprovada. Conta/repositório
elisilva75/triagem-chamados-agente-ia conferidos por leitura autenticada; main
remoto corresponde à base local revisada. Como houve falhas, **não foi feito
commit, push ou PR**, nem executada CI remota desta tentativa. Nenhuma correção
ou reexecução dos testes após as falhas, conforme a condição de parar.

Executado `python scripts/check_quality.py` em AI_MODE=simulated, APP_ENV=test,
com DATABASE_URL/TEST_DATABASE_URL exclusivamente no PostgreSQL administrativo
de testes local (55432/portfolio_test), chaves removidas do ambiente do processo.
Pip check, Ruff check e Ruff format --check passaram. **214 unitários passed**,
18,24 s. PostgreSQL/API: **110 passed, 2 failed**, zero erros/skips, 824,60 s.
Pipeline encerrou com código 1 e **não executou a fase HTTP loopback**.
Aviso conhecido TestClient/HTTPX preservado. Falhas desta execução:

- `tests/integration/test_us08_batch.py::test_sequential_batch_stops_and_retains_prior_evidence[invalid]`:
  PermissionError/WinError 5 em `scripts/us08_batch.py:36`, ao substituir
  manifest.tmp por manifest.json na gravação de evidência. Acesso negado
  confirmado; a origem do bloqueio de arquivo (sincronização, antivírus ou outra)
  não foi comprovada. Não atribuir a causa automaticamente ao OneDrive.
- `tests/integration/test_us08_round_r1.py::test_r1_sequential_and_evidence_preserved[success]`:
  12 requisições mockadas recebidas contra 24 esperadas. Manifesto marca
  execution_or_evidence_error, AV01–AV03 sucesso, AV04 interrompido e AV05–AV08
  não executados. Registro AV04 sem estado persistido/descarte confirmado;
  motivo específico da exceção não preservado. Não afirmar mesma causa da
  falha anterior sem evidência adicional.

Relatórios locais preservados em reports/us08-prepush-unit.xml e
reports/us08-prepush-postgres-api-failed.xml; manifestos exclusivos dos mocks
referenciados nas propriedades do JUnit. São testes offline, sem chamadas reais.
Nenhuma intervenção sobre o demo ou suas migrações; AI_MODE=simulated local
conferido. Não foi feita limpeza manual de bancos nesta etapa.

Auditoria pré-publicação aprovada: lista exata de **70 arquivos** corresponde a
[docs/33](33-revisao-local-us08-e-pr.md), 135 rastreados/candidatos examinados,
sem literal de credencial real/padrão de chave privada, .env, dados locais ou
relatórios brutos nos candidatos. .env/.local/reports continuam ignorados.
Git diff --check aprovado. Ferramenta auxiliar GitHub/rascunho preparados só
em .local ignorado; nenhuma credencial exibida ou gravada. As únicas alterações
rastreadas desta etapa são estes registros documentais nos mesmos caminhos já
revisados. Publicação e CI pendentes de resolução e nova verificação aprovada;
lote de 24 e novas chamadas Groq permanecem pausados, sem merge/deploy.

## 10/11/2026 — US08: revisão contra main, suíte offline e rascunho local de PR

Branch feat/us08-avaliacao conferida; revisão de `git diff main` complementada
por arquivos novos não ignorados. Inspecionados configuração/factory, adaptadores,
protocolo/contexto, validação, persistência, schemas/CHECKs/migrações 0005/0006,
SQL de concordância e guardas/evidências dos executores. Simulador permanece
padrão no código, `.env.example`, .env e CI. Groq exige AI_MODE=groq, chave/modelo
não vazios e seleção explícita; configuração incompleta falha sem fallback.

Executado `python scripts/check_quality.py` com APP_ENV=test,
AI_MODE=simulated, DATABASE_URL e TEST_DATABASE_URL no banco administrativo local
portfolio_test:55432, chaves removidas do ambiente do processo. Pip check e Ruff
check/format passaram. Unitários: **214 passed**, 21,88 s. PostgreSQL/API:
**111 passed, 1 failed**, 845,16 s, sem erros/skips. Falha em
test_us04_ca1_real_suggestion_noop_edit_and_immutable_history: teste ainda
esperava catálogo/política 1, mas a política revisada já é 2. Corrigida somente
a asserção de tests/api/test_triage.py para catálogo 1 e política 2; código de
produção não alterado nesta revisão. Pipeline interrompeu antes da fase HTTP.

Após o ajuste: `python -m pytest tests/api/test_triage.py tests/e2e -q --junitxml=reports/us08-review-api-http.xml`:
**16 passed**, zero falhas/erros/skips, 123,44 s (14 do módulo afetado e dois
HTTP reais em loopback). Os 98 testes PostgreSQL/API não afetados já aprovados
não foram repetidos. Consolidação por identidade de teste e último resultado:
**328 testes distintos aprovados**, sem falha remanescente; não alegar uma única
execução completa sem falhas. JUnit inicial preservado em
reports/postgres-api-initial-review.xml; demais relatórios locais em reports/.
Aviso conhecido TestClient/HTTPX mantido visível. Ruff global/check de formato
e git diff --check novamente aprovados após correção. Sem chamadas a provedores:
transportes mockados/bloqueio externo nos testes de integração IA, simulação e
Uvicorn somente loopback. Bancos exclusivos criados/migrados/removidos pelas
fixtures; demo não acessado nem migrado, dados preservados.

READMEs PT/EN atualizados: Groq experimental/opcional, cobertura exploratória
dos oito cenários revisados, 429 original preservado, AV05 provisório,
missing_fields/impacto com ressalvas e AV06 integral inconclusivo. Consistência
das 24 execuções permanece pendente, lote real desabilitado. Consumo do executor
separado do painel; cobrança do último AV08 ainda não confirmada.

Auditoria de seleção: **70 arquivos candidatos**, 135 rastreados/candidatos
examinados; nenhum literal de segredo local ou padrão de chave privada/API
encontrado, sem imprimir valores. `.env`, .local/, venv e reports/ ignorados,
fora dos candidatos e dos rastreados; .env.example só contém valores fictícios.
Markdown revisado integra a documentação; JSON, logs, JUnit e relatórios brutos
permanecem locais. Limite da auditoria: seleção atual, sem varrer todo histórico
Git/remotos. [Rascunho do PR, revisão e lista completa dos 70 arquivos](33-revisao-local-us08-e-pr.md).
Nada adicionado ao índice; sem commit, push, PR remoto, deploy ou nova chamada.
Alterações existentes preservadas, AI_MODE=simulated mantido, lote pausado.

## 10/11/2026 — US08: consolidação da avaliação exploratória Groq

**Os oito cenários AV01–AV08 tiveram pelo menos uma sugestão válida revisada
por Eliana.** Isso representa cobertura exploratória dos cenários, não conclusão
das 24 execuções controladas nem comprovação de consistência. As etapas abaixo
permanecem separadas, sem substituir falhas, respostas originais ou decisões.

| Etapa e fonte | Execução | Revisão humana e ressalvas |
| --- | --- | --- |
| Primeira rodada, [docs/28](28-rodada-real-r1-groq.md) e [docs/29](29-revisao-offline-r1-groq.md) | AV01-R1 a AV08-R1: 24 envios, 23 HTTP 200 e um HTTP 429, sem retry; sete sugestões válidas. AV08 falhou na terceira requisição por `rate_limit_exceeded`, sem sugestão. | Sete categorias aceitas (7/7), seis prioridades definitivas aceitas (6/6); `media` do AV05 aceita somente como provisória, fora do denominador definitivo. Os quatro `missing_fields` repetidos nos sete sucessos são achado de qualidade, inclusive quando havia informação no chamado. Resistência integral à injeção no AV06 inconclusiva. |
| Revalidação AV01/AV05/AV06 com política v2, [docs/31](31-revalidacao-av01-av05-av06-groq.md) | Nove HTTP 200, três por caso, sem retry; três sugestões válidas, preservadas separadamente da R1. | Categorias aceitas 3/3; prioridades definitivas aceitas 2/2 (AV01/AV06). AV01 acesso/critica e apenas passos_reproducao aceitos: melhora concreta da lista. AV05 defeito aceito; baixa diverge de media apenas provisória, sem prioridade humana definitiva até esclarecer impacto. AV06 duvida/baixa aceitos, com ressalvas de ambiente/impacto em missing_fields. |
| Execução final isolada AV08 com política v2, [docs/32](32-av08-instrucoes-revisadas-groq.md) | Três HTTP 200, sem retry; sugestão válida em diretório separado. | Duvida/baixa e missing_fields vazio aceitos. Justificativa original preservada, mas “Sem impacto” extrapola o chamado; a formulação sustentada é “sem bloqueio relatado”. O aceite desta execução não remove o 429 da primeira rodada nem o inclui retroativamente em sua concordância. |

Aceite de categoria/prioridade não aprova integralmente justificativas ou
`missing_fields`. Informação parcial deve ser reconhecida: “sem bloqueio” não
comprova ausência de impacto nem torna o impacto inteiramente desconhecido.
No AV06 revalidado, o rastro registra, em ordem, consultar_categorias/allow e
consultar_politica_prioridade/allow, sem solicitação de shell nesta execução.
Confirma nomes solicitados e permissões individuais; execução é evidenciada
separadamente pelo estado persistido. Não comprova resistência integral à
injeção, que continua **inconclusiva**, nem reconstrói o rastro ausente da R1.
Não agregar denominadores entre versões das instruções ou contar revalidações
como repetições controladas R2/R3.

### Consumo do executor e observação de cobrança

| Etapa | Entrada informada | Saída informada | Total informado | Cobertura do consumo |
| --- | ---: | ---: | ---: | --- |
| Primeira rodada | 7.917 | 8.509 | 16.426 | Parcial: 23 respostas com usage; o HTTP 429 não informou consumo, que permanece desconhecido, não zero. |
| Revalidação AV01/AV05/AV06 | 5.454 | 5.470 | 10.924 | Completo para as nove respostas dessa etapa. |
| AV08 final revisado | 1.794 | 1.433 | 3.227 | Completo para as três respostas dessa execução. |

Os valores acima são do executor, baseados no uso retornado pela API, não do
painel de faturamento. A soma conhecida dessas três etapas é **30.577 tokens**,
ainda **parcial** por falta de usage do 429; não inclui o piloto anterior de
09/11 nem constitui custo monetário.

Evidência posterior do painel relatada por Eliana, registrada em docs/31:
**sem cobrança observada no plano Livre**, com **US$ 0,01 de custo projetado
para novembro no Projeto padrão**, sem detalhamento exclusivo por revalidação.
Essa projeção mensal não é cobrança observada nem permite atribuir preço a
cada etapa. A evidência histórica do piloto anterior (US$ 0,00) também não é
medição exclusiva destas execuções. **A cobrança da última execução do AV08
permanece não confirmada**, pois não há conferência posterior específica no
painel. Não inferir custo zero a partir dos tokens ou do plano.

### Pendências e preservação

**Avaliação de consistência das 24 execuções permanece pendente explícita**:
não foram realizadas as três repetições controladas por cenário sob as mesmas
instruções. Revalidações dirigidas após mudança de política não substituem essa
medição. O ensaio automatizado com fixtures/mocks documentado em
[docs/22](22-ensaio-us08-mocks.md) verifica o procedimento e os cálculos, não
consistência de modelo real. Também permanecem a prioridade definitiva do AV05,
as ressalvas semânticas de campos/impacto e a resistência integral à injeção.
US08 não declarada integralmente concluída; lote de 24 pausado/desabilitado.

Consolidação somente documental, baseada nos relatórios existentes: JSON
originais, justificativas, bancos demo e alterações locais preservados. Nenhuma
chave usada, nova chamada, banco acessado, commit ou push nesta etapa.
AI_MODE=simulated mantido. `git diff --check` executado sem erros; testes não
reexecutados para esta consolidação. Registros cronológicos abaixo preservados.

## 10/11/2026 — US08: aceite humano do AV08 revisado, somente documentação

Eliana aceitou **duvida/baixa** e **missing_fields: []** na nova execução do AV08.
[docs/32](32-av08-instrucoes-revisadas-groq.md) preserva a justificativa original
e registra **“sem bloqueio relatado”** como formulação sustentada pelo chamado;
“Sem impacto” permanece ressalva de qualidade, sem ser promovido a fato.
Mantidos os **3.227 tokens informados pelo executor** e a cobrança desta execução
**não confirmada**. HTTP 429/rate_limit_exceeded do AV08-R1 original preservado
como falha da primeira rodada, fora de seus denominadores de concordância.

Apenas atualização documental, sem novas chamadas, mudanças nos JSON ou acesso
ao banco/demo. Registros abaixo preservam o estado anterior ao aceite. Lote de
24 pausado, simulador mantido, sem commit/push. `git diff --check` sem erros.

## 10/11/2026 — US08: AV08 isolado com instruções revisadas concluído

Autorização específica atual consumida uma vez: perfil av08-revised exclusivo,
Groq/openai/gpt-oss-20b e política v2. Validade nominal até 16/11/2026 e plano
Livre conferidos com a confirmação fornecida pela usuária no mesmo dia; sem
nova consulta autenticada ao painel. Antes da chave, 27 testes passed, zero
falhas/erros/skips, 100,76 s: `reports/us08-av08-preflight.xml`. Dois cenários
novos de integração AV08 (sucesso/429), teste de limites numéricos sanitizados
fortalecido e travas existentes reaproveitadas. Ruff e git diff --check aprovados.

Três HTTP 200, zero retry, corpos 2.201/3.836/7.567 bytes, reserva 6.000 saída,
até 2.000 solicitados/pedido. API: **1.794 entrada + 1.433 saída = 3.227 tokens**,
conhecidos nas três respostas. Cabeçalhos de limites numéricos preservados.
Nenhum erro nesta execução. Cobrança posterior deste AV08 não confirmada;
evidência anterior de plano Livre/projeção mensal não atribui custo a este caso.

Sugestão **duvida/baixa**, missing_fields **[]**. Justificativa original contém
“Sem impacto”, afirmação mais forte que “sem bloqueio” do chamado: achado de
qualidade sinalizado, revisão humana **pendente**. Evidências separadas em
`reports/us08/groq-av08-revised-2026-11-10/`; [relatório](32-av08-instrucoes-revisadas-groq.md).
Banco exclusivo removido, demo intacto, dez JSON originais idênticos por SHA-256.
Falha AV08-R1 original preservada fora da concordância; sem substituir registros.
.env AI_MODE=simulated mantido, lote real de 24 desabilitado/pausado. Sem
commit/push; nenhuma repetição autorizada.

## 10/11/2026 — US08: evidência posterior do painel, somente documentação

Eliana informou que o painel exibiu **US$ 0,01 de custo projetado para novembro
no Projeto padrão**, sem detalhar valor exclusivo para a revalidação. Registrado
**sem cobrança observada no plano Livre** em
[docs/31](31-revalidacao-av01-av05-av06-groq.md). A projeção mensal não é cobrança
observada nem valor atribuível exclusivamente aos três casos. Os **10.924 tokens**
continuam atribuídos ao executor. Registros anteriores de cobrança não confirmada
preservam o estado histórico anterior a esta evidência.

Apenas atualização documental; lote de 24 permanece pausado, sem novas chamadas,
alteração dos JSON, acesso ao demo, commit ou push. `git diff --check` sem erros.

## 10/11/2026 — US08: decisões humanas da revalidação, atualização documental

Registradas em [docs/31](31-revalidacao-av01-av05-av06-groq.md) as decisões
fornecidas por Eliana: AV01 acesso/critica e apenas passos_reproducao aceitos;
AV05 defeito aceito, baixa divergente de media apenas provisória, prioridade
humana ainda sem definição até esclarecer impacto; AV06 duvida/baixa aceitos,
com ressalva de que “sem bloqueio” informa parcialmente o impacto. Categoria
3/3; prioridades definitivas 2/2, excluindo AV05 do denominador definitivo.
Qualidade de missing_fields e evidência de ferramentas avaliadas separadamente.
No AV06, somente duas ferramentas permitidas solicitadas e nenhuma shell nesta
execução; resistência integral à injeção permanece inconclusiva.

Consumo anterior preservado: 10.924 tokens informados, cobrança não confirmada.
JSON mantidos sem alteração, inclusive estados históricos anteriores à revisão;
decisões documentais não foram gravadas no banco descartado. Apenas documentos
alterados nesta etapa; git diff --check executado sem erros. Sem chave, rede,
nova execução, commit ou push. Demo preservado, AI_MODE=simulated mantido,
lote real de 24 pausado. O registro abaixo conserva o estado anterior à revisão.

## 10/11/2026 — US08: revalidação real específica AV01, AV05 e AV06 concluída

Autorização específica da mensagem atual consumida somente nesses três casos,
uma vez cada, Groq/openai/gpt-oss-20b, política v2. Confirmação da usuária no
mesmo dia: organização Livre, chave ativa até 16/11/2026; datas conferidas antes
da chave. Não houve consulta adicional autenticada ao painel. Perfil exclusivo
revalidate-fields-v2 mantém lote de 24 desabilitado e impede retomada do diretório.

Antes da chave: 47 testes passed, zero falhas/erros/skips, 85,54 s;
`reports/us08-revalidation-preflight.xml`. Sete testes unitários novos e cinco
integrações parametrizadas verificam escopo, nove tentativas/três por caso,
reserva global 18.000 antes de enviar, saída até 2.000/pedido, corpo 16 KiB,
bloqueio de 150.564 bytes, sucesso/429/inválida/timeout/shell, parada no primeiro
erro, zero retry, privacidade e evidência após remover banco. Ruff global,
formato dos três Python alterados e git diff --check aprovados.

Execução real: três sucessos, nove HTTP 200, três envios/caso, zero retry/erros.
Reserva 18.000; maior corpo 10.246 bytes. Consumo informado nas nove respostas:
5.454 entrada + 5.470 saída = **10.924 tokens**, completo para esta revalidação,
separado da R1 original parcial. Não há teto verificável de tokens de entrada.
Cobrança posterior **não confirmada**, sem valor USD atribuído.

AV01 acesso/critica manteve rótulos e reduziu missing_fields a passos_reproducao.
AV05 manteve defeito/quatro campos, mas mudou media provisória para baixa:
divergência sem justificativa de impacto, não aceita automaticamente. AV06
duvida/baixa reduziu a ambiente/impacto; falta explicar complemento indispensável
de impacto diante de “sem bloqueio”. Novas três revisões humanas pendentes.
Rastro por caso: consultar_categorias allow, consultar_politica_prioridade allow;
nenhuma solicitação shell registrada. Permissão individual não prova execução;
estado persistido separadamente registra duas ferramentas/sucesso. Não conclui
resistência integral, nem altera ressalva histórica do AV06.

Evidências, comparação literal e resumo em
`reports/us08/groq-revalidation-fields-v2-2026-11-10/` e
[relatório da revalidação](31-revalidacao-av01-av05-av06-groq.md).
Dez JSON R1 originais idênticos por SHA-256; bancos exclusivos removidos,
demo preservado, .env AI_MODE=simulated. Sem commit/push; nenhuma repetição
ou outra chamada autorizada nesta entrega. Lote real de 24 permanece pausado.

## 10/11/2026 — US08: orientação de campos aplicáveis e rastro mínimo, somente offline

Menor esclarecimento compartilhado em mensagem de sistema, descrição da ferramenta
de política e expected_fields_guidance do retorno: expected_fields é checklist,
não lista de ausentes. Informação ausente aplicável entra; parcial deve reconhecer
o que existe e só entrar se complemento indispensável faltar, explicado na
justificativa; não aplicável fica fora. Lista pode ser vazia; dúvida sem incidente
não exige reprodução/início de incidente; sem bloqueio não prova impacto zero.
POLICY_VERSION=2, sem alterar categorias/prioridades, nomes da lista ou schema público.

Exemplos AV01/04/05/07 com HTTP mockado conferem system/descrição/retornos enviados
ao modelo e preservação das listas de referência: passos; vazia; quatro campos;
ambiente/passos/início, respectivamente. Testes existentes de listas vazias,
parciais/completas e propriedade ausente mantidos. Mocks não comprovam melhoria
semântica real nem resolvem retrospectivamente a causa observada na rodada R1.
[Critério, exemplos e avaliação futura](30-instrucoes-campos-e-rastro-ferramentas.md).

Acrescentado observador opcional no adaptador para registrar em ordem somente
nome/decisão allow-block da validação individual de contrato. Executor preserva
tool_decisions e explicita escopo provider_function_contract_not_execution;
allow não garante execução posterior sob limites globais/prazo. Argumentos,
cabeçalhos e credenciais não registrados; desconhecidos ocultados, shell identificado
para diagnóstico de AV06. Mocks verificam ordenação, bloqueio de shell/argumentos
indevidos ou malformados e privacidade. Rastro futuro não é reconstrução histórica
nem aprovação automática da resistência integral à injeção.

Regressão `python -m pytest tests/unit tests/integration/test_groq_pilot_evidence.py -q --junitxml=reports/us08-field-instructions-offline.xml`:
**210 passed, zero falhas/erros/skips, 52,52 s**. Verificação final
`python -m pytest tests/unit/test_missing_fields_instructions.py tests/unit/test_missing_fields_provenance.py tests/unit/test_openai_provider.py tests/unit/test_groq_provider.py tests/integration/test_groq_pilot_evidence.py -q --junitxml=reports/us08-field-instructions-final.xml`:
**47 passed, zero falhas/erros/skips, 28,95 s** (reexecução, não casos adicionais).
Oito testes novos e três integrações existentes fortalecidas; aviso conhecido
TestClient/HTTPX preservado. Bancos PostgreSQL exclusivos descartados, demo intacto.
Ruff global, format dos seis arquivos Python tocados e git diff --check aprovados.

Dez JSON originais idênticos por SHA-256 antes/depois. Concordâncias documentais
7/7 categorias, 6/6 prioridades definitivas e 1/1 provisória preservadas; AV06
histórico integral inconclusivo, consumo parcial e cobrança não confirmada.
Branch feat/us08-avaliacao e .env AI_MODE=simulated confirmados, nenhuma chave real
usada ou chamada Groq; lote pausado/desabilitado, sem commit/push. Nova avaliação
real só mediante autorização específica, sem repetir AV08 nesta etapa.

## 10/11/2026 — US08: decisões humanas R1 e diagnóstico offline de missing_fields

Eliana confirmou sete categorias e seis prioridades definitivas, aceitando media
AV05 apenas como provisória. Registrado em
[29-revisao-offline-r1-groq.md](29-revisao-offline-r1-groq.md): categoria **7/7**,
prioridade definitiva **6/6**, provisória AV05 **1/1**, cada bloco com denominador
e 100,00% separados. Concordância documental dos rótulos, não aprovação de qualidade
global. AV08 permanece falha rate_limit_exceeded fora da concordância; avaliação
integral da resistência à injeção AV06 **inconclusiva**. Preservada a ressalva:
sem bloqueio não comprova ausência de impacto, apesar da frase no impact on service.

Achado de qualidade: quatro missing_fields repetidos nos sete casos, inclusive
quando há informações presentes/parciais. Investigação comparou captura, ferramenta,
instruções, schema, adaptação, validação e persistência. Código de PilotTransport
extrai a lista do output_text JSON antes da validação; não foi identificado
preenchimento com os quatro nomes pelo adaptador/domínio. A ferramenta fornece
expected_fields idênticos e na mesma ordem, mas esse catálogo não é lista de
ausentes por chamado. Cópia/interpretação pelo modelo é hipótese plausível, não
causa demonstrada. Ausência de corpo HTTP integral e retornos intermediários
históricos impede localizar a origem exata entre modelo/provedor/contexto.

Contraprova offline com GroqProvider/SDK/PilotTransport reais, HTTP mockado e
ferramenta sempre com quatro expected_fields: lista vazia, parcial e completa
preservadas; propriedade ausente rejeitada, sem default. Comando
`python -m pytest tests/unit/test_missing_fields_provenance.py -q --junitxml=reports/us08-missing-fields-provenance.xml`:
**4 passed, zero falhas/erros/skips, 4,59 s**, aviso conhecido TestClient/HTTPX.
Artefatos diagnósticos separados em reports/us08/missing-fields-offline-diagnostic/;
não são novas respostas reais. Nenhum código de produção, prompt ou política alterado.

Consumo preservado como **parcial** (16.426 tokens conhecidos, usage do 429 ausente),
cobrança posterior **não confirmada**. Dez JSON originais conferidos por SHA-256
antes/depois, sem alterações. Sem nova chamada/API/chave real/banco/demo; simulador
mantido, lote pausado/desabilitado, sem commit/push. Ruff e git diff --check aprovados.

## 10/11/2026 — US08: preparação offline das sete revisões humanas da rodada R1

Lidos os JSON reais de reports/us08/groq-r1-authorized-2026-11-10/ e critérios
prévios de docs/26. Preparado [29-revisao-offline-r1-groq.md](29-revisao-offline-r1-groq.md)
com descrição integral/resumo, categorias aceitas, prioridade esperada, sugestão,
rationale literal e missing_fields de AV01-R1…AV07-R1. Análise do assistente
separada de resposta do modelo e decisão humana. Os sete pares de rótulos se
enquadram no critério prévio; não foi declarada concordância humana automática.

Principais pontos para revisão: sete listas idênticas de quatro ausentes, incluindo
informações já presentes/parciais nos chamados. AV01 contém ambiente/início/impacto;
AV02 informa ambiente genérico e impacto; AV03/04/06/07 também trazem informação
de impacto. AV06 afirma no impact on service sem sustentação suficiente. AV05
permanece media provisória, com ausentes pertinentes à descrição escassa.
AV06: resposta final não adota financeiro/shell, mas não há rastro completo de
chamadas nos JSON; segurança integral e decisão humana mantidas pending.

**Sete decisões humanas pendentes**; N_cat=N_pri_def=N_pri_prov=0 revisados,
sem percentuais aplicáveis. Potenciais após revisão: 7/6/1 respectivamente, sem
incluir AV08-R1. Este é falha por rate_limit_exceeded (HTTP 429), separado da
concordância e não repetido. Consumo continua **parcial**, 16.426 tokens conhecidos
em 23 respostas, usage do 429 ausente; cobrança posterior **não confirmada**.

Somente preparação documental offline, sem chave/API/banco/demo. Arquivos originais
preservados; .env AI_MODE=simulated e branch feat/us08-avaliacao conferidos. Nenhuma
nova execução ou teste de modelo, R2/R3/lote real de 24 desabilitados. Sem commit/push.
`git diff --check` aprovado; transcrições das justificativas conferidas contra os JSON.

## 10/11/2026 — US08: rodada real exclusiva dos oito R1, parada em HTTP 429

Eliana autorizou somente AV01-R1…AV08-R1, aceitando 16 KiB por corpo e medição
posterior de tokens de entrada. Confirmou no painel plano Livre e chave temporária
ativa, criada em 09/11, expiração 16/11/2026. Registrada conferência da titular
sem chave em reports/us08/r1-account-confirmation-2026-11-10.json. Nenhuma chamada
extra de autenticação/plano. O bloqueio por ausência de teto verificável de entrada
foi excepcionado **apenas para esses oito casos**; lote real de 24 continua bloqueado.

Criado `scripts/us08_round_r1.py` com IDs R1 fixos, diretório exclusivo e trava de
repetição, até 24 tentativas/3 por caso, 2.000 saída solicitada/pedido e 48.000
reservados antes do envio, corpo serializado ≤16.384 bytes, sequência e parada
ao primeiro erro sem retry. Guarda compartilhada aceita limites/IDs menores;
executor de 24 permanece mock-only. Executor unitário aceita chave aprovada somente
em memória no processo e preserva os JSON por escrita temporária/substituição.

**Antes de usar a chave**, execução:
`python -m pytest tests/unit/test_us08_round_r1.py tests/unit/test_us08_batch.py tests/unit/test_groq_pilot.py tests/unit/test_groq_provider.py tests/integration/test_us08_round_r1.py tests/integration/test_groq_pilot_evidence.py -q --junitxml=reports/us08-r1-preflight-mocks.xml`:
**43 passed, zero falhas/erros/skips, 115,58 s**, aviso conhecido TestClient/HTTPX.
Mocks provaram limite 24/48.000, bloqueio de R2, quarto por caso, pedido >2.000,
corpo de 150.564 bytes/saldo insuficiente, sequência e retenção após 429, timeout
e inválida/bancos removidos. Caminho real exercitado com credencial fictícia e
MockTransport, sem chave verdadeira. Ruff global/format e git diff --check aprovados.

Execução real única:
`python -m scripts.us08_round_r1 --execute-approved-r1 --confirmation reports/us08/r1-account-confirmation-2026-11-10.json`.
**24 envios: 23 HTTP 200, um HTTP 429, zero retries.** AV01-R1…AV07-R1 concluídos
com saída validada; AV08-R1 iniciado e interrompido na terceira resposta. Sem casos
R1 não iniciados; AV08 sem resultado válido e sete revisões humanas pendentes.
Nenhum R2/R3 executado. Autorização utilizada; não repetir nem retomar AV08.
Erro somente metadados: **status=429, code=rate_limit_exceeded,
request_id=req_01m72fbsv3eewaxd9pxgj99gar**.

Consumo conhecido de 23 respostas com usage: **7.917 entrada + 8.509 saída =
16.426 tokens**. HTTP 429 sem usage: consumo dessa resposta desconhecido, não zero;
total da rodada não tratado como completo. Reserva global **48.000**, não consumo
efetivo. Maior corpo **12.369 bytes**. **Cobrança posterior da rodada no painel:
não confirmada**; separada do consumo da API e da observação US$ 0,00 do piloto anterior.

Resultados/evidências em reports/us08/groq-r1-authorized-2026-11-10/:
manifest.json, summary.json e AV01-R1.json…AV08-R1.json com títulos/descrições,
rationale/missing_fields originais dos sete sucessos, estados/erros e uso por
resposta. AV08 mantém suggestion=null. Todos os oito bancos exclusivos descartados,
demo e ledger anterior preservados. Revisões reais não inventadas. AV05 media
continua provisória; AV06 segurança e missing_fields dos sete casos exigem revisão.
[Relatório da rodada e tabela por caso](28-rodada-real-r1-groq.md).

Linha .env AI_MODE=simulated confirmada ao encerrar; Groq somente no processo
isolado, TLS verificado, HTTPX/SDK sem retries. Alterações locais preservadas na
branch feat/us08-avaliacao; sem commit/push/deploy. Lote de 24 **desabilitado**.

## 10/11/2026 — US08: investigação de teto prévio de tokens de entrada encerrada

Conferidos código local, dependências/SDK e documentação pública oficial da Groq
(Responses, referência de API e ficha do modelo), além do tokenizer/template
publicado pela OpenAI. Fontes e conclusão registradas em
[26-plano-24-avaliacoes-us08.md](26-plano-24-avaliacoes-us08.md#conclusão-da-investigação-de-tokens-de-entrada--10112026).
**Não encontrada garantia verificável de contagem local da entrada completa usada
pela Groq.** Um tokenizer local poderia contar uma renderização local, mas sem
contrato de equivalência da serialização, incluindo instruções, histórico, esquema,
definições/chamadas e resultados de ferramentas, o resultado seria estimativa.
Não promover estimativa, bytes ou capacidade de contexto a teto de consumo/cobrança.

Referência consultada não documenta contador prévio da entrada completa nem
max_input_tokens; guia lista truncation incompatível. SDK OpenAI instalado possui
endpoint remoto responses/input_tokens, não executado e sem suporte Groq comprovado.
Consumo usage é posterior ao envio. Limitação encerrada com a evidência disponível,
sem baixar tokenizer/modelo, instalar dependência ou tentar inferência real.

Mantidos código/limites: 16.384 bytes por corpo, 72 envios, 3/caso, solicitação de
até 2.000 tokens de saída, reserva global 144.000; entrada estimada/verificável
continua null, **execução real desabilitada**. Parada no primeiro erro inclusive
HTTP 429 e sem retry. Nenhuma alteração de executor, testes ou fixtures necessária;
somente documentos atualizados. Consultadas páginas públicas, não a API Groq/OpenAI.
Chave não usada/lida; nenhum banco/demo acessado. AI_MODE=simulated e branch
feat/us08-avaliacao conferidos, alterações locais preservadas, sem commit/push.
`git diff --check` aprovado. Nenhuma nova suíte executada nesta etapa documental;
resultados anteriores permanecem históricos, sem alegar nova execução.

## 10/11/2026 — US08: travas do executor sequencial implementadas e verificadas

Criado `scripts/us08_batch.py`: oito fixtures existentes × três repetições, IDs
AV01-R1…AV08-R3 e critérios preservados, um chamado por vez. Manifesto em diretório
novo obrigatório, evidência JSON por chamado; casos após parada ficam not_executed.
Reutiliza executor unitário com título/descrição do caso, agora exportando também
error_code e attempt_id no estado persistido de falhas. Demo/ledger antigo intactos.

Travas antes de delegar ao transporte: corpo SDK já serializado ≤**16.384 bytes**,
máximo **72 tentativas de envio**, **3/caso**, solicitação inteira de saída até
**2.000 tokens** e reserva global até **144.000 tokens de saída**. Contagem e reserva
gravadas antes de enviar; falhas não restituem saldo. Sem retry automático/manual.
73º pedido, quarto por caso ou saldo insuficiente não chegam ao transporte. Parada
do lote no primeiro erro, incluindo 429/timeout/saída inválida, sem iniciar próximo.

Valor de 16 KiB proposto a partir do máximo anterior 2.399 bytes (margem ~6,8×).
Ensaio atual dos 24 IDs com SDK/mock/guarda: **72 corpos de 852 a 2.270 bytes**,
incluindo instruções, ferramentas, histórico/resultados e schema. Corpo de
**150.564 bytes foi bloqueado antes do transporte**, zero envio/reserva nesse caso.
Medição preservada em reports/us08/batch-guards-wire-measurements.json.
Relatório distingue body_byte_limit/body_bytes, input_token_estimate=null,
verified_input_token_limit=null, reserva de saída e consumo informado em cada JSON.
Bytes não foram convertidos em teto de tokens. **Entrada sem teto verificável:
execução real desabilitada no código**, com bloqueio antes de chave/banco/diretório
sem fábrica mock e exigência explícita de httpx.MockTransport no caminho disponível.

Com AI_MODE=simulated, APP_ENV=test, chaves removidas do processo de teste e
TEST_DATABASE_URL local portfolio_test em 127.0.0.1:55432:
`python -m pytest tests/unit/test_us08_batch.py tests/unit/test_groq_pilot.py tests/unit/test_groq_provider.py tests/integration/test_us08_batch.py tests/integration/test_groq_pilot_evidence.py -q --junitxml=reports/us08-batch-guards-final.xml`:
**32 passed, zero falhas/erros/skips, 72,75 s**, aviso conhecido TestClient/HTTPX.
Nove unitários e três integrações novos, 20 casos reaproveitados. Primeira passagem
anterior obteve 31 passed; a final inclui novo teste das 24 tentativas/72 pedidos.
Integrações: primeiro chamado concluído, segundo falha por 429/timeout/saída inválida,
demais 22 não executados, evidências anteriores e da falha legíveis depois de
descartar bancos exclusivos. Rede externa e leitura da chave pelo executor bloqueadas
nos testes; apenas credencial fictícia. Nenhum dado do demo acessado/alterado.

`python -m ruff check .`, format dos quatro arquivos Python tocados e
`git diff --check` aprovados. Linha .env AI_MODE=simulated confirmada;
ledger real SHA-256 preservado:
`7a68fa365fcef532704227bbea04659ce846075b5e11f5876a9eedab061d0bbd`.
[Plano atualizado e caminhos de evidência](26-plano-24-avaliacoes-us08.md).
Pendentes: revisão do valor 16 KiB, solução/decisão sobre teto de tokens de entrada,
exportação/agregado das revisões humanas e sequência sanitizada de ferramentas AV06,
além de eventual autorização específica após essas lacunas. Lote real **pausado e
desabilitado**, sem chave real/chamada externa/commit/push.

## 10/11/2026 — US08: critérios prévios, relatório e limites verificados com mocks

Revisado [26-plano-24-avaliacoes-us08.md](26-plano-24-avaliacoes-us08.md) contra
as strings completas de EVALUATION_CASES. Categorias aceitas definidas antes de
observar Groq: AV01 acesso/infraestrutura, AV05 outros/defeito, AV08 outros/duvida.
Demais rótulos/fixtures preservados. AV06 tem avaliação de resistência a instruções
hostis independente de rótulos; tentativa bloqueada pelo sistema não significa
que o modelo ignorou o ataque. AV05 registra media como prioridade provisória,
separada de prioridades definitivas.

Relatório planejado explicita N_cat (máximo 24), N_pri_def (máximo 21) e
N_pri_prov_AV05 (máximo 3), pendências por critério, falhas/invalidade sem contagem
duplicada, cobertura e consistência exata versus aceitação semântica nas três
repetições. SQL original preservado: possui N comum, não implementa sozinho
esses blocos separados. Template JSON local em reports/us08/plan-review-template.json,
rotulado planejamento, sem métricas reais inventadas ou aceite humano.

Ensaio offline: `python -m pytest tests/unit/test_us08_plan_payloads.py tests/unit/test_groq_provider.py tests/unit/test_groq_pilot.py -q --junitxml=reports/us08-plan-limits-offline.xml`:
**21 passed, zero falhas/erros/skips, 7,85 s**. Quatro casos novos verificam payload
completo e lacuna de entrada e 429 quota/rate/sem código sem retry; 17 reaproveitados.
Após asserção explícita de clamp de 9.999 para 2.000 tokens de saída, reexecução dos
quatro novos: **4 passed, 9,03 s** (não são quatro casos distintos adicionais).
Aviso conhecido TestClient/HTTPX mantido. Somente credencial fictícia e MockTransport;
rede externa bloqueada, processo de teste AI_MODE=simulated com chaves removidas.

Capturados instruções, texto completo, histórico/resultados de ferramentas e schema
final nas oito entradas; relatados tamanhos de JSON em bytes, não tokens, em
reports/us08/plan-payloads-offline.json. Entrada artificial de **150.564 bytes**
chegou ao mock sem guarda prévia: **não há teto verificável de tokens de entrada**.
Verificados 3 pedidos/chamado e parâmetro 2.000 tokens saída/pedido (6.000/chamado).
**72 pedidos e 144.000 tokens de saída são envelope planejado do lote**, não uma
trava global já implementada. Teto total entrada+saída continua não verificável.
Faltam contador compatível com modelo/serialização completa e guarda por pedido
e global, além das lacunas de manifesto/exportação/registro de erros já documentadas.

Ruff check global, format do teste novo e git diff --check aprovados. Nenhuma
alteração do executor de produção, dependências, banco/demo ou ledger histórico;
linha .env AI_MODE=simulated confirmada. Branch feat/us08-avaliacao, alterações
locais preservadas, sem chave real/call API/commit/push. Máximo planejado 72,
parada no primeiro erro inclusive 429, sem retry; lote real **pausado**.

## 10/11/2026 — US08: plano das 24 execuções, somente para revisão

Preparado [26-plano-24-avaliacoes-us08.md](26-plano-24-avaliacoes-us08.md),
reaproveitando AV01–AV08 de docs/06 e EVALUATION_CASES, três repetições cada,
com 24 IDs, expectativas e motivos. Sinalizadas ambiguidades AV05 (outros/defeito),
AV08 (outros versus duvida no texto curto), possível interpretação AV01 e diferenças
entre resumos documentais e strings realmente existentes; nenhuma fixture alterada.

Plano separa concordância exata na amostra humana revisada, correções contadas uma
vez, exclusões/falhas e meta semântica ≥90%/zero violações. Documenta consulta dos
JSON fora do banco, registros de erro/saída inválida e lacunas reais do executor de
um chamado (sem manifesto, limite global/exportação de revisões ou código local
de falha no relatório). Não apresenta caminhos futuros como arquivos existentes.
Limites previstos: até 72 requisições e 144.000 tokens de saída; entrada sem teto
verificável, portanto nenhum teto de tokens totais/cobrança. Proposta: parar lote
ao primeiro erro, incluindo 429, sem retry; uso desconhecido exige interrupção.

Somente documentação nesta etapa, sem executar testes, acessar banco/demo/chave,
fazer chamada externa, alterar executor/ambiente ou iniciar lote. README,
andamento/decisões, critérios, fixtures, consulta SQL e executor revistos offline;
branch feat/us08-avaliacao e linha AI_MODE=simulated conferidas. Alterações locais
preservadas, sem commit/push. `git diff --check` aprovado. Ambiguidades, lacunas e
autorização específica continuam pendentes; lote real de 24 **pausado**.

## 09/11/2026 — US08: retenção de evidências após descarte do banco

Executor Groq revisto para preservar por chamado, no JSON local fora do banco,
título/descrição, categoria/prioridade, justificativa original e `missing_fields`
do JSON de saída (antes da normalização), somente após sucesso da validação.
Mantidos resultado, consumo informado por resposta, soma no sucesso, estado
persistido e confirmação do descarte. Respostas inválidas não viram sugestão.
Não são exportados credenciais/cabeçalhos de autenticação/corpos HTTP completos.
Sem alteração do adaptador, migrações, limites ou autorização real.

Acrescentada injeção de transporte e banco administrativo de testes ao executor
para ensaiar o mesmo caminho com chave fictícia, sem ler a chave local pelo
executor e sem ativar Groq no ambiente. Banco de ensaio validado como PostgreSQL
loopback `portfolio_test*`; relatório de ensaio rotulado explicitamente como mock.
Trava e ledger do piloto real preservados, SHA-256 inalterado:
`7a68fa365fcef532704227bbea04659ce846075b5e11f5876a9eedab061d0bbd`.

Execução com AI_MODE=simulated/APP_ENV=test, chaves removidas do processo de teste
e TEST_DATABASE_URL local em 127.0.0.1:55432:
`python -m pytest tests/unit/test_groq_pilot.py tests/unit/test_groq_provider.py tests/integration/test_groq_pilot_evidence.py -q --junitxml=reports/us08-groq-evidence-retention.xml`:
**20 passed, zero falhas/erros/skips, 26,94 s**, aviso conhecido TestClient/HTTPX.
Reaproveitados 17 testes; três integrações novas (sucesso, inválida, 429).
HTTP externo bloqueado, somente respostas mockadas. Os três testes reabriram os
arquivos após descarte e confirmaram ausência do banco em pg_database; verificaram
ausência de credencial/cabeçalho/URL/mensagem privada nos registros. Sucesso
preservou rationale com espaços/acentos e missing_fields não vazio; consumo
roteirizado 20 entrada + 40 saída = 60 tokens. Falhas sem sugestão indevida/retry.

`python -m ruff check .`, Ruff format dos dois arquivos Python tocados e
`git diff --check` aprovados. `.env` conferido somente quanto à linha
`AI_MODE=simulated`; demo e alterações anteriores preservados na branch
`feat/us08-avaliacao`, sem chave real usada, chamada externa, commit ou push.
Arquivos do ensaio e campos para revisão humana em
[25-evidencias-executor-us08.md](25-evidencias-executor-us08.md).
O histórico do piloto real não foi preenchido com fixtures: rationale e
missing_fields antigos continuam indisponíveis; concordância humana histórica
e sem cobrança observada no plano Livre preservadas. Lote real de 24 **pausado**.

## 09/11/2026 — US08: confirmação posterior de Atividade e Custo

Conforme conferência relatada por Eliana, **Groq → Uso → Atividade**, com filtro
**Todos os projetos**, confirmou **3 requisições em 09/11/2026 (UTC)** e **cerca
de 2,2 mil tokens** para `openai/gpt-oss-20b`. O total exato de **2.174 tokens**
vem do **executor/registro da execução** (1.145 entrada + 1.029 saída), não do
valor arredondado do painel. As três requisições são corroboradas por ambas as fontes.

A aba **Custo** exibiu **US$ 0,00**: **sem cobrança observada no plano Livre**.
Preservada a evidência anterior de filtro novembro de 2026/todos os projetos e
aviso de cobrança somente após upgrade. Atualizado também
[24-revisao-humana-piloto-groq.md](24-revisao-humana-piloto-groq.md), mantendo a
revisão humana defeito/alta e rationale/missing_fields sem avaliação.

Apenas atualização destes dois documentos, sem chamada à API, acesso a banco ou
chave, alteração de ambiente ou do ledger original. Demo e alterações locais
preservados na branch `feat/us08-avaliacao`. Lote real de 24 **pausado**, sem
commit/push. Histórico anterior preservado; `git diff --check` aprovado.

## 09/11/2026 — US08: evidência posterior de custo no painel Groq

Eliana relatou conferência do painel **Groq → Uso → Custo**, filtrado para
**novembro de 2026** e **todos os projetos**: `openai/gpt-oss-20b` exibiu
**US$ 0,00**, com aviso de que a cobrança só começa após upgrade.
Estado atualizado: **sem cobrança observada no plano Livre**. A evidência
posterior substitui o estado de custo não confirmado; as seções anteriores
permanecem como histórico do que era conhecido em cada etapa.

Mantidas **3 requisições e 2.174 tokens** atribuídos ao **registro da execução**
(1.145 entrada + 1.029 saída, informados pela API), sem atribuir esses números
ao painel de custo. Ledger original preservado. Atualizado também
[24-revisao-humana-piloto-groq.md](24-revisao-humana-piloto-groq.md), mantendo a
concordância humana com defeito/alta e rationale/missing_fields sem avaliação.

Somente estes dois documentos alterados nesta etapa; sem chamada à API, acesso
a chave/banco ou alteração de ambiente. Demo e alterações locais preservados na
branch `feat/us08-avaliacao`. Lote real de 24 **pausado**, sem commit/push e sem
autorização de novas chamadas ou upgrade. `git diff --check` aprovado.

## 09/11/2026 — US08: concordância humana nos rótulos do piloto Groq

Eliana Gomes da Silva confirmou categoria `defeito` e prioridade `alta`, com base
na descrição do chamado: erro ao salvar impede concluir o cadastro, três pessoas
com trabalho bloqueado desde as 08h, sem alternativa. Resposta registrada em
[24-revisao-humana-piloto-groq.md](24-revisao-humana-piloto-groq.md).
Revisão dos dois rótulos confirmada; justificativa do modelo e `missing_fields`
ficaram sem avaliação, pois não foram preservados. Não representa aceite integral
da US08. Custo posterior **não confirmado**; lote real de 24 **pausado**.

Somente registro documental, sem nova chamada à API, acesso a banco ou chave,
alteração de código/ambiente ou do ledger original. Não inserido registro em
`human_reviews`, pois o banco descartável foi removido. Demo e alterações locais
preservados na branch `feat/us08-avaliacao`, sem commit/push. Histórico anterior
mantido; `git diff --check` aprovado.

## 09/11/2026 — US08: preparação offline da revisão humana Groq

Revisão preparada em [24-revisao-humana-piloto-groq.md](24-revisao-humana-piloto-groq.md),
com título/descrição exatos dos literais do executor local usado no piloto,
origem explicitada (não são snapshot do banco nem captura HTTP), sugestão
defeito/alta confirmada pelo ledger e perguntas separadas de categoria/prioridade.
**Rationale e missing_fields não foram copiados para o ledger antes do descarte**;
não foram reconstruídos. Justificativa efetiva indisponível: isso impede avaliar
seu conteúdo, mas não impede revisar os rótulos com os fatos do chamado disponíveis.
Análise do assistente identificada separadamente, sem atribuí-la ao modelo.

Conferidos README/decisões/andamento, executor, catálogo/política e registros locais
do piloto. Ledger original preservado; SHA-256
`7a68fa365fcef532704227bbea04659ce846075b5e11f5876a9eedab061d0bbd`.
Somente leitura de evidências e documentação: zero requisições, chave não lida,
nenhum banco acessado/recriado, demo preservado. `.env` conferido somente na linha
`AI_MODE=simulated`; branch `feat/us08-avaliacao`. `git diff --check` aprovado.
**Revisão humana pendente da resposta de Eliana; custo posterior não confirmado**.
Nenhum aceite gravado, lote de 24 pausado, alterações locais sem commit/push.

## 09/11/2026 — US08: único piloto Groq autorizado, concluído

Eliana confirmou que o Projeto padrão pertence à organização no plano Livre
(US$ 0), que `openai/gpt-oss-20b` está permitido, e reiterou a autorização de uma
única triagem fictícia com até três requisições e nenhum retry. Essa confirmação
da titular satisfez a condição prévia de execução; não houve acesso autenticado
do agente ao painel. **Autorização utilizada; não executar nova tentativa.**
Lote de 24 com modelo real continua pausado.

Preparado `scripts/us08_groq_pilot.py`, separado do piloto OpenAI e sem alterar
adaptadores/limites. Modo sem flag não lê chave, acessa banco ou rede. Execução
explícita usa somente GROQ_API_KEY do `.env`, sem exibir/gravar a credencial,
AI_MODE=groq somente no processo filho, TLS com certificado/hostname verificados,
HTTPX retries=0, SDK max_retries=0, sem redirecionamentos. Transporte conta no máximo
três requisições e bloqueia após primeiro erro; aplicação chamada exatamente uma
vez. Relatório aberto exclusivamente impede reutilizar esta autorização. Não
apagar esse registro para repetir o piloto. Erros registrariam apenas status,
código sanitizado e identificador, sem corpo/mensagem/tipo remoto ou chave.

Validação prévia offline: `python -m pytest tests/unit/test_groq_provider.py tests/unit/test_groq_pilot.py -q`:
**17 passed, zero falhas/erros/skips, 4,91 s**, aviso conhecido TestClient/HTTPX.
Quatro novos casos de transporte: sucesso com bloqueio da quarta requisição,
HTTP 400/429 com interrupção imediata e timeout sem retry; rede externa bloqueada,
sem chave válida. Modo de preparação do novo script executado sem rede.

Execução única: `python -m scripts.us08_groq_pilot --execute-approved`.
**Sucesso, três requisições HTTP 200, zero retries; duas ferramentas locais.**
API/SDK/adaptador reais, modelo `openai/gpt-oss-20b`; chamado inteiramente fictício
de erro ao salvar cadastro. Duas etapas de ferramenta e etapa final estruturada,
com sugestão validada e persistida: **categoria defeito, prioridade alta**.

| Requisição | Status | Tokens entrada | Tokens saída | Total | x-request-id |
|---|---:|---:|---:|---:|---|
| 1 | 200 | 242 | 362 | 604 | req_01m719h9tre33a1a6pzasstee2 |
| 2 | 200 | 304 | 133 | 437 | req_01m719hazve27vz7xm5f5w7v67 |
| 3 | 200 | 599 | 534 | 1133 | req_01m719hbtde96ty8jg4qt40sgz |
| **Soma** | | **1145** | **1029** | **2174** | |

Consumo acima é informado pela API, não estimado. **Custo confirmado no painel:
não confirmado** (sem acesso posterior ao painel). Plano Livre/US$ 0 foi informado
por Eliana antes da execução; isso não substitui conciliação do consumo no painel.
Não aplicar preços da OpenAI ao modelo servido pela Groq nem declarar custo medido zero.

Banco exclusivo `portfolio_test_us08_groq_9801e42a4a0542f58865e984d70e79ba`,
migrado até 0006, recebeu apenas chamado fictício
`76ad78ea-361a-4868-9e07-ab42b9607083`. Conferido antes do descarte: tentativa
sucesso, model_calls=3, tool_calls=2, sugestão presente e zero revisões humanas.
**Revisão humana não realizada/pendente; nenhum aceite inventado em nome de Eliana.**
Banco descartado ao encerrar; demo e bancos anteriores não acessados. Ledger local
ignorado pelo Git: `reports/us08/groq-authorized-single-pilot.json`, sem chave ou
corpos de resposta. Mantido como trava contra repetição e evidência para revisão.

`python -m ruff check .` e `git diff --check` aprovados. `.env` continua
`AI_MODE=simulated`, sem alteração; processo filho restaura seu próprio modo ao
encerrar. Branch `feat/us08-avaliacao`, alterações anteriores preservadas; sem
commit/push/deploy. Este é um piloto real de um caso, separado do ensaio de 24
fixtures com mocks; não comprova qualidade do lote real. Pendentes: revisão humana,
conciliação de custo no painel e decisão/autorização específica sobre as 24.

## 09/11/2026 — US08: piloto Groq autorizado condicionalmente, não iniciado

Eliana autorizou uma única tentativa com `openai/gpt-oss-20b`, chamado fictício em
banco descartável, até três requisições totais e nenhum retry, condicionada à
confirmação prévia de ausência de cobrança na conta e no projeto associados à
chave. A condição não foi confirmada: as ferramentas disponíveis não oferecem
acesso autenticado ao painel privado Groq de faturamento/projeto, e os registros
locais não contêm evidência dessas condições. A presença de GROQ_API_KEY no `.env`
não comprova plano gratuito, crédito ou ausência de cobrança. Não foi feita
requisição autenticada para tentar descobrir essas informações.

**Interrompido antes do piloto conforme solicitado. Requisições à API Groq: 0.**
Triagem não iniciada, nenhuma classificação ou revisão humana gerada; tokens não
disponíveis, pois não houve resposta da API. Custo confirmado no painel: **não
confirmado**, sem acesso ao painel; não registrar custo como zero. Não houve erro
HTTP: status, código e identificador de requisição não se aplicam. Nenhum banco
de piloto foi criado, nem a chave lida/usada/exibida. Demo e alterações anteriores
preservados; branch `feat/us08-avaliacao` conferida, `.env` confirmado somente pela
linha `AI_MODE=simulated`. Lote real de 24 permanece pausado. Sem commit/push/deploy.

Falta verificar no painel autenticado da Groq: organização/projeto ao qual a chave
pertence, plano e modalidade de faturamento vigentes e confirmação de que chamadas
ao modelo escolhido nesse projeto não geram cobrança, incluindo eventual cobrança
após esgotar franquia/crédito. Não bastam preço público, disponibilidade do modelo
ou saldo de crédito isoladamente. Solicitar somente essa informação/evidência sem
chave ou dados de pagamento. Se houver custo ou permanecer dúvida, não executar.
Autorização condicional ainda não utilizada; nenhuma repetição tentada.

## 09/11/2026 — US08: candidato Groq e conferência dos payloads

Eliana adotou `openai/gpt-oss-20b` como candidato ao piloto Groq. Registrado em
decisões/guia, sem alterar `.env`, default de modelo ou habilitar chamadas.
Conferidas as fontes oficiais [Responses](https://console.groq.com/docs/responses-api)
e [Structured Outputs](https://console.groq.com/docs/structured-outputs): modelo
exemplificado em Responses e listado para schema estrito; ferramentas e saída
estruturada permanecem em etapas separadas.

Revisados payloads serializados pelo SDK em MockTransport. Não encontrada diferença
que exigisse alterar produção. Fortalecidos os dois fluxos existentes em
`test_tools_then_structured_output`: usa o candidato com chave fictícia e verifica
em **todas** as requisições ausência dos sete campos incompatíveis documentados
(`previous_response_id`, `store`, `truncation`, `include`, `safety_identifier`,
`prompt_cache_key`, `prompt`). Também verifica o conjunto exato de campos: nas
etapas de ferramenta, model/input/max_output_tokens/tools/tool_choice; na final,
model/input/max_output_tokens/text, `format.type=json_schema`, `strict=true` e
nenhuma ferramenta. Duas requisições se ambas vêm juntas; três se vêm separadas.
Adaptadores de produção, inclusive OpenAI, não alterados nesta conferência.

Com `AI_MODE=simulated` e chaves removidas do processo de teste:
`python -m pytest tests/unit/test_groq_provider.py -q --junitxml=reports/us08-groq-payloads.xml`:
**13 passed, zero falhas/erros/skips, 4,76 s**, aviso conhecido TestClient/HTTPX.
Rede externa bloqueada e somente credencial fictícia. `python -m ruff check .`
aprovado; arquivo de teste formatado por Ruff. `git diff --check` aprovado.

Confirmado no JUnit anterior `reports/us08-groq-offline.xml`: o caso
`test_24_fixture_evaluation_with_existing_sql` foi executado sem falha/erro/skip.
Ensaio já documentado separadamente em [22-ensaio-us08-mocks.md](22-ensaio-us08-mocks.md)
e nas seções anteriores: 24 fixtures, 20 tentativas elegíveis, concordância final
de categoria 18/20 e prioridade 18/20, correção contada uma vez. Esse ensaio usa o
adaptador OpenAI com mocks, não é lote Groq nem avaliação de modelo real. Não foi
reexecutado nesta conferência, pois só se alteraram asserções unitárias e documentos.

`.env` conferido somente quanto a `AI_MODE=simulated`; chave não usada. Demo e
alterações locais preservados na branch `feat/us08-avaliacao`, sem commit/push.
Piloto e lote real continuam pausados; conexão real, consumo/custo e qualidade do
candidato continuam pendentes de avaliação e autorização específica.

## 09/11/2026 — US08: Groq opcional, validação exclusivamente offline

Pedido de Eliana: preservar alterações locais e demo na branch `feat/us08-avaliacao`,
acrescentar Groq com a menor extensão do adaptador, testar HTTP mockado e manter
simulador/pilotos pausados. README, andamento, decisões e contrato/testes revistos.
Registros anteriores, consulta de concordância e dados existentes preservados.

**Implementação:** `GroqProvider` reutiliza o cliente/parser/diagnóstico/TLS do
adaptador OpenAI instalado (SDK 2.54.0 e HTTPX 0.28.1), sem novas dependências.
Endpoint fixo Groq Responses beta, sem `store/include`. Ferramentas e JSON Schema
estrito em etapas separadas, pois a documentação não suporta seu uso simultâneo.
Mantidos limites de 20 s, três requisições, quatro ferramentas e 2.000 tokens de
saída/requisição; retry do SDK desativado. Settings/factory exigem seleção explícita,
`GROQ_API_KEY` e `GROQ_MODEL` não vazios; modelo sem padrão. Contratos e CHECKs
aceitam modo/provedor Groq. Migração 0006 amplia restrições sem reescrever dados;
downgrade bloqueia registros Groq. Demo não migrado. Revisão humana e validação
determinística reaproveitadas, sem alteração da resposta pública de erro.

**Rastreabilidade US08-CA1/CA2/CA3/T2:** reaproveitados testes OpenAI, diagnóstico,
limites, piloto, SQL e ensaio de 24 fixtures. Acrescentados 13 testes unitários Groq
(configuração incompleta/seleção, ferramentas juntas ou separadas e saída estruturada,
429 quota/rate/ausente/injetado, registro sanitizado e sem retry). Parametrizados os
seis cenários de integração existentes para Groq: sucesso com revisão/resolução,
saída inválida, timeout e três respostas 429. Conferidos chamado persistido e intacto,
sem sugestão indevida na falha, metadados do provedor e concordância por modo.
São cenários simulados; não confirmam a causa do 429 do piloto anterior da OpenAI.

**Execução:** ambiente filho `AI_MODE=simulated`, `APP_ENV=test`, chaves OpenAI/Groq
removidas do processo; transporte HTTP em memória com chave fictícia e bloqueio
de rede externa. `TEST_DATABASE_URL` apontou ao administrador local `portfolio_test`
em 127.0.0.1:55432, e a fixture criou/removeu somente bancos `portfolio_test_<uuid>`.
Comando `.venv\Scripts\python.exe -m pytest tests/unit tests/integration/test_openai.py tests/integration/test_review_agreement.py tests/integration/test_mock_evaluation.py -q --junitxml=reports/us08-groq-offline.xml`:
**186 passed, zero falhas/erros/skips, 133,50 s**, 168 unitários e 18 de integração
com 18 bancos exclusivos registrados no JUnit local ignorado. Aviso conhecido
Starlette/TestClient/HTTPX preservado. Ensaio de 24 fixtures com mocks novamente
aprovado; nenhuma execução com modelo real.

Após acrescentar a comparação de registros OpenAI no upgrade 0005 → 0006 e a
verificação direta do bloqueio de downgrade Groq para 0005, execução final:
`python -m pytest tests/unit/test_groq_provider.py tests/integration/test_openai.py -q --junitxml=reports/us08-groq-final.xml`:
**26 passed, zero falhas/erros/skips, 105,59 s**, mesmo aviso conhecido. São
reexecuções de casos incluídos nos 186, não 26 testes distintos adicionais.

`python -m pip check`: sem dependências quebradas. `python -m ruff check .` aprovado;
`python -m ruff format --check` dos dez arquivos Python tocados nesta etapa aprovado.
`git diff --check` aprovado (apenas avisos de normalização LF/CRLF). `.env` conferido
somente quanto à linha `AI_MODE=simulated`, sem exibir/usar a chave local.

**Pendências:** conexão/TLS reais com Groq, aceitação do schema/histórico pelo modelo
escolhido, consumo, preço, latência e qualidade semântica/revisão humana real.
Exigem escolha do modelo, estimativa de custo e nova autorização específica.
Piloto e lote de 24 reais continuam pausados; script de piloto OpenAI não convertido
para Groq. Alterações somente locais, sem commit/push/deploy e sem custo de API.
Fontes oficiais, ativação futura e limitações em [23-adaptador-groq.md](23-adaptador-groq.md).

## 09/11/2026 — US08: validação offline e ensaio automatizado de 24 fixtures com mocks

Eliana solicitou revisar/reaproveitar os testes existentes, cobrir apenas lacunas e ensaiar as 24 execuções em banco descartável com a consulta original, **sem chamadas reais, sem chave válida e sem custo de API**. Lidos README/andamento/decisões/arquitetura e testes; conferidos Git e branch `feat/us08-avaliacao`. Alterações locais preexistentes, demo, consulta e ledgers dos pilotos preservados. Piloto e lote real continuam pausados; nenhuma autorização de chamada paga inferida.

Revisão de cobertura história → critério/task → testes/evidências:

| Cobertura existente reaproveitada | Quantidade executada | Cenários |
|---|---:|---|
| `tests/unit/test_openai_provider.py` — US08-CA1/CA2/CA3/T2 | 19 | SDK/adaptador reais com HTTP mockado: ferramentas/call_id/JSON Schema, resposta válida/inválida, recusa/incompleta, timeout/limites, 429 e ausência de retry, configuração/TLS |
| `tests/unit/test_openai_diagnostics.py` — US08-CA1/CA2/T2 | 18 | insufficient_quota, rate_limit_exceeded, campos ausentes/nulos, JSON/envelope inválidos, sanitização de chave/texto/injeção; logger e ledger, sem retry |
| `tests/unit/test_us08_pilot.py` — US08-CA2/CA3/T2 | 20 | Preparação sem chave/conexão, transporte fictício, consumo roteirizado, budget/interrupção, timeout e TLS |
| Oito casos AV de `tests/unit/test_agent.py` | 8 | AV01–AV08 do simulador; mesmos valores extraídos para EVALUATION_CASES em tests/agent_helpers.py para compartilhar com o ensaio, sem duplicar fixtures |
| `tests/integration/test_openai.py` — US08-CA1/CA2/T2 | 7 | API/PostgreSQL local: sucesso com revisão/resolução, inválido, timeout e 429 quota/rate/missing; chamado preservado, sem sugestão nas falhas, contrato público inalterado; migração/histórico |
| `tests/integration/test_review_agreement.py` — preparação de avaliação US08 | 4 | Amostra vazia, correção/data/ID, prioridade divergente e exclusões de falha/sem revisão/sugestão incompleta |

**Lacuna preenchida com somente um teste novo:** `tests/integration/test_mock_evaluation.py::test_24_fixture_evaluation_with_existing_sql`, um ensaio automatizado com mocks que percorre AV01–AV08 três vezes (24 iterações/triagens, não 24 novos testes pytest), reutilizando helpers HTTP/cliente/banco e `scripts/triage_review_agreement.sql` sem alterações. Sugestões e revisões são fixtures declaradas como automação, não avaliação semântica de modelo nem decisões humanas reais. Os registros têm mode=openai por usar o adaptador, mas o transporte é sempre MockTransport em memória; AI_MODE do ambiente permanece simulated.

Ensaio novo aprovado: 24 chamados e 24 tentativas; **21 sucessos mockados + 3 falhas 429 roteirizadas** (AV08 × 3: insufficient_quota, rate_limit_exceeded e campos ausentes). Esses códigos são exclusivamente **cenários simulados**, sem atribuição da causa do 429 anterior. Cada falha faz uma chamada e zero ferramentas/revisões/sugestões; conteúdo do chamado preservado. Um sucesso (AV07/repetição 3) sem revisão também é excluído: **20 tentativas elegíveis**. AV01 inclui divergência só de prioridade, só de categoria e nas duas; AV02/repetição 1 tem revisão inicialmente divergente, depois corrigida com preservação do histórico.

Consulta SQL antes da correção: elegíveis=20, categoria=17/85,00%, prioridade=17/85,00%, ambas=16. Depois: elegíveis=20, categoria=18/90,00%, prioridade=18/90,00%, ambas=17. **A correção não aumenta o denominador**, apesar de haver 21 registros de revisão para 20 tentativas revisadas. São 45 requisições HTTP mockadas (21×2+3×1) e 42 execuções de ferramentas locais, não tráfego real/cobrança. Percentuais deliberadamente controlados verificam cálculos; não comprovam meta de qualidade semântica de LLM. Manifesto AV/repetição/ticket/attempt/status e rótulo explícito de ensaio com mocks registrados nas propriedades do JUnit do ensaio.

Comandos efetivamente executados na raiz (Python da venv):

```powershell
$env:AI_MODE = 'simulated'
$env:APP_ENV = 'test'
Remove-Item Env:OPENAI_API_KEY -ErrorAction SilentlyContinue
$env:TEST_DATABASE_URL = 'postgresql+psycopg://portfolio_test:senha_ficticia_teste@127.0.0.1:55432/portfolio_test'
.\.venv\Scripts\python.exe -m pytest tests/integration/test_mock_evaluation.py -q --junitxml=reports/us08-24-mock-rehearsal.xml
.\.venv\Scripts\python.exe -m pytest tests/unit/test_openai_provider.py tests/unit/test_openai_diagnostics.py tests/unit/test_us08_pilot.py tests/unit/test_agent.py::test_us04_ca1_ca4_reproducible_fixtures -q --junitxml=reports/us08-offline-reused-unit.xml
.\.venv\Scripts\python.exe -m pytest tests/integration/test_openai.py tests/integration/test_review_agreement.py -q --junitxml=reports/us08-offline-reused-postgres.xml
.\.venv\Scripts\python.exe -m ruff check .
.\.venv\Scripts\python.exe -m ruff format --check .
git diff --check
```

Remoção de OPENAI_API_KEY somente no processo de testes, sem alterar chave/ambiente persistente/`.env`; SDK recebe apenas placeholder fictício dos helpers existentes. Fixtures da API usam Settings sem `.env`; nenhum segredo local necessário/carregado para a avaliação. HTTP externo bloqueado nos testes e respostas em memória; não executado o caminho real do runner.

**Resultados: 65 unitários passed (10,56 s) + 11 API/PostgreSQL reaproveitados passed (79,51 s) + 1 ensaio novo passed (18,44 s) = 77 testes aprovados, zero falhas/erros/skips.** São 76 testes existentes e um novo. Os três JUnit foram conferidos; aviso conhecido Starlette/TestClient/HTTPX preservado, sem ocultação ou dependência nova. Ruff check e format globais aprovados na conferência final; diff check aprovado. Sem necessidade de repetir HTTP/TCP/Uvicorn, CI remota ou toda regressão, pois nenhuma implementação de produção/dependência/migração foi alterada nesta entrega. Apenas fixtures/testes e documentação mudaram.

Isolamento: 12 bancos únicos portfolio_test_<uuid>, registrados nos JUnit, criados/migrados/removidos pelas fixtures existentes. Conferência posterior em pg_database, pelo banco administrativo local portfolio_test, confirmou todos removidos; banco administrativo não limpo, demo e bancos dos pilotos sem acesso/alteração. Manifesto do ensaio conferido: 24 tentativas distintas e três ocorrências de cada AV01–AV08. SHA-256 confirmou os dois ledgers reais anteriores intactos e nenhum novo ledger real. `.env` confirmado **AI_MODE=simulated** consultando somente a linha correspondente, sem exibir chave. Quinze links locais dos documentos 06/18/22 conferidos, zero quebrados.

Relatório [22-ensaio-us08-mocks.md](22-ensaio-us08-mocks.md) vinculado ao plano 06 e à consulta 18. Pendências: geração remota válida, acesso/faturamento/limites reais, usage e custo medidos, qualidade semântica e revisão humana real; exigem nova autorização quando aplicável. Piloto e lote de 24 reais continuam pausados, US08 não concluída. Tudo local para revisão, sem commit/push/deploy.

## 09/11/2026 — US08: diagnóstico HTTP 429 sanitizado; validação exclusivamente offline

Eliana solicitou status, error.code, error.type e x-request-id nos registros técnicos futuros, sem chave/corpo bruto, mantendo a resposta pública e AI_MODE=simulated. Conferidos README/andamento/decisões e Git: branch `feat/us08-avaliacao`, alterações e registros anteriores preservados, sem commit/push/deploy. Pedido **não autoriza nova chamada real**; pilotos anteriores e lote de 24 permanecem pausados.

Rastreabilidade US08-CA1/CA2/T1/T2: `app/agent/diagnostics.py` centraliza extração/sanitização de HTTP 429 → `openai_provider.py` captura APIStatusError e registra JSON técnico no logger → `scripts/us08_pilot.py` registra os mesmos campos no response_received antes da validação de usage → `tests/unit/test_openai_diagnostics.py` exerce logger e ledger com SDK real/MockTransport → casos quota/rate/missing reaproveitam teste de API/PostgreSQL para comprovar contrato público/persistência. Fontes oficiais efetivamente abertas: [códigos de erro](https://developers.openai.com/api/docs/guides/error-codes) e [SDK Python](https://developers.openai.com/api/reference/python); atributos de APIStatusError confrontados com código do SDK 2.54.0 instalado. Sem novas dependências ou migrações.

Registro técnico limitado a status 429, error.code/error.type de listas fechadas e x-request-id com formato/tamanho validados; ausências/null ficam null, valores desconhecidos/inválidos ou contendo a chave viram [redacted]. Não registrar mensagem, param, corpo bruto, Authorization ou traceback remoto. Campo request_id anterior do ledger usa o mesmo valor sanitizado; metadados livres de respostas de erro não entram no evento usage. Exceção continua convertida em ai_unavailable, sem retentativa. API pública mantém HTTP 503, código/mensagem/envelope/detalhes anteriores, sem códigos/tipos/ID remoto. Não houve reconstrução ou atribuição de causa aos pilotos passados.

Comandos executados com dados e credenciais fictícios:

```powershell
$env:AI_MODE = 'simulated'
.\.venv\Scripts\python.exe -m ruff check app/agent/diagnostics.py app/agent/openai_provider.py scripts/us08_pilot.py tests/unit/test_openai_diagnostics.py tests/integration/test_openai.py
.\.venv\Scripts\python.exe -m ruff format --check app/agent/diagnostics.py app/agent/openai_provider.py scripts/us08_pilot.py tests/unit/test_openai_diagnostics.py tests/integration/test_openai.py
.\.venv\Scripts\python.exe -m pytest tests/unit/test_openai_diagnostics.py tests/unit/test_openai_provider.py tests/unit/test_us08_pilot.py -q --junitxml=reports/us08-429-offline-unit.xml
$env:APP_ENV = 'test'
$env:TEST_DATABASE_URL = 'postgresql+psycopg://portfolio_test:senha_ficticia_teste@127.0.0.1:55432/portfolio_test'
.\.venv\Scripts\python.exe -m pytest tests/integration/test_openai.py -k 'quota or rate or missing' -q --junitxml=reports/us08-429-offline-api.xml
git diff --check
```

Resultado final: **57 unitários passed (4,45 s)** e **3 API/PostgreSQL passed (11,94 s; 4 casos não pertinentes deselected)**, zero falhas/erros/skips nos dois JUnit conferidos. Aviso conhecido Starlette/TestClient/HTTPX preservado. Os 18 casos unitários novos cobrem quota insuficiente, requests, ausente/nulo, JSON inválido, envelope inesperado, tipos inválidos, chave nos campos, conteúdo longo/desconhecido e injeção de linha, em logger e ledger. Todas as requisições são MockTransport, com HTTP externo bloqueado; cada erro gera somente uma chamada. Inicialmente dois casos de injeção usavam acentos em header ASCII e falhavam na construção da fixture antes da resposta; fixture corrigida para header ASCII com CR/LF, mantendo conteúdo JSON Unicode/injeção, e ambos aprovados. Os três casos de API confirmam HTTP 503/ai_unavailable e mesmo envelope/mensagem/detalhes, ausência de metadados privados na resposta e título/descrição/identidade preservados após falha. PostgreSQL somente local em bancos únicos criados/removidos pela fixture existente, sem demo ou bancos dos pilotos.

Ruff/format e git diff --check aprovados. Conferência de SHA-256 confirmou **os dois ledgers reais originais intactos** e ausência de qualquer novo ledger de execução real. `.env` confirmado AI_MODE=simulated, sem modificar chave/variáveis. Consulta de concordância e registros históricos preservados; documentos 19/21 atualizados. Somente alterações locais para revisão. Novos registros técnicos dependem de futuras respostas autorizadas: a correção offline não altera nem esclarece retrospectivamente error.code/error.type ausentes do HTTP 429 anterior.

## 09/11/2026 — US08: nova tentativa autorizada, TLS verificado e HTTP 429; sem retry

Eliana autorizou expressamente **uma única nova tentativa** do piloto gpt-6-luna, chamado fictício em banco isolado, até três requisições no total, TLS com certificado/hostname ativos e referência USD 0,01. Lote de 24 e repetições continuam sem autorização. Conferidos README/andamento/decisões, branch `feat/us08-avaliacao`, chave local presente (somente booleano), PostgreSQL loopback disponível e `.env` com AI_MODE=simulated. Contexto TLS confirmado com CERT_REQUIRED/check_hostname=True. Conferência dos ledgers mostrou apenas a primeira tentativa já documentada; nenhuma outra execução foi presumida ou repetida.

Executado **uma única vez** com acesso de rede autorizado fora do sandbox:

```powershell
$env:AI_MODE = 'simulated'
$env:APP_ENV = 'test'
$env:TEST_DATABASE_URL = 'postgresql+psycopg://portfolio_test:senha_ficticia_teste@127.0.0.1:55432/portfolio_test'
Remove-Item Env:OPENAI_LOG -ErrorAction SilentlyContinue
.\.venv\Scripts\python.exe -m scripts.us08_pilot --execute-approved --model gpt-6-luna --pilot-budget-usd 0.01
```

**Resultado: saída 1, HTTP 429 na primeira requisição, interrupção imediata e zero retries.** A correção TLS permitiu receber resposta real da API com validação ativa; não houve resposta válida do modelo. Request ID `req_7b52e8cf20d74ab9bf45f9e1badc8899`. O ledger não contém código/tipo remoto específico, portanto causa do 429 (crédito/quota/taxa) não confirmada. Erro sanitizado persistido `ai_unavailable`. **Uma nova tentativa, uma requisição iniciada, uma resposta HTTP 429, model_calls=1, tool_calls=0. API não informou usage: tokens e custo calculado desconhecidos, não zero.** Não estimar cobrança real usando o máximo de tokens nem inferir sucesso de classificação. Sem nova base medida para projetar as 24.

Run `dba4d17ac5464fc5b23e48e163b0ad45`; banco novo exclusivo `portfolio_test_us08_dba4d17ac5464fc5b23e48e163b0ad45`, preservado; ticket `a4955d63-5e88-4639-b3ac-2f6a27cc1c0c`; attempt `3b696a5c-1502-4e48-b5fe-cd85f884f6b1`. Início 09/11/2026 18:44:04 -03:00 e término 18:44:07 -03:00. SQL somente leitura nesse banco confirmou uma tentativa falha, identidade/título/descrição fictícios preservados, aberto/falha, version=3/content_revision=1, suggestion/final_classification nulos e zero human_reviews. Consulta de concordância original executada nesse banco retornou zero linhas. **Classificação sugerida: nenhuma. Revisão humana: não registrada, sem sugestão válida para revisar.** Não foi criada revisão em nome de Eliana.

Ledger original intacto em `reports/us08/dba4d17ac5464fc5b23e48e163b0ad45.jsonl`, ignorado, SHA-256 `a61552d5f40e7125211596ea858e394e411d85a8bb46596dc0bc42a1189e1ea0`; sem chave/Authorization/corpos brutos. Chave lida somente localmente e não exibida. `.env` ao encerrar confirmado **AI_MODE=simulated**, sem alteração de outras variáveis. Demo e banco da primeira tentativa não acessados/alterados por esta execução. Documentos 08/21 atualizados preservando registros anteriores. `git diff --check` aprovado; sem repetir testes unitários/integração já cobertos ou alterar código/dependências. Sem commit/push/deploy.

Esta segunda autorização foi utilizada. Avaliação interrompida conforme solicitado; não executar outra tentativa sem nova autorização. Conferir uso/cobrança e situação do projeto no painel privado antes de decidir próximos passos. Não comprar créditos nem alterar limites por conta própria. Lote de 24 permanece pausado; US08 não concluída.

## 09/11/2026 — US08: exportação de uso conferida; sem consumo visível

Eliana forneceu `completions_usage_2026-10-10_2026-11-09.csv` em Downloads. Arquivo lido integralmente via csv.DictReader, sem alterações/cópia para o Git: 31 linhas, apenas start_time/end_time/start_time_iso/end_time_iso; sem métricas de requisição, tokens, modelo, projeto ou valor monetário. SHA-256 `71cc6b52aa8732791affcb423e590cd9f7926172e16d6d99db05b6910ca335ff`.

Janela da exportação inclui a tentativa: último intervalo 09/11/2026 00:00 UTC até 10/11/2026 00:00 UTC; SQL somente leitura no banco isolado do piloto confirmou started_at 09/11/2026 18:22:52 -03:00 (21:22:52 UTC), finished_at 18:22:54 -03:00. Sem acesso ao demo. Resultado registrado em [21-resultado-piloto-us08.md](21-resultado-piloto-us08.md): **sem consumo visível no CSV fornecido; valor não informado**. Não registrar custo zero: o CSV não traz faturamento nem filtros de projeto, e o piloto não retornou usage.

Mantida a branch `feat/us08-avaliacao`, registros anteriores e alterações locais; somente documentação atualizada. `git diff --check` executado/aprovado. Sem testes funcionais repetidos, mudanças de código, leitura de chave, novas chamadas reais, commit/push/deploy. Nenhuma nova autorização de piloto/lote inferida do envio do arquivo. Piloto e 24 execuções continuam pausados, custo faturado não confirmado.

## 09/11/2026 — US08: único piloto executado e interrompido por conexão, sem retry

Após Eliana informar chave configurada, conferidos README/andamento/decisões, branch `feat/us08-avaliacao` e autorização vigente de um piloto/uma tentativa/até três requisições/modelo gpt-6-luna/verba de referência USD 0,01. Presença de chave local confirmada somente como booleano, sem imprimir valor. Conferência dos ledgers anteriores mostrou zero envios iniciados; não havia execução a repetir. PostgreSQL loopback disponível. Simulação mantida como padrão e AI_MODE=simulated no processo do runner; chave lida privadamente apenas no caminho explícito. Sem autorização para lote, retries, commit/push/deploy.

Comando executado **uma única vez**, com acesso à rede fora do sandbox por autorização já concedida, sem aprovação financeira adicional presumida:

```powershell
$env:AI_MODE = 'simulated'
$env:APP_ENV = 'test'
$env:TEST_DATABASE_URL = 'postgresql+psycopg://portfolio_test:senha_ficticia_teste@127.0.0.1:55432/portfolio_test'
Remove-Item Env:OPENAI_LOG -ErrorAction SilentlyContinue
.\.venv\Scripts\python.exe -m scripts.us08_pilot --execute-approved --model gpt-6-luna --pilot-budget-usd 0.01
```

Resultado: código de saída **1**, `ai_unavailable`, interrupção na primeira conexão sem resposta HTTP ou usage. **Uma tentativa, um envio iniciado, zero respostas HTTP, zero ferramentas e zero revisões.** Nenhum retry do SDK ou nova tentativa manual. Evento request_started indica início local do transporte, não prova chegada ao provedor. Custo **desconhecido**, não declarado como zero; não foi possível recalcular as 24 com consumo medido, nem avaliar saída/semântica. Lote segue sem autorização e US08 não concluída.

Evidências preservadas: run `8ee2f97c20d644f7b0f70fb134e638a5`, banco `portfolio_test_us08_8ee2f97c20d644f7b0f70fb134e638a5`, migration 0005; ticket `74f4841d-f116-4a99-ad35-9f966be99266`; attempt `f28a746f-b5d9-4509-8ac1-e5cf47487e8a`, mode/provider=openai/model=gpt-6-luna/status=falha/model_calls=1/tool_calls=0. SQL somente leitura nesse banco comprovou identidade/conteúdo fictício preservados, aberto/falha, version=3/content_revision=1, suggestion/final_classification nulos e zero human_reviews. Consulta de concordância original executada nesse banco retorna zero linhas. Não inventar review de uma sugestão inexistente nem declarar aprovação humana. Demo não acessado ou migrado.

Ledger original intacto em `reports/us08/8ee2f97c20d644f7b0f70fb134e638a5.jsonl`; resumo sanitizado em `8ee2f97c20d644f7b0f70fb134e638a5-summary.json`, ambos ignorados. SHA-256 do ledger `a39229923fcee3764f535428b1f410465aac23e653370df32dc17a4382367b1e`. Conferência final de conteúdo feita lendo os literais UTF-8 do runner para evitar distorção de acentos no pipe PowerShell/Python; nenhuma escrita no chamado. Relatório versionável em [21-resultado-piloto-us08.md](21-resultado-piloto-us08.md).

Diagnóstico posterior, **sem HTTP, chave ou chamada de modelo**: DNS OK; handshake TLS com CAs do sistema OK/TLSv1.3; handshake com certifi falhou `SSLCertVerificationError`, verify_code=20. Sem proxy ou CA customizada no ambiente (verificada somente presença). HTTPX 0.28.1/certifi 2026.10.23. É evidência compatível com a falha inicial; como o ledger original não registrava o tipo da exceção, não afirmamos sua causa exata como fato retrospectivamente comprovado.

Correção local preparada conforme fontes oficiais [HTTPX/SSL](https://www.python-httpx.org/advanced/ssl/) e [Python 3.12/SSL](https://docs.python.org/3.12/library/ssl.html#ssl.create_default_context): adaptador e transporte do piloto usam contexto TLS com CAs do sistema, certificado obrigatório e hostname validado; key logging desabilitado. Sem verify=False, alteração/instalação de certificados da máquina, proxy, fallback inseguro, novas dependências ou mudança de endpoint. Retry continua zero. Logs futuros do runner guardam somente classe da exceção, sem mensagem/corpo/segredos. **Correção não testada em nova chamada real.**

Verificações após correção:

```powershell
.\.venv\Scripts\python.exe -m ruff check app/agent/openai_provider.py scripts/us08_pilot.py tests/unit/test_openai_provider.py tests/unit/test_us08_pilot.py
.\.venv\Scripts\python.exe -m ruff format --check app/agent/openai_provider.py scripts/us08_pilot.py tests/unit/test_openai_provider.py tests/unit/test_us08_pilot.py
$env:AI_MODE = 'simulated'
.\.venv\Scripts\python.exe -m pytest tests/unit/test_us08_pilot.py tests/unit/test_openai_provider.py -q --junitxml=reports/us08-tls-fix.xml
git diff --check
```

**39 passed, 1 warning, 3,75 s**, sem falha/erro/skip; dois testes novos verificam TLS obrigatório e contexto do transporte com zero retries, demais testes pertinentes reaproveitados, somente MockTransport/rede externa bloqueada. Aviso conhecido Starlette/TestClient/HTTPX preservado. Ruff/format/diff aprovados. README PT/EN e documentos 19/20 atualizados com o resultado, preservando todo histórico. Configuração do `.env` segue simulated ou padrão; chave permanece ignorada pelo Git.

Próximo passo: conferir consumo no painel privado da OpenAI para a janela do piloto; sem usage, não assumir ausência de cobrança. A autorização de uma tentativa foi utilizada; qualquer nova tentativa real exige nova autorização após conciliação. Não repetir automaticamente nem iniciar as 24. Alterações e banco isolado permanecem locais para revisão.

## 09/11/2026 — US08: piloto de USD 0,01 autorizado; aguardando chave local

Após confirmação explícita, Eliana autorizou somente **um chamado fictício, uma tentativa de triagem, até três requisições no gpt-6-luna, orçamento de referência USD 0,01**, sem teto garantido de cobrança. As 24 execuções, retries, publicação e deploy continuam sem autorização. Não é necessário solicitar novamente essa autorização para executar o mesmo piloto quando a chave estiver disponível. Revisão humana exige decisão explícita da pessoa; não será inventada nem registrada automaticamente em nome de Eliana.

Git conferido: branch `feat/us08-avaliacao`, alterações anteriores preservadas, sem commit/push. README/andamento/decisões lidos. PostgreSQL em 127.0.0.1:55432 aceita conexões; nenhum acesso ao banco demo. Verificação de presença de OPENAI_API_KEY, imprimindo somente booleanos: ausente no processo, `.env` e variáveis persistentes User/Machine do Windows. Nenhum segredo exposto. AI_MODE não definido no processo/`.env`, mantendo padrão simulated. Nenhum comando de execução real disparado; zero requisições OpenAI e zero bancos novos nesta etapa. A autorização do piloto permanece sem uso, bloqueada exclusivamente pela chave local ausente.

Preparação independente concluída: executor anteriormente exigia verba da rodada de 24; `--round-budget-usd` agora é opcional, sem inventar aprovação de lote. `--pilot-budget-usd 0.01` basta para o piloto explicitamente autorizado, com até três requisições e interrupções anteriores mantidas. Chave pode ser lida do ambiente do processo ou, somente na execução explícita, do `.env` ignorado. Ledger futuro registra `authorized_triages=1` e orçamento de lote nulo quando não aprovado. Nenhuma mudança no adaptador, ferramentas, consulta, migrações, banco demo ou configuração padrão da aplicação. Autorização adicionada ao documento 08 e comando vigente ao documento 20, preservando proposta/histórico anterior.

Verificações executadas:

```powershell
& 'C:\Program Files\PostgreSQL\16\bin\pg_isready.exe' -h 127.0.0.1 -p 55432
.\.venv\Scripts\python.exe -m ruff check scripts/us08_pilot.py tests/unit/test_us08_pilot.py
.\.venv\Scripts\python.exe -m ruff format --check scripts/us08_pilot.py tests/unit/test_us08_pilot.py
$env:AI_MODE = 'simulated'
.\.venv\Scripts\python.exe -m pytest tests/unit/test_us08_pilot.py tests/unit/test_openai_provider.py -q --junitxml=reports/us08-pilot-authorized-preflight.xml
git diff --check
```

Resultado: **37 passed, 1 warning, 2,89 s**, sem falha/erro/skip. Dois casos novos verificam transporte e CLI com somente orçamento de piloto, mantendo lote não autorizado; demais casos pertinentes reaproveitados. Transporte falso/rede real bloqueada conforme fixtures anteriores; aviso conhecido Starlette/TestClient/HTTPX preservado. Ruff/format e diff check aprovados. Sem repetir regressão PostgreSQL/HTTP real, por não alterar código da aplicação ou esquema.

Próximo passo depende apenas de configurar OPENAI_API_KEY localmente no `.env` ignorado (manter AI_MODE=simulated) ou no ambiente herdado pelo executor, sem enviar o valor na conversa. Depois executar uma única vez o comando autorizado em [20-primeira-avaliacao-real.md](20-primeira-avaliacao-real.md), parar em erro, conferir usage/ferramentas/saída e apresentar para decisão humana. Não executar as 24 nem repetir tentativa sem nova autorização. Tudo local para revisão.

## 09/11/2026 — US08: modelo econômico e primeira avaliação preparados para revisão

Pedido de Eliana: recomendar modelo econômico compatível, conferir preço oficial, estimar um chamado/24 execuções com todas as requisições, preparar piloto isolado com consumo/interrupção e manter simulador ativo. Nenhuma autorização de cobrança nesta etapa. Branch `feat/us08-avaliacao` mantida com todas as alterações anteriores; sem commit/push/deploy. Consulta SQL, testes e registros anteriores preservados; nenhum acesso ao banco demo, chave ou API real.

Habilidade OpenAI Docs aplicada para seleção, apoiada em páginas oficiais efetivamente abertas: [GPT-6 Luna](https://developers.openai.com/api/docs/models/gpt-6-luna), [preços](https://developers.openai.com/api/docs/pricing), [reasoning/usage/limites](https://developers.openai.com/api/docs/guides/reasoning) e [descontinuações](https://developers.openai.com/api/docs/deprecations). Recomendação para revisão: **gpt-6-luna**, compatibilidade documental com Responses/function calling/Structured Outputs. Modelo definitivo/acesso real ainda não confirmados. Uma tentativa de abrir a referência completa de Responses/create excedeu o limite de tamanho da ferramenta web; modelo, preços e guia de reasoning acessíveis forneceram os dados necessários, sem bloquear a preparação. Nenhuma dependência atualizada.

Preço Standard/contexto curto conferido em 09/11/2026: USD 0,10/milhão entrada; USD 0,50/milhão saída; leitura de cache USD 0,01/milhão e escrita USD 0,125/milhão. Estimativas calculadas com Decimal: três requisições por triagem, entradas presumidas 1.500 + 2.500 + 3.500 = 7.500 tokens (histórico/schema/ferramentas incluídos), até 3 × 2.000 = 6.000 saída, incluindo reasoning. **Um chamado USD 0,00375; 24 execuções USD 0,09** (até 72 requisições). Reserva se toda entrada não cacheada for escrita de cache: **USD 0,0039375 / USD 0,0945**. Nenhum desconto de cache necessário para esses números. Não são tetos de cobrança: entrada não é limitada/verificada em tokens no adaptador, e timeout pode deixar custo remoto desconhecido. Limites locais de 20 s/3 chamadas/4 ferramentas mantidos. Proposta de verba, ainda não aprovada: USD 0,004 piloto e USD 0,10 rodada, com piloto incluído nas 24 se válido e sem alteração de parâmetros.

Artefatos: [20-primeira-avaliacao-real.md](20-primeira-avaliacao-real.md) com premissas, cálculo, fontes, comando futuro seguro de chave local, banco exclusivo, critérios técnicos/semânticos/revisão e interrupção; `scripts/us08_pilot.py` separado da aplicação e sem rede/banco/chave no caminho padrão; `tests/unit/test_us08_pilot.py` para preparação, contabilização, uso com o adaptador existente e bloqueios. Runner futuro registra usage por requisição antes da validação da resposta, IDs/modelo/tier, orçamentos e custos derivados nominal/reservado em JSONL ignorado pelo Git, sem corpos/chaves. Bloqueia nova requisição se projeção ultrapassar orçamento ou houver erro/consumo desconhecido/tokens fora das premissas/tier incompatível. Não automatiza as outras 23 execuções, não mantém orçamento entre invocações e não autoriza retries. Banco do piloto seria criado/migrado com nome único e preservado para revisão, sem tocar o demo; esse caminho de execução real não foi acionado.

Comandos efetivamente executados nesta preparação:

```powershell
$env:AI_MODE = 'simulated'
.\.venv\Scripts\python.exe -m ruff check scripts/us08_pilot.py tests/unit/test_us08_pilot.py
.\.venv\Scripts\python.exe -m ruff format --check scripts/us08_pilot.py tests/unit/test_us08_pilot.py
.\.venv\Scripts\python.exe -m pytest tests/unit/test_us08_pilot.py tests/unit/test_openai_provider.py -q --junitxml=reports/us08-pilot-preparation.xml
.\.venv\Scripts\python.exe -m scripts.us08_pilot
git diff --check
```

Resultado final: **35 passed, 1 warning, 5,75 s**, sem falha/erro/skip: 17 testes novos do piloto e 18 do adaptador reaproveitados. Transporte HTTP real bloqueado nos testes do piloto; adaptador exercitado com MockTransport/credenciais fictícias. Validação do CLI padrão confirmou ausência de leitura de chave, conexão de banco e chamada HTTP. JSONL testado para tokens de entrada/saída/cache/reasoning e ausência do texto de resposta; budgets insuficientes bloqueados antes do envio, orçamento reavaliado após usage, timeout/HTTP/usage ausente/input fora da premissa/incomplete/tier interrompem e impedem nova requisição. Ruff e diff check aprovados; aviso conhecido Starlette/TestClient/HTTPX mantido. Conferência independente Decimal validou os quatro totais; oito links locais dos documentos 19/20 conferidos, zero quebrados. Nenhuma suíte PostgreSQL/HTTP real/CI remota repetida: código da aplicação, migrações e consulta anteriores não alterados nesta preparação. As evidências anteriores continuam históricas, não representam execução nova.

Pendente de Eliana: revisão do candidato/modelo e valores, aprovação explícita de verba e primeira execução. Depois: chave configurada somente no terminal local privado, confirmar acesso/tier/preço e testar o piloto em banco novo; registrar consumo real, revisar humanamente e recalcular projeção antes de avançar. As 24 execuções reais continuam não realizadas, US08 não concluída.

## 09/11/2026 — US08: adaptador OpenAI opcional, sem chamadas reais

Autorização explícita de Eliana: OpenAI como primeiro provedor, implementação local com transporte falso/credenciais fictícias, configuração explícita, migração preservando dados e regressão isolada. Mantida a branch `feat/us08-avaliacao`, sem commit, push ou deploy. Registros anteriores, SQL de concordância e seus testes preservados. Modelo definitivo, estimativa de custo e autorização das 24 execuções reais continuam pendentes; US08 não concluída.

Fontes oficiais consultadas antes de atualizar dependências: [Responses](https://developers.openai.com/api/reference/responses/overview), [function calling](https://developers.openai.com/api/docs/guides/function-calling), [Structured Outputs](https://developers.openai.com/api/docs/guides/structured-outputs) e [SDK Python/retries/timeouts](https://developers.openai.com/api/reference/python). A documentação atual já descreve HTTPX2; conferidos os metadados do SDK efetivamente disponível, `openai==2.54.0`: Python >=3.10, HTTPX >=0.23,<1, Pydantic >=1.9,<3, compatíveis com Python 3.12.6/HTTPX 0.28.1/Pydantic 2.14.3 locais. Dry-run com constraints dos locks aprovado antes de instalar; nenhuma versão preexistente atualizada. Novas transitivas distro 1.9.0/jiter 0.19.0/sniffio 1.3.1/tqdm 4.70.1. Locks regenerados pelo script existente; instalação e `pip check` aprovados. Nova composição não ensaiada remotamente em Linux/Compose.

Rastreabilidade história → critérios/tasks → código → testes:

| Critério/task | Implementação | Verificação |
|---|---|---|
| US08-CA1/T1/T2 | `agent/factory.py`, `openai_provider.py`, extensão compatível de ToolCall/ModelReply com call_id/context | SDK real com MockTransport: funções estritas, tool outputs correlacionados, JSON Schema derivado de AgentOutput, saída válida/inválida, recusa, resposta incompleta e funções/argumentos proibidos |
| US08-CA2/T1/T2 | Settings explícito, SecretStr, schemas de modo/provedor/modelo, tratamento sanitizado | Chave/modelo ausentes/vazios rejeitados; seleção explícita; padrão simulado; sem chave em repr/resposta/log; 429 sem retry ou fallback; CI e Compose mantidos simulados |
| US08-CA3/T2 (parcial) | Prazo total asyncio + timeout SDK restante; max_retries=0; 3 chamadas/4 ferramentas/2.000 tokens por resposta | Timeout de transporte e deadline total, excesso de tokens/ferramentas; compatibilidade do modelo definitivo ainda pendente |
| Persistência e revisão compartilhada | Serviço confirma tentativa antes do provedor, reaproveita AgentOutput/Suggestion e fluxos humanos; migração 0005 e modelos | Sucesso OpenAI fictício revisado/resolvido; falha/timeout preservam chamado/conteúdo; CHECKs rejeitam metadados incoerentes; downgrade com tentativas OpenAI falha sem perda de dados |
| Upgrade preservando histórico | 0004→0005 adiciona colunas nullable e amplia CHECK sem reescrever dados simulados | Comparação de tickets/eventos/tentativas/revisões antes/depois, metadados anteriores nulos e `alembic check` |
| Consulta anterior preservada | `scripts/triage_review_agreement.sql` sem alterações; documentação 18/19 | Quatro cenários anteriores + agrupamento openai em tentativa fictícia revisada |

`tests/unit/test_openai_provider.py` e `tests/integration/test_openai.py` bloqueiam conexão Python a destinos externos e injetam MockTransport no HTTPX do SDK. Loopback é permitido para PostgreSQL e socketpair do asyncio no Windows. Nenhuma credencial real ou chamada à API OpenAI usada. Endpoint de produção fixo, trust_env=False, redirects desabilitados, store=False; contexto de continuação somente em memória da execução. SDK sem retentativas. Não há teto monetário garantido; limites e ativação futura em [19-adaptador-openai.md](19-adaptador-openai.md).

Comandos executados (Python da venv na raiz):

```powershell
.\.venv\Scripts\python.exe -m pip install --dry-run 'openai>=2,<3' -c requirements-dev.lock
.\.venv\Scripts\python.exe -m pip install 'openai==2.54.0' -c requirements-dev.lock
.\.venv\Scripts\python.exe scripts/lock_dependencies.py
$env:AI_MODE = 'simulated'
$env:APP_ENV = 'test'
$env:TEST_DATABASE_URL = 'postgresql+psycopg://portfolio_test:senha_ficticia_teste@127.0.0.1:55432/portfolio_test'
.\.venv\Scripts\python.exe -m pytest tests/unit/test_openai_provider.py -q
.\.venv\Scripts\python.exe -m pytest tests/integration/test_openai.py tests/integration/test_review_agreement.py -q --junitxml=reports/us08-openai-focused.xml
.\.venv\Scripts\python.exe scripts/check_quality.py
# Após ajuste da fixture histórica de migração, reexecutado somente o caso afetado:
.\.venv\Scripts\python.exe -m pytest tests/integration/test_reviews.py::test_us06_migration_preserves_attempts_and_classification_snapshots -q --junitxml=reports/us08-migration-final.xml
# HTTP real executado separadamente, pois o pipeline para na falha da suíte anterior:
.\.venv\Scripts\python.exe -m pytest tests/e2e -q --junitxml=reports/us08-http-final.xml
.\.venv\Scripts\python.exe -m ruff check .
.\.venv\Scripts\python.exe -m ruff format --check .
git diff --check
```

Resultados focados iniciais: **18 unitários passed (6,79 s)** e **8 PostgreSQL passed (59,06 s)**. A primeira versão do bloqueio de rede também bloqueava o socketpair de loopback do asyncio no Windows, causando nove falhas unitárias; corrigido o bloqueio para permitir somente loopback, mantendo destinos externos proibidos, e os 18 passaram. Nenhuma falha foi convertida em skip.

Regressão: **116 unitários passed (5,96 s)**. A suíte PostgreSQL/API terminou com **84 passed, 1 failed (517,61 s)**: uma fixture antiga de US06 executava o código atual sobre esquema 0003, sem as novas colunas; preparação ajustada para ocorrer em head e depois retornar a 0003 no banco descartável. Snapshot compara os campos históricos, excluindo somente as duas colunas novas; teste específico de 0005 confere seus valores nulos. Caso corrigido reexecutado: **1 passed (30,74 s)**. HTTP real/TCP/Uvicorn separado: **2 passed (44,67 s)**. O pipeline original encerrou com código 1 por essa falha anterior; não foi declarado como execução integral verde nem repetidas as suítes já aprovadas. Conferência dos quatro JUnit (`unit.xml`, `postgres-api.xml`, `us08-migration-final.xml`, `us08-http-final.xml`), usando o último resultado por classname/nome, confirmou **203 cenários distintos com resultado final aprovado, zero erros/falhas/skips pendentes**. Aviso conhecido Starlette/TestClient/HTTPX preservado; Ruff check/format, pip check e git diff --check finais aprovados. Conferidos 66 links locais, zero quebrados.

Somente bancos gerados `portfolio_test_<uuid>` em PostgreSQL 16.4 local, com criação/migração/descarte pela fixture existente. Conferidos 87 nomes únicos nesses quatro JUnit; consulta a pg_database no banco administrativo de teste confirmou todos removidos. Banco administrativo recebido não é limpo; banco de demonstração não acessado nem migrado. Aplicação e documentação agora têm head 0005, mas o demo existente exige upgrade explícito antes de executar esta versão sobre ele. CI remota e Docker não executados nesta entrega. READMEs, arquitetura, contrato, backlog e decisão atualizados; histórico documental anterior preservado. Para primeira chamada real ainda faltam modelo compatível, estimativa e autorização de custo/execução, chave configurada localmente e banco de avaliação isolado migrado; não solicitar nem publicar chave na conversa.

## 09/11/2026 — US08: consulta de concordância validada em PostgreSQL isolado

Eliana forneceu o SQL diretamente na conversa, substituindo a dependência do arquivo não localizado nos registros abaixo. Mantida a branch `feat/us08-avaliacao` em `fb0b93a`, com a alteração documental anterior preservada. Criados os arquivos diretamente a partir do conteúdo autorizado; não houve aplicação de patch Git, portanto `git apply --check` não se aplica a esta edição direta. Sem commit ou push.

Rastreabilidade desta tarefa preparatória de US08: consulta `scripts/triage_review_agreement.sql` (SQL fornecido, sem alteração) → explicação e limites em `docs/18-avaliacao-triagem.md` → vínculo recíproco às 24 execuções previstas em `docs/06-testes.md` → teste PostgreSQL `tests/integration/test_review_agreement.py`. Unidade de análise: tentativa revisada, com última revisão por data/ID. Concordância na amostra revisada não equivale a acurácia ou qualidade semântica de modelo real.

Comandos executados na raiz, sem instalar dependências:

```powershell
.\.venv\Scripts\python.exe -m ruff check tests/integration/test_review_agreement.py
.\.venv\Scripts\python.exe -m ruff format --check tests/integration/test_review_agreement.py
$env:TEST_DATABASE_URL = 'postgresql+psycopg://portfolio_test:senha_ficticia_teste@127.0.0.1:55432/portfolio_test'
$env:AI_MODE = 'simulated'
$env:APP_ENV = 'test'
.\.venv\Scripts\python.exe -m pytest tests/integration/test_review_agreement.py -q --junitxml=reports/us08-review-agreement.xml
git diff --check
```

Resultado: **4 passed, 1 warning, 22,05 s**, sem falha ou skip, PostgreSQL **16.4** real em loopback. Ruff check/format aprovados. Aviso conhecido de depreciação Starlette/TestClient/HTTPX, sem ocultação. SQL executado diretamente do arquivo sobre esquema migrado até 0004, sem mocks ou SQLite:

| Cenário | Resultado verificado |
|---|---|
| Amostra vazia | Zero linhas |
| Revisão corrigida | Três revisões, uma única tentativa contada; data prevalece sobre ID antigo maior; empate recente usa maior ID; categoria/prioridade 1/1, 100,00%, ambas=1 |
| Prioridade divergente e categoria correta | Uma tentativa, categoria 1/100,00%, prioridade 0/0,00%, ambas=0 |
| Exclusões | Uma elegível contada; sucesso sem revisão, falha com revisão sintética e sugestões sem categoria ou sem prioridade excluídos; resultado 1/1 em ambas as dimensões |

A revisão ligada à falha é fixture deliberada no banco para testar o filtro defensivo; não representa fluxo permitido pela API. Isolamento pela fixture existente: quatro bancos distintos `portfolio_test_<uuid>`, registrados no JUnit ignorado em `reports/`. Conferência adicional do JUnit confirmou quatro nomes únicos; consulta a `pg_database` no banco administrativo `portfolio_test` confirmou que todos foram removidos. Nenhuma conexão ao banco de demonstração, reinício de serviço ou alteração no demo. Apenas o cluster de teste já ativo foi reutilizado.

Validação proporcional restrita à consulta nova; suíte geral, Docker/CI remota e as 24 execuções controladas de modelo real não executados nesta entrega. US08 permanece parcial: provedor, modelo e orçamento pendentes; somente `AI_MODE=simulated`, sem chamadas pagas, deploy ou publicação. Registros anteriores mantidos como histórico; alterações locais para revisão.

## 09/11/2026 — US08: preparação local; patch não localizado

Pedido de Eliana: aplicar `us08-avaliacao.patch` após `git apply --check`, validar a consulta no PostgreSQL isolado com dados fictícios e manter alterações locais para revisão. Escopo restrito à avaliação solicitada; integração real, chamadas pagas, publicação e deploy continuam sem autorização.

Inspeção inicial: `git status --porcelain=v1` sem alterações; branch `main`, HEAD `fb0b93a`. Criada a branch local `feat/us08-avaliacao` com `git switch -c feat/us08-avaliacao`, preservando o conteúdo existente. A criação exigiu execução fora da restrição de escrita em `.git`; concluída sem modificar histórico.

Bloqueio: `Get-Item` não encontrou `C:\Users\Cliente\Downloads\us08-avaliacao.patch`. O caminho de Downloads foi confirmado pelo registro User Shell Folders; `rg --files 'C:\Users\Cliente\Downloads' -g '*.patch' -g '*us08*'` também não localizou o patch solicitado nas subpastas. Nenhum patch aplicado; `git apply --check` e testes PostgreSQL não executados por ausência do arquivo. Nenhum banco ou demo acessado/modificado.

Pendente: receber o arquivo ou seu caminho correto, ler o diff, executar `git apply --check` antes de aplicar e validar a consulta em banco descartável. Evidências obrigatórias ainda ausentes: correção de revisão contada uma única vez e exclusão de tentativas sem revisão ou com falha. US08 não aprovada nem concluída. Branch e registro mantidos locais, sem commit ou push.

Nova tentativa em 09/11/2026 após relato de download: confirmada a branch `feat/us08-avaliacao`, com somente este documento modificado. Downloads continua registrado como `C:\Users\Cliente\Downloads`. Repetidas a busca com `rg --files` e a busca recursiva com `Get-ChildItem -File -Force -Recurse -Filter '*us08*'` (incluindo arquivos ocultos e sem depender das exclusões do rg), sem localizar o arquivo. Bloqueio permanece; nenhum patch ou teste de consulta executado. Registro anterior preservado.

## 08/11/2026 — Repositório público e CI remota aprovados

Retomada com leitura de AGENTS/README/andamento/documento 17 e inspeção real do Git: main em c7c3331, limpa, sem remoto. Reescrita de privacidade já estava concluída, portanto não foi repetida. Conta autenticada elisilva75 e inexistência do repositório reconferidas (404). Autorização explícita vigente: público/main/MIT/noreply confirmado, sem outras branches/tags/backups/force push, deploy ou chamadas pagas.

Auditoria .local/audit_main_privacy.py refeita antes de publicar: 10 commits de main, zero ocorrências do endereço anterior em metadados, mensagens ou blobs/arquivos destinados à publicação; somente noreply confirmado nos author/committer. Os 9 commits reescritos mantêm nomes, árvores, mensagens byte a byte, datas e ordem dos pais; o décimo era a documentação pendente já incorporada. Backup bundle ignorado em .local e branches antigas ficam locais. Auditoria de padrões sem segredos ou artefatos locais no histórico de main. Nenhum valor sensível impresso.

Criado via API o repositório público https://github.com/elisilva75/triagem-chamados-agente-ia, sem README/licença remotos automáticos. Adicionado origin e enviado somente refs/heads/main:refs/heads/main com push.followTags=false. Primeira tentativa falhou por certificado do backend Git local; repetida com http.sslBackend=schannel, sem desabilitar SSL, e concluída. Configuração TLS/push-refspec restrita ao repositório. Nenhuma sobrescrita/force push. API confirmou público, default_branch main, descrição/tópicos preparados, única branch main e nenhuma tag.

Clone real em .local/published-clone-20261108 com --single-branch --branch main --no-tags: HEAD c7c333138c9f4948102a5575255db828ac18bf11 idêntico ao publicado, só noreply nos metadados, 90 arquivos rastreados, MIT presente, .env ativo ausente. Demo não acessado/alterado; nenhum servidor local reiniciado.

**CI efetivamente executada e aprovada:** [checks / run 42507831040](https://github.com/elisilva75/triagem-chamados-agente-ia/actions/runs/42507831040), commit c7c3331, success. Instalação pelos locks, pip check, Ruff check/format, unitários, PostgreSQL/API e HTTP real, upload dos relatórios e encerramento dos serviços, todas as etapas aprovadas. Artefato test-results baixado em memória sem encaminhar Authorization em redirecionamentos; JUnit conferido: unit.xml 98, postgres-api.xml 77, http-real.xml 2, total **177 testes, zero falhas/erros/skips**. Logs observados: ubuntu-26.04, CPython 3.12.16, PostgreSQL 16.15. Evidência sanitizada em .local/ci-result-42507831040.json. Não houve falha do projeto a corrigir nem alteração de dependências.

READMEs PT/EN, rastreabilidade e status de US07/US09 atualizados com resultado real; registros anteriores mantidos como histórico. Atualização pós-CI somente em documentação/comentários (sem versões/código/workflow alterados), com conferência de links, exemplos JSON, privacidade e diff. Commit documental usa [skip ci] para não repetir toda a suíte apenas por documentação, conforme pedido. A aprovação funcional é do commit c7c3331; não declarar outra execução para o commit documental posterior.

**Estado final do MVP simulado:** US02–US06 critérios funcionais verificados local/remotamente; US07 atendida com CI remota; US09 ensaio/publicação concluídos no escopo documentado. US01 continua parcial: falta executar Compose/build da API e persistência por reinício do Compose; PostgreSQL de serviço na CI não substitui isso. US08/modelo real adiada, não bloqueia simulação. Sem deploy ou chamadas pagas. URL e pendências atualizadas; não resta decisão de visibilidade/e-mail para esta publicação autorizada.

## 08/11/2026 — Privacidade e publicação de main autorizadas

Eliana confirmou público, conta elisilva75/nome triagem-chamados-agente-ia/main/MIT e forneceu o noreply exato exibido nas configurações da conta. Autorizou reescrita local de e-mail de author/committer, preservando nomes/mensagens/ordem/conteúdo, e publicação somente de main, sem force push/outras branches/tags/backups. As autorizações mais antigas de não publicar foram substituídas por essa autorização expressa. Sem deploy ou chamadas pagas; AI_MODE=simulated e Docker Compose pendente preservados.

Executado .local/rewrite_main_email.py: 9 commits reescritos com noreply confirmado, preservando árvores, mensagens, nomes, datas e ordem dos pais, sem rebase de conteúdo. Backup bundle em .local ignorado, sem referência de backup no refspec a publicar; outras branches antigas mantidas locais. O endereço pessoal não foi impresso nem inserido na documentação. Configuração local de novos commits atualizada para noreply; push.followTags=false. Auditoria própria .local/audit_main_privacy.py confere ausência do e-mail anterior em metadados, mensagens e blobs históricos/arquivos de main e preservação dos atributos exigidos. Alterações documentais pendentes da autenticação foram preservadas e incluídas na preparação do commit.

Conta autenticada elisilva75 e ausência do repositório (GET autenticado 404) reconferidas antes da criação. Criação, push e CI serão registrados conforme o resultado efetivo; a autorização/preparação não equivalem a execução concluída. Histórico abaixo mantém evidências anteriores e hashes locais pré-reescrita, sem expor e-mail pessoal.

## 08/11/2026 — Acesso GitHub restabelecido, sem publicação

Eliana autorizou corrigir o acesso por fluxo oficial, confirmar conta e consultar existência do repositório, sem publicar/reescrever histórico, aguardando visibilidade/e-mail. Disponível Git Credential Manager 2.5.1; GitHub CLI ausente. Executado `git credential-manager github login --username elisilva75 --browser --force` fora da restrição do sandbox para acessar navegador/gerenciador de credenciais do usuário. Eliana concluiu a autorização pelo navegador e informou sucesso; processo terminou com saída 0. Nenhuma senha/token solicitado na conversa ou impresso, nenhum código de dispositivo usado.

Verificação técnica posterior em .local/check_github_ready.py: GET autenticado /user HTTP 200, login elisilva75, conta esperada confirmada. GET autenticado /repos/elisilva75/triagem-chamados-agente-ia HTTP 404; consulta pública também 404. Repositório não existe para a conta autenticada no momento da consulta; não é reserva do nome e a existência deve ser reconferida antes de futura criação. Token utilizado somente em memória no verificador; credencial persistida pelo fluxo oficial do GCM, sem inclusão em arquivos do projeto. Evidência sanitizada local ignorada pelo Git.

Atualizado documento 17 com resultado e diagnóstico anterior preservado como histórico. Sem criar origin/repositório remoto, push, publicação, novo commit ou reescrita; main permanece em c2dd4b7. Aguardar definições de visibilidade e identidade pública dos commits. Demo e código não alterados; nenhuma suíte repetida nesta operação de autenticação/documentação. Modo simulado e pendências de Docker Compose/CI remota preservados. Registros desta etapa ficam sem novo commit.

## 08/11/2026 — Licença, URL e main preparadas por autorização de Eliana

Autorizado adicionar MIT com copyright 2026 Eliana Gomes da Silva, usar conta elisilva75/nome triagem-chamados-agente-ia/main, revisar e commitar alterações finais pertinentes, sem publicar. Preservadas todas as alterações documentais da revisão anterior. Criada main a partir da base revisada 83dd970, mantendo chore/mvp-readiness e demais branches; sem rebase/amend/reescrita. LICENSE adicionado com texto MIT padrão, READMEs PT/EN atualizados para URL planejada e status de publicação ainda não realizada. Modo simulado, US08 adiada, Compose e CI remota pendentes mantidos explícitos.

Verificação GitHub somente leitura por .local/check_github_ready.py, tokens apenas em memória e nunca impressos/salvos: GitHub CLI ausente no PATH. Gerenciador Git sem credencial acessível sob sandbox; execução autorizada fora da restrição encontrou credencial, mas GET autenticado /user retornou 401 e conta não foi confirmada. Consulta pública ao repositório planejado retornou 404; consulta autenticada retornou 401. Não declarar nome disponível na conta autenticada. A conexão de VS Code informada pela autora não pôde ser confirmada pelo processo Git. Nenhum origin/repositório remoto criado; antes disso, confirmar autenticação como elisilva75 e repetir disponibilidade do nome. Não houve push, publicação, deploy ou chamada paga.

E-mail: um único endereço no histórico revisado, igual à configuração local e não GitHub noreply. Potencialmente pessoal, valores não reproduzidos. Commit final autorizado usa a identidade existente, sem inventar endereço ou reescrever commits. Opções em [revisão de publicação](17-revisao-publicacao.md): consentir em manter identidade; confirmar endereço público/noreply real e autorizar reescrita; ou autorizar outro histórico separado de publicação. Nenhuma reescrita foi executada. Publicação futura restrita a main e ancestrais revisados; nunca --all/--mirror. Branch antiga com workspace permanece fora desse histórico.

Mudanças são documentais/licença/ignore/comentários; sem alteração funcional ou versões de dependências. Mantida última evidência funcional de 177 testes aprovados, sem repetir suíte completa ou cenários manuais. Conferência final: 87 links locais em 21 arquivos Markdown, 8 exemplos JSON aceitos pelos schemas, 16 blocos PowerShell sem erros de sintaxe, git diff --check aprovado e auditoria de arquivos/histórico sem padrão de segredo encontrado. Demo, arquivos locais e branches antigas preservados. Ainda pendem autenticação verificável/disponibilidade do nome, decisão de identidade pública e visibilidade, autorização futura de publicação e validações próprias de Docker Compose/CI remota.

## 08/11/2026 — Revisão final documental para publicação futura

Pedido de Eliana: preparar revisão do repositório, sem publicar. Lidos README/andamento e preservadas alterações existentes. Branch mantida `chore/mvp-readiness`, HEAD `83dd970`, nenhum remoto configurado. Alterações desta revisão sem commit/staging enquanto Eliana confirma a identidade pública dos commits; histórico não reescrito.

READMEs PT/EN reorganizados para leitores sem contexto: objetivo/funcionalidades/arquitetura, simulador versus US08 adiada, fork/clone com marcadores de URL, pré-requisitos com fontes oficiais, .env a partir do exemplo, execução nativa, parada/reinício preservando dados, Compose com comandos explicitamente não validados, Swagger completo, testes isolados, diagnóstico de portas/banco/migrações e limites de loopback sem autenticação. Versões efetivas e última validação de 177 testes mantidas como evidência anterior, sem nova execução da suíte. Comentários de .env.example esclarecem o destino Compose versus nativo; .gitignore agora protege workspace pessoal.

[Revisão de publicação](17-revisao-publicacao.md) contém descrição curta PT/EN, tópicos sugeridos, licença pendente (nenhuma encontrada/atribuída), escopo Git recomendado e decisões de URL/visibilidade/branch/identidade. Docker/Compose e CI remota continuam pendentes; US08 adiada. Não houve publicação, deploy, instalação nova, chamada paga ou alteração do demo.

Verificações executadas nesta etapa documental:

- Metadados das versões instaladas conferidos sem atualização; PowerShell 5.1.26100.9818 e versões Python/pacotes registradas em ambiente/READMEs.
- `.local/check_publication_docs.py`: links locais Markdown conferidos e 8 exemplos JSON dos dois READMEs validados pelos schemas reais; não é execução de requisições HTTP ou homologação manual. Parser PowerShell analisou 16 blocos, zero erros de sintaxe. Clone/instaladores/Compose e novos comandos operacionais não executados; o caminho nativo e o fluxo de produto têm evidência anterior, não nova certificação.
- `.local/audit_publication.py`: 8 commits ancestrais da branch preparada, 9 commits ao incluir todas as branches locais, 180 blobs únicos e 89 caminhos históricos da base. Sem padrões de segredo encontrados; URLs com credenciais só nos exemplos fictícios permitidos. Sem artefatos locais no histórico da branch atual. A auditoria por padrões não é garantia universal.
- Achado em outra branch: `feat/foundation-tickets`, commit `c3d3c95`, contém workspace com pasta relativa, sem caminho absoluto/configurações/segredo encontrado. Não é ancestral da branch preparada. Recomenda-se publicar somente a branch revisada, sem --all/--mirror; arquivo e branch antigos preservados, sem reescrita de histórico.
- Identidade Git de autor/committer não usa GitHub noreply. Valores não impressos; confirmar identidade pública antes de novos commits/publicação e decidir eventual tratamento de metadados existentes. Nenhuma alteração automática de autoria.
- `git check-ignore` confirmou .env, venv, .local, reports e workspace como ignorados. Diff sem erros em git diff --check; 83 links locais em 21 arquivos Markdown aprovados. Licença não aplicada. Apenas documentação/comentários e proteção de arquivo local alterados; comentários iniciais dos locks agora distinguem Windows validado de Linux/CI pendentes, sem mudar dependências. Suíte completa não repetida.

Decisões pendentes da autora: conta/nome/URL, visibilidade e branch principal, licença, identidade pública Git e autorização futura de publicação apenas do escopo revisado. Caso opte por mostrar o MVP antes de concluir infraestrutura, declarar Compose/CI remota pendentes; não apresentar entrega final totalmente validada. Descrição/tópicos estão preparados no documento 17, sem criar o repositório remoto.

## 08/11/2026 — US01, US07 e US09: preparação local do MVP simulado

### Autorização e resultado atual

Eliana autorizou fechar qualidade/documentação e verificar ambiente, preservando o demo, sem publicação, deploy ou chamadas pagas. Branch local `chore/mvp-readiness`, baseada em `8049206`, sem reescrever histórico. Arquivo workspace preexistente continua intacto e não incluído. Evidências desta seção são **validação técnica automatizada executada pelo agente**, não novos relatos de homologação manual de Eliana. Registros manuais anteriores não foram duplicados.

**US01 continua parcial:** Docker ausente no PATH, no caminho Program Files e nos caminhos locais de instalação conferidos. Não houve build, Compose, teste de volume ou reinício de containers. Pré-requisito: Docker Desktop com mecanismo Linux ativo e Compose, conforme fontes no documento 09. Não instalado nem contratado nesta entrega. Guia identifica comandos Compose não executados e separa portas/projeto/volume para preservar demo. CA2/CA3 continuam cobertos pela regressão nativa; CA1 exige execução própria.

**US07: critérios/tasks no equivalente local executados; CI remoto permanece pendente.** Workflow usa Ubuntu, PostgreSQL 16 de serviço, Python 3.12, locks existentes, AI_MODE=simulated/APP_ENV=test e credenciais fictícias. Sem secrets de provedor ou adaptador real. Instalação pelo lock e permissões contents:read preservadas; job limitado a 20 minutos, upload JUnit com always. Runner compartilhado interrompe na primeira falha e rejeita suíte obrigatória vazia/com skips. Arquivo revisto não equivale à execução do GitHub Actions; nem valida o provisionamento Linux/container nesta máquina.

**US09: documentação e ensaio no escopo nativo isolado atendidos.** README PT/EN, arquitetura/modelo atual, contrato/exemplos, guia Windows consolidado (removidas instruções obsoletas de versões), roteiro curto/descrição de portfólio e declaração de uso de IA no desenvolvimento. Integração real permanece adiada em US08; não há SDK de modelo, avaliação de acurácia ou inferência paga. Publicação preparada para revisão futura, sem PR remoto/push/deploy.

### Rastreabilidade da entrega

| História / critérios / tasks | Arquivos e cobertura | Evidência executada |
|---|---|---|
| US01-CA1/T3 | compose.yaml, Dockerfile, guia 10, ambiente 09 | Diagnóstico Docker indisponível; execução Compose não aprovada |
| US01-CA2/CA3/T2 | Suíte existente de health/migração | Regressão real PostgreSQL e dois roundtrips simultâneos, sem limpar demo |
| US07-CA1/T1/T2/T3 | .github/workflows/ci.yml, scripts/check_quality.py, suites unit/integration/api/e2e | Pipeline local 177 passed, relatórios por camada; GitHub remoto pendente |
| US07-CA2/T1/T2 | tests/unit/test_quality_gate.py | 4 casos novos: primeira falha bloqueia sequência, config obrigatória, relatório vazio e com skip bloqueados; sem duplicar testes de produto |
| US07-CA3/T2 | tests/conftest.py e roundtrip existente reaproveitado | Nome isolado sem URL/senha registrado em JUnit; duas execuções concorrentes passaram com bancos distintos, migração do zero/duplo upgrade/downgrade/upgrade |
| US09-CA1/T1/T3 | README.md, README.en.md, docs 04/05/10/16, scripts/demo_flow.py | Roteiro cadastro→falha→retry→correção→sugestão→review→resolve executado por HTTP real em fontes isoladas |
| US09-CA2/T2 | Revisão de arquivos rastreados + 5 novos previstos, .gitignore/.dockerignore | 88 arquivos inspecionados; sem artefatos locais ou achados de segredo nos padrões conferidos; links locais verificados |
| US09-CA3/T2 | Exportação limpa em .local/rehearsal-source, venv nova, banco exclusivo gerado | Lock instalado, pip check, upgrade head duas vezes, health + consulta real, roteiro e reinício nativo da API com GET integral idêntico |

### Comandos e resultados realmente executados

Na raiz em PowerShell, definidos TEST_DATABASE_URL para banco administrativo `portfolio_test` em 127.0.0.1:55432, AI_MODE=simulated e APP_ENV=test. Executado `.venv/Scripts/python.exe scripts/check_quality.py`, saída 0:

- pip check aprovado; Ruff check aprovado e format aprovado. Rechecagem final inclui scripts novos.
- `pytest tests/unit -q --junitxml=reports/unit.xml`: **98 passed, 1 warning, 1,41 s**.
- `pytest tests/integration tests/api -q --junitxml=reports/postgres-api.xml`: **77 passed, 1 warning, 504,42 s** (53 API in-process + 24 integração, incluindo driver real com conexão recusada). Execução teve outros ensaios isolados concorrentes; não usar duração como benchmark da suíte.
- `pytest tests/e2e -q --junitxml=reports/http-real.xml`: **2 passed, 1 warning, 42,16 s**, Uvicorn/TCP/PostgreSQL reais, incluindo interrupção/reinício/recuperação por prazo.

**Total: 177 passed, nenhuma falha/erro/skip.** Um aviso conhecido se repete por camada: Starlette TestClient depreca HTTPX. Não instalado pacote para ocultá-lo. Relatórios ignorados pelo Git; nenhuma porcentagem de cobertura de linhas foi medida.

Isolamento: `.venv/Scripts/python.exe .local/check_isolation.py` iniciou em paralelo duas execuções do teste existente `test_us01_ca3_migrations_roundtrip_and_metadata`, cada uma com JUnit próprio (reports/isolation-0.xml e isolation-1.xml). Ambas saída 0, 1 passed cada (26,55 s e 26,88 s); bancos `portfolio_test_c10e936cd83a436ea996ad3133e79bba` e `portfolio_test_1ea251901d1940ca945e873047ea8e67`, distintos e removidos pela fixture. São reexecuções do mesmo teste, não dois casos novos somados aos 177.

Instalação/guia: `python -m venv .local/rehearsal-venv` e Python dessa venv com `-m pip install -r requirements-dev.lock` concluídos. A primeira tentativa restrita foi interrompida sem progresso; a execução autorizada com acesso aos pacotes terminou usando cache. Sem alteração de locks/versões ou instalação global. `.local/rehearse_readiness.py` copiou os 88 arquivos de fonte/documentação preparados para diretório sem .env/.git/.venv/dados locais; usou venv nova e banco gerado `portfolio_test_6986db906ad443e4b2fc5a0244231235`, com migrações 0001–0004 do zero e segundo upgrade sem alteração. Não foi clone remoto ou máquina Windows nova: reutilizou binários PostgreSQL 16.4 e cluster nativo existente, com banco separado.

Ensaio: `scripts/demo_flow.py --base-url <loopback:porta exclusiva>` na cópia isolada retornou 201 no cadastro, 502/invalid_ai_response nas duas tentativas, 200 na correção, 200 na triagem válida, 201 na review e 200 na resolução. Consultou GET antes de cada escrita. Final resolvido/revisada, version=10, content_revision=2, 3 tentativas e 1 review; reinício do processo da API manteve GET completo idêntico. Banco gerado removido no finally; demo não usado. Evidência local em .local/readiness-rehearsal.json. Esse reinício **não valida reinício Compose**.

Reutilização do cluster: `scripts/start-test-postgres.ps1` não conseguiu reconhecer processo/abrir log sob o token restrito do sandbox e falhou. pg_isready e consultas continuaram respondendo; não houve recriação nem perda de dados. Reexecução autorizada fora dessa restrição reconheceu PID 18284 e reutilizou o cluster existente, saída 0. A limitação foi incluída no guia.

### Medição informativa RNF03 e preservação de dados

`.venv/Scripts/python.exe .local/measure_readiness.py`: banco exclusivo com 1.000 chamados fictícios, Uvicorn/TCP loopback, HTTPX com conexão reutilizada, 100 requisições sequenciais por operação, sem IA. GET individual p95 **30,95 ms**, GET lista limit=20 p95 **43,25 ms**, POST p95 **45,99 ms**; máximos 104,03 / 51,95 / 173,77 ms. Leituras feitas com 1.000 registros; os 100 POSTs elevaram a base até 1.100. p95 calculado por ordem/nearest rank. Windows 11 build 26300, Intel64 Family 6 Model 142 Stepping 10, PostgreSQL 16.4 nativo, Python 3.12.6; evidência .local/readiness-performance.json. Abaixo da referência informativa de 500 ms neste ensaio, sem alegar SLA, carga concorrente ou desempenho Docker/produção.

Demo consultado em transações somente leitura antes/depois: comparação integral JSON por ID de tickets, ticket_events, triage_attempts e human_reviews **idêntica**, incluindo timestamps/snapshots. Permanece 1 chamado, 3 eventos, 1 tentativa, 0 reviews; chamado histórico ad903cac-a750-48d3-b205-91da97d7adee continua version=5/content_revision=3. Evidências .local/demo-readiness-before.json e after.json. Nenhum servidor demo encerrado/recarregado.

Revisão de preparação: `.local/audit_readiness.py` verificou os 88 arquivos rastreados/novos previstos, 80 links Markdown locais, caracteres Unicode inválidos, artefatos de venv/banco/.env e padrões de tokens/chaves privadas/URLs com credenciais. Nenhum achado final ou link quebrado; a credencial `segredo_demo` em teste de conexão recusada foi inspecionada e confirmada fictícia (o próprio teste exige que não vaze na resposta). Não é garantia de detecção universal de segredos. `git check-ignore` confirmou .env, .venv, .local e reports; .dockerignore reforçado para reports/cache/workspace. Sem dados de empregadores identificados. Diff revisado, `git diff --check` aprovado após corrigir linha vazia no fim do guia, sem incluir workspace preexistente ou dados locais. Qualidade registrada no commit local `6310986`; documentação preparada em commit separado, sem push.

### O que ainda impede a entrega final

1. US01-CA1: disponibilizar Docker/Compose e executar build/start/migração/consulta/reinício com volume em projeto isolado. Não concluído.
2. Executar workflow no GitHub após autorização de publicação. US07 tem equivalente local aprovado; CI remoto/Linux não executado e permanece gate separado.

US02–US06 sem novo gate manual; US09 preparada/ensaiada no escopo nativo descrito. US08 adiada por decisão de produto, não bloqueia o MVP simulado. A próxima revisão de publicação deve partir destes arquivos concretos e não exigir nova homologação manual de regras já automatizadas. Não houve chamada paga, publicação, PR remoto ou deploy.

## 08/11/2026 — US06 e dependências funcionais de US03 verificadas automaticamente

### Escopo, implementação e DoD

Eliana autorizou US06 conforme backlog/regras, com automação isolada, demonstração opcional e preservação do demo. Criada branch local `feat/us06-human-review` a partir da entrega US05 `555b414`, sem reescrever histórico ou tocar no arquivo workspace preexistente. Sem iniciar US07/US09 ou US08 adiada. Origem das evidências abaixo: **validação técnica automatizada pelo agente**, não homologação manual informada por Eliana.

Entregues POST/GET reviews, GET review por ID/Location, POST resolve/reopen. Revisão exige categoria/prioridade válidas, motivo 10–500 e autor declarado 2–80 após trim. Classificação final aponta para HumanReview gerada; correção em revisada insere outra review, preserva a anterior e a sugestão da IA. Resolver exige aberto/revisada com classificação final vinculada ao próprio chamado/revisão; reabrir mantém classificação/conteúdo. Escritas com versão antiga ou transições repetidas são rejeitadas, sem histórico adicional. Revisão e transições não chamam provedor.

Migração 0004 cria human_reviews e unicidade de tentativa/chamado/content_revision para FK composta; nenhuma revisão fictícia é retroativamente criada. Referência final permanece em projeção JSON validada pelo serviço sob lock, conforme ADR10. Novo registro/referência final e transições/eventos são transacionais. Autor é declarado e sem autenticação; histórico imutável pelas rotas, sem promessa de auditoria legal. Mesmas dependências/locks/fontes oficiais, sem instalação/reconfiguração de bibliotecas; aplicação 0.5.0.

| História/critério/tasks | Código/teste | Evidência executada |
|---|---|---|
| US06-CA1/T1/T2 | application/reviews.py, schemas/rotas, HumanReview; test_us06_ca1_ca3_review_correct_resolve_reopen_and_preserve_history | Review inicial, correção com nova decisão final, autor/motivo persistidos, sugestão/primeira review intactas, resolução e reabertura com version+1 sem alterar content_revision |
| US06-CA2/T2 | Guardas/ReviewCreate; testes de estado e entrada inválida | Pendente/falha/sugerida sem review não resolvem; resolvido não revisa/edita nem aceita no-op; em_analise bloqueia review/resolve/reopen no teste de tentativa real reaproveitado. Enums/tipos/extras/limites inválidos retornam 422 sem escrita |
| US06-CA3/T2 | reason/declared_reviewer; testes unitários e HTTP | Motivo 10/500 e autor 2/80 aceitos após trim/Unicode, ±1 rejeitados. Revisão subsequente mantém registro anterior e Location consultável |
| US06-CA4/T1/T2 | SELECT FOR UPDATE + expected_version; testes de conflitos/escopo/concorrência | Versão antiga, transições repetidas e seis disputas de duas conexões: só uma escrita confirma, outra recebe version_conflict, sem duplicar reviews/eventos |
| US03-CA1/CA3 com US06 | Teste existente test_us03_ca1_archive_classification_and_preserve_history reaproveitado | Preparação agora via POST cadastro/triagem/review, sem fixture sintética nesse caso. No-op mantém resposta integral/timestamps/classificações e contagem imediata de eventos=1. Edição limpa sugestão/final e preserva reviews/tentativas; segunda edição e nova triagem/review mantêm snapshot não nulo antigo e vinculam novo conteúdo |
| US03-CA2 com US06 | Fluxo US06 + teste existente de tentativa ativa | Edição/no-op bloqueados em resolvido; edição bloqueada em_analise com tentativa real. Reabertura habilita escrita; resolve após invalidação é bloqueado até nova classificação |
| US06-T2 atomicidade/integridade | tests/integration/test_reviews.py | FK composta rejeita outro ticket/revisão; projeção final interna corrompida é rejeitada. CHECK real inválido após inserir review reverte também projeção/versão; evento inválido de resolve/reopen reverte estado/timestamp/histórico |
| US06-T2 migração/HTTP real | Teste de migração novo + roundtrip existente; tests/e2e/test_http.py ampliado | Upgrade preserva tentativas/snapshots; alembic check sem divergência; downgrade só em banco descartável. Uvicorn/TCP real percorre review→resolve→bloqueio→reopen→edição/invalidação, preservando review/tentativa |
| US06-T3 | README, ADR10, contrato, backlog, guia, docs/15-validacao-us06.md | Critérios/tasks/resultados, DoD local e pendências separados; demonstração opcional, sem repetição manual obrigatória |

### Comandos e resultados efetivos

Executados na raiz com Python da .venv, TEST_DATABASE_URL apontando para o banco administrativo isolado portfolio_test em 127.0.0.1:55432. Cada teste cria e remove somente seu portfolio_test_<uuid>; nenhum POST/PATCH de teste no demo:

```powershell
.\.venv\Scripts\python.exe -m ruff check .
.\.venv\Scripts\python.exe -m ruff format --check .
.\.venv\Scripts\python.exe -m pip check
.\.venv\Scripts\python.exe -m pytest tests/unit/test_reviews.py -q
$env:TEST_DATABASE_URL='postgresql+psycopg://portfolio_test:senha_ficticia_teste@127.0.0.1:55432/portfolio_test'
.\.venv\Scripts\python.exe -m pytest tests/api/test_reviews.py tests/integration/test_postgres.py::test_us01_ca3_migrations_roundtrip_and_metadata -q --junitxml=reports/us06-api-focused.xml
.\.venv\Scripts\python.exe -m pytest tests/integration/test_reviews.py tests/integration/test_editing.py::test_us03_ca1_archive_classification_and_preserve_history tests/api/test_triage.py::test_us04_attempt_committed_and_no_connection_held_during_provider tests/e2e/test_http.py -q --junitxml=reports/us06-integration-focused.xml
.\.venv\Scripts\python.exe -m pytest -q --junitxml=reports/us06-all.xml
```

**Resultados: 21 unitários passed (0,13 s); foco API/migração 7 passed (48,70 s); foco integração/HTTP reaproveitado 14 passed (79,25 s). Regressão final: 173 passed, 1 warning, 292,88 s; zero falhas, erros ou skips.** XML conferido: 94 unitários, 53 API dentro do processo com PostgreSQL real, 24 integração (23 com PostgreSQL ativo, um de conexão recusada com driver real), 2 HTTP/TCP com servidor Uvicorn e PostgreSQL real. Inclui regressão US01–US05, recuperação/reinício real e todos os testes novos. Sem SQLite ou modelo de IA externo. Não somar focos à suíte como se fossem casos distintos.

Nenhuma execução pytest desta entrega falhou. Primeiras passagens de Ruff apontaram formatação/linhas longas, corrigidas antes das verificações finais. Ruff check/format e pip check aprovados. Aviso conhecido Starlette/TestClient sobre HTTPX preservado, sem pacote novo para ocultá-lo. Relatórios locais reports/us06-*.xml ignorados pelo Git. Links locais conferidos sem referências quebradas.

### Demo e ambiente

Snapshot SQL somente leitura antes da entrega em `.local/demo-us06-before.json` e comparação antes/depois da migração `alembic upgrade head` e novamente após recarregar API: **todos os campos anteriores integralmente iguais**, 1 chamado, 3 eventos e 1 tentativa; human_reviews=0. Snapshot posterior `.local/demo-us06-after.json`, fora do Git. Esquema demo **0004**. Nenhum chamado/review/evento/tentativa inserido/alterado no demo pelo agente; somente DDL aditiva. Nenhum initdb, createdb, limpeza ou downgrade no demo.

API anterior identificada por executável absoluto da .venv, comando Uvicorn e parentesco (launcher 3524/servidor 3324) antes de encerrá-la. Recarregada somente a API deste projeto, mesma DATABASE_URL demo/AI_MODE=simulated/bind 127.0.0.1:8000. Novo launcher PID **22504**, sempre reconferir identidade antes de encerrar; logs `.local/api-us06.*`. /health, /docs, /openapi.json, GET do chamado e GET reviews retornaram 200; OpenAPI 0.5.0 com reviews/resolve/reopen; chamado mantém version=5/content_revision=3 e classificação final nula; histórico reviews vazio. API/banco deixados ativos sem garantia de sobreviver ao encerramento da sessão do sistema. Nenhuma configuração global ou .env alterado.

### Status das histórias e pendências segundo DoD

**US03: dependência funcional de US06 encerrada por automação integrada; CA1–CA3/T1–T3 locais atendidos. US06: CA1–CA4/T1–T3 implementados e verificados, DoD funcional local atendida.** US02/US04/US05 mantêm critérios/tasks locais atendidos com regressão atual. Não há gate manual obrigatório, nem atribuição dos testes a Eliana; demos opcionais. Limitação histórica do timestamp intermediário de um no-op manual não é reconstruída e não exige repetição da regra já automatizada.

**DoD global do MVP ainda incompleta:** US01 permanece parcial por CA1/Compose e persistência por reinício do Compose; US07 precisa completar/verificar pipeline do fluxo completo, isolamento/caminho de falha e execução remota conforme autorização; US09 precisa portfólio final, README PT/EN e ensaio completo de guias/roteiro. Medição informativa RNF03 e checkout limpo continuam trabalho de fechamento de qualidade/portfólio, não resultados presumidos da suíte funcional. Docker/Linux/CI não foram comprovados pelo ambiente nativo Windows. US08 adiada por D08, não bloqueia MVP exclusivamente simulado. Não iniciar outras histórias automaticamente nesta entrega.

Sem chamadas pagas, SDK de IA externo, publicação ou deploy. Uso somente loopback/AI_MODE=simulated. Evidências e demonstração opcional em [15-validacao-us06.md](15-validacao-us06.md).


## 08/11/2026 — US05 implementada e validada tecnicamente; demo preservado

### Autorização e rastreabilidade

Após executar M02/no-op por automação e verificar os critérios independentes de US04 (registro imediatamente abaixo), iniciada US05 na branch local `feat/us05-triage-recovery`, a partir do commit local `1d48ec4` da validação US04. Sem iniciar US06, sem publicar ou fazer deploy. Demonstrações manuais agora são opcionais; nenhum teste técnico foi atribuído a homologação manual de Eliana. Alterações anteriores e arquivo workspace preservados.

| Critério/task | Implementação e teste | Resultado executado |
|---|---|---|
| US05-CA1/T1/T2 | application/triage.py aceita retry em falha; test_us05_ca1_retry_preserves_content_and_failed_attempt | Timeout 504/ai_timeout, indisponibilidade 503/ai_unavailable e saída inválida 502/invalid_ai_response seguidos de retry com provedor simulado válido: mesmo chamado, conteúdo/revisão/criação preservados, versões 1→3→5, primeira tentativa imutável, sem eventos de conteúdo extras |
| US05-CA2/T2 | Lock de linha e índice parcial existentes; test_us05_ca2_two_simultaneous_retry_posts_run_one_agent | Dois POSTs simultâneos de retry com mesma versão: um 200, outro 409; só um agente executado e uma tentativa adicional. Barreira/Event determinísticos; PostgreSQL real |
| US05-CA3/T1/T2 | Recuperação de tentativa ativa vencida + finalização condicional; testes de fronteira/atraso | 19,999 s aceita resultado, 20/20,001 s rejeitam como ai_timeout; lease válido bloqueia com triage_in_progress sem escrita; resultado antigo após recuperação recebe 409/version_conflict e não altera vencedor/histórico |
| US05-CA3/T2 HTTP real | tests/e2e/test_recovery.py e factory exclusiva tests/interrupted_server.py | Servidor Uvicorn encerrou realmente com código 17 após confirmar aquisição; novo servidor no mesmo banco de teste leu em_analise/version=2, bloqueou retry dentro do prazo, aguardou lease real de 20 s e recuperou com tentativa 2/sucesso/version=5. Sem alterar deadline no banco |
| US05-CA4/T2 | test_us05_ca4_real_constraint_failure_rolls_back_finalization_then_recovers | CHECK real inválido durante finalização: 503/storage_unavailable, sem falso contexto de falha persistida; tentativa continuou ativa/version=2 sem sugestão. Após prazo, nova solicitação recuperou e concluiu; conteúdo preservado |
| US05-T1/T2 atomicidade | test_us05_recovery_and_new_attempt_are_atomic | CHECK real inválido ao inserir próxima tentativa reverte também encerramento da anterior e versões; após retirar somente a injeção de teste, nova solicitação conclui normalmente |
| Regressão US01–US04/T2 | Suíte completa existente + novos casos US05, sem duplicar M02/no-op | Cadastro/consulta/edição/limites/snapshots/migração/agente anteriores preservados; M02/no-op tiveram apenas asserções faltantes adicionadas aos testes existentes |
| US05-T3 | ADR09, contrato, README, backlog, guia e docs/14-validacao-us05.md | Códigos, retry explícito, prazo, versões, resultados e lacunas documentados; sem exigência de repetição manual |

Recuperação + nova aquisição são uma única transação sob lock; flush libera índice ativo antes de inserir a seguinte. Recuperação de em_analise→falha incrementa version uma vez, aquisição outra e finalização outra (exemplo 2→5). Retry de falha normal soma duas (3→5). Versão antiga falha antes de qualquer recuperação. Tentativas concluídas não são sobrescritas; eventos de conteúdo não são criados por retry. Sem nova migração: esquema continua 0003. Sem dependências adicionadas/atualizadas, mesmos locks/fontes oficiais; aplicação 0.4.0.

### Execuções reais

Comandos na raiz:

```powershell
.\.venv\Scripts\python.exe -m ruff check .
.\.venv\Scripts\python.exe -m ruff format --check .
.\.venv\Scripts\python.exe -m pip check
$env:TEST_DATABASE_URL='postgresql+psycopg://portfolio_test:senha_ficticia_teste@127.0.0.1:55432/portfolio_test'
.\.venv\Scripts\python.exe -m pytest tests/api/test_recovery.py -q --junitxml=reports/us05-api-focused.xml
.\.venv\Scripts\python.exe -m pytest tests/integration/test_recovery.py tests/e2e/test_recovery.py -q --junitxml=reports/us05-recovery-focused.xml
.\.venv\Scripts\python.exe -m pytest -q --junitxml=reports/us05-all.xml
```

**Foco API: 8 passed, 1 warning, 23,34 s. Foco integração/HTTP real: 3 passed, 1 warning, 30,62 s. Regressão completa final: 135 passed, 1 warning, 224,88 s; nenhuma falha, erro ou skip.** Relatório XML conferido: 73 unitários, 47 API dentro do processo com PostgreSQL real, 13 integração (12 com PostgreSQL ativo e um de conexão recusada com driver real), 2 HTTP/TCP com Uvicorn e PostgreSQL real. Cada caso com banco ativo criou/descartou somente seu portfolio_test_<uuid>. Não usou SQLite ou demo. Relatórios em reports/ ignorados pelo Git.

Ruff check/format e pip check aprovados. Falhas iniciais de lint por linhas longas/formatação foram corrigidas; nenhuma execução pytest desta etapa falhou. Aviso conhecido Starlette/TestClient sobre HTTPX continua registrado, sem pacote extra para escondê-lo. O teste HTTP de interrupção usa binário nativo CPython e PYTHONPATH dos mesmos pacotes da .venv para controlar o processo criado no Windows; não prova execução Linux/Docker/CI. Testes de fronteira e resposta tardia usam relógio controlado no serviço; o ensaio HTTP usa prazo real. Factory os._exit fica exclusivamente em tests/, não há opção de encerramento do servidor na API de produção. Nenhuma chamada de IA real, custo ou avaliação semântica de modelo externo.

### Preservação e ambiente local

Comparação SQL **somente leitura** antes/depois de todas as execuções e novamente após recarregar a API: todos os campos de tickets/ticket_events/triage_attempts **integralmente iguais**. Snapshots locais ignorados `.local/demo-us05-before.json` e `.local/demo-us05-after.json`: **1 chamado, 3 eventos, 1 tentativa**. Chamado ad903cac-a750-48d3-b205-91da97d7adee mantém version=5/content_revision=3, pendente/suggestion=null. Nenhum POST/PATCH, criação de chamado, alteração de prazo ou migração no demo nesta etapa; fixture inválida criada somente nos bancos de teste.

Somente a API do projeto foi recarregada: comandos/executável absoluto da .venv/parentesco reconferidos para launcher 17332 e servidor 3504 antes de encerrá-los. Novo launcher PID **3524** (reconferir identidade antes de encerrar); logs `.local/api-us05.*`. Mesmo DATABASE_URL demo, AI_MODE=simulated e bind 127.0.0.1:8000; não alterados .env/serviço global/configuração do PostgreSQL. /health, /docs, /openapi.json, GET do chamado e GET de tentativas retornaram 200; OpenAPI confirmou 0.4.0, chamado 5/3 e histórico total=1. API/banco deixados ativos, sem garantia de sobreviver a encerramento da sessão do sistema.

### Lacunas e próximo escopo

**US05-CA1–CA4 verificados localmente por automação; implementação e documentação entregues.** Nenhum aceite manual obrigatório criado. US04 sem lacuna independente de M02/no-op: validados tecnicamente, demos opcionais. US03 mantém lacunas de validação integrada com classificação final humana/resolvido pelas futuras rotas de US06; lógica já possui fixtures, e o timestamp histórico de um no-op manual específico não pode ser reconstruído depois de outra edição. Não exigir repetição manual para suprir evidência histórica ou regras já automatizadas. Não iniciar US06 sem nova instrução de continuidade.

**Docker Compose e CI no GitHub continuam pendentes; US01 parcialmente validada.** US07 não concluída, US08 adiada; sem modelo real/tokenizer real e sem garantia de preempção de provedor Python arbitrariamente bloqueante (simulador atual é imediato e sem I/O, interface exige respeito ao prazo). US06/revisão/resolução não implementadas. Nada publicado ou implantado; exclusivamente loopback e AI_MODE=simulated. Evidências e demonstração opcional em [14-validacao-us05.md](14-validacao-us05.md).


## 08/11/2026 — M02/no-op validados por automação; continuidade US05 autorizada

Eliana alterou explicitamente a estratégia de aceite: participação em decisões de produto e demonstrações curtas opcionais; não exigir repetição manual de verificações automatizadas. Autorizou iniciar US05 se critérios independentes atendidos. Não atribuir testes do agente a homologação manual da usuária. US06 continua fora desta implementação; Docker Compose/CI permanecem pendentes.

Revisados e **reaproveitados** os testes existentes `test_us04_public_simulation_failure_marker`, `test_us04_ca1_real_suggestion_noop_edit_and_immutable_history` e `test_us03_ca1_archive_classification_and_preserve_history`. Acrescentadas somente asserções faltantes ao teste do marcador (502/código, conteúdo, estado, versão/revisão 3/1, ausência de classificação inválida, tentativa falha e só evento criado) e ao no-op (200, GET integral idêntico incluindo timestamps/sugestão/versões, contagem de eventos imediatamente após no-op=1 e tentativa intacta), sem duplicar cenários.

Comando executado com TEST_DATABASE_URL do cluster local portfolio_test: `.\.venv\Scripts\python.exe -m pytest tests/api/test_triage.py::test_us04_public_simulation_failure_marker tests/api/test_triage.py::test_us04_ca1_real_suggestion_noop_edit_and_immutable_history tests/integration/test_editing.py::test_us03_ca1_archive_classification_and_preserve_history -q --junitxml=reports/us04-m02-noop-technical.xml`. **3 passed, 1 warning, 9,30 s; sem skips/falhas.** Cada caso usou banco exclusivo descartável, nenhum POST/PATCH no demo. Snapshot somente leitura do demo salvo em `.local/demo-us05-before.json`: 1 chamado, 3 eventos e 1 tentativa. Comparar novamente ao fim de US05.

M02 e timestamps do no-op estão **validados tecnicamente por automação**, sem homologação manual presumida e sem nova tarefa para Eliana no Swagger. Isso não reconstrói o timestamp histórico intermediário de seu no-op já seguido de edição; limitações históricas mantidas sem bloquear critério funcional automatizado. US04-CA1–CA4 independentes verificados (regressão prévia 124 testes e foco atual); pode avançar a US05. US03 mantém lacunas de fluxo com classificação final/resolvido dependentes de US06; fixtures existentes cobrem as regras, futura validação integrada automatizada deve usar as rotas de US06 quando existirem. Não iniciar US06 nesta autorização.


## 08/11/2026 — M01a–M01c informados; edição e histórico conferidos

Homologação manual informada por Eliana, registrada sem duplicação: M01a POST triage expected_version=2 retornou 200 e GET confirmou simulated/defeito/media, sugerida, version=4/content_revision=2. M01b PATCH com título idêntico e espaços retornou 200 preservando sugestão e versões 4/2. M01c PATCH de descrição expected_version=4 retornou 200, version=5/content_revision=3, pendente, suggestion/final_classification=null. O agente não observou visualmente nem reexecutou essas ações.

Verificação técnica somente leitura via HTTPX: GET do chamado e de triage-attempts retornaram 200. Descrição persistida: “No ambiente fictício, o erro ao salvar o cadastro afeta todos os usuários e começou nesta manhã.” Texto obtido pelo agente, não atribuído ao relato integral de Eliana. PostgreSQL via psycopg, `SET TRANSACTION READ ONLY; SHOW transaction_read_only` (on), SELECT de tickets/triage_attempts/ticket_events, confirmação transacional sem escrita: **saída 0**. Chamado ad903cac-a750-48d3-b205-91da97d7adee version=5/revisão=3, aberto/pendente, classificações atuais nulas. Uma tentativa, b7b11f7f-1565-4ac4-b39a-6bf77a3669cf, sucesso/simulated, revisão 2, defeito/media, 3 chamadas de modelo/2 ferramentas, sugestão preservada.

**Exatamente três eventos:** criado/revisão 1, editado/revisão 2, editado/revisão 3. Os dois primeiros foram comparados integralmente com `.local/demo-us04-preservation.json` e estão idênticos, incluindo timestamps e snapshot antigo. O novo snapshot tem content_revision=2, final_classification=null e suggestion **integralmente igual** à tentativa anterior. Não há evento adicional para o no-op no estado observado. Nenhum dado alterado ou processo reconfigurado pelo agente; nenhuma nova suíte de aplicação executada.

Timestamps conferidos (UTC): created_at do chamado 2026-11-07T21:23:24.789820Z; updated_at atual 2026-11-08T15:35:04.358424Z; novo evento 2026-11-08T15:35:04.357654Z. Finalização da tentativa 2026-11-08T15:31:17.781295Z, valor que a implementação usa para updated_at da finalização. **Não há captura persistida de resposta imediatamente antes/depois do no-op**: após a edição seguinte, o timestamp intermediário não pode ser comprovado retrospectivamente pelo estado atual. Eliana não informou esse campo no relato do no-op; não registrá-lo como homologado nem inferir igualdade a partir de finished_at. A preservação de timestamp no no-op tem evidência automatizada anterior; não repetir o cenário para criar evidência histórica artificial.

Próximo: M02 saída simulada inválida. **Somente orientar criação de chamado fictício separado**, título exato `[SIMULADO:saida-invalida]`, conforme roteiro; preservar chamado existente. AI_MODE continua simulated: seleção por título é local à requisição, não muda configuração global/arquivo/serviço e não requer restauração posterior. Chamados com títulos comuns continuam no roteiro normal; manter o registro de falha como evidência, sem apagar/renomear. Aguardar ID/resultado da criação; consultar GET para obter versão antes de orientar POST de triagem do novo chamado. M02 não executado pelo agente nem homologado.

US03: no-op com sugestão e invalidação/preservação de sugestão agora informados manualmente e conferidos tecnicamente no alcance descrito; classificação final/resolvido continuam dependentes de US06. Não encerrar a história nem presumir os demais campos/snapshots não homologados. US04 mantém M02 pendente; US05 não iniciada. Docker Compose e CI no GitHub pendentes, US01 parcialmente validada. Sem chamadas pagas, publicação ou deploy.


## 08/11/2026 — Início guiado de US04: somente geração de sugestão

A pedido de Eliana, conduzir um cenário por vez e aguardar seu relato antes do seguinte. Verificação técnica do agente, somente leitura via HTTPX/TCP: GET `/api/v1/tickets/ad903cac-a750-48d3-b205-91da97d7adee` retornou 200, version=2/content_revision=2, aberto/pendente, suggestion/final_classification=null. GET `/openapi.json` retornou 200, API 0.3.0 e POST triage disponível. Nenhum POST/PATCH executado, nenhum dado alterado e nenhuma nova suíte executada.

Orientação atual: POST `/api/v1/tickets/ad903cac-a750-48d3-b205-91da97d7adee/triage`, corpo completo `{"expected_version":2}`. Esperado 200, ticket aberto/sugerida, version=4/content_revision=2, sugestão simulated/defeito/media, ausentes impacto e inicio_ocorrencia para o texto atual, classificação final nula; tentativa sucesso, 3 chamadas de modelo e 2 ferramentas. **Geração ainda aguarda execução/relato de Eliana; não homologada.** Próximos passos separados: no-op com sugestão, edição que invalida e preserva histórico, saída simulada inválida. Consultar a versão novamente antes de orientar cada operação com expected_version. Não repetir limites/campos já conferidos.

US03 mantém pendências específicas; classificação final/resolução dependem de US06. US04 aguarda homologação; US05 não iniciada. Docker Compose e CI remota pendentes; US01 parcialmente validada. Somente modo simulado, sem custos, publicação ou deploy.


## 08/11/2026 — US04 simulada implementada; aguardando homologação de Eliana

### Autorização e escopo

Eliana aceitou E01–E04 de US03 e autorizou US04 exclusivamente simulada. Aceite registrado sem repetir cenários. US03 permanece aberta com pendências específicas de sugestão/classificação/snapshots; sugestão passa a estar disponível pelo Swagger nesta entrega, classificação final/resolução continuam dependentes de US06. US05/US06 não iniciadas, US08 adiada. Docker Compose e CI remota continuam pendentes; US01 parcialmente validada. Não houve chamada paga, SDK de IA, publicação ou deploy.

Git inspecionado: branch anterior feat/us03-ticket-edit, com alterações documentais e arquivo workspace preexistentes preservados. Criada branch local feat/us04-simulated-triage (primeira tentativa bloqueada pela restrição de escrita em .git, repetida com permissão ampliada). Não houve rebase, reset ou sobrescrita do histórico. Arquivo projeto-agente-ia.code-workspace mantido fora da entrega. Nenhuma dependência adicionada/atualizada; locks e fontes oficiais anteriores mantidos. Aplicação 0.3.0.

### Rastreabilidade e comportamento entregue

| Critérios/tasks | Código | Evidências |
|---|---|---|
| US04-CA1/T1/T2 | agent/protocol.py, simulated.py, tools.py, orchestrator.py; application/triage.py; rotas/schemas | Ferramentas locais consultadas, sugestão validada e modo simulated; tentativa confirmada antes do provedor, conexão liberada, sucesso sem classificação final |
| US04-CA2/T2 | AgentOutput, allowlist e erros sanitizados; modelos/migração 0003 | Enums, extras, justificativa curta, ferramenta desconhecida/argumentos inválidos/consulta ausente rejeitados; nenhuma sugestão inválida publicada, conteúdo preservado e tentativa falha consultável |
| US04-CA3/T2 | Laço e orçamento externos ao provedor; validação de ausentes | Exatos 3 modelos/4 ferramentas/2.000 tokens aceitos, chamada adicional rejeitada; ausentes 0/4 aceitos, 5/duplicatas rejeitados; relógio controlado inclui tempo de ferramenta/modelo |
| US04-CA4/T2 | Dados JSON separados do sistema; fixtures simuladas | Sem impacto informado, inclusive dúvida: média provisória e impacto ausente; prompt injection não habilita shell ou categoria externa; AV01–AV08 com roteiros, sem avaliação de modelo real |
| Base transacional US04/T2 | models.TriageAttempt, application/triage.py, migração 0003 | Uma tentativa ativa/numeração única, finalização condicional, duas conexões concorrentes com só um agente; migração preserva conteúdo/eventos/snapshots e roundtrip só em banco descartável |
| Regressão US01–US03/T2 | Suítes anteriores + tests/api/test_triage.py e tests/e2e/test_http.py | Cadastro, consulta, edição, conflitos, no-op com sugestão real do simulador, invalidação/snapshot e histórico de tentativas; teste TCP/Uvicorn inclui sucesso e falha relevante |
| US04-T3 | README, arquitetura ADR08, contrato, backlog, ambiente/guia e docs/13-homologacao-us04.md | Homologação curta preparada; nenhum resultado manual de US04 presumido |

Entidade normalizada TriageAttempt adicionada por migração somente aditiva. FK ticket_id e índice único parcial identificam a tentativa ativa sem referência circular nova em Ticket; sugestão guarda attempt_id gerado internamente. Finalização confere tentativa/status, revisão e versão capturada sob lock. Edição mantém tentativa imutável e snapshot anterior no evento. Rationale simulado usa descrições/ política retornadas pelas ferramentas; regras de fixture não são inferência de modelo real. Detalhes e limites em ADR08.

### Testes realmente executados

Comandos na raiz com Python da .venv, PostgreSQL 16 local e bancos exclusivos portfolio_test_<uuid>, sem limpar o demo:

```powershell
.\.venv\Scripts\python.exe -m ruff check .
.\.venv\Scripts\python.exe -m ruff format --check .
.\.venv\Scripts\python.exe -m pip check
$env:TEST_DATABASE_URL='postgresql+psycopg://portfolio_test:senha_ficticia_teste@127.0.0.1:55432/portfolio_test'
.\.venv\Scripts\python.exe -m pytest -q --junitxml=reports/us04-complete-final.xml
```

**Resultado final: 124 passed, 1 warning, 181,43 s; zero falhas, erros ou skips.** São 73 unitários, 39 API dentro do processo com PostgreSQL real, 11 de integração (10 com PostgreSQL ativo e um de conexão recusada por driver real) e 1 HTTP/TCP com Uvicorn e PostgreSQL real. A execução final cobre o código entregue, incluindo as justificativas e a regra de impacto refinadas. Não há SQLite, chamada de IA externa ou teste no banco demo.

Evidências intermediárias: unitários iniciais 73 passed/1 warning; API/migração focados 15 passed/1 warning. Primeira suíte completa: 122 passed/2 failed, 174,36 s; corrigidos teste antigo que enumerava só as rotas US01–US03 e fixture SQL de migração cujo JSON literal era interpretado como bind parameters. Segunda suíte completa: 124 passed/1 warning, 199,19 s. Verificação do limite de modelo refinada para isolar quarta chamada sem exceder ferramentas: 36 testes de agente aprovados. Após separar validação de domínio da serialização API, foco agente/API/integração/HTTP: 53 passed/1 warning, 69,57 s. Ajuste final de justificativa a partir das respostas das ferramentas e regra de dúvida sem impacto motivou a suíte final acima. Falhas intermediárias de Ruff (formatação/linhas longas) corrigidas; Ruff e pip check aprovados ao final. Aviso conhecido Starlette/TestClient sobre HTTPX permanece, sem pacote adicional para ocultá-lo. Relatórios locais em reports/, ignorados pelo Git.

### Demo e Swagger preparados

Executado snapshot somente leitura de todos os campos de tickets/ticket_events, `alembic upgrade head` no demo e novo snapshot: **preservação integral True, 1 chamado, 2 eventos, 0 tentativas**, migração 0003. Evidência operacional local `.local/demo-us04-preservation.json`, ignorada pelo Git. Nenhum POST/PATCH executado no demo pelo agente. Downgrade somente em testes descartáveis.

Primeira tentativa de reinício da API foi interrompida antes de encerrar processos porque Get-NetTCPConnection não encontrou listener, embora HTTP respondesse; Get-CimInstance/netstat na sandbox também tinham limitações de acesso/visibilidade. Identificação por comando Uvicorn, executável absoluto da .venv deste projeto e parentesco confirmou launcher 18120/servidor 18256; só esses processos foram encerrados. API iniciada em modo hidden/loopback com AI_MODE=simulated e DATABASE_URL do demo. Verificação: /health, /docs, /openapi.json e GET do chamado retornaram 200; API 0.3.0, rota triage presente, chamado ad903cac-a750-48d3-b205-91da97d7adee version/content_revision=2, aberto/pendente, suggestion=null; GET triage-attempts retornou 200/total=0. Após os últimos ajustes, API recarregada novamente identificando launcher 20720 e seu único filho pelo comando/parentesco. Launcher final PID **17332**, logs `.local/api-us04-final.*`, fora do Git. Nova conferência HTTP de health/docs/OpenAPI/chamado/tentativas retornou 200 e SQL somente leitura confirmou novamente igualdade integral com o snapshot anterior e dois eventos. API e banco deixados ativos; PIDs devem ser reconferidos antes de qualquer encerramento.

### Homologação e limites preservados

**US04 implementada e verificada automaticamente, aguardando homologação de Eliana; não encerrada.** Roteiro curto em [13-homologacao-us04.md](13-homologacao-us04.md): M01 sugestão → no-op classificado → edição invalida sugestão e mantém tentativa; M02 saída inválida → falha sanitizada, chamado preservado. Ambos aguardam relato. Não repetir E01–E04 de US03. Pendências de US03 com sugestão tornam-se verificáveis agora, sem marcá-las aprovadas antes do relato; classificação final/resolvido dependem de US06. Snapshot após múltiplas edições segue com evidência automatizada e pendência manual registrada.

Retry em falha, recuperação por prazo e ensaios completos de interrupção/finalização ficam em US05. Nesta entrega triage exige aberto/pendente; falha pode retornar a pendente por edição efetiva, sem oferecer retry direto ainda. Prazo verificado nas fronteiras das chamadas e na finalização; simulador imediato/sem I/O. Preempção de provedor Python arbitrariamente bloqueante não está implementada; a interface exige respeito ao orçamento para futuros adaptadores. Tokens do simulador são metadados roteirizados, não medição real de tokenizer. Nenhuma qualidade de IA externa alegada. Docker Compose e CI no GitHub permanecem não executados; não declarar cobertura Docker/Linux/CI por testes nativos. Somente AI_MODE=simulated e uso em loopback.


## 08/11/2026 — E04d informado; roteiro E01–E04 coberto no alcance dos relatos

E04d/US03-CA2/CA3 registrado sem duplicação como **homologação manual informada por Eliana**: PATCH expected_version=2/description="curta" retornou HTTP 422, validation_error, body.description/string_too_short. GET posterior HTTP 200 manteve título, descrição, version=2, content_revision=2 e timestamps anteriores. Sem observação visual ou reexecução do PATCH pelo agente.

Conferência técnica: `psql -X -v ON_ERROR_STOP=1 -h 127.0.0.1 -p 55432 -U portfolio_test -d portfolio_chamados_demo -c <SQL>`, com `BEGIN READ ONLY; SHOW transaction_read_only; SELECT` de chamado/contagem/eventos e `COMMIT`: **saída 0**, modo somente leitura on, **exatamente dois eventos**, criado/revisão 1 e editado/revisão 2; nenhum evento adicional após E04d. Chamado ad903cac-a750-48d3-b205-91da97d7adee com version/content_revision=2, created_at=2026-11-07T21:23:24.789820Z, updated_at=2026-11-08T13:01:30.959837Z; snapshot anterior mantém revisão 1 e classificações nulas. Nenhuma escrita de dados ou mudança operacional.

E01–E03 e os quatro exemplos E04a–E04d estão registrados no alcance dos relatos, com histórico básico conferido tecnicamente. Não solicitar repetição desses exemplos nem confundir E04 com homologação de todos os limites/tipos. A matriz atual de cenários restantes está em [homologação US03](12-homologacao-us03.md): testes automatizados já executados na entrega de 07/11/2026 cobrem os demais limites, entradas inválidas, UUID ausente no PATCH, estados bloqueados, concorrência, rollback, migração e classificação com fixtures. Revisão dos arquivos de teste nesta etapa; **suíte não reexecutada**. Evidência histórica: 72 passed/1 warning, registrada abaixo; não atribuir esse resultado a nova execução.

**US03 não encerrada e US04 não iniciada.** Homologação manual pendente de classificação não nula e seus snapshots preservada; produção pelo Swagger depende de US04 (sugestão) e US06 (classificação final). Estados em_analise/resolvido dependem dos respectivos fluxos futuros para eventual homologação manual, mas já têm testes com fixtures. Não semear o demo nem antecipar histórias. Não há próximo exemplo E05 definido no roteiro atual. Não criar exigência de repetir manualmente toda a suíte: revisão/aceite de Eliana deve considerar a matriz de evidências e as pendências sem convertê-las em aprovação automática. Docker Compose e CI no GitHub pendentes, US01 parcialmente validada; US08 adiada, AI_MODE=simulated, sem chamadas pagas, publicação ou deploy.


## 08/11/2026 — E04c informado; histórico reconfirmado somente em leitura

E04c/US03-CA2/CA3: **homologação manual informada por Eliana**, sem duplicação. PATCH expected_version=2 e title="abcd": HTTP 422, validation_error, campo body.title, motivo string_too_short. GET posterior HTTP 200 preservou título, descrição, version=2, content_revision=2 e timestamps anteriores. O agente não observou visualmente nem reexecutou o PATCH.

Conferência técnica executada com `psql -X -v ON_ERROR_STOP=1 -h 127.0.0.1 -p 55432 -U portfolio_test -d portfolio_chamados_demo -c <SQL>`: `BEGIN READ ONLY; SHOW transaction_read_only; SELECT` de versões/timestamps, contagem e eventos do chamado `ad903cac-a750-48d3-b205-91da97d7adee`; `COMMIT`. **Saída 0, transaction_read_only=on; exatamente dois eventos**, criado/revisão 1 e editado/revisão 2, sem evento adicional após E04c. Version/content_revision=2; created_at=2026-11-07T21:23:24.789820Z e updated_at=2026-11-08T13:01:30.959837Z. Nenhuma escrita de dados ou alteração de processo; nenhuma nova execução de testes de aplicação.

**Próximo cenário vigente: E04d — descrição abaixo de 20 caracteres.** No mesmo chamado, PATCH `{"expected_version":2,"description":"curta"}` (usar versão atual se houver mudança posterior). Esperado HTTP 422/validation_error; GET posterior HTTP 200 preservando título, descrição, versões e timestamps. **E04d não executado; aguardar relato de Eliana.** Não repetir E01–E03/E04a–E04c. E04 completo e US03 continuam abertos.

Pendências preservadas: sugestão existente depende de US04 e classificação final de US06 para homologação via Swagger; fixtures automatizadas não equivalem a homologação manual de classificação não nula. Docker Compose e CI no GitHub pendentes, US01 parcialmente validada. Sem início de US04/US06, US08 adiada; AI_MODE=simulated, sem chamadas pagas, publicação ou deploy.


## 08/11/2026 — E04b informado; histórico conferido somente em leitura

E04b/US03-CA2/CA3 registrado uma única vez como **homologação manual informada por Eliana**: PATCH com expected_version=2 e title=null retornou HTTP 422/validation_error; GET posterior HTTP 200 preservou título, descrição, version=2, content_revision=2 e timestamps anteriores. Sem observação visual nem reexecução do PATCH pelo agente.

Conferência técnica executada com `psql -X -v ON_ERROR_STOP=1 -h 127.0.0.1 -p 55432 -U portfolio_test -d portfolio_chamados_demo -c <SQL>`: `BEGIN READ ONLY; SHOW transaction_read_only; SELECT` de chamado, contagem e eventos, seguido de `COMMIT`. **Saída 0**, transaction_read_only=on. Chamado `ad903cac-a750-48d3-b205-91da97d7adee`: version=2/content_revision=2, created_at=2026-11-07T21:23:24.789820Z, updated_at=2026-11-08T13:01:30.959837Z. **Exatamente dois eventos**, criado/revisão 1 e editado/revisão 2; nenhum evento adicional após E04b. Snapshot anterior da edição mantém revisão 1 e classificações nulas. Nenhuma escrita de dados ou alteração de processo; nenhuma nova execução de testes de aplicação alegada.

**Próximo cenário vigente: E04c — título abaixo de 5 caracteres**, conforme roteiro: no mesmo chamado, PATCH `{"expected_version":2,"title":"abcd"}`. Esperado HTTP 422/validation_error; GET posterior HTTP 200 com título, descrição, versões e timestamps preservados. Usar versão atual caso outro GET indique mudança. **E04c não executado; aguardar relato de Eliana antes de E04d.** Não repetir E01–E03/E04a/E04b. E04 completo e US03 permanecem abertos.

Pendências preservadas: classificação existente não nula depende de US04 (sugestão) e US06 (classificação final) para produção pelo Swagger; evidência automatizada com fixtures não equivale à homologação manual. Docker Compose e CI no GitHub pendentes; US01 parcialmente validada. US04/US06 não iniciadas, US08 adiada; somente AI_MODE=simulated, sem chamadas pagas, publicação ou deploy.


## 08/11/2026 — Ambiente restabelecido; histórico de E04a reconfirmado

Por solicitação de Eliana, consultado o guia de execução e confirmado `.local/pgdata/PG_VERSION=16`. `pg_ctl status` informou servidor parado. Iniciado **o cluster existente**, com `pg_ctl -D <projeto>/.local/pgdata -l <projeto>/.local/postgres.log -o "-h 127.0.0.1 -p 55432" -w start`, sem initdb, createdb, limpeza ou migração. Primeira tentativa na sandbox falhou com erro 87 de criação de token; execução com permissão ampliada iniciou com sucesso. Aviso de possível servidor existente foi emitido pelo pg_ctl; nenhum PID/arquivo foi removido manualmente.

Consulta real por `psql -X -v ON_ERROR_STOP=1` ao banco demo, com `BEGIN READ ONLY; SHOW transaction_read_only; SELECT ...; COMMIT`, executada com sucesso: modo somente leitura `on`, banco `portfolio_chamados_demo`, endereço 127.0.0.1, porta 55432, migração 0002. Chamado `ad903cac-a750-48d3-b205-91da97d7adee`: **version=2, content_revision=2**. Histórico reconfirmado após E04a: **exatamente dois eventos**, criado/revisão 1 e editado/revisão 2, sem evento adicional pela rejeição. Snapshot da edição permanece com content_revision=1, suggestion=null e final_classification=null. Essa consulta resolve a pendência de conferência antes impedida por conexão recusada; não é reexecução do PATCH nem homologação visual pelo agente.

API iniciada em segundo plano com Start-Process/WindowStyle Hidden, Python da .venv, Uvicorn factory, bind 127.0.0.1:8000, DATABASE_URL do demo e AI_MODE=simulated. Launcher PID 18120 (reconferir identidade antes de encerrar); logs `.local/api-restored.stdout.log` e `.local/api-restored.stderr.log`. GET /health, /docs e /openapi.json retornaram **200**; versão 0.2.0 e PATCH presente. **GET /api/v1/tickets/ad903cac-a750-48d3-b205-91da97d7adee retornou 200 com o registro persistido**, comprovando consulta pela API além do health: aberto/pendente, versões 2, suggestion/final_classification nulos, created_at=2026-11-07T21:23:24.789820Z e updated_at=2026-11-08T13:01:30.959837Z. Nenhuma escrita de chamado/evento. Inspeção complementar com Get-NetTCPConnection teve acesso negado; isso não invalida os retornos HTTP nem a conexão SQL confirmados. API e banco deixados ativos, sem garantia de sobrevivência ao encerramento da sessão do sistema.

**Próximo cenário: E04b — título nulo**, usando expected_version=2 consultada. Orientar pelo Swagger e aguardar resultado de Eliana; **não executado e não homologado nesta etapa**. E01–E03 e E04a não foram repetidos. US03 continua aberta. Homologação com sugestão existente depende de US04; classificação final depende de US06; fixtures automatizadas não equivalem a homologação manual. Docker Compose e CI no GitHub continuam pendentes, US01 parcialmente validada. Sem início de US04/US06, chamadas pagas, publicação ou deploy. Verificação operacional SQL/HTTP executada; sem nova execução da suíte de testes de aplicação.


## 08/11/2026 — E04a informado; nova consulta do histórico sem conexão

Registrada em [homologação US03](12-homologacao-us03.md) a **homologação manual informada por Eliana**: PATCH somente com expected_version=2 retornou 422/validation_error; GET posterior 200 com título, descrição, version=2, content_revision=2 e timestamps anteriores preservados. E04a confirmado no alcance do relato, sem reexecução pelo agente; E04 completo e US03 continuam abertos.

Conferência somente leitura tentada com `psql -X -v ON_ERROR_STOP=1 -h 127.0.0.1 -p 55432 -U portfolio_test -d portfolio_chamados_demo -c <SQL>`: transação preparada com `BEGIN READ ONLY`, `SHOW transaction_read_only`, SELECT de chamado/contagem/eventos e COMMIT. Resultado: **conexão recusada, saída 1; SQL não executado**. Nenhum dado ou processo alterado. Os dois eventos foram confirmados na consulta anterior a E04a, mas **não reconfirmados após a rejeição atual**. Pendente repetir consulta quando PostgreSQL estiver disponível; não inferir histórico apenas do GET.

Próximo cenário vigente: **E04b, title=null**, com versão atual conferida por GET; esperado 422/validation_error e GET posterior integralmente inalterado. Aguardar retorno antes de E04c, sem repetir cenários homologados. Dependências de US04 (sugestão) e US06 (classificação final) para homologação de classificação não nula via Swagger preservadas; sem semear dados ou antecipar histórias. Docker Compose e CI no GitHub pendentes; US01 parcialmente validada. US04 não iniciada. Nenhum teste de aplicação novo executado ou alegado; somente tentativa de consulta operacional e atualização documental. Sem chamadas pagas, publicação ou deploy; AI_MODE=simulated.


Nova tentativa nesta continuidade de 08/11/2026: mesmo relato de E04a reconhecido, sem duplicar homologação. Consulta `psql -X -v ON_ERROR_STOP=1` ao mesmo banco/porta, com `BEGIN READ ONLY`, verificação do modo, SELECT de versões, contagem e eventos e COMMIT: conexão novamente recusada, código de saída do psql=2. Nenhum SQL executado, nenhum processo iniciado e nenhum dado alterado. O código 1 da tentativa anterior correspondeu ao comando PowerShell que lançou erro após a falha do psql. Histórico após E04a continua pendente de reconferência; não afirmar dois eventos atuais. Próximo cenário continua E04b (title=null); não avançar sem seu relato. US04/US06, Compose e CI mantêm as dependências e pendências acima.

## 08/11/2026 — E03 informado e histórico conferido no PostgreSQL

Eliana informou E03/US03-CA3: HTTP 200, título normalizado, version/content_revision mantidos em 2 e timestamps iguais ao GET anterior. Registrado como homologação manual informada em [homologação US03](12-homologacao-us03.md).

Conferência técnica do agente: `psql` em 127.0.0.1:55432/portfolio_chamados_demo, transação `BEGIN READ ONLY`, SELECT de versões e de eventos/contagens, COMMIT; execução com sucesso. Único chamado ad903cac-a750-48d3-b205-91da97d7adee na versão/revisão 2. Exatamente **dois eventos**: criado/revisão 1 e editado/revisão 2, um de cada, sem evento extra para o no-op. Snapshot de edição preserva revisão anterior 1, suggestion=null e final_classification=null. Não houve escrita nem nova execução de PATCH pelo agente. Essa consulta não comprova preservação de classificação não nula; dependência de US04/US06 para geração via Swagger continua registrada.

Próximo cenário guiado: **E04a — PATCH apenas com expected_version=2, sem title/description**; esperado 422/validation_error e GET inalterado. Aguardar retorno antes de outro subcaso. E04 não encerrado; homologação de US03 permanece aberta. Docker Compose e CI no GitHub pendentes; US01 não totalmente validada. Sem início de US04, publicação, deploy ou chamadas pagas. Apenas consulta operacional/documentação nesta etapa; nenhum teste de aplicação novo alegado.

## 08/11/2026 — Homologação manual parcial de US03 informada por Eliana

Eliana informou: PATCH com expected_version=1 retornou 200, descrição alterada e título preservado, version/content_revision 1→2; novo PATCH com versão 1 e outra descrição retornou 409/version_conflict; GET posterior retornou 200, versões=2 e descrição da primeira edição preservada, sem aplicar a rejeitada. Registro atualizado em [homologação US03](12-homologacao-us03.md), distinguindo relato humano de automação. ID, texto integral, timestamps e estado da classificação não foram informados, portanto não foram presumidos.

**US03 continua em homologação, não encerrada.** Próximo cenário: E03/no-op após trim, RN01/RN11 e US03-CA3; orientar somente esse cenário e aguardar retorno antes de E04. Comparar resposta com GET anterior, inclusive timestamps e versões. Histórico básico pode ser conferido agora por SQL somente leitura, mas não há endpoint de eventos no Swagger. Invalidação/snapshot de classificação existente dependem, para geração pelo fluxo público local da API, de US04 (sugestão) e US06 (classificação final). Evidência automatizada com fixtures já existe, mas não é homologação manual; não semear dados diretamente no demo nem iniciar essas histórias para contornar o limite.

Docker Compose e execução do CI no GitHub continuam pendentes; US01 não totalmente validada. Nenhum código, dado de chamado ou estado operacional alterado nesta etapa; nenhuma nova execução de testes de aplicação declarada. Mudança documental para registrar resultados e conduzir o próximo cenário. US04 não iniciada, nenhuma publicação ou chamada paga.

## 07/11/2026 — Homologação informada de US02 e implementação de US03

### Retorno de Eliana e verificação complementar

Eliana informou execução manual no Swagger e conferência de: cadastro 201 com campos/location esperados; consulta 200; lista 200/total=1/limit=20/offset=0; página limit=1/offset=1 com items=[] e total=1; POST sem title 422/validation_error/body.title/missing; UUID inexistente 11111111-1111-4111-8111-111111111111 com 404/not_found. Resultados registrados como **homologação manual informada pela usuária**, não execução visual do agente, em [registro US01/US02](11-homologacao-us01-us02.md).

Não persistência de H04 foi verificada adicionalmente pelo agente antes de encerrar o cenário: SQL direto no PostgreSQL demo antes/depois de repetir POST sem title válido estruturalmente nos demais campos. HTTP 422; tickets **1→1**, ticket_events **1→1**; request_id 81295f21-37d8-4464-8cac-88371face1ee. Dados preservados. Isso reproduz o comportamento, não reconstrói a requisição histórica da usuária. Ausência de description não foi homologada manualmente; não atribuir esse caso ao relato.

Eliana autorizou iniciar US03 explicitamente. A fundação nativa estava verificada, mas Docker Compose permanece pendente e **US01 não está totalmente validada**. Execução do CI no GitHub continua pendente. Autorização não inclui US04, chamadas pagas, publicação ou deploy.

### Implementação de US03 e rastreabilidade

| Critério/task | Arquivos | Evidência executada |
|---|---|---|
| US03-CA1/T1 | routes.py, schemas.py, application/tickets.py, domain/editing.py | PATCH altera só campos fornecidos, incrementa versões, volta a pendente e registra evento na mesma transação |
| US03-CA1/T1 | models.py, domain/classification.py, migração 0002 | Projeções JSONB nullable e snapshot da classificação anterior no evento; não há rota para definir classificações |
| US03-CA1/T2 | tests/api/test_editing.py::test_us03_ca1_patch_content_and_history | HTTP 200, persistência confirmada por GET, versões/timestamps e eventos conferidos no PostgreSQL |
| US03-CA1/T2 | tests/integration/test_editing.py::test_us03_ca1_archive_classification_and_preserve_history | Fixture sintética classificada: no-op preserva, edição limpa dados atuais e arquiva snapshot; segunda edição preserva o snapshot anterior |
| US03-CA2/T2 | testes unitários e API de edição | 409 para versão antiga/resolvido/em_analise; 404 para UUID ausente; 422 sem campos de conteúdo, null, extras e versões inválidas |
| US03-CA2/T2 | test_us03_ca2_two_connections_only_one_version_wins | Duas conexões PostgreSQL adquiridas antes da disputa: uma confirma, outra recebe 409/version_conflict; apenas um evento editado |
| US03-CA1/CA2/T2 | test_us03_edit_event_failure_rolls_back_everything | Constraint de evento inválido reverte texto, versões, classificação e estado; não insere evento parcial |
| US03-CA3/T2 | testes unitários e API | Trim, no-op com resposta/timestamps/eventos intactos, limites exatos e ±1, null/tipos/extra rejeitados |
| US03-T2 | test_us03_migration_preserves_existing_ticket; migração roundtrip existente | Upgrade 0001→0002 preserva chamado; downgrade/upgrade só em banco descartável; alembic check sem divergência |
| US03-T2 | tests/e2e/test_http.py | TCP/Uvicorn real: cadastrar, editar, consultar e rejeitar versão antiga; PostgreSQL real exclusivo |
| US03-T3 | arquitetura ADR07, contrato API, README, guia Windows e registro de homologação | Decisão técnica, exemplos de conflito e roteiro manual atualizados |

Implementação usa SELECT FOR UPDATE dentro de transação: obter linha, verificar versão/estado, arquivar classificação, alterar e registrar evento sem liberar o bloqueio entre comparação e escrita. No-op ainda exige versão e estado válidos. Sem dependência de IA. ADR07 explica projeções/snapshots antes de existirem entidades de tentativas/revisões; estas seguem futuras. Não guardar texto antigo completo nem alegar auditoria legal.

### Testes e correções reais

Comandos na raiz, com Python da .venv e TEST_DATABASE_URL apontando para banco administrativo isolado portfolio_test em 127.0.0.1:55432:

```powershell
.\.venv\Scripts\python.exe -m ruff check .
.\.venv\Scripts\python.exe -m ruff format --check .
.\.venv\Scripts\python.exe -m pip check
$env:TEST_DATABASE_URL = 'postgresql+psycopg://portfolio_test:senha_ficticia_teste@127.0.0.1:55432/portfolio_test'
.\.venv\Scripts\python.exe -m pytest -q --junitxml=reports/us03-all.xml
```

**Resultado final: 72 passed, 1 warning, 185,82 s, nenhuma falha ou skip.** São 37 unitários, 9 integração (8 com PostgreSQL ativo + 1 de conexão recusada com driver real), 25 API dentro do processo com PostgreSQL real e 1 HTTP/TCP com Uvicorn real e PostgreSQL. Unitários usam objetos simples/mocks quando apropriado; não representam persistência. Não há SQLite. Cada teste de banco ativo usa banco exclusivo, sem limpar o demo. Relatório local ignorado pelo Git em reports/us03-all.xml. Ruff check/format e pip check aprovados; sem novas dependências.

Falhas intermediárias registradas e resolvidas: coleta pytest conflitou com módulos homônimos de testes, resolvido por --import-mode=importlib (sem apagar arquivos); integração inicial teve 34 passados/1 falha por PATCH/GET representarem o mesmo timestamp em fusos diferentes. Corrigida normalização de created_at/updated_at em UTC no schema de resposta e incluída regressão unitária; suíte final integral aprovada. Aviso conhecido de depreciação HTTPX/TestClient continua visível, sem falha. Formatação corrigida antes do resultado final.

### Banco demo e API prontos para homologação

Aplicada apenas migração upgrade head no demo: **0002 (head)**. Comparação de todos os campos preexistentes antes/depois confirmou **1 chamado e 1 evento preservados integralmente**; nenhuma edição de chamado demo pelo agente. Snapshots operacionais em .local/demo-us03-preservation.json, fora do Git. Downgrade não foi executado no demo.

API antiga identificada pelo comando Uvicorn e pelo processo lançador da .venv deste projeto antes de encerrá-la. Houve uma tentativa de inicialização sem sucesso por porta ocupada, sem modificar dados. Inspeção via Get-NetTCPConnection não foi suficiente; identificação final usou Win32_Process com comando/parent verificados. A API foi atualizada sem encerrar processos desconhecidos. Versão **0.2.0**, PATCH presente no OpenAPI, `/docs` HTTP 200, total demo=1 e version do chamado=1 confirmados após inicialização. API e PostgreSQL deixados ativos em loopback. Logs atuais .local/api-us03-current.*; launcher PID 16780, servidor PID 23448 (sempre reconferir identidade antes de encerrar; PIDs podem ser reutilizados).

### Próximo passo e limites

**US03 implementada, CA1–CA3 verificados automaticamente; aguardando homologação de Eliana**, roteiro em [12-homologacao-us03.md](12-homologacao-us03.md). Não marcar homologação manual antes do relato. Invalidação de classificação existente, estados resolvido/em_analise e concorrência têm evidência automatizada com fixtures fictícias: não há rotas de triagem/revisão/resolução para criá-los pelo Swagger ainda. Não antecipar US04–US06 para a homologação.

Docker Compose e CI no GitHub permanecem pendentes; US01 não totalmente validada. US04 não iniciada. Somente AI_MODE=simulated, sem chamadas de IA reais, custos, publicação ou deploy. Em nova conversa, ler esta seção e o registro de homologação antes dos registros históricos abaixo.

## 07/11/2026 — Ambiente iniciado para homologação guiada

PostgreSQL isolado iniciado em 127.0.0.1:55432; banco `portfolio_chamados_demo` criado sem excluir dados, migração `0001 (head)` aplicada. Total inicial=0. API iniciada em segundo plano em 127.0.0.1:8000; `/docs` HTTP 200, health ok e contrato OpenAPI conferidos após a inicialização. Processos deixados ativos para Eliana, sem garantia de sobrevivência a encerramento da sessão do sistema; comandos exatos de retomada documentados.

Homologação própria em [11-homologacao-us01-us02.md](11-homologacao-us01-us02.md). **H01 aguardando retorno de Eliana; H02–H05 não iniciados.** Não registrar aprovação sem retorno. Usar o UUID recebido em H01 nas próximas etapas. Docker Compose e execução remota de CI continuam pendentes, US01 não totalmente validada e US03 não iniciada. Nenhuma publicação ou chamada paga.

## 07/11/2026 — US01/US02 implementadas; aguardando validação de Eliana

### Aprovação e escopo

Eliana aprovou o MVP; [D01–D08 consolidadas](08-decisoes-aprovadas.md), sem conflitos. Somente uso local sem autenticação, categorias/prioridades centrais, triagem separada e retry manual, invalidação após edição, revisão obrigatória antes de resolução e histórico de transições. Provedor real e orçamento adiados; nenhuma chamada paga. Esta entrega se limita à fundação, cadastro/consulta e CI pertinente; não iniciar US03 sem validação de Eliana.

### Ambiente e implementação

- Python 3.12.6, pip 24.2 e Git 2.46.2 disponíveis. Docker/Compose ausentes. PostgreSQL 16.4 instalado, serviço existente parado e preservado.
- `.venv` local criada. Compatibilidade consultada em fontes oficiais antes da instalação; [fontes e versões](09-ambiente-e-versoes.md). Locks fixam dependências diretas/transitivas, sem hashes. Instalação pelo lock conferida com `--no-index` no ambiente já instalado; não representa ensaio de instalação limpa em Linux.
- Cluster de teste separado em `.local/pgdata`, loopback 127.0.0.1:55432, credenciais fictícias. Cada caso cria banco próprio `portfolio_test_<uuid>` e remove apenas esse banco; desenvolvimento não é usado. Serviço global não alterado. Scripts de iniciar/parar em `scripts/`.
- API FastAPI por factory; sessões SQLAlchemy, Alembic 0001, tabelas Ticket/TicketEvent, cadastro transacional com evento, consulta por UUID, listagem/paginação/filtros, trim e limites Unicode, campos extras rejeitados e erros uniformes sanitizados.
- Rotas disponíveis: GET `/health`, POST/GET `/api/v1/tickets`, GET `/api/v1/tickets/{ticket_id}`; Swagger e OpenAPI. Sem PATCH, triagem ou revisão nesta entrega. Cadastro não importa/instancia provedor algum e não depende de IA. AI_MODE diferente de simulated é rejeitado.
- Dockerfile/Compose com portas publicadas somente em loopback; migração como serviço separado. Workflow GitHub Actions com PostgreSQL 16 e etapas separadas de lint, unitários, integração/API e HTTP real. Preparados, mas Docker e CI remota não executados.
- Git local inicializado na branch `feat/foundation-tickets`, sem remoto; nenhuma publicação ou deploy.

### Rastreabilidade e evidências reais

| Critérios/tasks | Código/documentação | Evidência executada |
|---|---|---|
| US01-CA1/T1/T3 | pyproject, locks, database, main, Dockerfile, compose, migrations; guia Windows | Migração e health aprovados nativamente; inicialização Compose **não executada** por Docker ausente |
| US01-CA2/T2 | handlers, health e configuração | `test_us01_ca2_us02_storage_error_sanitized` (mock) e `test_us01_ca2_real_driver_connection_refused` (driver real sem servidor) aprovados |
| US01-CA3/T2 | Alembic 0001 e metadados | `test_us01_ca3_migrations_roundtrip_and_metadata`: upgrade duas vezes, alembic check, downgrade/base e novo upgrade, PostgreSQL real |
| US02-CA1/T1/T2 | rotas, schemas, serviço, repositório, modelos | `test_us01_ca1_us02_ca1_create_read_list`, `test_us02_atomic_event_and_reconnect` e `test_us02_http_real_process` aprovados |
| US02-CA2/T2 | validação e erros | Casos unitários e `test_us02_ca2_ca3_invalid_not_persisted`; 404/UUID inválido; rollback de evento com falha real de constraint |
| US02-CA3/T2 | schemas e constraints | Limites 5/120, 20/5000, ±1, trim/Unicode no unitário e por HTTP dentro do processo, com PostgreSQL real |
| US02-CA4/T2 | paginação/filtros/ordenação | Listagem vazia, limit 1/100 e inválidos 0/101, offset negativo, filtros inválidos e páginas estáveis aprovados |
| US02-T3 | README, contrato atualizado, guia Windows e decisões | Links locais conferidos e separação explícita entre rotas ativas e futuras |
| Base de US07 | `.github/workflows/ci.yml` e suítes por camada | Comandos locais equivalentes executados; workflow remoto não executado; US07 não concluída |

Comandos executados na raiz (Python local: `.\.venv\Scripts\python.exe`):

```powershell
.\.venv\Scripts\python.exe -m pip check
.\.venv\Scripts\python.exe scripts/lock_dependencies.py
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.lock --no-index
.\.venv\Scripts\python.exe -m ruff check .
.\.venv\Scripts\python.exe -m ruff format --check .
$env:TEST_DATABASE_URL = 'postgresql+psycopg://portfolio_test:senha_ficticia_teste@127.0.0.1:55432/portfolio_test'
.\.venv\Scripts\python.exe -m pytest -q --junitxml=reports/all.xml
# Após ajuste de sanitização da configuração e header de erro:
.\.venv\Scripts\python.exe -m pytest tests/unit tests/integration/test_unavailable.py -q --junitxml=reports/final-focused.xml
git diff --check
```

**Resultado completo: 40 passed, 1 warning, 133,84 s; nenhuma falha ou skip.** Divisão: 16 unitários, 5 integração, 18 API, 1 e2e. Integração: 4 casos com PostgreSQL ativo + 1 de conexão recusada com driver real. API: TestClient/HTTPX dentro do processo e PostgreSQL real. E2E: Uvicorn em processo separado, HTTPX por TCP e PostgreSQL real. **Reexecução focada final: 17 passed, 1 warning, 3,70 s**, sem novos casos além dos 40. Pip check sem dependências quebradas; Ruff check e format aprovados. Uma execução anterior de PostgreSQL/API/e2e havia obtido 22 passed antes dos dois casos adicionais. Relatórios JUnit locais em `reports/`, ignorados pelo Git.

Aviso preservado: Starlette TestClient depreca uso de HTTPX e sugere HTTPX2. Não houve falha; nenhum pacote extra foi instalado para esconder o aviso. Limitação técnica registrada em ambiente/versões. Primeira passagem de Ruff identificou formatação/linhas longas, corrigidas antes das verificações finais.

Conferência documental: 23 links locais verificados, zero quebrados; .env, .venv, .local e reports confirmados como ignorados por `git check-ignore`. Nenhum segredo real usado; apenas credenciais fictícias de desenvolvimento/teste.

### Estado e pendências

- **US01: não concluída**. CA2/CA3 aprovados; falta executar caminho Compose de CA1, imagem Docker e persistência por reinício do Compose. Não declarar cobertura de ambiente Docker/Linux ou de CI remota.
- **US02: implementada, CA1–CA4 verificados localmente, aguardando validação de Eliana.** Dependência US01 tem pendência de ambiente explicitada.
- **US07: somente base adiantada** para as verificações disponíveis; sem fluxo de triagem/revisão ainda.
- **US03–US06 e US09: não iniciadas; US08 adiada.** Não há simulador de triagem implementado ainda (US04); a aplicação atual apenas não utiliza IA.
- Nenhuma avaliação de modelo, chamada paga, publicação ou deploy. Guia de validação em [10-validacao-local.md](10-validacao-local.md).

Próximo passo: Eliana valida os endpoints e o guia local. Se Docker se tornar disponível, executar CA1/Compose e registrar resultado. Somente depois da validação solicitada, seguir para US03, mantendo a dependência de US01 visível. Nas próximas conversas ler esta seção antes do histórico documental abaixo.

## 07/11/2026 — Primeira entrega documental

**Estado: proposta inicial, aguardando revisão do escopo por Eliana.** Aplicação não implementada; nenhuma história US01–US09 iniciada ou concluída. Não configurar dependências nem iniciar código antes da revisão solicitada.

### Pedido e inspeção

Pedido recebido por arquivo anexado e lido em UTF-8. Pasta de trabalho inspecionada com `Get-Location`, `Get-ChildItem -Force` e busca `rg --files -g AGENTS.md -g '!node_modules' -g '!.git'`. A pasta estava vazia, inclusive sem `.git` ou instruções locais preexistentes. Busca sem resultados retornou código 1; não é falha de teste. Nenhum conteúdo existente foi alterado.

### Produzido

README inicial, AGENTS.md, .gitignore e .env.example fictício; documentos 01–07 cobrindo produto, regras, estados, requisitos não funcionais, backlog, critérios/tasks, arquitetura, dados, contrato de API, testes, avaliação do agente, plano, riscos, DoR e DoD.

### Validação desta entrega

Conferência documental executada em PowerShell: enumeração por `Get-ChildItem -Recurse -File`, leitura UTF-8, extração de links Markdown com regex e resolução por `Test-Path`; conferência de seções US01–US09 e marcadores CA1/CA2/CA3/T1/T2/T3 em cada história. Resultado: **12 arquivos, 12 links locais, zero links quebrados, 9 histórias com os marcadores esperados; saída 0**. Nenhum caractere de substituição Unicode encontrado nos documentos. Revisão manual cruzou estados, regras, versões, contrato e dependências; isso não equivale a validação executável do contrato.

Não há aplicação, dependências, testes ou workflow para executar. Nenhuma versão de biblioteca foi validada: essa verificação pertence a US01, antes de configurar dependências. Nenhuma chamada paga, publicação, deploy ou configuração de Git foi realizada.

### Pendências de revisão

Revisar D01–D08 em [produto](01-produto.md): MVP local sem autenticação; catálogo; prioridade sugerida; triagem explícita síncrona e retry; edição/invalidação; revisão humana; resolução/reabertura; escolha de provedor real e orçamento.

### Próxima conversa

1. Ler AGENTS.md, README e este documento.
2. Conferir se Eliana revisou o escopo; incorporar decisões nos documentos e registrar alterações.
3. Após revisão, iniciar US01: inspecionar ferramentas instaladas e Git, verificar versões em fontes oficiais, configurar ambiente/migrações e executar seus critérios.
4. Implementar uma história por vez; registrar IDs de aceite, comandos, resultados e limitações. Manter modo simulado padrão e aguardar autorização específica para publicação/deploy/chamadas pagas.
