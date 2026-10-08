# Instruções de Deploy no Render

## Problema Atual

O Render está detectando o `package.json` na pasta `frontend/` e tentando fazer deploy como Node.js em vez de Python.

## Solução: Deploy Manual via Painel do Render

### 1. Criar Novo Serviço Python no Render

1. Acesse: https://dashboard.render.com/
2. Clique em "New +" → "Web Service"
3. Conecte ao repositório `jhowkojac/monitor_leiloes`
4. Configure assim:

**Name:** `monitor-leiloes-backend`

**Environment:** `Python`

**Build Command:**
```
pip install -r requirements.txt
```

**Start Command:**
```
python main.py
```

### 2. Configurar Variáveis de Ambiente

Adicione estas variáveis de ambiente obrigatórias:

```
ENVIRONMENT = production
SECRET_KEY = [Use "Generate" no Render]
API_TOKEN = [Use "Generate" no Render]
JWT_SECRET_KEY = [Use "Generate" no Render]
RATE_LIMIT_CALLS = 50
RATE_LIMIT_PERIOD = 60
```

### 3. Configurar Health Check

**Health Check Path:** `/health`

### 4. Deploy do Frontend (Separado)

O frontend React deve ser deployado separadamente em Vercel ou Netlify:

**Opção A: Vercel**
1. Conecte o repositório
2. Root directory: `frontend`
3. Build command: `npm run build`
4. Output directory: `dist`

**Opção B: Netlify**
1. Conecte o repositório
2. Base directory: `frontend`
3. Build command: `npm run build`
4. Publish directory: `dist`

### 5. Atualizar CORS no Backend

Após deploy do frontend, atualize as origens permitidas em `main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://seu-frontend-vercel.vercel.app",  # Substitua pela URL real
        "https://seu-frontend-netlify.netlify.app",  # Substitua pela URL real
        "http://localhost:5173",
        "http://localhost:3000"
    ],
    ...
)
```

## Por que Deploy Manual?

O Render usa detecção automática baseada em arquivos presentes:
- `package.json` → Node.js
- `requirements.txt` → Python
- `Gemfile` → Ruby

Como temos ambos no repositório (backend e frontend), o deploy manual garante que o Render use a configuração correta.
