# 🚀 GUIA RÁPIDO: PUBLICAR EM DOMÍNIO PÚBLICO

## 🎯 ETAPA 1: O MÍNIMO PARA PUBLICAR (1-2 dias)

### ✅ O QUE PRECISA AGORA:
1. **Servidor cloud** (Vercel - grátis e fácil)
2. **HTTPS automático** (vem com Vercel)
3. **Configurar variáveis de ambiente**
4. **Fazer deploy**

---

## 🌐 OPÇÃO 1: VERCEL (RECOMENDADO - GRÁTIS)

### Passo 1: Preparar para Vercel
```bash
# 1. Criar vercel.json na raiz
{
  "version": 2,
  "builds": [
    {
      "src": "main.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "main.py"
    }
  ],
  "env": {
    "ENVIRONMENT": "production"
  }
}

# 2. Criar requirements.txt (já existe)
# 3. Criar .env.local (não commitar)
API_TOKEN=seu_token_super_secreto_aqui_2024
RATE_LIMIT_CALLS=100
```

### Passo 2: Deploy no Vercel
```bash
# 1. Instalar Vercel CLI
npm i -g vercel

# 2. Fazer login
vercel login

# 3. Deploy
vercel --prod
```

### Passo 3: Configurar Domínio
```bash
# No dashboard Vercel:
# 1. Settings → Domains
# 2. Adicionar seu domínio (ex: monitorleiloes.com)
# 3. Configurar DNS (Vercel fornece os registros)
```

---

## 🔧 ETAPA 2: AJUSTES MÍNIMOS DE PRODUÇÃO

### 1. Variáveis de Ambiente
```python
# Em .env.local (NÃO commitar)
ENVIRONMENT=production
API_TOKEN=change_this_super_secret_token_2024
RATE_LIMIT_CALLS=50  # Mais conservador em prod
```

### 2. Ajustar main.py para produção
```python
# Adicionar no main.py
import os

# No início do arquivo
if os.getenv("ENVIRONMENT") == "production":
    # Configurações de produção
    print("🚀 MODO PRODUÇÃO ATIVADO")
```

### 3. Verificar se funciona localmente
```bash
# Testar em modo produção
ENVIRONMENT=production python main.py
```

---

## 📋 CHECKLIST MÍNIMA

### ✅ ANTES DO DEPLOY:
- [ ] App funciona localmente
- [ ] Todos os testes passam
- [ ] .env.local configurado
- [ ] vercel.json criado

### ✅ DEPLOY:
- [ ] Conta Vercel criada
- [ ] Projeto deployado
- [ ] HTTPS funcionando
- [ ] Domínio configurado

### ✅ PÓS-DEPLOY:
- [ ] Site acessível via domínio
- [ ] API endpoints funcionando
- [ ] Rate limiting ativo
- [ ] Logs de erros funcionando

---

## 🆘 SE DER ERRADO:

### Problema 1: Build falha
```bash
# Verificar requirements.txt
pip install -r requirements.txt
python main.py  # Testar local
```

### Problema 2: API não responde
```bash
# Verificar logs no Vercel Dashboard
# Testar endpoints:
curl https://seu-dominio.com/api/leiloes
```

### Problema 3: Rate limiting muito restrito
```bash
# Ajustar no dashboard Vercel:
# Settings → Environment Variables
# RATE_LIMIT_CALLS=200
```

---

## 📈 CUSTO REAL:

### Vercel (Plano Hobby):
- **Grátis**: 100GB bandwidth/mês
- **Pro**: $20/mês (ilimitado)
- **Domínio**: $15/ano (separado)

### Total inicial: **$15/ano** (domínio apenas)

---

## 🎯 PLANO DE AÇÃO (HOJE):

### 🕐 MANHÃ (30 min):
1. Criar conta Vercel
2. Instalar Vercel CLI
3. Criar vercel.json

### 🕐 TARDE (30 min):
1. Configurar .env.local
2. Fazer primeiro deploy
3. Testar no domínio vercel.app

### 🕐 NOITE (30 min):
1. Configurar domínio próprio
2. Ajustar DNS
3. Testes finais

---

## 🚀 COMEÇAR AGORA:

```bash
# 1. Criar arquivo vercel.json
cat > vercel.json << 'EOF'
{
  "version": 2,
  "builds": [
    {
      "src": "main.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "main.py"
    }
  ]
}
EOF

# 2. Criar .env.local
echo "ENVIRONMENT=production" > .env.local
echo "API_TOKEN=super_secure_token_2024" >> .env.local

# 3. Instalar Vercel
npm i -g vercel

# 4. Fazer deploy
vercel --prod
```

---

## 🎯 RESULTADO ESPERADO:

### ✅ Após 2-3 horas:
- **Site publicado** em https://monitorleiloes.vercel.app
- **HTTPS automático** funcionando
- **API endpoints** operacionais
- **Rate limiting** ativo
- **Logs básicos** funcionando

### ✅ Após 1 dia:
- **Domínio próprio** configurado
- **Email profissional** (contato@monitorleiloes.com)
- **Google Analytics** instalado
- **Monitoramento básico** ativo

---

## 🤔 AINDA EM DÚVIDA?

### **Vercel vs Outros:**
- **Vercel**: Mais fácil, grátis para começar
- **Railway**: Similar ao Vercel
- **DigitalOcean**: Mais controle, mas complexo

### **Recomendação:**
Comece com **Vercel grátis**. Quando o site crescer, migre para plano pago ou outro hosting.

---

## 🚀 VAMOS COMEÇAR?

Qual desses passos você quer que eu implemente agora:
1. **Criar vercel.json** e configurar para deploy
2. **Ajustar o código** para produção
3. **Fazer deploy** no Vercel
4. **Configurar domínio** próprio

**Qualquer um desses já coloca o site no ar!** 🎯
