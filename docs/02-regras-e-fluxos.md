# Fluxos, regras e qualidade

**Proposta inicial — aguardando revisão.**

## Estados e fluxos

Estado operacional: `aberto` ou `resolvido`. Estado independente de triagem: `pendente`, `em_analise`, `sugerida`, `falha` ou `revisada`. Classificação final só existe após revisão humana.

| Evento | Origem | Destino | Condição |
|---|---|---|---|
| Criar | inexistente | aberto / pendente | Entrada válida persistida |
| Solicitar triagem | pendente ou falha | em_analise | Chamado aberto; aquisição atômica da execução |
| Saída válida | em_analise | sugerida | Mesma revisão do conteúdo e ferramentas obrigatórias consultadas |
| Falha/timeout/saída inválida | em_analise | falha | Registrar código de erro seguro |
| Revisar | sugerida | revisada | Categoria, prioridade e motivo válidos |
| Editar conteúdo | aberto, exceto em_analise | aberto / pendente | Incrementar revisão e limpar classificação atual |
| Resolver | aberto / revisada | resolvido / revisada | Classificação final presente |
| Reabrir | resolvido / revisada | aberto / revisada | Sem alterar conteúdo |

Demais transições: 409. Revisão humana pode ser corrigida em `revisada`, gerando novo histórico. Retry em `sugerida` ou `revisada` é 409; para nova análise o conteúdo deve mudar. Edição sem mudança efetiva é 200 sem invalidar dados. Chamado resolvido só permite leitura e reabertura.

Fluxo principal: criar → solicitar triagem → consultar ferramentas → validar sugestão → revisar → resolver. Alternativo: criar → falhar triagem → consultar chamado preservado → tentar novamente → revisar. Conteúdo incompleto continua aceito e gera campos ausentes; não existe preenchimento automático do texto pelo modelo.

## Regras determinísticas

| ID | Regra verificável |
|---|---|
| RN01 | Título de 5–120 e descrição de 20–5000 caracteres Unicode após trim; rejeitar campos desconhecidos e texto em branco com 422. Não normalizar acentos nem aceitar coerção de números para texto |
| RN02 | Cadastro inicia aberto/pendente, sem classificação, antes de qualquer chamada de IA; falha de banco retorna 503 e não sucesso |
| RN03 | Categoria pertence ao catálogo D02 e prioridade a D03; restrições valem para IA e pessoa |
| RN04 | Saída IA exige categoria, prioridade, justificativa de 10–500 caracteres e lista de 0–4 campos ausentes únicos dentre ambiente, passos_reproducao, impacto, inicio_ocorrencia; rejeitar propriedades extras |
| RN05 | Sugestão não altera estado operacional nem classificação final; somente RN06 define classificação final |
| RN06 | Revisão informa categoria, prioridade e motivo de 10–500 caracteres; registra autor declarado de 2–80 caracteres, data e referência à tentativa; identidade não autenticada no MVP |
| RN07 | Falha de IA preserva chamado; marca falha com código seguro, sem armazenar resposta bruta ou segredos |
| RN08 | Somente pendente/falha podem iniciar triagem; uma tentativa ativa por chamado, garantida no banco. Tentativas recebem número sequencial único |
| RN09 | Máximo de 3 chamadas de modelo, 4 chamadas de ferramenta e 20 segundos totais por tentativa, incluindo ferramentas; sem retry automático do SDK. Até 2.000 tokens de saída por chamada; excesso encerra com falha |
| RN10 | Modelo deve consultar consultar_categorias e consultar_politica_prioridade antes da saída final; ferramenta desconhecida, argumentos inválidos, limite excedido ou ausência de consulta obrigatória invalidam tentativa |
| RN11 | Edição efetiva de título/descrição incrementa content_revision, remove sugestão/classificação atuais e volta a pendente; histórico permanece |
| RN12 | Resolver/reabrir e editar seguem tabela de transições; transições repetidas de resolver/reabrir retornam 409 |
| RN13 | Histórico de tentativas e revisões é imutável e ordenado por data e ID; timestamps UTC, IDs UUID |
| RN14 | Catálogo e política têm versão registrada na tentativa. Texto de chamado é dado não confiável e nunca pode definir ferramentas, categorias ou instruções do sistema |
| RN15 | Ao iniciar nova triagem, tentativa em_analise com prazo vencido vira falha/execucao_expirada atomicamente antes de criar nova; resultado atrasado não pode sobrescrever nova tentativa |
| RN16 | Escritas em chamado existente exigem expected_version; divergência gera 409. Incrementar version em cada mudança de estado ou conteúdo; comparação e escrita atômicas |

## Política consultada pelo agente (sugestão, não aplicação automática)

Crítica: indisponibilidade total de serviço essencial para todos, sem alternativa. Alta: impacto relevante em vários usuários ou bloqueio individual essencial sem alternativa. Média: falha parcial com alternativa. Baixa: dúvida ou melhoria sem bloqueio. Sem impacto informado: sugerir média provisória e incluir `impacto` nos ausentes. O modelo interpreta linguagem para sugerir a faixa; a aplicação apenas valida enumeração e estrutura. Pessoa revisora pode discordar mediante motivo. Não criar SLA contratual a partir dessas faixas.

## Requisitos não funcionais e verificação

| ID | Meta proporcional | Evidência planejada |
|---|---|---|
| RNF01 | Cadastro não depende do provedor; transações atômicas | Integração com provedor indisponível e rollback do banco |
| RNF02 | Sem credenciais no repositório/logs; registrar IDs, duração e códigos seguros | Inspeção de logs e casos com texto simulando segredo |
| RNF03 | Cadastro/consulta p95 ≤ 500 ms em 100 requisições sequenciais locais com 1.000 chamados, excluindo IA | Medição informativa, registrar máquina e ambiente; não alegar SLA |
| RNF04 | Tentativa limitada a 20 s; tolerância de 2 s no teste do servidor | Relógio controlado em unitários e teste HTTP de timeout |
| RNF05 | Banco mantém dados após reiniciar API/Compose | Teste com volume local; dados de teste em banco separado |
| RNF06 | Execução reproduzível, dependências fixadas e migrações verificadas no PostgreSQL | Ambiente limpo e pipeline; sem SQLite como substituto |
| RNF07 | Diagnóstico sem texto integral dos chamados nem saída bruta | Logs estruturados e histórico sanitizado; conteúdo fictício persiste só no chamado |
| RNF08 | Uso local; bind em loopback e banco sem exposição pública | Revisão do Compose e guia Windows antes da entrega executável |
