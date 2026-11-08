# Arquitetura e dados

**Arquitetura do MVP — implementação incremental até US06.** Fundação, cadastro, consulta, edição, agente simulado, recuperação/retry, revisão humana e resolução/reabertura implementados. Os complementos por história ao final atualizam o desenho inicial abaixo.

**Estado atual:** migrações 0001–0004 criam chamados, eventos/snapshots, tentativas e revisões humanas. ADR01–ADR10 foram implementadas incrementalmente; os complementos abaixo preservam a motivação de cada etapa. [Decisões aprovadas](08-decisoes-aprovadas.md), [ambiente/versões](09-ambiente-e-versoes.md) e [andamento](andamento.md) registram aceite e evidências. Somente provedor simulado existe; US08 está adiada.

## Estrutura implementada

Monólito modular FastAPI: rotas e schemas Pydantic → serviços de aplicação → domínio/repositórios → PostgreSQL com SQLAlchemy e Alembic. O serviço de triagem usa orquestrador → interface AIProvider → simulador. Ferramentas locais consultam catálogo e política, sem rede ou escrita no banco. Adaptador real é evolução de US08, ausente nesta versão.

Diretórios existentes: app/api, app/application, app/domain, app/infrastructure, app/agent, migrations e testes separados em unit/integration/api/e2e. Casos do agente ficam em tests/unit, sem diretório tests/agent. Sem microserviços, broker, RAG ou framework externo de agentes.

## Decisões arquiteturais

- ADR01: PostgreSQL também nos testes de integração; necessário para testar transações, índices e concorrência reais. SQLite não representa essas garantias.
- ADR02: cadastro e triagem separados. Confirmar transação de cadastro antes de chamar modelo elimina dependência de IA para registrar o chamado.
- ADR03: execução de triagem síncrona limitada a 20 s, sem fila. Persistir tentativa antes, liberar transação durante chamada externa e finalizar com condição de ID/status/versão. Reinício deixa tentativa recuperável pelo prazo. Se o volume crescer, avaliar worker/fila.
- ADR04: agente com duas ferramentas e laço limitado, sem autonomia para alterar chamados. Justificativa: catálogo/política são fontes controladas, acessíveis durante raciocínio; o modelo escolhe consultas e usa respostas para formular sugestão. Consultas obrigatórias e validação externa evitam confiar apenas em prompt. Uma cadeia fixa seria mais simples, mas não demonstraria escolha de ferramentas; aqui a autonomia é pequena e testável.
- ADR05: simulador implementa o mesmo protocolo de tool calls do provedor. Não se apresenta como modelo inteligente real; serve para demonstrar orquestração e falhas reproduzíveis.
- ADR06: sem autenticação no MVP local, conforme D01. Autor de revisão é texto declarado, não evidência de identidade. Autorização será requisito antes de uso público.

As decisões de produto e autorizações constam no documento 08; versões exatas, compatibilidade e fontes oficiais constam no documento 09. Não há SDK externo de IA. A validação nativa não comprova Docker/Linux nem CI remoto.

## Modelo de dados

| Entidade | Campos principais e restrições |
|---|---|
| Ticket | id UUID PK; title; description; status; triage_status; content_revision ≥ 1; version ≥ 1; suggestion/final_classification JSONB nullable; created_at; updated_at |
| TriageAttempt | id UUID PK; ticket_id FK; attempt_number; content_revision; status (em_analise/sucesso/falha); mode; provider/model nullable; catalog_version; policy_version; started_at; deadline_at; finished_at nullable; category/priority/rationale/missing_fields nullable; error_code nullable; model_calls; tool_calls |
| HumanReview | id UUID PK; ticket_id FK; attempt_id FK; content_revision; category; priority; reason; declared_reviewer; created_at |
| TicketEvent | id UUID PK; ticket_id FK; type (criado/editado/resolvido/reaberto); content_revision; previous_classification JSONB nullable; created_at |

Catálogo e política são dados locais versionados, sem CRUD no MVP. Enums/constraints no banco e schemas na borda limitam valores; FK de referência atual deve pertencer ao mesmo chamado (restrição composta ou checagem transacional com teste). Unicidade `(ticket_id, attempt_number)` e índice único parcial para tentativa ativa por ticket. Estado persistido de sucesso corresponde a triagem `sugerida` no Ticket; revisão não altera a tentativa bem-sucedida.

