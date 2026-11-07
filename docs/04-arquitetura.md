# Arquitetura e dados

**Arquitetura do MVP — implementação incremental.** Fundação, cadastro e consulta nesta entrega; demais módulos permanecem planejados.

**Atualização:** ADR01/ADR02/ADR06 aceitas para US01/US02 em 07/11/2026. Fundação e cadastro/consulta implementados; ferramentas/agente/revisão permanecem futuros. [Decisões aprovadas](08-decisoes-aprovadas.md), [ambiente/versões](09-ambiente-e-versoes.md) e [andamento](andamento.md) prevalecem sobre o status inicial acima. Migração 0001 cria Ticket e TicketEvent; tabelas/referências de tentativas e revisões serão criadas nas respectivas histórias, sem antecipar funcionalidades.

## Estrutura proposta

Monólito modular FastAPI: rotas e schemas Pydantic → serviços de aplicação → domínio/repositórios → PostgreSQL com SQLAlchemy e Alembic. O serviço de triagem usa um orquestrador de agente → interface `AIProvider` → simulador ou adaptador real. Ferramentas locais consultam catálogo e política, sem rede ou escrita no banco.

Diretórios futuros: `app/api`, `app/application`, `app/domain`, `app/infrastructure`, `app/agent`, `migrations`, `tests/unit`, `tests/integration`, `tests/api`, `tests/e2e`, `tests/agent`. Não criar abstrações de microserviços, broker, RAG ou framework de agentes sem necessidade comprovada.

## Decisões propostas

- ADR01: PostgreSQL também nos testes de integração; necessário para testar transações, índices e concorrência reais. SQLite não representa essas garantias.
- ADR02: cadastro e triagem separados. Confirmar transação de cadastro antes de chamar modelo elimina dependência de IA para registrar o chamado.
- ADR03: execução de triagem síncrona limitada a 20 s, sem fila. Persistir tentativa antes, liberar transação durante chamada externa e finalizar com condição de ID/status/versão. Reinício deixa tentativa recuperável pelo prazo. Se o volume crescer, avaliar worker/fila.
- ADR04: agente com duas ferramentas e laço limitado, sem autonomia para alterar chamados. Justificativa: catálogo/política são fontes controladas, acessíveis durante raciocínio; o modelo escolhe consultas e usa respostas para formular sugestão. Consultas obrigatórias e validação externa evitam confiar apenas em prompt. Uma cadeia fixa seria mais simples, mas não demonstraria escolha de ferramentas; aqui a autonomia é pequena e testável.
- ADR05: simulador implementa o mesmo protocolo de tool calls do provedor. Não se apresenta como modelo inteligente real; serve para demonstrar orquestração e falhas reproduzíveis.
- ADR06: sem autenticação no MVP local, conforme D01. Autor de revisão é texto declarado, não evidência de identidade. Autorização será requisito antes de uso público.

Cada ADR deverá ganhar status aceito/data após revisão. A base técnica solicitada é mantida. Versões exatas, matriz Python/SDK/driver e fontes oficiais serão pesquisadas antes de US01; nenhum número de versão ou compatibilidade foi presumido como validado nesta entrega.

## Modelo de dados

| Entidade | Campos principais e restrições |
|---|---|
| Ticket | id UUID PK; title; description; status; triage_status; content_revision ≥ 1; version ≥ 1; current_attempt_id nullable; current_review_id nullable; created_at; updated_at |
| TriageAttempt | id UUID PK; ticket_id FK; attempt_number; content_revision; status (em_analise/sucesso/falha); mode; provider/model nullable; catalog_version; policy_version; started_at; deadline_at; finished_at nullable; category/priority/rationale/missing_fields nullable; error_code nullable; model_calls; tool_calls |
| HumanReview | id UUID PK; ticket_id FK; attempt_id FK; content_revision; category; priority; reason; declared_reviewer; created_at |
| TicketEvent | id UUID PK; ticket_id FK; type (criado/editado/resolvido/reaberto); content_revision; created_at |

