# US08 — revisão local e rascunho de pull request

## Retomada autorizada após a correção — 10/11/2026

Eliana autorizou commit/push somente da branch feat/us08-avaliacao e PR draft
para main. Evidência final reutilizável: **334 passed** (219 unitários,
113 PostgreSQL/API e dois HTTP loopback), nenhuma falha/erro/skip. Não encontrados
candidatos de código/configuração modificados depois do início desse pipeline;
somente documentação atualizada posteriormente. Nesta retomada, pip check,
Ruff check/format e diff check novamente aprovados. Seleção exata dos 71 arquivos
abaixo, sem artefatos locais ou credenciais. CI remota será acompanhada após
publicar; os registros anteriores de suspensão/preparação são históricos.
Sem merge, chamada Groq ou execução do lote real de 24.

## Correção local da gravação de evidências — 10/11/2026

Reproduções solicitadas, sem mudança inicial de código: teste batch invalid
isolado passou; R1 success isolado passou com 24 envios mockados; juntos passaram
os dois. Plugin diagnóstico local registrou 36/137/173 substituições,
respectivamente, sem handles Python abertos nos caminhos fonte/destino, um
escritor por execução, diretórios UUID exclusivos e execuções sequenciais.
Isso não exclui handles transitórios de processos externos. Consulta de processos
via CIM foi negada; nenhum processo externo foi identificado como responsável.

Estresse do escritor original reproduziu WinError 5 após 4.833 gravações, com
um único escritor observado, nenhum handle Python aberto e atributos 32 em
fonte/destino (sem somente leitura). A mesma substituição teve sucesso depois,
sem alterar permissões. Confirmada negação transitória na substituição pelo
Windows; não confirmados OneDrive, antivírus ou outro agente específico.

Menor correção compartilhada: piloto e lote usam o mesmo escritor atômico;
temporário fechado antes do replace. Somente replace local recebe até cinco
tentativas para PermissionError Windows 5/32/33, com esperas configuradas de
10/20/40/80 ms; erro persistente e erro não reconhecido são propagados. Manifesto
anterior e temporário pendente são preservados se não for possível substituir.
Não há fallback para escrita parcial no destino, retry HTTP, repetição de
triagem, devolução de orçamento ou relaxamento da parada no primeiro erro.
Estresse corrigido: 10.000 gravações concluídas, quatro negações transitórias
recuperadas em 10.004 tentativas de replace, nenhum handle próprio aberto.

R1 histórico parou no AV04-R1 após 12 requisições, mas sua primeira exceção não
foi preservada e **não pode ser atribuída retroativamente ao bloqueio de disco**.
Nova captura sanitizada de tipo/errno/winerror no piloto e executor evita ocultar
essas informações. Tracebacks completos só no diagnóstico offline temporário,
sem mensagens remotas/credenciais nos relatórios públicos. Injeção explícita de
erro persistente após a terceira resposta do AV04 comprova captura de
PermissionError/13/5, parada aos 12 envios e nenhum AV05; não é reprodução da
causa histórica. Expectativa do sucesso permanece 24 envios, sem alteração.

Cinco testes unitários novos verificam transiência, limite de tentativas,
propagação e preservação atômica. Na primeira elaboração do teste de injeção,
o ponto era antes do envio e resultou em 11 respostas; corrigido o ponto para
após a resposta HTTP, sem alterar expectativa ou código de execução.
Reexecução dos dois testes originais e regressão de disco: **3 passed**, 65,72 s.
Injeção com captura de traceback isolada também passou. Resultados do pipeline
final desta correção, na mesma execução de scripts/check_quality.py: pip check,
Ruff check/formato aprovados; **219 unitários** (21,42 s), **113 PostgreSQL/API**
(548,67 s) e **2 HTTP loopback** (31,74 s) passaram, zero falhas/erros/skips.
Total **334**, exit 0, sem somar execuções anteriores. Diff check final aprovado;
aviso conhecido TestClient/HTTPX mantido. A publicação não foi executada nesta etapa.

