# Backlog e refinamento

**Backlog do MVP aprovado em 07/11/2026.** P0 = essencial ao fluxo; P1 = necessário para entrega do portfólio. Ordem e dependências em [entregas](07-entregas.md). IDs dos critérios e tasks são locais à história: por exemplo, US02-CA1 e US02-T1.

| História | Estado nesta entrega | Pendência |
|---|---|---|
| US01 | Implementada, validação parcial; não concluída | Docker ausente: CA1/Compose não executado; CA2 e CA3 com evidências locais |
| US02 | Implementada; CA1–CA4 automatizados; cenários manuais informados por Eliana registrados | Dependência US01/Compose pendente; não persistência do POST rejeitado confirmada pelo agente |
| US03 | CA1–CA3 e tasks verificados localmente; dependência funcional de US06 coberta por rotas reais e testes | Sem lacuna funcional/manual obrigatória de classificação; pendência de ambiente de US01 continua separada |
| US04 | Critérios independentes verificados; M01 manual informado e M02/no-op por automação isolada | Sem gate manual obrigatório; CI remota aprovada; Compose pendente separadamente |
| US05 | CA1–CA4 e tasks verificados localmente por automação; regressão ampliada em US06 | Sem demonstração manual obrigatória; CI remota aprovada; Compose pendente |
| US06 | CA1–CA4/T1–T3 e DoD funcional atendidos; regressão ampliada de 177 testes local e remotamente | Sem gate manual; DoD global do MVP ainda depende de US01/Compose |
| US07 | CA1–CA3/T1–T3 atendidos; pipeline local e CI remota aprovados com 177 testes, isolamento e gates verificados | DoD de qualidade atendida; Compose continua pertencendo a US01 |
| US08 | Adiada | Somente provedor simulado autorizado; integração real e orçamento pendentes |
| US09 | CA1–CA3/T1–T3 atendidos no escopo nativo isolado; README PT/EN, roteiro, portfólio e publicação pública autorizada executados | Clone publicado e CI Ubuntu verificados; guia Compose explicitamente não validado |

Rastreabilidade dos arquivos, critérios e resultados em [andamento](andamento.md). Nenhuma pendência foi convertida em aceite aprovado.

| Épico | Histórias | Resultado |
|---|---|---|
| E01 Fundação | US01 | Ambiente e persistência confiáveis |
| E02 Chamados | US02, US03 | Registro, consulta e edição |
| E03 Agente | US04, US05, US08 | Sugestão validada e integração isolada |
| E04 Decisão humana | US06 | Revisão e ciclo operacional |
| E05 Qualidade e portfólio | US07, US09 | Automação, documentação e demonstração |

## US01 — Preparar ambiente e banco (P0, E01)

Como desenvolvedora, quero iniciar API e PostgreSQL localmente para executar o projeto de modo reproduzível. Regras: RNF05, RNF06, RNF08.

- CA1 positivo: ambiente limpo inicia por Compose, migração cria esquema e `/health` retorna 200 com banco acessível.
- CA2 negativo: banco inacessível faz `/health` responder 503 sem URL/credencial; processo não aplica migração silenciosamente por requisição.
- CA3 limite: aplicar migração duas vezes não altera esquema na segunda; upgrade → downgrade em banco descartável → upgrade funciona.
- T1 desenvolvimento: verificar versões oficiais e compatibilidade; fixar dependências e lock; criar estrutura, configuração, Compose, health e migração inicial.
- T2 testes: integração PostgreSQL, migrações e indisponibilidade de health; validar bind local.
- T3 documentação: registrar versões/fontes, requisitos Windows, variáveis e comandos realmente verificados.

## US02 — Registrar e consultar chamados (P0, E02)

Como solicitante, quero registrar um chamado e recuperá-lo mesmo sem IA. Regras: RN01–RN03, RN13.

- CA1 positivo: POST válido retorna 201, Location e UUID; GET mantém texto e aberto/pendente, sem chamar provedor.
- CA2 negativo: título em branco, número no texto ou campo extra retornam 422 sem inserir; UUID existente ausente retorna 404.
- CA3 limite: título 5/120 e descrição 20/5000 após trim aceitos; 4/121 e 19/5001 rejeitados.
- CA4 positivo/limite: lista ordenada de forma estável, limit 1–100 (padrão 20), offset ≥ 0; vazia retorna 200/items=[]; limit 0/101 e offset -1 retornam 422.
- T1 desenvolvimento: schemas, entidade, repositório, transação de cadastro, GET individual e paginação.
- T2 testes: limites parametrizados, rollback, persistência, contrato HTTP e provedor que falha caso seja chamado no cadastro.
- T3 documentação: exemplos fictícios de cadastro/consulta e rastreio dos critérios.

