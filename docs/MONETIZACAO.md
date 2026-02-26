# Estratégia de Monetização – MedQuestResearch

## 1. Visão geral

O MedQuestResearch monetiza por **créditos**: cada ação (explicar, análise crítica, metanálise, etc.) consome créditos. A estratégia combina **planos recorrentes** (assinatura) e **pacotes avulsos** de créditos.

---

## 2. Custos atuais por módulo (créditos)

| Módulo | Créditos | Uso típico |
|--------|----------|------------|
| Upload PDF/DOCX | 3 | Por arquivo |
| Explicar conteúdo | 5 | Por análise |
| Verificar fatos | 5 | Por análise |
| Mapear estrutura | 6 | Por análise |
| Análise crítica | 7 | Por análise |
| Visualizar estrutura | 8 | Por análise |
| Perspectivas científicas | 10 | Por análise |
| Metanálise (etapa) | 12 | Por etapa/job |
| **Upload + análise PRISMA (por artigo)** | **3 + 12 = 15** | Por artigo na metanálise |

*Valores configuráveis via `CREDIT_COST_<MODULO>` no `.env` (backend).*

---

## 3. Conversão créditos ↔ R$

Sugestão de referência (ajustável):

| Métrica | Valor sugerido |
|---------|----------------|
| **1 crédito** | R$ 0,15 a R$ 0,25 |
| **100 créditos** | R$ 15,00 a R$ 25,00 |
| **Custo por “análise média”** | ~7 créditos ≈ R$ 1,05 a R$ 1,75 |

Objetivo: manter preço por uso **abaixo de alternativas** (tempo do pesquisador, ferramentas pagas por documento), com margem para custos de API (OpenRouter, etc.) e lucro.

---

## 4. Planos sugeridos

### 4.1 Plano Gratuito (triagem / teste)

| Item | Valor |
|------|--------|
| Créditos iniciais | 20–30 (uma vez no cadastro) |
| Recarga | Nenhuma |
| Objetivo | Conhecer a ferramenta; limitado a 1–2 análises completas |

### 4.2 Plano Básico (estudante / uso leve)

| Item | Valor |
|------|--------|
| Preço | R$ 29,90/mês |
| Créditos/mês | 200 |
| Equivalente | ~R$ 0,15/crédito |
| Uso típico | 2–3 artigos por semana (explicar, fatos, crítica leve) |

### 4.3 Plano Pesquisador (uso intenso)

| Item | Valor |
|------|--------|
| Preço | R$ 79,90/mês |
| Créditos/mês | 600 |
| Equivalente | ~R$ 0,13/crédito |
| Bônus | +10% de créditos (60 extras) = 660/mês |
| Uso típico | Metanálise, múltiplos artigos, todas as ferramentas |

### 4.4 Plano Laboratório / Grupo (equipe)

| Item | Valor |
|------|--------|
| Preço | R$ 199,90/mês |
| Créditos/mês | 1.800 |
| Equivalente | ~R$ 0,11/crédito |
| Bônus | +15% (270 extras) = 2.070/mês |
| Usuários | Até 5 contas (ou “créditos compartilhados” – ver seção 7) |

### 4.5 Pacotes avulsos (sem assinatura)

| Pacote | Créditos | Preço sugerido | Preço/crédito |
|--------|----------|----------------|---------------|
| Pequeno | 50 | R$ 9,90 | R$ 0,20 |
| Médio | 150 | R$ 24,90 | R$ 0,17 |
| Grande | 400 | R$ 59,90 | R$ 0,15 |
| Metanálise | 200 | R$ 39,90 | Focado em 1 metanálise (~15 artigos) |

---

## 5. Regras de negócio (implementação)

1. **Créditos disponíveis** = `creditos - creditos_usados` (já implementado).
2. **Novos usuários:** ao cadastrar, conceder X créditos iniciais (ex.: 25) – configurável.
3. **Renovação mensal (planos):** no início de cada ciclo, definir `creditos += creditos_do_plano` (e opcionalmente zerar ou não `creditos_usados` conforme regra).
4. **Pacotes avulsos:** ao comprar, `creditos += N`.
5. **Sem créditos:** retornar 402 e mensagem “Créditos insuficientes. Compre mais ou assine um plano.” (já existe fluxo de débito).

---

## 6. Gateway de pagamento e integração

- **Recomendação:** Stripe (internacional) e/ou **Mercado Pago** (Brasil).
- **Fluxo sugerido:**
  1. Frontend: página “Planos” e “Comprar créditos” com botão “Assinar” / “Comprar”.
  2. Backend: criar sessão de checkout (Stripe Checkout ou Mercado Pago preference) com `metadata`: `user_id`, `plano_id` ou `pacote_id`, `creditos`.
  3. Webhook: ao receber pagamento aprovado, chamar `adicionar_creditos_usuario(user_id, creditos)` e (se assinatura) registrar `plano_ativo` e data de renovação.
- **Segurança:** validar assinaturas dos webhooks; não confiar apenas em parâmetros da URL.

---

## 7. Próximos passos técnicos

| Prioridade | Tarefa |
|------------|--------|
| 1 | Definir tabela `planos` (id, nome, creditos_mes, preco_centavos, recorrente) e `pacotes` (id, nome, creditos, preco_centavos). |
| 2 | Endpoint `GET /planos` e `GET /pacotes` para o frontend exibir preços. |
| 3 | Página “Planos e preços” no app (tabela de planos + pacotes avulsos). |
| 4 | Integrar gateway (Stripe ou Mercado Pago): checkout + webhook para creditar. |
| 5 | Créditos iniciais no cadastro (variável de ambiente ou valor fixo na criação do usuário). |
| 6 | (Opcional) Cron para renovação mensal de assinaturas (recarga de créditos). |

---

## 8. Métricas sugeridas

- Receita mensal (MRR) por plano.
- Créditos consumidos por usuário/mês.
- Conversão: cadastro → primeira compra/assinatura.
- Custo médio de API por crédito (OpenRouter, etc.) para validar margem.

---

*Documento criado para alinhar produto e desenvolvimento. Ajuste preços e créditos conforme custos reais e posicionamento de mercado.*