Diagnósticos completos fora do checkout em `TEMP/us08-diagnostics-*`, incluindo
stdout/stderr, JUnit, logs de substituição, tracebacks e cópias de evidências.
O caminho exato está em `.local/us08-diagnostics-location.txt` (ignorado).
Nenhum commit/push ou chamada Groq nesta correção. Lista abaixo atualizada com
o novo teste unitário; a autorização anterior de publicar não foi executada.

## Atualização pré-publicação — 10/11/2026

Publicação da branch e PR em rascunho autorizados, mas **suspensos** pela
condição da usuária: parar antes do push se alguma verificação falhar.
Nova execução completa de scripts/check_quality.py: pip check/Ruff/formato
aprovados; unitários 214 passed (18,24 s); PostgreSQL/API **110 passed e 2 failed**
(824,60 s), sem erros/skips. Fase HTTP não executada pelo pipeline após falhar.
Falhas: PermissionError/WinError 5 na substituição do manifesto no cenário
batch invalid; ensaio R1 success interrompido após 12 pedidos mockados contra
24 esperados, causa específica não preservada. Não atribuir a segunda falha
ao mesmo bloqueio de arquivo sem evidência. Detalhes e JUnit no andamento.
Nenhuma correção ou nova tentativa após essas falhas. Sem commit, push, PR ou
CI remota nesta etapa. A aprovação anterior abaixo é histórica e não substitui
o resultado atual. Auditoria da lista de 70 arquivos e diff check aprovados;
demo preservado e AI_MODE=simulated mantido. Nenhuma chamada real à Groq.

## Registro da revisão anterior à autorização de publicar

Base: `main` local; origem: `feat/us08-avaliacao`. Nenhum fetch, commit, push ou
PR remoto foi realizado. O diff de arquivos rastreados foi complementado pela
inspeção dos arquivos novos não ignorados, que `git diff main` não exibe.

## Resultado da revisão

O simulador continua padrão em Settings, `.env.example` e CI. A presença de
uma chave/modelo Groq não seleciona o provedor: exige `AI_MODE=groq`, chave e
modelo não vazios; configuração incompleta falha sem fallback. Os testes de
seleção usam `_env_file=None` e credenciais fictícias. O ambiente local permanece
`AI_MODE=simulated`; nenhuma chave foi usada para autenticação nesta revisão.

Revisados os adaptadores, protocolo de ferramentas/contexto, validação da saída,
persistência antes da triagem, metadados de provedor nos schemas/domínio/banco,
migrações 0005/0006, SQL de concordância e executores. As migrações ampliam os
modos e preservam histórico; testes cobrem upgrade com dados e bloqueio de
downgrade incompatível. TLS verifica certificado/hostname, sem retries do SDK
ou transporte. Groq separa ferramentas da saída final JSON Schema e omite os
parâmetros incompatíveis verificados pelos mocks. Respostas inválidas/falhas
preservam o chamado, sem sugestão indevida. Diagnóstico 429 registra somente
metadados sanitizados. As travas dos executores são separadas da API comum:
16 KiB é limite de corpo HTTP, não teto verificável de tokens de entrada.

O lote real de 24 permanece bloqueado; os perfis reais históricos têm escopos
fixos, confirmação de data/plano e diretório exclusivo. Suas autorizações foram
consumidas; publicação de código não constitui autorização para executá-los.
O demo não foi migrado ou acessado nesta revisão.

Achados documentais corrigidos nos READMEs PT/EN: alegação desatualizada de
validação exclusivamente mockada, omissão da avaliação exploratória Groq e
referência PT a head 0005 (atual 0006). Descrição agora distingue cobertura de
oito cenários, qualidade semântica, falha 429 original e consistência pendente.
Na suíte completa foi identificada uma asserção desatualizada em
`tests/api/test_triage.py`: igualava catálogo e política à versão 1. Corrigida
para catálogo 1/política 2, refletindo as instruções revisadas já existentes;
sem alteração de produção. A conclusão tem os limites da revisão e dos testes
locais, sem certificação de produção.

## Verificação executada

