# Backend - MedQuest Research API

Backend Python (Flask) para o MedQuestResearch.

## 📁 Estrutura

```
backend/
├── api.py                 # Aplicação Flask principal
├── database.py            # Configuração do banco de dados
├── gpt_engine.py          # Engine de IA (OpenAI)
├── pdf_processor.py       # Processamento de PDFs
├── critical_analysis.py   # Análise crítica
├── Fact_checker.py        # Verificação de fatos
├── explain_concept.py     # Explicação de conceitos
├── Perspective_research.py # Pesquisa de perspectivas
├── structure_visualizer.py # Visualização de estrutura
├── structure_mapper.py    # Mapeamento de estrutura
├── chunker.py            # Chunking de texto
├── requirements.txt      # Dependências Python
└── wsgi.py               # WSGI para PythonAnywhere (não versionado)
```

## 🚀 Instalação

```bash
pip install -r requirements.txt
```

## 🛠️ Desenvolvimento

```bash
python api.py
```

O servidor estará disponível em `http://localhost:5000`

## 🚀 Deploy no Render

Siga o guia em `../DEPLOY_RENDER.md` ou `README_RENDER.md`

## ⚙️ Variáveis de Ambiente

Configure no Render:
- `DB_HOST`, `DB_USER`, `DB_PASSWORD`, `DB_NAME`
- `API_OPENAI_KEY_RESEARCH`
- `RESEARCH_API_KEY`
- `OPENAI_MODEL` (padrão: gpt-4o-mini)
- `FLASK_ENV` (production)

## 📝 Documentação

- `API_CONFIG.md` - Documentação completa da API
- `README_RENDER.md` - Guia de deploy no Render
- `DEPLOY_RENDER.md` - Guia rápido de deploy

