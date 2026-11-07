# Entregas, qualidade e riscos

**Proposta inicial — sem estimativa de prazo fechada.** Avançar em pequenas entregas, uma história por vez, somente após revisão do escopo.

## Plano e dependências

| Entrega | História | Depende de | Resultado revisável |
|---|---|---|---|
| E0 | Planejamento atual | Inspeção da pasta | Documentos e decisões D01–D08 para revisão |
| E1 | US01 | Revisão de E0 | Ambiente, banco, migração e compatibilidade documentada |
| E2 | US02 | US01 | Cadastro e consultas persistentes |
| E3 | US03 | US02 | Edição e concorrência |
| E4 | US04 | US02/US03 | Agente simulado, ferramentas e validação |
| E5 | US05 | US04 | Falhas, prazos, recuperação e retry |
| E6 | US06 | US04/US05 | Revisão humana e resolução/reabertura |
| E7 | US07 | US01–US06 | Pipeline completo e fluxo HTTP real |
| E8 | US08 | US04/US05 e decisão D08 | Adaptador real testado com transporte falso; avaliação paga opcional |
| E9 | US09 | US07 e situação de US08 documentada | Repositório preparado e demonstração, sem publicação automática |

Testes locais são desenvolvidos junto com cada história; US07 integra as suítes no pipeline, não adia a qualidade. Configuração de CI pode começar tecnicamente em US01 e ser completada em US07. Git local, branch e commits entram após revisão e inspeção do ambiente, sem publicação remota. Sem inventar commits para etapas já ocorridas.

## Definition of Ready

- História com ator, benefício, prioridade e dependências identificados.
- Critérios positivos, negativos e de limite verificáveis; regras e contrato consistentes.
- Decisões de produto que afetem a história revisadas; dúvidas e suposições registradas.
- Tasks de desenvolvimento, testes e documentação identificadas; dados fictícios disponíveis.
- Ferramentas/ambiente necessários acessíveis; configuração de dependências precedida de verificação oficial de compatibilidade.

## Definition of Done

- Todos os critérios obrigatórios da história implementados e verificados com evidências reais.
- Regras e falhas relevantes testadas; migração testada quando houver mudança de esquema.
- Validações de entrada/saída, concorrência e logs seguros revisados quando afetados.
- Documentação, exemplos, decisões e andamento atualizados; limitações declaradas.
- Testes locais pertinentes aprovados e comandos registrados. Após US07, pipeline local equivalente obrigatório; execução remota depende de publicação autorizada e é registrada separadamente.
- Sem segredos/dados internos; escopo revisável em diff e commits claros se Git estiver disponível.
- Nenhum critério pendente mascarado como concluído. Avaliação real de IA é opcional e seu status deve ser explícito.

## Riscos e resposta

| Risco | Impacto | Mitigação / responsável |
|---|---|---|
| Escopo crescer antes de demonstrar fluxo | Atraso e excesso de complexidade | Eliana revisa D01–D08; implementação preserva MVP e registra mudanças |
| IA inventar classificação ou obedecer texto malicioso | Sugestão inadequada | Implementação limita ferramentas/estrutura; avaliação e pessoa revisora validam sentido |
| Provedor cair ou exceder custo | Bloqueio/cobrança | Cadastro independente, simulação padrão, timeout e autorização antes de pago |
| Processo morrer durante triagem | Estado em análise persistente | Deadline persistida e recuperação atômica; testes de reinício |
| Revisão/edição concorrente | Perda de atualização | Versionamento otimista e constraints PostgreSQL |
| Dependências incompatíveis ou Docker indisponível no Windows | Ambiente não executável | Verificar versões oficiais e requisitos antes de configurar; registrar limitações e solução |
| Ausência de autenticação | Escrita por qualquer cliente com acesso | Bind local e dados fictícios; autenticação obrigatória antes de uso público |
| Modelo real não escolhido/autorizado | Integração remota sem evidência | Manter adaptador desacoplado; marcar avaliação não executada, sem alegar qualidade real |
| Perda de resposta no cadastro | Possível duplicação em retry | Documentar limitação; idempotência como evolução |

## Roteiro futuro de demonstração

Explicar problema → criar chamado → mostrar registro sem IA → executar modo simulado com ferramentas → provocar falha e mostrar registro preservado → repetir → corrigir sugestão por revisão humana → resolver → mostrar testes dentro do processo e por HTTP real. Encerrar com decisões, limites e próximos passos. Esse roteiro ainda não tem comandos executáveis; será ensaiado em US09.