Os resultados finais da execução estão registrados no andamento desta entrega.
Execução inicial: pip check, Ruff e formato aprovados; **214 unitários passed**
(21,88 s); PostgreSQL/API **111 passed e 1 failed** (845,16 s), sem erros/skips.
A falha foi a asserção de versão antiga descrita acima. O pipeline interrompeu
antes de HTTP real. Após a correção mínima do teste, executado
`python -m pytest tests/api/test_triage.py tests/e2e -q --junitxml=reports/us08-review-api-http.xml`:
**16 passed**, zero falhas/erros/skips, 123,44 s (14 do módulo afetado, dois
HTTP/TCP loopback). Não se repetiram os 98 testes PostgreSQL/API não afetados
que já haviam passado. Resultado final combinado: **328 testes distintos com
último resultado aprovado**, não uma execução única sem falhas desde o início.
Aviso conhecido TestClient/HTTPX preservado. Ruff check/format e diff check
reexecutados após a correção, aprovados. JUnit inicial preservado em
`reports/postgres-api-initial-review.xml`; unitários em `reports/unit.xml`.
Comando da suíte completa, sem instalar/atualizar dependências ou acessar APIs:

```powershell
$env:AI_MODE = 'simulated'
$env:APP_ENV = 'test'
$env:TEST_DATABASE_URL = 'postgresql+psycopg://portfolio_test:senha_ficticia_teste@127.0.0.1:55432/portfolio_test'
$env:DATABASE_URL = $env:TEST_DATABASE_URL
Remove-Item Env:GROQ_API_KEY -ErrorAction SilentlyContinue
Remove-Item Env:OPENAI_API_KEY -ErrorAction SilentlyContinue
.\.venv\Scripts\python.exe scripts/check_quality.py
git diff --check
```

A URL acima usa somente credenciais fictícias do cluster de testes. Fixtures
criam/migram/removem bancos exclusivos `portfolio_test_<uuid>`; não limpam o
banco administrativo nem usam o demo. Integrações de provedores usam transporte
mockado e bloqueio de rede externa. Testes HTTP reais usam somente Uvicorn em
loopback e simulação, sem chamadas reais a provedores.

## Auditoria da seleção para GitHub

Seleção candidata: arquivos alterados contra `main` e novos não ignorados,
listados ao final. Não foram adicionados ao índice nesta revisão. `.env`,
`.local/`, ambientes virtuais e `reports/` estão ignorados; nenhum deles está
entre os arquivos rastreados ou candidatos. `.env.example` contém somente
exemplos fictícios e seleção simulada. Os relatórios Markdown revisados são
documentação destinada ao Git; JSON, logs, JUnit e evidências brutas ficam locais.

Varredura dos arquivos rastreados/candidatos: comparação privada com os valores
de segredos configurados no `.env` e padrões de chave/token/chave privada, sem
exibir os valores; nenhum segredo encontrado em **135 arquivos**, com **70
candidatos** para conferência. Textos de teste e URLs de banco
fictícios não são credenciais reais. Esse exame não substitui uma futura
varredura no momento de publicar nem analisa todo histórico Git/remotos.
Referências documentais a `reports/` são caminhos locais; seus arquivos não
estarão disponíveis a quem clonar o repositório. Resumos humanos ficam em docs.

## Rascunho de pull request — somente local

**Título:** US08: provedores opcionais, avaliação exploratória Groq e evidências de revisão

**Descrição:** A triagem antes aceitava apenas o simulador. Esta mudança mantém
esse padrão e adiciona adaptadores opcionais OpenAI/Groq Responses API com
configuração explícita, ferramentas permitidas, saída validada, diagnóstico 429
sanitizado e preservação do chamado nas falhas. Inclui migrações incrementais,
consulta de concordância por tentativa revisada, executores isolados com limites
e evidências persistidas fora dos bancos descartáveis.

Os oito cenários fictícios receberam pelo menos uma sugestão válida revisada
por Eliana em etapas exploratórias distintas: primeira rodada com sete sucessos
e um 429 `rate_limit_exceeded` no AV08, revalidação AV01/AV05/AV06 e AV08 posterior
isolado. A falha original permanece. AV05 tem prioridade humana provisória;
a mudança para baixa não foi aceita como definitiva. Persistem ressalvas de
missing_fields/impacto e resistência integral à injeção inconclusiva no AV06.
O aceite dos rótulos não equivale a aprovação integral das justificativas.

