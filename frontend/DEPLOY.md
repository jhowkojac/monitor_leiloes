# 🚀 Deploy para Produção - Frontend React

## 📋 Pré-requisitos

- ✅ Build do frontend gerado
- ✅ Backend FastAPI rodando em produção
- ✅ Configuração de CORS no backend

## 🏗️ Passo 1: Gerar Build

### Opção A: Script Automático
```bash
# Executar script de build
.\build.bat
```

### Opção B: Manual
```bash
# Configurar PATH
set PATH=%PATH%;C:\Program Files\nodejs

# Build para produção
npm run build

# Testar localmente
npm run preview
```

## 🌐 Opções de Deploy

### 1. Render (Recomendado)

#### Criar Novo Serviço
1. Acessar [dashboard.render.com](https://dashboard.render.com)
2. **New +** → **Static Site**
3. **Name**: `monitor-leiloes-frontend`
4. **Build Command**: `npm run build`
5. **Publish Directory**: `dist`
6. **Branch**: `main`
7. **Advanced Settings** → **Add Custom Domain** (opcional)

#### Upload dos Arquivos
```bash
# Fazer upload da pasta frontend
git add frontend/
git commit -m "feat: Add React frontend for production"
git push origin main
```

#### Configuração de Rotas
- O arquivo `render.yaml` já está configurado
- Redireciona `/api/*` para o backend
- SPA routing configurado

### 2. Vercel

#### Deploy via CLI
```bash
# Instalar Vercel CLI
npm i -g vercel

# Fazer deploy
vercel --prod
```

#### Deploy via Dashboard
1. Acessar [vercel.com](https://vercel.com)
2. **Import Project** → **Git Repository**
3. Selecionar repositório `monitor_leiloes`
4. **Root Directory**: `frontend`
5. **Build Command**: `npm run build`
6. **Output Directory**: `dist`
7. **Deploy**

### 3. Netlify

#### Deploy via Drag & Drop
1. Gerar build: `npm run build`
2. Arrastar pasta `dist/` para [netlify.com](https://netlify.com)
3. Configurar domínio se necessário

#### Deploy via CLI
```bash
# Instalar Netlify CLI
npm i -g netlify-cli

# Fazer deploy
netlify deploy --prod --dir=dist
```

## 🔧 Configuração de CORS (Backend)

### FastAPI - Adicionar ao main.py
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://monitor-leiloes-frontend.onrender.com",
        "https://monitor-leiloes-frontend.vercel.app",
        "https://monitor-leiloes-frontend.netlify.app",
        "http://localhost:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## 📊 URLs de Produção

### Render
- **Frontend**: `https://monitor-leiloes-frontend.onrender.com`
- **Backend**: `https://monitor-leiloes.onrender.com`

### Vercel
- **Frontend**: `https://monitor-leiloes-frontend.vercel.app`
- **Backend**: `https://monitor-leiloes.onrender.com`

### Netlify
- **Frontend**: `https://monitor-leiloes-frontend.netlify.app`
- **Backend**: `https://monitor-leiloes.onrender.com`

## 🔄 Atualizações Automáticas

### GitHub Actions (Opcional)
```yaml
# .github/workflows/deploy.yml
name: Deploy Frontend
on:
  push:
    branches: [main]
    paths: [frontend/**]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Setup Node.js
        uses: actions/setup-node@v2
        with:
          node-version: '18'
      - name: Install dependencies
        run: |
          cd frontend
          npm ci
      - name: Build
        run: |
          cd frontend
          npm run build
      - name: Deploy to Render
        run: |
          # Deploy commands aqui
```

## 🧪 Testes Pós-Deploy

### Checklist de Verificação
- [ ] Carrega a página inicial
- [ ] Header e navegação funcionam
- [ ] Hero section com stats aparece
- [ ] Filtros funcionam corretamente
- [ ] Grid/List toggle funciona
- [ ] Cards carregam com dados da API
- [ ] Carrossel de imagens funciona
- [ ] Responsivo no mobile
- [ ] API responde corretamente
- [ ] CORS configurado corretamente

### Teste de API
```bash
# Testar endpoint
curl https://monitor-leiloes.onrender.com/api/leiloes

# Testar CORS
curl -H "Origin: https://seu-frontend.com" \
     https://monitor-leiloes.onrender.com/api/leiloes
```

## 🔧 Troubleshooting

### Erros Comuns

#### CORS Error
```
Solução: Adicionar origem do frontend no middleware CORS do backend
```

#### 404 nas Rotas
```
Solução: Verificar configuração de SPA routing na plataforma de deploy
```

#### Build Falha
```
Solução: Verificar se todas as dependências estão instaladas
npm install
npm run build
```

#### API Não Responde
```
Solução: Verificar se backend está rodando e CORS configurado
```

## 📈 Performance

### Otimizações Aplicadas
- ✅ Code splitting automático
- ✅ Lazy loading de componentes
- ✅ Imagens otimizadas
- ✅ Bundle minificado
- ✅ Cache headers configurados

### Métricas Esperadas
- **Performance**: 90+
- **Accessibility**: 95+
- **Best Practices**: 90+
- **SEO**: 85+

## 🎆 Deploy Concluído!

Após seguir esses passos, seu frontend React estará em produção com:
- 🎨 Design moderno e profissional
- 📱 Totalmente responsivo
- 🔗 Integração completa com API FastAPI
- ⚡ Performance otimizada
- 🔄 Deploy automático via Git
