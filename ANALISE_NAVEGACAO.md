# Análise de Navegação e Amarrações de Páginas

## 📊 Problemas Identificados

### 1. ❌ Frontend e Backend Desconectados

**Frontend (React) está em outro domínio:**
- Frontend: Vercel/Netlify (separado)
- Backend: Render (https://monitor-leiloes.onrender.com)
- Não há comunicação entre eles

**Problema no AuctionCard.tsx:**
```tsx
<a
  href="#"  // ❌ Link morto - não navega para lugar nenhum
  className="..."
>
  Ver detalhes
</a>
```

### 2. ❌ IDs Inconsistentes Entre Frontend e Backend

**Backend gera IDs assim:**
- Editais: `detran_mg_edital_3452_2026_0`
- Veículos/Lotes: `detran_mg_edital_3452_2026_lote_1`

**Frontend parece usar IDs diferentes:**
- Não há passagem de ID do card para o link
- Card não tem `id` prop para passar para o link

### 3. ❌ Rotas do Backend Não Usadas pelo Frontend

**Rotas disponíveis no backend:**
- `/` - Página principal (index.html) ✅
- `/editais/{id}` - Página de detalhes do edital ✅
- `/veiculos/{veiculo_id}` - Página de detalhes do veículo ✅
- `/lote/{lote_id}` - Página de detalhes do lote ✅
- `/login` - Página de login ✅
- `/dashboard` - Dashboard administrativo ✅
- `/api/leiloes` - API JSON ✅
- `/api/leiloes/atualizar` - API para atualizar ✅

**Problema:** Frontend React não chama nenhuma dessas rotas!

### 4. ❌ API JSON Não Está Sendo Consumida

**Backend tem API JSON:**
```python
@router.get("/api/leiloes")
async def api_listar_leiloes(...)
    return {"total": len(itens), "leiloes": itens}
```

**Frontend React não usa essa API - usa dados mockados!**

## 🔧 Soluções Necessárias

### Opção A: Usar Apenas Backend (Recomendado)

**Vantagens:**
- Simplicidade - um único domínio
- IDs consistentes
- Menos latência
- Já funcionando no Render

**Ações:**
1. Converter frontend React para templates Jinja2
2. Remover frontend React do projeto
3. Usar apenas o backend com templates

### Opção B: Integrar Frontend React com Backend

**Ações:**
1. Configurar React para consumir API do backend
2. Substituir dados mockados por chamadas reais à API
3. Atualizar links no frontend para usar URLs do backend
4. Configurar CORS corretamente (já está configurado)
5. Deploy do frontend em Vercel/Netlify apontando para backend

## 📝 Fluxo de Navegação Atual (Backend)

```
Usuário acessa: https://monitor-leiloes.onrender.com/
    ↓
Rota: GET / (index.html)
    ↓
Renderiza: Lista de 10 editais
    ↓
Usuário clica em edital
    ↓
Rota: GET /editais/detran_mg_edital_3452_2026_0
    ↓
Busca veículos do edital
    ↓
Renderiza: Página com lista de veículos
    ↓
Usuário clica em veículo/lote
    ↓
Rota: GET /lote/detran_mg_edital_3452_2026_lote_1
    ↓
Busca detalhes do lote + FIPE
    ↓
Renderiza: Página de detalhes
```

## 🐛 Problemas de IDs (Backend)

**Formato de IDs:**
- Editais: `detran_mg_edital_{codigo}_{count}`
  - Ex: `detran_mg_edital_3452_2026_0`
- Veículos: `detran_mg_edital_{edital_id}_lote_{lote_numero}`
  - Ex: `detran_mg_edital_3452_2026_lote_1`

**Workaround implementado:**
- Se ID termina com `_lote` (sem número), usa primeiro lote do edital
- Isso corrige links que não incluem o número

## 🎯 Recomendação

**Usar apenas o backend com templates** porque:
1. ✅ Já está funcionando no Render
2. ✅ Navegação está implementada
3. ✅ IDs são consistentes
4. ✅ Menos complexidade de manutenção
5. ✅ Não precisa de CORS entre domínios

Se quiser continuar com frontend React, precisa:
1. Fazer API calls reais para `/api/leiloes`
2. Configurar URLs corretas nos links
3. Sincronizar geração de IDs