## US03 — Editar com controle de concorrência (P0, E02)

Autorizada explicitamente por Eliana após relato de homologação de US02. Verificações e rastreabilidade em [andamento](andamento.md); [roteiro de homologação](12-homologacao-us03.md). A fundação nativa foi verificada; a pendência Compose de US01 não foi convertida em aceite aprovado.

Como solicitante, quero corrigir o conteúdo sem reutilizar classificação antiga. Regras: RN01, RN11, RN16.

- CA1 positivo: alterar descrição de aberto com versão atual incrementa content_revision/version, limpa dados atuais e mantém histórico.
- CA2 negativo: edição de resolvido, em análise ou com versão antiga retorna 409 sem alteração; PATCH sem título/descrição retorna 422.
- CA3 limite: texto idêntico após trim retorna 200, sem incrementar versão nem invalidar; limites de RN01 também valem no PATCH.
- T1 desenvolvimento: PATCH parcial, atualização atômica por versão e invalidação de referências atuais.
- T2 testes: concorrência de duas edições com mesma versão, preservação de histórico e limites de conteúdo.
- T3 documentação: exemplo de conflito e instrução para consultar versão atual antes de repetir.

## US04 — Executar agente com ferramentas no modo simulado (P0, E03)

Como analista, quero sugestão explicável e campos ausentes para revisar a classificação. Regras: RN03–RN05, RN09, RN10, RN14.

- CA1 positivo: fixture de defeito consulta ambas as ferramentas; resultado válido gera sugerida e nenhuma classificação final; resposta identifica modo simulated.
- CA2 negativo: categoria externa, prioridade desconhecida, propriedade extra, justificativa curta, ferramenta desconhecida ou ausência de consulta obrigatória gera falha sem publicar sugestão.
- CA3 limite: até 3 chamadas de modelo/4 de ferramenta; necessidade de uma chamada adicional encerra por limite; listas de 0 e 4 ausentes aceitas, 5 ou duplicatas rejeitadas.
- CA4 positivo: caso sem impacto informa impacto ausente; prompt injection no texto não muda permissões nem catálogo.
- T1 desenvolvimento: interface de provedor, simulador com roteiros fixos de tool calls, orquestrador limitado, duas ferramentas somente leitura e validação estrita.
- T2 testes: ferramenta/argumentos, estrutura, limites de tokens/tempo, casos fictícios e tentativas de injeção.
- T3 documentação: explicar agente versus chamada única, ferramentas, regras e identificação visível da simulação.

## US05 — Recuperar falhas e repetir triagem (P0, E03)

Como analista, quero repetir análise falha sem duplicar o chamado. Regras: RN07–RN09, RN13, RN15, RN16.

- CA1 positivo: timeout preserva conteúdo, cria tentativa falha com código timeout; novo POST com versão atual pode criar tentativa seguinte e obter sugerida.
- CA2 negativo: dois POSTs simultâneos para mesma versão executam no máximo um agente; outro recebe 409. Saída inválida nunca vira sugestão utilizável.
- CA3 limite: prazo vencido após interrupção do processo pode ser recuperado no próximo POST; prazo ainda válido bloqueia retry; resultado antigo não sobrescreve tentativa nova.
- CA4 negativo: banco falha ao finalizar tentativa: resposta 503, sem alegar sucesso; após recuperação, tentativa expirada pode ser encerrada e repetida.
- T1 desenvolvimento: tentativa persistida antes da chamada, prazo, finalização condicional e recuperação atômica; mapear erros seguros.
- T2 testes: indisponibilidade, timeout, reinício, duas conexões PostgreSQL concorrentes, falha na finalização e resultado tardio.
- T3 documentação: tabela de códigos e roteiro de recuperação manual, sem retry automático.

## US06 — Revisar e concluir chamado (P0, E04)

Como pessoa revisora, quero confirmar/corrigir classificação e resolver o chamado. Regras: RN03, RN06, RN12, RN13, RN16.

