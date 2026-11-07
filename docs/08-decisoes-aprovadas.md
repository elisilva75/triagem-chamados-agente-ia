# Decisões aprovadas e limites desta entrega

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
