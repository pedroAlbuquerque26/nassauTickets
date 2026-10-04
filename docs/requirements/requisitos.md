# Requisitos do nassauTickets

Este resumo separa as instruções de organização da atividade dos requisitos do sistema descritos nos PDFs.

## Agentes e perfis
- **AS — Agente Sistema:** emite senhas, controla filas, registra eventos e atualiza o painel.
- **AA — Agente Atendente:** autenticado, chama a próxima senha e realiza o atendimento no guichê.
- **AC — Agente Cliente:** emite senha anonimamente e acompanha as chamadas no painel.
- Gestor administra cadastros e acessa relatórios.

## Requisitos funcionais
1. Emitir senhas SP (prioritária), SG (geral) e SE (retirada de exames) sem login no totem.
2. Gerar código no formato `YYMMDD-PP` seguido de sequência diária com três dígitos.
3. Seguir a alternância `[SP] → [SE|SG] → [SP] → [SE|SG]`, escolhendo SE antes de SG quando ambas aguardam.
4. Permitir qualquer tipo de senha em qualquer guichê.
5. Exibir as cinco chamadas mais recentes sem revelar a próxima senha ainda não chamada.
6. Permitir chamar, chamar novamente, iniciar, finalizar e registrar não comparecimento.
7. Após duas chamadas sem comparecimento, marcar a senha abandonada e avançar a fila.
8. Operar das 7h às 17h, concluir atendimentos iniciados e descartar senhas pendentes no encerramento.
9. Apresentar relatórios diários e mensais com totais, detalhamento, tempo médio e auditoria.
10. Autenticar atendentes e restringir cadastros e relatórios ao gestor.

## Regras de negócio
- SP tem prioridade maior; SE vem após SP e antes de SG quando disponível; SG tem menor prioridade.
- A ordem se repete a cada atendimento e se adapta às filas vazias.
- Tempo médio esperado: SG 5 min (variação uniforme ±3); SP 15 min (±5); SE 1 min em 95% dos atendimentos e 5 min em 5%.
- Cerca de 5% das senhas podem não ser atendidas.
- Estados: `EMITIDA`, `AGUARDANDO`, `CHAMADA`, `CHAMADA_NOVAMENTE`, `EM_ATENDIMENTO`, `ATENDIDA` e `NAO_COMPARECEU`.

## Requisitos não funcionais
- Proteger credenciais e restringir ações por perfil.
- Auditar atendente, guichê, senha, chamadas e horários do atendimento.
- Tratar chamadas concorrentes sem direcionar a mesma senha a dois atendentes.
- Informar indisponibilidade quando API ou banco falharem.
- Considerar LGPD e acessibilidade, incluindo contraste, foco visível e controles acessíveis.
- Áudio anuncia tipo, código e guichê; a segunda chamada é precedida de “Última chamada”.

## Organização definida pela atividade
Repositório público `nassauTickets`, licença MIT, `.gitignore` Node.js, README com seção `## Membros`, diretórios `backend/`, `frontend/` e `docs/{branding,mer,mockups,models/uml,requirements}`. Frontend React executado via `npm install` e `npm run dev`; branches exigidas: `dev` e `main`, com merge de dev para main.

## Integração
A API incluída expõe emissão em `POST /senhas/emissir`, fila em `GET /senhas/fila`, painel em `GET /painel`, autenticação em `POST /auth/login`, atendimento em `/atendimento` e relatórios em `/relatorios`. O resumo de numeração dos PDFs tem uma possível inconsistência (“PPSQ”); a regra detalhada e o backend correspondem a dois caracteres de tipo e três dígitos.
