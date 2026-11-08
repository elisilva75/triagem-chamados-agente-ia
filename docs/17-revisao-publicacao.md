# Publicação e revisão do repositório

## Autorização e privacidade — 08/11/2026

Eliana confirmou repositório público elisilva75/triagem-chamados-agente-ia, branch main, licença MIT e uso de seu noreply GitHub exato, copiado por ela das configurações da conta. Autorizou reescrever somente o histórico destinado à publicação e publicar somente main, sem force push, branches adicionais, tags ou backups. Visibilidade e identidade não são mais decisões pendentes. Integração real US08 permanece adiada; Docker Compose ainda não validado.

Reescritos os 9 commits de main: somente endereço nos campos author/committer e hashes de pais derivados foram substituídos. Preservados nomes, mensagens byte a byte, ordem dos pais/commits, datas e árvores de conteúdo. Configuração local de novos commits usa o noreply confirmado. Backup anterior em bundle ignorado dentro de .local; branches antigas e reflogs permanecem exclusivamente locais, fora do refspec a enviar. Não foram criadas referências refs/original. Auditoria específica compara metadados/árvores/mensagens e procura o endereço anterior nos commits e blobs de main e arquivos rastreados, sem imprimir o valor.

Conta elisilva75 reconfirmada por API autenticada; repositório retornou 404 imediatamente antes da criação autorizada. Repositório público criado sem auto-inicialização e main publicada no commit c7c3331, sem force push. Descrição/tópicos configurados e main definida como padrão. API remota confirmou somente main e nenhuma tag; backup e branches antigas não enviados.