Edição mantém tentativas e revisões antigas, limpa referências atuais e registra evento; não guardar cópias integrais de cada texto no MVP. Essa limitação impede reconstruir textos antigos e será declarada na demonstração. Histórico não será mecanismo de auditoria legal.

Controle de concorrência compara version sob lock do Ticket. Começar triagem incrementa version e insere tentativa ativa (índice parcial único); finalizar exige mesma tentativa ativa, revisão, versão e prazo, então incrementa version novamente. Não existe coluna current_attempt_id no Ticket: a identidade é capturada pelo serviço e validada na finalização. Resultado obsoleto é descartado. Conteúdo/revisão ficam bloqueados durante análise. Nenhuma conexão/transação permanece aberta enquanto aguarda o provedor.

## Complemento histórico de US03 — ADR07: projeção e snapshot de classificação

Este trecho registra a etapa anterior a US04/US06. Na versão atual, sugestão e classificação final são produzidas pelas rotas implementadas; ADR08–ADR10 abaixo descrevem o desenho final.

Decisão técnica para cumprir RN11 antes de US04/US06: migração 0002 adiciona `Ticket.suggestion` e `Ticket.final_classification` como JSONB nullable e `TicketEvent.previous_classification` como JSONB nullable. Não há endpoint para definir esses campos; cadastro/PATCH rejeitam sua entrada. Schemas de leitura validam categorias/prioridades pelos enums centrais. Na produção atual ambos permanecem nulos; testes usam fixtures fictícias explicitamente identificadas para comprovar invalidação de classificação existente.

Uma edição efetiva, na mesma transação, obtém `SELECT FOR UPDATE`, compara expected_version, verifica estado, arquiva snapshot com revisão anterior/sugestão/classificação final, atualiza conteúdo, incrementa as duas versões e registra evento editado. O snapshot não guarda cópia integral do texto anterior. Atualiza updated_at, preservando created_at. Edição sem mudança após trim não altera timestamp, versões, estado, classificação nem eventos, mas ainda exige versão e estado válidos.

O bloqueio de linha serializa concorrentes; a segunda edição com a mesma versão lê a versão já incrementada e recebe 409. O banco não fica bloqueado enquanto há chamadas de IA, pois nenhuma chamada de IA é feita aqui. A gravação do evento e do chamado é atômica: falha em qualquer parte reverte tudo.

Esses JSONBs são projeções/snapshots, não substituem o futuro histórico de tentativas e revisões. US04/US06 deverão introduzir as entidades normalizadas previstas e suas referências, preservando os snapshots existentes via migração. A decisão evita simular uma revisão/triagem de produção nesta história e possibilita verificar RN11 agora. Downgrade de 0002 remove esses campos e perderia snapshots: ensaiado somente em bancos descartáveis, nunca no banco de homologação.

## Contrato do agente (implementado em US04, complemento ADR08 abaixo)

`AIProvider` recebe mensagens, definições de ferramentas e orçamento restante; devolve pedidos de ferramenta ou resultado final estruturado. Orquestrador executa apenas allowlist, valida argumentos e conta chamadas. Ferramentas: `consultar_categorias({})` devolve slugs/descrições/versão; `consultar_politica_prioridade({})` devolve faixas, campos esperados e versão. Argumentos adicionais são inválidos.

Resultado: `{category, priority, rationale, missing_fields}` conforme RN04. Validar enumeração, tamanhos, campos extras e consultas obrigatórias fora do modelo. O backend não prova a verdade semântica da justificativa; avaliação e revisão humana tratam essa limitação.

Texto do chamado fica em mensagem de dados delimitada, nunca interpolado como instrução de sistema. Nenhuma ferramenta lê arquivos, executa código, navega na internet ou altera chamado. Logs guardam nomes/contagens de ferramentas, duração e códigos; não guardar raciocínio interno, prompt completo ou saída bruta.

Variáveis propostas em [`.env.example`](../.env.example). Modo real deve falhar claramente se configuração faltar. Custo máximo monetário não é garantido só pelo teto de tokens: antes de ativar será preciso conferir preços e suporte a limite de entrada do provedor, definir orçamento e obter autorização. Nenhuma chamada real faz parte do planejamento.


