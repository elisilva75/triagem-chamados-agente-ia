# Instruções do projeto

- Comunicar em português, com explicações objetivas. Autora do portfólio: Eliana Gomes da Silva.
- Ler README.md e docs/andamento.md antes de continuar; preservar arquivos existentes.
- Escopo aprovado em 07/11/2026: ler docs/08-decisoes-aprovadas.md. Entrega atual limitada a US01/US02 e CI pertinente; aguardar validação de Eliana antes de US03.
- Após revisão, trabalhar em uma história por vez, com rastreabilidade história → critérios → tasks → código → testes → evidências.
- Decisões rotineiras não exigem confirmação. Perguntar sobre produto quando necessário, bloqueios reais ou ações que exigem autorização.
- Usar a base técnica de docs/04-arquitetura.md. Consultar documentação oficial para compatibilidade de versões antes de configurar dependências; registrar versões e fontes.
- Separar regras determinísticas de sugestões de IA. Persistir o chamado antes da triagem; validar toda saída do agente. Provedor isolado por interface; modo simulado padrão.
- Usar dados fictícios; nunca incluir conteúdo interno de empregadores, credenciais ou senhas reais. Manter .env fora do Git.
- Não executar chamadas pagas, publicar no GitHub, fazer deploy ou contratar serviços sem autorização explícita. Explicar credenciais e custos antes de usar provedor real.
- Somente AI_MODE=simulated nesta fase; integração real (US08) adiada. Sem autenticação, uso exclusivo em loopback; não disponibilizar publicamente.
- Executar testes proporcionais à história; não declarar aprovação sem execução. Registrar comandos, resultados e limitações em docs/andamento.md.
- Testes comuns e CI usam simulação reproduzível. Separar testes HTTP dentro do processo, contra servidor real e avaliações opcionais de modelo real.
- Atualizar documentação e andamento em cada entrega. Não concluir história com aceite obrigatório pendente.
- Após aprovação do escopo, verificar Git local; usar branches e commits claros sem inventar histórico. Não sobrescrever alterações do usuário.
