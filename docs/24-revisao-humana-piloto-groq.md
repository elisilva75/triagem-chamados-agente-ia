# US08 — revisão humana do único piloto Groq

**Estado: revisão humana dos dois rótulos confirmada por Eliana. Custo posterior: sem cobrança observada no plano Livre.**
Preparação offline em 09/11/2026, branch `feat/us08-avaliacao`, simulador ativo.
Nenhuma nova chamada, recuperação de banco ou alteração do ledger original.

## Evidências disponíveis e origem

O [executor local](../scripts/us08_groq_pilot.py) contém os literais enviados a
`register_ticket` na execução. O [andamento](andamento.md) identifica esse comando
e seu resultado; o ledger local ignorado `reports/us08/groq-authorized-single-pilot.json`
confirma ticket `76ad78ea-361a-4868-9e07-ab42b9607083`, modelo
`openai/gpt-oss-20b`, classificação, três respostas 200 e descarte do banco.
SHA-256 do ledger conferido, sem alteração:
`7a68fa365fcef532704227bbea04659ce846075b5e11f5876a9eedab061d0bbd`.

Título e descrição abaixo são transcrição exata dos literais do executor usado,
com as strings adjacentes da descrição concatenadas conforme Python. Não são
um snapshot recuperado do PostgreSQL nem uma captura do payload HTTP; esses
registros não foram preservados. Não foram completados ou parafraseados.

## Fatos do chamado fictício

**Título:** Erro ao salvar cadastro fictício

**Descrição:**

> No ambiente fictício de demonstração, três pessoas não conseguem salvar o cadastro desde 08h, sem alternativa. Preencher o formulário e clicar em Salvar retorna erro e bloqueia o trabalho.

Os fatos declarados são ambiente fictício de demonstração, três pessoas afetadas,
início às 08h, falha ao salvar após preencher formulário, bloqueio de trabalho e
ausência de alternativa. Não há evidência de indisponibilidade para todos ou de
um serviço essencial. Não inferir hora da avaliação ou duração total a partir de 08h.

## Sugestão e justificativa do modelo

**Categoria: `defeito`. Prioridade: `alta`.** Ambas constam no ledger original.

**Justificativa textual (`rationale`): não registrada nos artefatos remanescentes.**
Ela fez parte da saída estruturada validada/persistida no banco durante o piloto,
mas o executor só copiou categoria/prioridade para o ledger antes do descarte.
Não é possível citar a justificativa efetiva do modelo ou recuperar seu texto
pelos totais de tokens. O campo `missing_fields` também não foi copiado. Não
substituir esses campos por texto do simulador, fixtures ou análise do assistente.

O executor foi posteriormente ajustado para preservar esses campos em relatórios
fora do banco; [guia de consulta e ensaio offline](25-evidencias-executor-us08.md).
Isso não recupera os campos ausentes deste piloto nem altera seu ledger histórico.

## Análise do assistente, separada da resposta do modelo

O catálogo local define `defeito` como erro no comportamento da aplicação: a
falha ao salvar descrita permite avaliar a adequação dessa categoria, sem provar
a causa técnica do erro. A política local define `alta` como vários usuários
afetados ou bloqueio essencial sem alternativa. Três pessoas afetadas e trabalho
bloqueado sem alternativa oferecem elementos para avaliar essa prioridade.
Essa é uma interpretação do assistente da política em [tools.py](../app/agent/tools.py),
não uma justificativa recuperada do modelo nem uma decisão humana.

A falta de `rationale` **não impede avaliar categoria e prioridade com os fatos
disponíveis**, mas impede avaliar a justificativa que o modelo efetivamente deu.
A falta de `missing_fields` impede verificar quais lacunas ele apontou. A ausência
de snapshot do banco/payload limita a confirmação independente do texto de entrada;
o texto apresentado tem como fonte o executor local associado ao piloto.
Contexto de serviço essencial/abrangência total não foi declarado; não acrescentar
isso para justificar prioridade crítica. A decisão de concordância é de Eliana.

## Perguntas para Eliana

1. **Categoria** — você concorda com `defeito`? Se discordar, qual categoria escolheria e por quê?
2. **Prioridade** — o impacto descrito justifica `alta`? Se discordar, qual prioridade escolheria e por quê?

## Resposta de Eliana — 09/11/2026

Revisora: **Eliana Gomes da Silva**. Revisão feita com base na descrição do chamado.
Houve **concordância com categoria `defeito` e prioridade `alta`**, sem alteração
dos rótulos sugeridos pelo modelo.

Justificativa humana informada por Eliana:

> O erro ao salvar impede concluir o cadastro, e três pessoas estão com o trabalho bloqueado desde as 08h, sem alternativa.

A justificativa do modelo (`rationale`) e o campo `missing_fields` ficaram **sem
avaliação**, porque não foram preservados. A concordância registrada se limita
aos dois rótulos deste chamado; não representa avaliação desses campos nem aceite
da US08 inteira ou autorização do lote real.

Registro exclusivamente documental: nenhuma revisão foi inserida em `human_reviews`
(banco removido), e o ledger original não foi alterado. As perguntas acima são
preservadas como histórico da solicitação, agora respondida por Eliana.

## Evidência posterior de atividade e custo — 09/11/2026

Eliana confirmou também a aba **Groq → Uso → Atividade**, com filtro **Todos os
projetos**: **3 requisições em 09/11/2026 (UTC)** e **cerca de 2,2 mil tokens**
para `openai/gpt-oss-20b`. São os valores exibidos no painel; o total exato de
**2.174 tokens vem do executor**, não da apresentação arredondada de Atividade.

Conforme conferência do painel relatada por Eliana, em **Groq → Uso → Custo**,
com filtro de **novembro de 2026** e **todos os projetos**, o modelo
`openai/gpt-oss-20b` exibiu **US$ 0,00**. O painel informou que a cobrança só
começa após upgrade. Registro: **sem cobrança observada no plano Livre**.
Essa evidência posterior atualiza o estado anterior de custo não confirmado.

As **3 requisições** constam tanto no **registro da execução** quanto na aba
**Atividade**. Os **2.174 tokens exatos** permanecem atribuídos ao executor:
1.145 tokens de entrada e 1.029 de saída, informados pela API e preservados no
ledger original. A aba Custo sustenta o registro de cobrança, não a contagem de
requisições ou tokens. O ledger não foi alterado.
Esta atualização não autoriza novas chamadas ou upgrade.

Demo e alterações locais preservados, `AI_MODE=simulated`, lote real de 24
**pausado**, sem commit ou push. Somente atualização documental, sem chamada à API.