## US04 — ADR08: agente simulado e tentativas persistidas (08/11/2026)

ADR04/ADR05 aceitas para US04: `app/agent/protocol.py` define AIProvider/ModelReply/ToolCall; `simulated.py` implementa roteiros reproduzíveis sem SDK/rede/credenciais. `tools.py` contém somente catálogo e política locais versionados, com argumentos vazios. Orquestrador valida allowlist, argumentos, saída Pydantic, consultas obrigatórias, 3 chamadas de modelo, 4 de ferramenta, orçamento de 20 s e teto informado de 2.000 tokens por resposta. Histórico de mensagens separa instrução de sistema de JSON com ticket_data não confiável. Só DTO validado chega à persistência; logs guardam nomes de ferramentas permitidas, IDs, contagens, duração e códigos, sem texto ou saída bruta.

Simulador usa correspondências fixas de palavras para escolher fixtures; não é inferência de IA nem evidência de qualidade de modelo real. O título exato `[SIMULADO:saida-invalida]` seleciona fixture inválida para demonstrar a barreira de validação, sem acrescentar campos de controle ao contrato. Contagem de tokens é metadado roteirizado do simulador, não medição por tokenizer real. Prazos são verificados antes/depois de cada chamada e ferramenta e na finalização; o único provedor disponível é imediato e sem I/O. A interface exige que futuros adaptadores respeitem remaining_seconds/max_output_tokens; preempção de código Python arbitrariamente bloqueante não é oferecida por este laço síncrono. Integração externa permanece adiada.

Migração 0003 **adiciona somente triage_attempts**, preservando tickets/eventos/snapshots. Tentativas têm FK ticket_id, número sequencial único por chamado e índice parcial único para status em_analise; constraints de modo, estado, contagens e coerência de resultado. Em vez de introduzir agora uma referência circular current_attempt_id, a tentativa ativa é identificada pela FK ticket_id + status em_analise único. Sugestão contém attempt_id produzido pelo próprio serviço; cliente não pode definir essa referência. Finalização compara ID da tentativa, status, versão capturada e revisão do chamado sob lock. Essa escolha evita FK circular e mantém pertencimento ao chamado por construção e pelos testes transacionais; atualizações das referências de revisão permanecem em US06.

Serviço abre transação, bloqueia chamado, valida versão/estado, confirma tentativa e em_analise/version+1. Fecha sessão antes do agente. Em nova transação, publica resultado validado ou falha sanitizada e incrementa version outra vez; content_revision não muda. Tentativas concluídas não são alteradas pelas rotas; edição limpa a projeção atual, preservando tentativa e snapshot do evento. GET de tentativas é paginado por started_at/id. Cadastro, consulta e edição continuam sem chamar provedor.

ADR03 implementada nesta entrega apenas na base necessária a US04: aquisição/finalização transacionais, prazo e descarte de resultado obsoleto. **Retry em falha, recuperação de execução expirada e ensaios completos de interrupção/falha na finalização são US05**. Nesta etapa POST triage aceita somente aberto/pendente; falha tem conteúdo preservado e edição efetiva pode retornar a pendente. Não prometer retry sem edição. Falha de armazenamento na finalização responde 503 e pode deixar em_analise; não prometer recuperação automática ainda. Estados de revisão/resolução continuam em US06.

Nenhuma dependência adicionada ou reconfigurada: mantidos os locks e versões/fontes oficiais de [ambiente](09-ambiente-e-versoes.md). Execução exclusivamente AI_MODE=simulated.


## US05 — ADR09: recuperação atômica e retry explícito (08/11/2026)

ADR03 implementada na parte de recuperação prevista: POST triage aceita aberto/pendente ou aberto/falha, com expected_version atual. Não existe retry automático. Chamado em_analise exige localizar sua tentativa ativa (índice parcial único). Antes de deadline_at, retorna 409/triage_in_progress sem escrita nem provedor. No instante do prazo ou depois, encerra a tentativa ativa com falha/execucao_expirada, incrementa version para a transição a falha, libera o índice com flush e adquire a tentativa seguinte na **mesma transação sob lock do chamado**. Se a inserção seguinte falhar, a recuperação inteira reverte, inclusive a tentativa anterior. Versão divergente é rejeitada antes de qualquer recuperação.

