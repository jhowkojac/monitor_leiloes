# Frontend React - Monitor de Leilões

Frontend moderno em React + TypeScript + Tailwind CSS para o Monitor de Leilões.

## 🚀 Tecnologias

- ⚛️ **React 18** - Component-based UI
- 🎨 **TypeScript** - Type safety
- 🎭 **Tailwind CSS** - Design system moderno
- ⚡ **Vite** - Build ultra rápido
- 🎬 **Framer Motion** - Animações suaves
- 🎯 **Lucide React** - Ícones modernos

## 📁 Estrutura

```
frontend/
├── src/
│   ├── components/          # Componentes React
│   │   ├── Header.tsx      # Cabeçalho com navegação
│   │   ├── HeroSection.tsx # Hero com stats
│   │   ├── FilterSection.tsx # Filtros avançados
│   │   ├── AuctionCard.tsx # Card de leilão
│   │   └── AuctionGrid.tsx # Grid com toggle
│   ├── services/
│   │   └── api.ts          # Serviço de API
│   ├── App.tsx             # Componente principal
│   ├── main.tsx            # Entry point
│   └── index.css           # Design system
├── package.json            # Dependências
├── tailwind.config.ts      # Configuração Tailwind
├── vite.config.ts          # Configuração Vite
└── tsconfig.json           # Configuração TypeScript
```

## 🛠️ Instalação

### Pré-requisitos
- Node.js 18+
- npm ou yarn

### Passos

1. **Instalar dependências**
```bash
cd frontend
npm install
```

2. **Iniciar desenvolvimento**
```bash
npm run dev
```

3. **Build para produção**
```bash
npm run build
```

4. **Preview do build**
```bash
npm run preview
```

## 🔗 Integração com API

O frontend está configurado para consumir a API FastAPI existente:

### Endpoints
- `GET /api/leiloes` - Lista todos os leilões
- `GET /api/leiloes/:id` - Detalhes do leilão
- `GET /api/leiloes/filter` - Filtragem avançada
- `GET /api/leiloes/atualizar` - Atualizar dados

### Configuração
A URL base da API é configurada automaticamente:
- **Desenvolvimento**: `http://localhost:8000/api`
- **Produção**: `https://monitor-leiloes.onrender.com/api`

## 🎨 Design System

### Cores
- **Primary**: Gold (#fbbf24) - Amarelo dourado
- **Background**: Dark theme (#0f0f12)
- **Cards**: Glass morphism com blur
- **Text**: High contrast para acessibilidade

### Fontes
- **Inter**: Textos e parágrafos
- **Space Grotesk**: Títulos e headers

### Utilitários
- `.text-gradient-gold` - Texto com gradiente dourado
- `.bg-gradient-gold` - Fundo com gradiente dourado
- `.glass` - Efeito glass morphism
- `.shadow-gold` - Sombra dourada

## 📱 Features

### ✅ Implementadas
- Header responsivo com navegação
- Hero section com estatísticas animadas
- Filtros avançados com toggle
- Grid/List toggle para visualização
- Cards de leilão com carrossel
- Integração completa com API
- Loading states e empty states
- Design 100% responsivo

### 🔄 Em desenvolvimento
- Paginação
- Ordenação
- Detalhes do leilão
- Favoritos
- Notificações

## 🚀 Deploy

### Render
O frontend pode ser deployado no Render como um serviço estático:

1. Fazer upload da pasta `frontend`
2. Configurar build command: `npm run build`
3. Configurar publish directory: `dist`
4. Adicionar variáveis de ambiente se necessário

### Outras plataformas
- **Vercel**: Ideal para React apps
- **Netlify**: Fácil deploy com GitHub
- **AWS S3 + CloudFront**: Para alta escala

## 🔧 Desenvolvimento

### Comandos úteis
```bash
# Instalar nova dependência
npm install nome-do-pacote

# Instalar dependência de desenvolvimento
npm install -D nome-do-pacote

# Executar testes
npm run test

# Lint do código
npm run lint

# Formatar código
npm run format
```

### Estrutura de componentes
Cada componente segue a estrutura:
```typescript
interface Props {
  // Props tipadas
}

export function ComponentName({ ...props }: Props) {
  // Lógica do componente
  return (
    // JSX com Tailwind classes
  );
}
```

## 🎯 Performance

### Otimizações
- **Code splitting**: Lazy loading de componentes
- **Images**: Otimização com lazy loading
- **Animations**: GPU accelerated com Framer Motion
- **Bundle**: Minificação e tree shaking

### Métricas
- **Lighthouse**: 90+ performance
- **Bundle size**: <500KB gzipped
- **FCP**: <1.5s
- **TTI**: <2s

## 🐛 Troubleshooting

### Problemas comuns

**Node.js não encontrado**
```bash
# Instalar Node.js
winget install OpenJS.NodeJS
```

**Dependências não instaladas**
```bash
# Limpar cache e reinstalar
npm cache clean --force
rm -rf node_modules package-lock.json
npm install
```

**Erro de TypeScript**
```bash
# Verificar tipos
npm run type-check
```

**API não responde**
```bash
# Verificar se backend está rodando
curl http://localhost:8000/api/leiloes
```

## 🤝 Contribuição

1. Fork do projeto
2. Criar branch feature: `git checkout -b feature/nova-feature`
3. Commit: `git commit -m "Add nova feature"`
4. Push: `git push origin feature/nova-feature`
5. Pull request

## 📄 Licença

MIT License - ver arquivo LICENSE para detalhes.
