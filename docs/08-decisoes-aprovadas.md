# Decisões aprovadas e limites desta entrega

## US08: execução exclusiva AV08 revisado — 10/11/2026

Mensagem atual autorizou somente AV08 uma vez com instruções atuais, até três
envios, 16 KiB/corpo e 2.000 tokens de saída/pedido, sem retry, parada no primeiro
erro/429. Perfil exclusivo com reserva global 6.000; confirmação de plano Livre
e validade até 16/11/2026 fornecida no mesmo dia, sem consulta adicional ao painel.
Mocks antes da chave: 27 passed. Executado: três HTTP 200, duvida/baixa, lista
vazia, 3.227 tokens informados. Revisão humana pendente, ressalva “sem impacto”;
cobrança posterior não confirmada. Autorização consumida, sem repetição; AV08
original preservado. Lote de 24 permanece desabilitado e simulador ativo.
[Evidências](32-av08-instrucoes-revisadas-groq.md).

## US08: revalidação exclusiva de três casos — 10/11/2026

Mensagem atual autorizou especificamente AV01-R1, AV05-R1 e AV06-R1 uma vez
cada após política v2: até nove tentativas, três/caso, 16 KiB/corpo, até 2.000
tokens de saída/pedido e reserva global 18.000, sequência e parada no primeiro
erro/429 sem retry. Confirmação do mesmo dia: organização Livre, chave ativa
até 16/11/2026. Mocks antes da chave: 47 passed. Executados três sucessos,
nove HTTP 200 sem retry; autorização consumida, nenhuma retomada autorizada.
Cobrança posterior não confirmada; novas revisões humanas pendentes. Dez JSON
originais preservados, demo intacto, simulador local ativo e lote de 24
desabilitado. [Resultados e divergências](31-revalidacao-av01-av05-av06-groq.md).

## US08: exceção autorizada exclusiva dos oito R1 — 10/11/2026

Eliana autorizou AV01-R1…AV08-R1 uma vez cada na Groq/openai/gpt-oss-20b,
aceitando limite de 16 KiB por corpo e medição posterior da entrada, até 24 envios,
três por caso e reserva global de 48.000 tokens de saída (até 2.000/pedido).
Confirmou plano Livre e chave ativa com expiração 16/11/2026. Mocks obrigatórios
executados antes da chave: 43 passed. Rodada executada uma única vez e interrompida
na resposta final do AV08 por HTTP 429; 24 envios, sem retry, sete sucessos, uma
falha. Autorização utilizada, não autoriza repetição/retomada ou R2/R3. Lote real
de 24 permanece desabilitado. Cobrança posterior desta rodada ainda não confirmada.
[Evidências e pendências de revisão humana](28-rodada-real-r1-groq.md).

## US08: confirmação do plano e piloto Groq executado — 09/11/2026

Eliana confirmou Projeto padrão na organização no plano Livre (US$ 0), modelo
`openai/gpt-oss-20b` permitido, e autorizou executar o piloto previamente condicionado.
Uma triagem fictícia concluída com três requisições HTTP 200, sem retry. Autorização
utilizada; nenhuma nova tentativa autorizada. Sugestão defeito/alta; revisão humana
pendente, custo posterior no painel não confirmado. Banco descartável removido,
demo preservado, simulador local ativo. Lote real de 24 pausado. [Evidência](andamento.md).

## US08: piloto Groq condicionado à ausência de cobrança — 09/11/2026

Eliana autorizou uma única triagem fictícia em banco descartável com
`openai/gpt-oss-20b`, até três requisições totais, sem retry automático/manual,
interrupção ao primeiro erro e Groq ativa somente no processo isolado. Antes de
qualquer requisição, confirmar ausência de cobrança na conta/projeto da chave;
sem confirmação ou com custo previsto, parar. Nesta conferência não há acesso
ao painel privado: piloto não iniciado, zero requisições e autorização ainda não
utilizada. Chave/demo preservados, simulador ativo, lote de 24 pausado. Evidência
e informação faltante em [andamento](andamento.md).

## US08: candidato ao piloto Groq — 09/11/2026

Eliana escolheu `openai/gpt-oss-20b` como candidato, com revisão dos payloads apenas
em mocks. Isso não autoriza uso da chave nem chamada real. Simulador segue ativo;
piloto e lote real pausados. Modelo continua configurável, sem default no código.

