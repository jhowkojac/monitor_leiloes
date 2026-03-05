# Monitor de Leilões de Veículos (MG e SP)

Aplicação web em **FastAPI** para monitorar leilões de veículos com foco em **Minas Gerais** e **São Paulo**.

## Funcionalidades

- Listagem de leilões de múltiplas fontes (Detran MG, Detran SP, Superbid)
- Filtros por estado (MG/SP), fonte e cidade
- Atualização manual da lista (busca nas fontes)
- API REST para integração
- **Carrossel de imagens** com navegação suave
- **Pop-up modal** para visualização em alta resolução
- **Interface profissional** e moderna
- **Busca otimizada** de veículos
- **Monitoramento em tempo real** do Detran MG

## Como rodar

**Requisito:** Use **Python 3.10, 3.11, 3.12 ou 3.13**. Python 3.14 ainda não é suportado pelo Pydantic (não há wheels; a instalação falha ao compilar `pydantic-core`). Se você só tiver 3.14, instale o Python 3.12 pelo [site oficial](https://www.python.org/downloads/) ou pela Microsoft Store.

### 1. Criar ambiente virtual (recomendado)

```bash
cd monitor_leiloes
python -m venv venv
venv\Scripts\activate
```

### 2. Instalar dependências

```bash
pip install -r requirements.txt
```

### 3. Subir o servidor

```bash
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Acesse: **http://localhost:8000**

- Página inicial: listagem de leilões e filtros
- API: `GET /api/leiloes` (query params: `estado`, `fonte`, `cidade`)
- Atualizar cache: `GET /api/leiloes/atualizar`
- Documentação: http://localhost:8000/docs

## Estrutura do projeto

```
monitor_leiloes/
├── main.py              # App FastAPI e lifespan
├── requirements.txt
├── app/
│   ├── __init__.py
│   ├── models.py        # Modelos (VeiculoLeilao, Estado, FonteLeilao)
│   ├── servico.py       # Cache e agregação das fontes
│   ├── routers.py       # Rotas web e API
│   ├── fontes/          # Fontes de dados (Detran MG/SP, Superbid)
│   │   ├── base.py
│   │   ├── mock_mg_sp.py # Dados de exemplo (substituir por scrapers reais)
│   │   └── __init__.py
│   └── templates/
│       └── index.html   # Página principal
```

## Dados atuais

Os leilões exibidos são **dados de exemplo** (mock) para demonstrar a interface e os filtros. Para usar dados reais:

1. Implemente classes em `app/fontes/` que herdem de `FonteLeilaoBase`.
2. Cada fonte deve implementar `listar_leiloes()` retornando uma lista de `VeiculoLeilao`.
3. Registre a nova fonte em `app/servico.py` na lista `_fontes`.

Ao implementar scrapers, respeite os termos de uso dos sites e evite sobrecarregar os servidores (rate limiting, cache).

## Requisitos

- Python 3.10 a 3.13
- FastAPI, Uvicorn, Jinja2 (ver `requirements.txt`)

### Erro ao instalar (pydantic-core / Rust)

Se aparecer erro ao rodar `pip install -r requirements.txt` relacionado a `pydantic-core` ou Rust, use um ambiente com **Python 3.11 ou 3.12**:

1. Instale o Python 3.12 em https://www.python.org/downloads/ (marque "Add to PATH").
2. Crie o venv com esse Python: `py -3.12 -m venv venv` (ou `python3.12 -m venv venv`).
3. Ative e instale: `venv\Scripts\activate` e `pip install -r requirements.txt`.

## 🛠️ Pré-requisitos para Colaboradores
Para rodar este projeto em Windows (especialmente no Python 3.14), precisas de:
1. **Visual Studio Community 2022**: Com a carga de trabalho "Desenvolvimento para desktop com C++" instalada.
2. **Rust**: Necessário para compilar o `pydantic-core`.
3. **Python 3.14+**.
