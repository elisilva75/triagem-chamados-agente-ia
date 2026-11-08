# Demonstração curta e portfólio

Autora: **Eliana Gomes da Silva**. Demonstração opcional em banco fictício separado; não repetir homologações nem usar o chamado histórico do demo. Origem do ensaio técnico e resultados: [andamento](andamento.md). Não há nova homologação manual atribuída a Eliana.

## Roteiro de 5 minutos

Ensaio automatizado opcional do mesmo roteiro: Python da venv com `scripts/demo_flow.py --base-url http://127.0.0.1:18000`, depois de iniciar a API em banco isolado. O comando cria um chamado fictício novo, consulta versões antes de escrever e não limpa dados. Requer as dependências de desenvolvimento. Não apontar para a API do demo histórico.

Abrir Swagger da API isolada. Usar o ID retornado pelo cadastro abaixo. Antes de **cada** operação posterior, GET /api/v1/tickets/{ticket_id} e copiar version para expected_version; os números ilustrados pressupõem somente esta sequência.

1. POST /api/v1/tickets:

   ```json
   {"title":"[SIMULADO:saida-invalida]","description":"No ambiente fictício, salvar o cadastro retorna erro para todos os usuários."}
   ```

   Esperado: 201, aberto/pendente, version=1, content_revision=1. O chamado já está persistido sem IA.

2. POST /api/v1/tickets/{ticket_id}/triage com `{"expected_version":1}`. Esperado: 502, error.code=invalid_ai_response. GET confirma texto preservado, aberto/falha, version=3, content_revision=1, suggestion/final_classification nulos. GET triage-attempts mostra uma tentativa falha, sem saída inválida persistida.

3. Retry explícito: consultar GET e POST triage com `{"expected_version":3}`. Esperado: outra resposta 502, version=5 e duas tentativas preservadas. O marcador é determinístico: repetir a entrada não a torna válida.

4. Corrigir o título fictício com PATCH /api/v1/tickets/{ticket_id}:

   ```json
   {"expected_version":5,"title":"Erro ao salvar cadastro fictício"}
   ```

   Esperado: 200, version=6, content_revision=2, triagem pendente. GET e POST triage com `{"expected_version":6}`: 200, ticket version=8, sugestão mode=simulated, triagem sugerida. Mostrar ferramentas/contagens no attempt e as três tentativas preservadas.

5. POST /api/v1/tickets/{ticket_id}/reviews:

   ```json
   {"expected_version":8,"category":"defeito","priority":"alta","reason":"Confirmei o bloqueio no ambiente fictício.","declared_reviewer":"Pessoa Revisora Demo"}
   ```

   Esperado: 201, version=9, triagem revisada, classificação final vinculada à review. Autor é declarado, não autenticado. GET reviews mostra decisão/motivo; a sugestão permanece separada.

6. GET e POST /api/v1/tickets/{ticket_id}/resolve com `{"expected_version":9}`: 200, resolvido, version=10, content_revision=2. GET confirma persistência. Mostrar rapidamente que o histórico permanece disponível. Encerrar com limites e próximos passos, sem solicitar novas verificações manuais.

## Texto para portfólio

**Triagem Inteligente de Chamados — MVP local com agente simulado.** API desenvolvida para demonstrar o ciclo de chamados, do registro independente de IA à sugestão validada, revisão humana e resolução. Inclui edição com controle de concorrência, invalidação de classificação após mudanças, recuperação de tentativas interrompidas e preservação de decisões anteriores.

A solução usa Python, FastAPI, Pydantic, PostgreSQL, SQLAlchemy e Alembic. Um monólito modular separa regras determinísticas, orquestração do agente e persistência. O simulador segue um protocolo de ferramentas locais, com limites de execução e validação estrita da saída. A pessoa revisora decide a classificação final. Testes abrangem regras, transações, concorrência, migrações e HTTP contra servidor real, sempre com bancos exclusivos e dados fictícios.

As decisões privilegiam reprodutibilidade e segurança dos dados antes de integração externa. Esta versão não usa modelo real nem mede acurácia de IA. Não possui autenticação, acesso público à aplicação, fila distribuída ou reconstrução integral de textos antigos. Código publicado e CI remota aprovada com 177 testes; Docker Compose permanece não validado. US08 está adiada e não bloqueia o MVP simulado.

**Uso de IA no desenvolvimento:** assistência do Codex na implementação, revisão, testes e documentação, com decisões de produto e revisão de Eliana. A assistência usada para construir o software não representa um provedor integrado à aplicação. Código publicado por autorização expressa; nenhum deploy ou chamada paga realizado.

## Descrição preparada para revisão de publicação

API local de triagem de chamados com simulação reproduzível, revisão humana e histórico de classificação. Documentação PT/EN, guias de instalação/testes, roteiro de demonstração e pipeline compartilhado com GitHub Actions. Repositório público publicado por autorização da autora, com CI remota aprovada; a pendência de Docker Compose impede anunciar validação integral de infraestrutura. Não houve deploy ou PR remoto.