**CI remota aprovada:** [run 42507831040](https://github.com/elisilva75/triagem-chamados-agente-ia/actions/runs/42507831040), commit c7c3331, conclusão success. JUnit baixado e conferido: 98 unitários, 77 integração/API, 2 HTTP real, total 177; zero falhas/erros/skips. Logs identificaram Ubuntu 26.04, Python 3.12.16 e PostgreSQL 16.15. Não foi preciso corrigir código ou workflow. Atualização posterior apenas documental/comentários usa [skip ci], respeitando a orientação de não repetir toda a suíte por documentação; o êxito da execução é atribuído ao commit c7c3331, sem inventar outro run.

Clone com --single-branch --branch main --no-tags em .local isolada confirmado: mesmo commit remoto, somente noreply nos author/committer, 90 arquivos rastreados, LICENSE presente e .env ativo ausente. Conferência local de links e schemas repetida para a documentação, sem suíte funcional adicional. Git local inicialmente recusou certificado com seu backend anterior; envio funcionou com Schannel/Windows, mantendo verificação TLS, e a opção foi configurada apenas neste repositório.

**Pendência real:** US01-CA1 e persistência Compose continuam sem execução; CI Ubuntu/PostgreSQL de serviço não valida imagem Docker da API ou Compose. US07 atendida incluindo remoto; US09 publicada/ensaiada no escopo descrito. US08 adiada não bloqueia o MVP simulado. Sem deploy, chamada de modelo real ou chamada paga. As seções abaixo preservam o histórico anterior; decisões pendentes/hashes antigos ali citados pertencem àquelas etapas.

## Histórico da preparação anterior à autorização

Revisão documental em 08/11/2026. Autora do portfólio: **Eliana Gomes da Silva**. Branch principal preparada: `main`, criada a partir de `chore/mvp-readiness`, base revisada `83dd970`. Destino planejado: [elisilva75/triagem-chamados-agente-ia](https://github.com/elisilva75/triagem-chamados-agente-ia). Nenhum remoto configurado, push, PR remoto, deploy ou chamada paga. Licença [MIT](../LICENSE), copyright 2026 Eliana Gomes da Silva, adicionada por autorização expressa.

Eliana autorizou o commit das alterações finais pertinentes com preservação do histórico revisado. Usada a identidade Git já configurada; nenhuma identidade inventada e nenhuma reescrita. O workspace local foi preservado e é ignorado. Commits anteriores e outras branches permanecem intactos; somente main e seus ancestrais integram o escopo de publicação futura.

## Material preparado

READMEs [português](../README.md) e [inglês](../README.en.md) autossuficientes para objetivo, funcionalidades, arquitetura, pré-requisitos, clone/fork com URL marcadora, .env, execução nativa, Compose explicitamente não validado, parada/reinício sem remoção de dados, Swagger completo, testes isolados e diagnóstico de portas/banco/migração. Os valores de negócio dos exemplos permanecem em português também no README inglês, conforme o contrato da API.

`.env.example` explica que seu padrão é o do Compose e que o caminho nativo usa outro usuário/porta/banco. `.gitignore` passou a ignorar arquivos code-workspace, preservando o workspace local. Configuração funcional da aplicação, dependências, Compose e testes não foram alterados. Não houve nova suíte completa nem nova homologação manual.

## Descrição sugerida para o GitHub

**Português:** API local de chamados com agente simulado, revisão humana e histórico de classificação. Python, FastAPI, PostgreSQL e testes automatizados isolados.

**English:** Local ticket API with simulated triage, human review and classification history. Python, FastAPI, PostgreSQL and isolated automated tests.

Tópicos sugeridos: `python`, `fastapi`, `postgresql`, `sqlalchemy`, `alembic`, `pytest`, `test-automation`, `human-in-the-loop`, `simulated-agent`, `ticket-management`, `portfolio`. Não usar tópicos que sugiram LLM/provedor real integrado nesta versão.

Nome escolhido pela autora: `triagem-chamados-agente-ia`, conta `elisilva75`, branch principal `main`. READMEs usam a URL planejada, deixando claro que a publicação ainda não ocorreu.

## Conferência de conta e nome — somente leitura

**Atualização após login autorizado em 08/11/2026:** Git Credential Manager 2.5.1, fluxo oficial de navegador com `git credential-manager github login --username elisilva75 --browser --force`, concluído com saída 0 e autorização confirmada por Eliana. Verificação posterior: GET autenticado /user **200**, login **elisilva75**; GET autenticado /repos/elisilva75/triagem-chamados-agente-ia **404**, assim como a consulta pública. Repositório não existe para a conta autenticada neste momento; nome não reservado. Credencial gerenciada pelo GCM, sem token impresso ou salvo nos arquivos do projeto. Nenhum remoto/repositório criado, push, publicação ou alteração de commits. Aguardar definições de visibilidade e e-mail; repetir a consulta de existência antes de futura criação.

O parágrafo abaixo preserva o diagnóstico anterior, agora resolvido pelo login:

GitHub CLI não foi encontrado no PATH; não há ferramenta GitHub conectada disponível nesta sessão. Conferido o gerenciador de credenciais Git sem imprimir tokens. Sob o sandbox a credencial não estava acessível; na execução autorizada fora dessa restrição foi encontrada, mas GET autenticado /user retornou **401**, sem identidade confirmada. GET autenticado do repositório também retornou 401. A conexão informada no VS Code não foi presumida válida para o processo Git.

Consulta pública GET /repos/elisilva75/triagem-chamados-agente-ia retornou **404**. Isso informa ausência de repositório publicamente visível nesse endereço; não prova disponibilidade na conta autenticada, inclusive diante de repositórios privados ou restrições. Não houve criação de repositório nem configuração de origin. Antes de criar qualquer remoto, autenticar o cliente efetivamente utilizado, confirmar /user=elisilva75 e repetir a verificação de existência do nome como proprietária. A disponibilidade é temporal e não fica reservada por esta consulta. Evidência local sanitizada em .local/github-readiness.json; nenhum token salvo pelo script.

## Auditoria de arquivos e histórico

Escopo histórico da base `83dd970`, antes do commit final: **8 commits alcançáveis pela branch revisada**; inspeção ampliada das branches locais nessa base: **9 commits, 180 blobs únicos, 89 caminhos históricos**. Leitura por git rev-list/ls-tree/cat-file; nenhuma reescrita ou exclusão de branch. Conteúdo atual preparado também foi examinado. Valores encontrados e identidades Git não são impressos neste relatório.

Não foram encontrados padrões de chaves privadas, tokens de provedores/GitHub/AWS ou credenciais PostgreSQL fora dos exemplos fictícios permitidos. Não há bancos, .env ativo, venvs, logs ou relatórios rastreados no histórico da branch preparada. Revisão por padrões e inspeção contextual não garantem detectar todo segredo possível. Os relatórios JUnit e as evidências locais continuam ignorados; não serão enviados como arquivos do projeto.

**Achado fora do histórico a publicar:** a branch local `feat/foundation-tickets` contém o commit `c3d3c95`, com o arquivo `projeto-agente-ia.code-workspace`. Esse commit não é ancestral de `chore/mvp-readiness`; a branch atual e seus ancestrais não contêm o workspace. Inspeção do arquivo histórico: apenas uma entrada de pasta relativa, sem caminho absoluto, configurações ou padrão de segredo. Mesmo assim é artefato local e deve ficar fora do escopo publicado.

**Escopo autorizado para preparação: somente main e seus ancestrais revisados.** Não usar publicação de todas as branches, --all ou --mirror, nem enviar a branch local antiga. Não é necessário reescrever o histórico de main para excluir aquele arquivo. Se Eliana desejar publicar também a branch antiga, será necessária outra revisão e decisão explícita; nada foi apagado agora.

**Metadados Git:** encontrado um único e-mail de autor/committer no histórico revisado, coincidente com a configuração local, fora do padrão GitHub noreply. Tratado como potencialmente pessoal; não é possível inferir consentimento de exposição pela configuração. Nome/e-mail fazem parte dos commits e seriam visíveis quando publicados. Valores não reproduzidos. O novo commit autorizado mantém a identidade existente; nenhuma alteração de autoria, e-mail ou histórico foi feita automaticamente.

Opções antes da publicação: (1) Eliana confirma que deseja manter essa identidade e o histórico permanece intacto; (2) fornece/confirma um endereço público real ou seu noreply exato obtido no GitHub e autoriza a reescrita dos metadados, com novos hashes e nova auditoria; (3) autoriza preparar um histórico de publicação separado a partir do estado revisado, preservando as branches locais antigas. Opções 2 e 3 não foram executadas. Não foi inventado endereço noreply nem usada a autenticação como prova da identidade de autor.

## Última validação funcional — preservada, não reexecutada

Em 08/11/2026, com AI_MODE=simulated, APP_ENV=test e TEST_DATABASE_URL do PostgreSQL administrativo isolado em loopback, foi executado:

```powershell
.\.venv\Scripts\python.exe scripts/check_quality.py
```

Resultado já registrado: **177 passed, nenhum erro/falha/skip**; 98 unitários, 77 integração/API, 2 HTTP real. Pip check e Ruff aprovados; aviso conhecido TestClient/HTTPX. Instalação em venv nova e fontes isoladas, migração repetida, roteiro de falha/retry/revisão/resolução e reinício nativo da API foram ensaiados com preservação integral do demo. Comandos detalhados, tempos e limites em [andamento](andamento.md); versões exatas nos READMEs/locks e [ambiente](09-ambiente-e-versoes.md).

Esta revisão não certifica as instalações dos pré-requisitos numa máquina nova, clone/fork remoto, Docker/Linux ou GitHub Actions. Comandos desses caminhos estão documentados e rotulados conforme a evidência existente. Os novos exemplos Swagger foram conferidos contra schemas/rotas e os fluxos automatizados já executados; não apresentados como nova execução manual.

Verificações após licença/URL: 16 blocos PowerShell dos READMEs analisados pelo parser, sem erro de sintaxe; 8 corpos JSON validados contra os schemas reais (TicketCreate, TriageRequest, ReviewCreate e VersionRequest). Conferidos 87 links Markdown locais em 21 arquivos, sem quebra, e git diff --check aprovado; padrões de segredos examinados no estado atual e histórico ampliado. Nenhum comando de inicialização/parada, operação no banco demo ou exemplo Swagger foi executado nesta etapa documental. Versões instaladas consultadas por metadados, sem nova instalação. Nos dois locks, somente o comentário inicial foi corrigido para distinguir Windows nativo validado de Linux/CI pendentes; nenhuma versão alterada.

## Decisões para Eliana antes de publicar

- Visibilidade do repositório. Conta, nome, URL planejada, licença MIT e branch main já definidos/autorizados.
- Autenticação como elisilva75 confirmada após login; consulta autenticada não encontrou o repositório. Repetir a consulta antes de criar qualquer remoto, pois o nome não está reservado.
- Confirmar identidade pública dos commits entre as opções descritas acima; alterar metadados existentes exige decisão específica. Escopo de apenas main e seus ancestrais revisados já definido.
- Momento de publicar: Docker/Compose (US01-CA1 e persistência por reinício) e CI remota continuam pendentes. É possível revisar uma publicação com essas limitações declaradas, mas não anunciar a entrega final integralmente validada. US08/modelo real segue adiada, sem bloqueio para o MVP simulado.
- Autorização explícita futura para criar/conectar repositório e enviar conteúdo. Esta etapa apenas prepara o material; não executa publicação.
