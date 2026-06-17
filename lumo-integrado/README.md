# 🌻 Lumo

Gerenciador de tarefas com backend FastAPI, banco SQLite e frontend HTML/CSS/JS.

O projeto agora salva usuários e tarefas no banco `backend/lumo.db`.

## Rodar

### Windows
```
setup.bat
cd backend
venv\Scripts\activate
uvicorn main:app --reload
```

### Linux / Mac
```
./setup.sh
cd backend
source venv/bin/activate
uvicorn main:app --reload
```

Depois abra `frontend/index.html` no navegador.

## O que foi integrado

- Cadastro de conta direto na tela de login
- Login real com validação no backend
- Usuários gravados no banco SQLite
- Tarefas separadas por usuário
- Sessão mantida no navegador

## Como usar

1. Inicie o backend com `uvicorn main:app --reload`
2. Abra `frontend/index.html`
3. Na tela de login, escolha:
   - `Entrar` para usar uma conta existente
   - `Criar conta` para cadastrar um novo usuário
4. Após entrar, suas tarefas serão buscadas e salvas no banco
5. O projeto não possui mais conta padrão; o acesso é feito pela conta que você criar

## Banco de dados

- Arquivo do banco: `backend/lumo.db`
- Tabelas principais:
  - `users`
  - `tasks`

API disponível em: http://localhost:8000/docs