Catálogo e política são dados locais versionados, sem CRUD no MVP. Enums/constraints no banco e schemas na borda limitam valores; FK de referência atual deve pertencer ao mesmo chamado (restrição composta ou checagem transacional com teste). Unicidade `(ticket_id, attempt_number)` e índice único parcial para tentativa ativa por ticket. Estado persistido de sucesso corresponde a triagem `sugerida` no Ticket; revisão não altera a tentativa bem-sucedida.

Edição mantém tentativas e revisões antigas, limpa referências atuais e registra evento; não guardar cópias integrais de cada texto no MVP. Essa limitação impede reconstruir textos antigos e será declarada na demonstração. Histórico não será mecanismo de auditoria legal.

Controle de concorrência usa `version` do Ticket em comparação atômica. Começar triagem incrementa version e define current_attempt_id; finalizar exige que tentativa ainda seja a ativa, em análise e dentro do prazo, então incrementa version novamente. Qualquer resultado obsoleto é descartado. Escritas de conteúdo/revisão bloqueadas durante análise. Não manter conexão/transação aberta enquanto aguarda o provedor.

## Complemento de US03 — ADR07: projeção e snapshot de classificação

Decisão técnica para cumprir RN11 antes de US04/US06: migração 0002 adiciona `Ticket.suggestion` e `Ticket.final_classification` como JSONB nullable e `TicketEvent.previous_classification` como JSONB nullable. Não há endpoint para definir esses campos; cadastro/PATCH rejeitam sua entrada. Schemas de leitura validam categorias/prioridades pelos enums centrais. Na produção atual ambos permanecem nulos; testes usam fixtures fictícias explicitamente identificadas para comprovar invalidação de classificação existente.

Uma edição efetiva, na mesma transação, obtém `SELECT FOR UPDATE`, compara expected_version, verifica estado, arquiva snapshot com revisão anterior/sugestão/classificação final, atualiza conteúdo, incrementa as duas versões e registra evento editado. O snapshot não guarda cópia integral do texto anterior. Atualiza updated_at, preservando created_at. Edição sem mudança após trim não altera timestamp, versões, estado, classificação nem eventos, mas ainda exige versão e estado válidos.

O bloqueio de linha serializa concorrentes; a segunda edição com a mesma versão lê a versão já incrementada e recebe 409. O banco não fica bloqueado enquanto há chamadas de IA, pois nenhuma chamada de IA é feita aqui. A gravação do evento e do chamado é atômica: falha em qualquer parte reverte tudo.

Esses JSONBs são projeções/snapshots, não substituem o futuro histórico de tentativas e revisões. US04/US06 deverão introduzir as entidades normalizadas previstas e suas referências, preservando os snapshots existentes via migração. A decisão evita simular uma revisão/triagem de produção nesta história e possibilita verificar RN11 agora. Downgrade de 0002 remove esses campos e perderia snapshots: ensaiado somente em bancos descartáveis, nunca no banco de homologação.

## Contrato do agente (histórias futuras)

`AIProvider` recebe mensagens, definições de ferramentas e orçamento restante; devolve pedidos de ferramenta ou resultado final estruturado. Orquestrador executa apenas allowlist, valida argumentos e conta chamadas. Ferramentas: `consultar_categorias({})` devolve slugs/descrições/versão; `consultar_politica_prioridade({})` devolve faixas, campos esperados e versão. Argumentos adicionais são inválidos.

Resultado: `{category, priority, rationale, missing_fields}` conforme RN04. Validar enumeração, tamanhos, campos extras e consultas obrigatórias fora do modelo. O backend não prova a verdade semântica da justificativa; avaliação e revisão humana tratam essa limitação.

Texto do chamado fica em mensagem de dados delimitada, nunca interpolado como instrução de sistema. Nenhuma ferramenta lê arquivos, executa código, navega na internet ou altera chamado. Logs guardam nomes/contagens de ferramentas, duração e códigos; não guardar raciocínio interno, prompt completo ou saída bruta.

Variáveis propostas em [`.env.example`](../.env.example). Modo real deve falhar claramente se configuração faltar. Custo máximo monetário não é garantido só pelo teto de tokens: antes de ativar será preciso conferir preços e suporte a limite de entrada do provedor, definir orçamento e obter autorização. Nenhuma chamada real faz parte do planejamento.
