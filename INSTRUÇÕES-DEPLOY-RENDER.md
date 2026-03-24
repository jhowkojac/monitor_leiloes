# 🚀 Deploy do Frontend React no Render (Projeto Existente)

## 📋 Situação Atual

- ✅ Backend já rodando em: https://monitor-leiloes.onrender.com
- ✅ Frontend React criado na pasta `frontend/`
- ✅ Configuração CORS atualizada
- ✅ Commit enviado para o GitHub

## 🎯 Objetivo

Atualizar o serviço **monitor-leiloes** no Render para:
- Servir o frontend React em vez dos templates Jinja2
- Manter a API FastAPI funcionando
- Configurar routing correto para SPA

## 🛠️ Passos para Atualizar no Render

### 1. Acessar Dashboard Render
1. Ir para: https://dashboard.render.com
2. Selecionar serviço: **monitor-leiloes**
3. Ir para aba **Settings**

### 2. Atualizar Configuração do Serviço
Na seção **Build & Deploy**:

#### Mudanças necessárias:
```
Type: Static Site (em vez de Web Service)

Build Command:
cd frontend && npm install && npm run build

Publish Directory:
frontend/dist

Environment Variables:
NODE_ENV = production
```

### 3. Configurar Rotas (Importante!)
Na seção **Advanced → Custom Routes**:

```
# 1. API routes - manter backend funcionando
Type: Rewrite
Source: /api/*
Destination: /api/:splat

# 2. SPA routing - frontend React
Type: File
Source: /**
Destination: /index.html
```

### 4. Configurar Headers
Na seção **Advanced → Custom Headers**:

```
Path: /*
Name: Cache-Control
Value: no-cache, no-store, must-revalidate

Path: /*
Name: Pragma
Value: no-cache

Path: /*
Name: Expires
Value: 0
```

## 🎯 Alternativa: Criar Novo Serviço

Se preferir manter o backend separado:

### 1. Renomear Serviço Atual
- Vá em Settings → General
- Mude o nome para: **monitor-leiloes-backend**

### 2. Criar Novo Serviço Frontend
- **New +** → **Static Site**
- Name: **monitor-leiloes**
- Build Command: `cd frontend && npm install && npm run build`
- Publish Directory: `frontend/dist`
- Conectar ao mesmo repositório GitHub

## 🔧 Configuração do Backend (se separado)

Se criar serviços separados, atualizar CORS no backend:

```python
# No main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://monitor-leiloes.onrender.com",  # Frontend
        "https://monitor-leiloes-backend.onrender.com",  # Backend (se necessário)
        "http://localhost:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## 📱 Estrutura Final Esperada

### URL Final:
- **Frontend**: https://monitor-leiloes.onrender.com
- **API**: https://monitor-leiloes.onrender.com/api/*

### Funcionamento:
1. Usuário acessa https://monitor-leiloes.onrender.com
2. Vê o frontend React moderno
3. Filtros e dados funcionam via API
4. SPA routing funciona corretamente

## 🧪 Testes Pós-Deploy

### Checklist:
- [ ] Página carrega com frontend React
- [ ] Header e navegação funcionam
- [ ] Hero section aparece
- [ ] Filtros funcionam
- [ ] Grid/List toggle funciona
- [ ] Cards carregam dados da API
- [ ] API endpoints respondem
- [ ] SPA routing funciona
- [ ] Mobile responsivo

### Teste de API:
```bash
# Testar se API ainda funciona
curl https://monitor-leiloes.onrender.com/api/leiloes

# Testar CORS
curl -H "Origin: https://monitor-leiloes.onrender.com" \
     https://monitor-leiloes.onrender.com/api/leiloes
```

## 🚀 Deploy Automático

Após configurar, toda vez que fizer push para o main:
1. Render detecta mudanças
2. Roda `cd frontend && npm install && npm run build`
3. Publica arquivos da pasta `frontend/dist`
4. Frontend atualizado automaticamente

## 🔧 Troubleshooting

### Erro 404 nas rotas
- **Problema**: SPA routing não configurado
- **Solução**: Adicionar rota `/** → /index.html`

### API não responde
- **Problema**: Rotas de API não configuradas
- **Solução**: Adicionar rewrite `/api/* → /api/:splat`

### CORS error
- **Problema**: Frontend não autorizado
- **Solução**: Atualizar middleware CORS no backend

### Build falha
- **Problema**: Dependências não instaladas
- **Solução**: Verificar build command e node_modules

## 🎆 Resultado Final

Após configuração:
- 🎨 Frontend React moderno em produção
- 📱 100% responsivo e funcional
- 🔗 API integrada funcionando
- ⚡ Deploy automático via Git
- 🌐 URL única para frontend + API

**Monitor de Leilões com frontend moderno pronto!** 🎉