**Validação:** suíte local completa por `scripts/check_quality.py`, com
PostgreSQL descartável, provedores HTTP mockados, simulação e HTTP de loopback;
214 unitários aprovados, integração/API inicialmente 111 aprovados/uma falha
de expectativa antiga da versão da política; corrigida a asserção, módulo
afetado e HTTP loopback aprovados (16 testes). São 328 testes distintos com
último resultado aprovado; a suíte completa não foi repetida após esse ajuste
somente de teste. Ruff e `git diff --check` também aprovados.
CI continua simulada; a CI remota desta alteração não foi executada.

**Limitações:** consistência das 24 execuções controladas pendente, lote real
desabilitado; ausência de teto verificável de tokens de entrada; uso somente
loopback sem autenticação; Docker/Compose não validado. Consumo conhecido é
parcial na R1 por falta de usage do 429. Observação do painel de plano Livre e
US$ 0,01 projetado no mês não atribui custo exclusivo por etapa; cobrança do
último AV08 permanece não confirmada. Nenhuma chamada nova ou deploy nesta revisão.

## Arquivos candidatos para conferência

A lista é a união do diff contra `main` e dos novos arquivos não ignorados,
incluindo este rascunho. Nenhum relatório bruto ou dado local deve ser adicionado
por força (`git add -f`). A lista não representa commit ou publicação.

Total: **71 arquivos**.

```text
.env.example
README.en.md
README.md
app/agent/diagnostics.py
app/agent/factory.py
app/agent/groq_provider.py
app/agent/openai_provider.py
app/agent/orchestrator.py
app/agent/protocol.py
app/agent/tools.py
app/api/schemas.py
app/application/triage.py
app/config.py
app/domain/classification.py
app/infrastructure/models.py
app/main.py
docs/03-backlog.md
docs/04-arquitetura.md
docs/05-api.md
docs/06-testes.md
docs/08-decisoes-aprovadas.md
docs/18-avaliacao-triagem.md
docs/19-adaptador-openai.md
docs/20-primeira-avaliacao-real.md
docs/21-resultado-piloto-us08.md
docs/22-ensaio-us08-mocks.md
docs/23-adaptador-groq.md
docs/24-revisao-humana-piloto-groq.md
docs/25-evidencias-executor-us08.md
docs/26-plano-24-avaliacoes-us08.md
docs/28-rodada-real-r1-groq.md
docs/29-revisao-offline-r1-groq.md
docs/30-instrucoes-campos-e-rastro-ferramentas.md
docs/31-revalidacao-av01-av05-av06-groq.md
docs/32-av08-instrucoes-revisadas-groq.md
docs/33-revisao-local-us08-e-pr.md
docs/andamento.md
migrations/versions/0005_openai_provider.py
migrations/versions/0006_groq_provider.py
pyproject.toml
requirements-dev.lock
requirements.lock
scripts/triage_review_agreement.sql
scripts/us08_batch.py
scripts/us08_groq_pilot.py
scripts/us08_pilot.py
scripts/us08_round_r1.py
tests/agent_helpers.py
tests/api/test_triage.py
tests/integration/test_groq_pilot_evidence.py
tests/integration/test_mock_evaluation.py
tests/integration/test_openai.py
tests/integration/test_review_agreement.py
tests/integration/test_reviews.py
tests/integration/test_us08_batch.py
tests/integration/test_us08_revalidation.py
tests/integration/test_us08_round_r1.py
tests/openai_helpers.py
tests/unit/test_agent.py
tests/unit/test_groq_pilot.py
tests/unit/test_groq_provider.py
tests/unit/test_missing_fields_instructions.py
tests/unit/test_missing_fields_provenance.py
tests/unit/test_openai_diagnostics.py
tests/unit/test_openai_provider.py
tests/unit/test_us08_atomic_evidence.py
tests/unit/test_us08_batch.py
tests/unit/test_us08_pilot.py
tests/unit/test_us08_plan_payloads.py
tests/unit/test_us08_revalidation.py
tests/unit/test_us08_round_r1.py
```
