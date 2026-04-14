# Reference Checklist

## Stack preferencial

### Frontend
- React 18+ com TypeScript strict
- Next.js 14+ (App Router, SSR/SSG/ISR)
- Tailwind + shadcn/ui
- Zustand para estado global
- Zod para validacao de schema

### Backend
- Python 3.11+ com FastAPI + Pydantic v2
- SQLAlchemy 2.0 + Alembic
- PostgreSQL (producao) / SQLite (dev)
- JWT (preferencia RS256) + OAuth2
- Celery + Redis para assinc

### Desktop e DevOps
- Tauri 2.x (Rust + React)
- Docker + Docker Compose
- GitHub Actions (lint/test/SAST/deploy)
- Railway/Vercel para deploy

## Checklist de qualidade

- [ ] Implementacao funcional e testavel (sem placeholders)
- [ ] Type safety em toda superficie publica
- [ ] Sem magic strings em regras centrais
- [ ] DRY/SOLID respeitados
- [ ] Tratamento de erro em fluxos assincronos
- [ ] Docstrings em funcoes publicas (Python)
- [ ] Arquitetura por camadas:
  - FastAPI: routes -> services -> repositories
  - Next.js: pages -> hooks -> api

## Checklist de seguranca (OWASP)

- [ ] Injection: apenas ORM/query parametrizada
- [ ] Broken Auth: expiracao e estrategia de refresh/revogacao
- [ ] XSS: sanitizacao + headers adequados
- [ ] IDOR: validacao de ownership
- [ ] SSRF: allowlist de dominios externos
- [ ] Segredos fora do codigo e do git
- [ ] CORS restritivo (sem wildcard perigoso)
- [ ] Rate limiting em endpoints publicos
- [ ] Logs sem PII/tokens/senhas
- [ ] Upload com validacao de MIME e tamanho

## Guardrails de API

- [ ] FastAPI endpoint com `response_model` e `status_code`
- [ ] Validacao de entrada/saida consistente
- [ ] Erros tipados e centralizados
- [ ] Variaveis de ambiente validadas no startup
- [ ] Migracoes versionadas via Alembic

## Guardrails de frontend

- [ ] Componentes React com props tipadas via `interface`
- [ ] Evitar `any` e coercao insegura
- [ ] Error boundaries para falhas de renderizacao

## Guardrails de DevOps

- [ ] Dockerfile com imagem base atualizada
- [ ] Build multi-stage quando aplicavel
- [ ] Container rodando como usuario nao-root
- [ ] Pipeline CI com lint + test + SAST
- [ ] Secrets no provedor (GitHub/Railway/Vercel), nunca no repo

## Proibicoes

- `eval()`/`exec()` com input externo
- `pickle` em dados nao confiaveis
- Expor stack traces em producao
- Hash de senha com MD5/SHA1
- Commit de `.env`, tokens, chaves privadas
- `SELECT *` em queries criticas de producao
- `verify=False` em requests TLS
- `allow_origins=["*"]` com `allow_credentials=True`
