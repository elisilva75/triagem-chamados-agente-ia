# Avaliação de concordância da triagem

Novo [ensaio automatizado com mocks de 24 execuções](22-ensaio-us08-mocks.md) exercita este SQL sem alterações, pelo adaptador/SDK e banco descartável, com divergências e correções controladas. Não substitui as 24 execuções com modelo real, que continuam pendentes. As revisões desse ensaio são fixtures, sem aceite humano real.

Atualização US08: OpenAI escolhida como primeiro provedor; [adaptador opcional](19-adaptador-openai.md) validado com transporte falso, sem chamadas reais. A consulta abaixo é preservada e agrupa tentativas elegíveis por modo, inclusive openai após migração 0005. Modelo, custo e autorização da rodada real continuam pendentes. A referência a 0004 abaixo identifica o esquema em que a consulta foi originalmente validada.

Preparação local de US08: [consulta SQL](../scripts/triage_review_agreement.sql), somente leitura, compatível com o esquema da migração 0004. Executar no PostgreSQL com `psql -X -v ON_ERROR_STOP=1 -f scripts/triage_review_agreement.sql`, usando conexão local explicitamente selecionada e dados fictícios. Não usar banco de empregador. A aplicação continua exclusivamente em `AI_MODE=simulated`; provedor, modelo e orçamento reais permanecem pendentes.

A unidade de análise é a **tentativa revisada**, não o chamado nem cada registro de revisão. A consulta seleciona uma revisão por `attempt_id`, a mais recente por `created_at DESC, id DESC`; o ID desempata timestamps iguais. Uma correção humana substitui a revisão anterior no cálculo, preservando o histórico no banco. A junção exige o mesmo chamado e revisão de conteúdo. Somente tentativas com sucesso, categoria e prioridade presentes na sugestão e uma revisão correspondente entram no denominador. Tentativas falhas ou sem revisão ficam fora. Não há filtro de revisão de conteúdo atual: tentativas históricas elegíveis também entram.

Por modo, o relatório mostra quantidade de tentativas revisadas, contagem e percentual de concordância de categoria e prioridade, e contagem de concordância simultânea. Categoria correta com prioridade divergente soma apenas na concordância de categoria. Quando não há tentativas elegíveis, retorna **zero linhas**, não uma linha com percentuais zero.

O resultado mede **concordância na amostra revisada**. Não prova acurácia, representatividade, qualidade semântica da justificativa ou qualidade de modelo real. A seleção de casos revisados pode introduzir viés; a revisão humana também pode conter erros.

## Relação com as 24 execuções controladas

O [plano de avaliação em docs/06-testes.md](06-testes.md#pequeno-conjunto-de-avaliação-do-agente) prevê AV01–AV08 com três repetições por caso, totalizando 24 execuções. Esta consulta complementa esse plano: cada execução deve ter sua tentativa e revisão rastreáveis, com identificação dos casos/IDs no relatório da rodada. O SQL agrega todas as tentativas elegíveis do banco, sem filtrar uma rodada; usar um banco exclusivo da avaliação para não misturar amostras. Relatar o total executado e o total elegível, além das falhas e ausências de revisão, para não esconder exclusões.

As 24 execuções reais continuam previstas, não realizadas nesta entrega. Registrar futuramente modelo, parâmetros, versões, custo e avaliação semântica por critério conforme o plano, após autorização de provedor/modelo/orçamento. A consulta não substitui os critérios de ferramentas, catálogo, ausentes, justificativa ou resistência à injeção, nem a meta de adequação semântica. Fixtures simuladas validam o cálculo, sem inferência paga.

## Validação reproduzível

`tests/integration/test_review_agreement.py` executa o arquivo SQL diretamente no PostgreSQL migrado em banco exclusivo `portfolio_test_<uuid>`, criado e removido pela fixture existente, sem acessar o demo. Cobre amostra vazia, correção por data e desempate por ID, categoria correta com prioridade divergente e exclusões de falha, ausência de revisão e sugestão incompleta. Comando e resultado efetivamente executados em [andamento](andamento.md).