## US08: Groq opcional somente offline — 09/11/2026

Eliana autorizou a menor extensão do adaptador para Groq, com testes HTTP mockados,
credencial fictícia e banco isolado. Simulador segue padrão; a existência de chave
local não autoriza seu uso. Piloto e lote real continuam pausados, sem commit/push.
Implementação, compatibilidade e pendências em [23-adaptador-groq.md](23-adaptador-groq.md).

## US08: segunda tentativa isolada autorizada e executada — 09/11/2026

Após conferir a exportação sem consumo visível, Eliana autorizou expressamente uma única nova tentativa do piloto com gpt-6-luna, chamado fictício em banco isolado, até três requisições no total, TLS com certificado/hostname verificados e orçamento de referência USD 0,01. Interromper ao primeiro erro sem retry; manter AI_MODE=simulated no `.env` ao encerrar. Essa autorização cobre somente a segunda tentativa, já executada e interrompida após uma requisição/HTTP 429, sem usage. Custo desconhecido. Não autoriza terceira tentativa nem lote de 24. Evidência em andamento e documento 21; chave e bancos preservados localmente, sem publicação/deploy.

## US08: um único piloto real autorizado — 09/11/2026

Eliana confirmou expressamente autorização para **um chamado fictício, uma tentativa de triagem, até três requisições no gpt-6-luna, com orçamento de referência de USD 0,01**. Não é teto garantido de cobrança, por ausência de limite de tokens de entrada verificado. Não autoriza retries, as 24 execuções, push ou deploy. Chave somente local, fora da conversa/Git; simulador continua padrão. Após piloto, conferir ferramentas, validação e consumo, solicitar/registrar decisão humana sem atribuir ao assistente identidade de pessoa revisora, e recalcular projeção antes de qualquer lote. Esta autorização substitui a proibição anterior de chamadas reais exclusivamente para esse piloto. Estado e bloqueios em andamento.

## US08: adaptador OpenAI autorizado para testes locais — 09/11/2026

Eliana escolheu OpenAI como primeiro provedor e autorizou adaptador Responses API, configuração explícita, migração preservando dados e testes com transporte falso/rede externa bloqueada. Esta autorização substitui a restrição anterior de implementar somente o simulador, mantendo `simulated` como padrão e CI simulada. Não autoriza chamadas reais, custos, push ou deploy. Modelo definitivo, estimativa de custo e autorização para as 24 execuções reais permanecem pendentes. Consulta de concordância, seus testes, histórico documental e banco demo devem ser preservados. [Implementação e ativação futura](19-adaptador-openai.md).

## Publicação autorizada e executada — 08/11/2026

Eliana autorizou publicar código em repositório público elisilva75/triagem-chamados-agente-ia, main, licença MIT 2026 Eliana Gomes da Silva, com noreply exato fornecido por ela e reescrita somente dos e-mails do histórico de publicação. Preservar nomes/mensagens/ordem/conteúdo; backups e outras branches ficam locais; sem force push. Publicação e CI realizadas conforme [andamento](andamento.md). US08 adiada, AI_MODE=simulated, aplicação apenas loopback/sem autenticação; publicar o código não autoriza deploy da aplicação nem chamadas pagas. Compose permanece não validado até execução própria.

## Autorização US01/US07/US09 — 08/11/2026

Eliana autorizou avançar nas pendências de ambiente/qualidade/portfólio do MVP simulado: verificar Docker, executar Compose isolado somente se disponível, concluir revisão do workflow e guias, ensaiar ambiente isolado e preparar publicação para revisão futura. Preservar demo e alterações existentes; sem publicar no GitHub, deploy ou chamadas pagas. Decisões técnicas rotineiras e validação automatizada estão autorizadas; não exigir repetição manual de cenários cobertos. Resultado desta autorização em [andamento](andamento.md); Docker ausente não foi convertido em aceite de Compose, nem revisão de workflow em CI remoto aprovado.

Em **07/11/2026**, Eliana aprovou o escopo geral do MVP com as definições abaixo. Não há conflito com D01–D08; D08 foi explicitamente adiada, sem implementação de integração real.

