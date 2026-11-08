# Decisões aprovadas e limites desta entrega

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
