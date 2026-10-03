# nassauTickets

Sistema web para controlar a emissão e o atendimento de senhas em um Laboratório de Análises Clínicas.

## Objetivo

Organizar a fila de atendimento, apoiar os atendentes e exibir chamadas recentes no painel. O cliente pode emitir uma senha anonimamente no totem.

## Tecnologias

- Frontend: React 19, Vite e JavaScript.
- Backend: Python, FastAPI e SQLAlchemy.
- Banco de dados: MySQL 8.
- API REST com autenticação Bearer/JWT.

O backend Python/FastAPI foi escolhido por já estar implementado e incluído em `backend/`; essa escolha aproveita o trabalho existente e está entre as tecnologias aceitas na especificação do projeto.

## Organização

```text
backend/                 API FastAPI, serviços, modelos e configuração Docker
docs/                    requisitos e artefatos do projeto
  branding/
  mer/
  mockups/
  models/uml/
  requirements/
frontend/                aplicação React executada com Vite
```

O frontend consome a API em `http://localhost:8000` por padrão. Para mudar o endereço, defina `VITE_API_URL` no ambiente do Vite.

## Execução local

### 1. Banco e API

Copie `backend/.env.example` para `backend/.env` e ajuste os valores se necessário. A partir da raiz do repositório:

```bash
docker compose --env-file backend/.env -f backend/docker-compose-dev.yml up --build
```

A API ficará disponível em `http://localhost:8000` e a documentação interativa em `http://localhost:8000/docs`. O MySQL é publicado na porta `3308` do host.

### 2. Frontend

Em outro terminal:

```bash
cd frontend
npm install
npm run dev
```

Abra o endereço indicado pelo Vite (normalmente `http://localhost:5173`). Entre com um usuário atendente/gestor cadastrado no backend. Para emissão de senha no totem, use a opção **Totem** sem login.

## Funcionalidades da interface

- Totem anônimo para emitir senhas SP, SG e SE.
- Login e visão do atendente com seleção de guichê.
- Chamada, chamada novamente, início, finalização e registro de não comparecimento.
- Painel público das cinco últimas chamadas, com leitura de voz opcional.
- Acesso de gestor a relatórios diários e mensais, com detalhamento, tempos médios e auditoria.
- Atualização periódica do painel e da fila, com aviso quando a API não estiver acessível.

As regras operacionais e os requisitos resumidos estão em [`docs/requirements/requisitos.md`](docs/requirements/requisitos.md). Consulte `backend/routers/` e `backend/services/` para os contratos e regras fornecidos pela API.

## Configuração e segurança

As variáveis de desenvolvimento estão documentadas em `backend/.env.example`. Não publique arquivos `.env` com credenciais. Altere as senhas de demonstração e o segredo JWT antes de qualquer implantação compartilhada.

## Git e branches

O desenvolvimento da atividade deve ocorrer na branch `dev` e ser integrado à `main` por merge. O checkout recebido contém a branch `Dev` e a branch `main`; confirme a convenção de nomes do grupo antes de publicar para que ela corresponda exatamente ao critério de avaliação.

## Membros

Preencha os nomes, matrículas e papéis do grupo antes da entrega.

| Nome | Matrícula | Papel |
|---|---|---|
| A preencher | A preencher | Scrum Master |
| A preencher | A preencher | Desenvolvedor |

## Licença

Este projeto está sob a licença MIT. Consulte [`LICENSE`](LICENSE).