Cada aquisição e finalização incrementa version; content_revision não muda. Retry de falha normalmente soma duas versões (ex.: 3→5). Recuperação de uma execução interrompida soma três mudanças lógicas (em_analise→falha→em_analise→sugerida/falha; ex.: 2→5). Clientes usam o valor retornado por GET, sem presumir incrementos. Número de tentativa é sequencial por chamado, calculado sob lock, sem duplicar ticket ou eventos de conteúdo.

Finalização continua condicional à tentativa capturada ainda em_analise, mesma revisão e versão adquirida. Uma resposta tardia da tentativa encerrada não modifica a nova tentativa, a sugestão ou timestamps; recebe 409/version_conflict. No limite de 20 segundos, resultado ainda não finalizado é rejeitado com ai_timeout, sem sugestão. Relógio UTC é injetável apenas na função de serviço para testes determinísticos; não há parâmetro HTTP ou variável de produção que altere o prazo.

Falha real no banco ao finalizar retorna 503/storage_unavailable sem contexto que prometa persistência de falha: rollback mantém tentativa em_analise, permitindo recuperação apenas no próximo POST com versão atual e prazo vencido. O processo não mantém conexão durante o provedor. Testes usam violação real de CHECK em banco descartável, duas requisições HTTP concorrentes, resposta tardia e interrupção real de um servidor seguida de reinício e espera real do lease de 20 s. A factory de interrupção existe apenas em tests/interrupted_server.py, nunca na aplicação de produção.

Sem nova migração/dependência: reutiliza triage_attempts de 0003 e seus índices/constraints. A execução permanece exclusivamente simulada; limites de preempção de Python e metadados de tokens explicados em ADR08 continuam válidos para este simulador sem I/O. US06 não implementada. Compose e CI remota permanecem pendentes.


## US06 — ADR10: revisão normalizada e projeção final validada (08/11/2026)

Migração 0004 adiciona human_reviews e unicidade (id,ticket_id,content_revision) em triage_attempts, permitindo FK composta da review para a tentativa do **mesmo chamado e revisão de conteúdo**. HumanReview tem ID, ticket_id, attempt_id, content_revision, category, priority, reason, declared_reviewer e created_at. Checks no PostgreSQL reforçam catálogo, prioridade, motivo 10–500, autor 2–80 e revisão positiva. Nenhum backfill de revisões fictícias; tickets/eventos/tentativas/snapshots existentes são preservados.

A referência atual permanece na projeção Ticket.final_classification (review_id/category/priority), consistente com ADR07, evitando uma FK circular nova em Ticket. Somente o serviço gera essa projeção após inserir a HumanReview; resolve/reopen e correção em revisada verificam sob lock que o ID pertence ao próprio ticket/content_revision e que categoria/prioridade coincidem com a review. Testes exercitam FK composta e rejeição de uma projeção interna corrompida apontando para outro chamado. Sugestão é validada e deve coincidir com a tentativa bem-sucedida da revisão atual antes de permitir nova review.

Revisão é append-only pelas rotas: não há update/delete; uma correção insere outro registro e atualiza a projeção na mesma transação. Histórico imutável no fluxo da aplicação, sem promessa de auditoria legal ou de impedir alterações por administrador do banco. Autor é declarado, não autenticado. Revisão não altera a sugestão/tentativa, não muda content_revision e não chama provedor.

Revisão, resolução e reabertura usam SELECT FOR UPDATE para serializar comparação de version, verificação de estado, gravação e incremento. Resolve/reopen gravam TicketEvent na mesma transação, com revisão do conteúdo mantida; erro de review/projeção/evento reverte toda a operação. Correções em revisada são novas decisões explícitas; repetições de resolve/reopen retornam 409. Edição/no-op continuam conforme US03, agora verificados com classificação produzida pelas rotas reais de US06.

Sem dependências novas/reconfiguradas; mesmos locks/fontes oficiais anteriores. Migração aditiva aplicada ao demo apenas após testes, com comparação integral de dados; downgrade ensaiado só em bancos descartáveis. Não há autenticação, IA real, publicação ou deploy. Infraestrutura Compose/CI continua pendente.