| Decisão | Status e definição aprovada |
|---|---|
| D01 | Aprovada: uso local, sem autenticação; não disponibilizar publicamente |
| D02 | Aprovada: acesso, defeito, infraestrutura, duvida e outros, em fonte central com validação |
| D03 | Aprovada: baixa, media, alta e critica; decisão final humana |
| D04 | Aprovada: solicitar triagem separadamente; retry manual após falha |
| D05 | Aprovada: edição efetiva de título/descrição invalida classificação, preserva histórico e exige nova triagem |
| D06 | Aprovada: revisão humana obrigatória antes de resolver |
| D07 | Aprovada: resolução e reabertura por transições explícitas, com histórico |
| D08 | Adiada: somente simulação; provedor real e orçamento serão decididos depois; nenhuma chamada paga |

Categorias, prioridades e estados ficam centralizados em `app/domain/catalog.py`. Valores fora dos enums são rejeitados; nenhuma categoria/prioridade é aceita no cadastro, pois pertencem à triagem/revisão futuras. Alterações de catálogo que afetem persistência exigirão migração e revisão dos testes.

Esta entrega autoriza US01 e US02 e a base de CI pertinente a elas. US03–US06, o simulador de triagem de US04 e US08 não são implementados agora. A configuração já aceita exclusivamente AI_MODE=simulated. Isso não significa que a triagem já existe: cadastro não instancia nem chama provedor algum.

ADR01, ADR02 e ADR06 aceitas para a fundação. ADR03–ADR05 continuam como desenho para histórias futuras. Não há autenticação/identidade verificável nem adequação a acesso público. Não executar publicação, deploy ou chamadas de IA real.

Aguardar validação desta entrega por Eliana antes de US03. US01/US02 só podem ser consideradas concluídas quando seus critérios tiverem evidência; limitações de ambiente não viram testes aprovados.

Atualização: Eliana relatou homologação manual de cadastro, consulta, listagem/paginação, title ausente e UUID inexistente, registrada em [homologação US01/US02](11-homologacao-us01-us02.md), e autorizou US03. A ausência de persistência no POST rejeitado foi verificada adicionalmente pelo agente com contagem SQL antes/depois. US01 continua parcialmente validada; autorização de US03 não elimina a pendência de Compose. US04 e integração real continuam futuras.


## Autorização de continuidade — 08/11/2026

Eliana aceitou os resultados manuais E01–E04 de US03 e autorizou explicitamente iniciar **US04 conforme o backlog aprovado, exclusivamente em modo simulado**. Não repetir os cenários aceitos. US03 permanece com as pendências específicas de homologação de classificação/snapshots e estados dependentes dos fluxos de US04/US06. A autorização permite implementar/testar US04 e preparar homologação curta, incluindo invalidação de sugestão após edição. Não autoriza iniciar US05/US06, chamadas pagas, publicação ou deploy. Docker Compose e CI remota continuam pendentes; US01 parcialmente validada. Esta autorização atualiza o limite das entregas anteriores, sem converter pendências em aceite.


## Continuidade automatizada para US05 — 08/11/2026

Eliana autorizou executar M02/no-op por automação isolada e, atendidos os critérios independentes, implementar/testar US05 conforme backlog. M02 não exige sua execução no Swagger; não converter testes em homologação manual nem solicitar repetição de cobertura existente. Demonstrações curtas são opcionais; decisões de produto continuam com Eliana. Critérios independentes verificados por testes reaproveitados (3 passed), permitindo US05. US06 continua dependência futura para classificação final/resolução; Docker Compose e CI remota pendentes. Sem chamadas pagas, publicação ou deploy. Esta instrução substitui a exigência anterior de aguardar homologação manual de US04 para avançar.


## Autorização de US06 e validação integrada — 08/11/2026

Eliana autorizou implementar US06 conforme backlog/regras, incluindo revisão humana, classificação final, resolução/reabertura e as dependências pendentes de US03: no-op/edição/invalidação com classificação final, preservação de histórico e bloqueios nos estados pertinentes. Usar automação isolada, reaproveitar testes e preservar demo; demonstração manual opcional, sem repetição obrigatória. Atualizar critérios/dependências/DoD com evidências reais. Docker Compose e CI permanecem pendentes até execução; nenhuma autorização para chamada paga, publicação ou deploy. US07/US09 continuam próximas histórias, US08 adiada.