- CA1 positivo: revisão de sugerida grava decisão final, autor declarado e motivo; resolver muda aberto para resolvido; reabrir mantém classificação e volta a aberto.
- CA2 negativo: resolver pendente/falha retorna 409; revisar com categoria inválida retorna 422; resolved não admite revisão até reabrir.
- CA3 limite: motivo de 10/500 caracteres aceito, 9/501 rejeitado; revisão subsequente em revisada mantém registro anterior e atualiza referência final.
- CA4 negativo: versão desatualizada ou transição repetida retorna 409, sem criar histórico duplicado.
- T1 desenvolvimento: revisão imutável, classificação final e comandos de resolver/reabrir com controle de versão.
- T2 testes: matriz de transições permitidas/proibidas, revisão corrigida, limites e concorrência.
- T3 documentação: exemplos de concordância/discordância e limitação da identidade declarada.

## US07 — Automatizar qualidade e fluxo HTTP real (P1, E05)

Como mantenedora, quero feedback reproduzível sem custo de IA. Regras: RNF01–RNF08.

- CA1 positivo: CI executa validação estática, unitários, integração PostgreSQL, contrato dentro do processo e fluxo HTTP contra servidor real, com modo simulado e relatório por camada.
- CA2 negativo: falha obrigatória bloqueia pipeline; CI não carrega chave nem aciona adaptador real; dados do teste nunca usam banco de desenvolvimento.
- CA3 limite: dois jobs/execuções de testes usam bancos isolados; migrações executam a partir de banco vazio; health tem espera limitada para iniciar fluxo real.
- T1 desenvolvimento: workflow Actions, separação de marcadores/suítes, inicialização e encerramento do servidor e relatório de cobertura dos caminhos críticos.
- T2 testes: executar os comandos locais equivalentes; validar isolamento e caminho de falha do pipeline. Execução remota somente quando houver publicação autorizada.
- T3 documentação: diferenças entre ASGI in-process e HTTP real; evidências locais e remotas separadas.

## US08 — Preparar adaptador de IA real (P1, E03)

Como desenvolvedora, quero trocar o simulador por provedor configurável sem mudar o domínio. Regras: RN04, RN09, RN10, RN14 e D08.

- CA1 positivo: configuração seleciona adaptador; testes com transporte falso comprovam tradução de ferramentas, saída e erros mantendo o mesmo contrato.
- CA2 negativo: modo real sem chave/modelo falha na configuração, sem fallback silencioso; credenciais não aparecem em resposta/log; CI continua simulated.
- CA3 limite: timeouts/tokens respeitam teto local; modelo sem suporte ao contrato de ferramentas é rejeitado antes de habilitar integração.
- T1 desenvolvimento: escolher provedor/modelo após discussão de custos, verificar SDK oficial, implementar adaptador e configuração segura.
- T2 testes: contrato com transporte simulado; avaliação paga separada somente após autorização; se não autorizada, registrar que integração remota não foi validada.
- T3 documentação: credencial própria, cobrança, limites e instrução de opt-in; não vincular acesso ao Codex a créditos da aplicação.

A história pode validar o adaptador localmente sem realizar chamada paga. A aceitação deve declarar explicitamente o que foi testado por transporte falso e o que ficou sem avaliação remota.

## US09 — Preparar portfólio para publicação (P1, E05)

Como Eliana, quero demonstrar e explicar o projeto em entrevistas. Regras: documentação coerente e autorização antes de publicação.

- CA1 positivo: README PT/EN, guia Windows, dados fictícios, decisões arquiteturais, limitações e roteiro cobrem cadastro → falha → retry → revisão → resolução.
- CA2 negativo: nenhum segredo ou dado de empregador nos arquivos preparados; comandos não comprovados são identificados; nenhuma publicação sem autorização.
- CA3 limite: checkout limpo executa apenas com requisitos documentados e sem credencial de IA; ambiente Windows não disponível para alguma etapa implica limitação registrada.
- T1 desenvolvimento: preparar exemplos, configuração final e descrição de PR; verificar Git e branch sem reescrever histórico.
- T2 testes: ensaio do guia e roteiro; inspecionar arquivos rastreados e diferenças antes de preparar publicação.
- T3 documentação: explicar decisões, trade-offs, resultados reais e próximos passos; pedir autorização somente para publicação concreta.
