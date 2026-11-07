# Visão e escopo

**Visão do MVP — escopo geral aprovado em 07/11/2026.** Este documento descreve o produto completo; implementação e evidências são incrementais e registradas no andamento.

**Atualização de 07/11/2026:** escopo geral aprovado, com definições consolidadas em [decisões aprovadas](08-decisoes-aprovadas.md). D01–D07 aprovadas; D08 adiada, somente simulação. Implementação incremental de US01/US02 em andamento; os demais comportamentos continuam planejados. A tabela abaixo preserva a proposta que foi revisada.

## Problema, público e benefícios

Chamados chegam com descrições incompletas e classificação inconsistente. A triagem manual consome tempo e dificulta explicar por que uma prioridade foi atribuída. Público: solicitante que registra via API e analista que revisa a triagem, representados por dados fictícios na demonstração.

Proposta de valor: manter um registro confiável, sugerir classificação explicável e apontar dados ausentes sem delegar decisões finais ao modelo. Benefícios esperados, ainda sem medição: reduzir retrabalho, melhorar consistência e demonstrar engenharia de software, QA e uso responsável de ferramentas de IA no portfólio.

Indicadores para demonstração: nenhum chamado perdido por falha da IA; 100% das saídas inválidas rejeitadas no conjunto de testes; trilha de todas as tentativas e revisões. Ganho real de tempo depende de avaliação futura com usuários e não será alegado como resultado comprovado.

## MVP

- API para criar, listar, consultar e editar título/descrição de chamados abertos.
- Triagem solicitada explicitamente após cadastro, com ferramentas de consulta ao catálogo e à política de prioridade.
- Sugestões de categoria, prioridade, justificativa e campos ausentes, validadas antes de persistir como sugestão.
- Revisão humana com classificação final; resolução e reabertura explícitas.
- Persistência PostgreSQL, histórico de tentativas e revisões, tratamento de falha e retry manual.
- Simulador padrão sem custo; adaptador real configurável após escolha do provedor.
- Testes, CI, execução local por Compose e documentação para entrevista.

Futuro: interface web, autenticação e perfis, múltiplas organizações, anexos, notificações, SLA, distribuição de responsáveis, integrações externas, busca semântica/RAG e processamento por fila. Não haverá exclusão de chamados no MVP.

## Decisões de produto para revisão

| ID | Proposta | Consequência a revisar |
|---|---|---|
| D01 | MVP local sem autenticação, somente dados fictícios | Solicitante e revisor são papéis de negócio, sem identidade comprovada; uso público exigirá autenticação/autorização antes |
| D02 | Categorias: acesso, defeito, infraestrutura, duvida, outros | Catálogo pequeno; dúvidas ou contexto insuficiente podem ir para outros |
| D03 | Prioridades baixa, media, alta, critica; decisão final humana | IA nunca aplica prioridade operacional automaticamente |
| D04 | Criar sem chamar IA; POST separado para triagem síncrona e retry manual | Cadastro independente e fluxo demonstrável com duas chamadas; sem fila no MVP |
| D05 | Editar somente aberto; edição invalida sugestão e classificação anteriores | Evita classificar texto diferente; revisão precisa ser refeita |
| D06 | Pessoa informa categoria/prioridade finais e motivo da revisão | Confirmação ou correção auditável; não se aprova saída por omissão |
| D07 | Resolver exige classificação humana final; reabrir preserva classificação se texto não mudou | Fluxo simples, sem atribuição de responsável nem SLA |
| D08 | Provedor real e modelo pendentes; simulação é padrão | Escolha e orçamento precisam ser discutidos antes de ativar integração paga |

Suposições: um ambiente local, baixo volume, um catálogo global versionado, nenhum dado pessoal necessário. Sugestões são apoio à decisão; não há promessa de acerto sem revisão. Revisão solicitada agora cobre D01–D08; escolhas técnicas rotineiras permanecem autônomas após aprovação.
