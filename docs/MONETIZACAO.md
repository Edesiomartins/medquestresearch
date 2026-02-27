# Estratégia de Monetização – MedQuestResearch

## 1. Visão geral

O MedQuestResearch monetiza **apenas pela compra de créditos**. Não há planos de assinatura: o usuário compra o pacote de créditos que quiser e usa quando precisar.

---

## 2. Preço e bônus

| Regra | Valor |
|-------|--------|
| **Preço** | **R$ 0,25 por crédito** |
| **Bônus** | Compras **acima de 300 créditos** ganham **+20%** de créditos grátis |

### Fórmula

```text
valor = quantidade * PRECO_CREDITO   # PRECO_CREDITO = 0.25
bonus = 0
if quantidade > BONUS_THRESHOLD:     # BONUS_THRESHOLD = 300
    bonus = int(quantidade * BONUS_PERCENT)   # BONUS_PERCENT = 0.20
creditos_finais = quantidade + bonus
```

No webhook: adicionar **creditos_finais** à conta do usuário.

### Exemplos

| Comprar | Pagar | Recebe (créditos) |
|---------|--------|-------------------|
| 50 | R$ 12,50 | 50 |
| 100 | R$ 25,00 | 100 |
| 300 | R$ 75,00 | 300 |
| 400 | R$ 100,00 | **480** (400 + 20%) |
| 500 | R$ 125,00 | **600** |
| 1000 | R$ 250,00 | **1.200** |

---

## 3. Custos por módulo (quanto cada ação consome)

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
| **Upload + análise PRISMA (por artigo)** | **15** | Por artigo na metanálise |

*Valores configuráveis via `CREDIT_COST_<MODULO>` no `.env` (backend).*

---

## 4. Regras de negócio

1. **Créditos disponíveis** = `creditos - creditos_usados` (já implementado).
2. **Novos usuários:** créditos iniciais no cadastro (ex.: 20–30) – configurável.
3. **Compra:** usuário escolhe quantidade → valor = quantidade × R$ 0,25 → paga (Asaas) → no webhook, sistema entrega **creditos_finais** (quantidade + bônus se > 300) via `adicionar_creditos_usuario`.
4. **Sem créditos:** API retorna 402 e mensagem “Créditos insuficientes. Compre mais créditos.” (já existe).

---

## 5. Gateway de pagamento (Asaas)

- **Checkout:** criar cobrança única no Asaas com **valor = quantidade × 0,25** (em reais).
- **externalReference:** usar formato **pacote_&lt;quantidade&gt;** (ex.: `pacote_400`) para o webhook saber a quantidade e calcular creditos_finais.
- **Webhook:** evento `PAYMENT_CONFIRMED` → ler quantidade do reference → calcular creditos_finais (quantidade + 20% se > 300) → chamar `adicionar_creditos_usuario(user_id, creditos_finais)` → registrar em `pagamentos`.

---

## 6. Próximos passos técnicos

| Prioridade | Tarefa |
|------------|--------|
| 1 | Endpoint `GET /pacotes` retornando regra (R$ 0,25, bônus 20% acima de 300) e sugestões de pacotes. |
| 2 | Endpoint `POST /checkout/creditos` (quantidade) → valor = quantidade × 0,25 → cria cobrança Asaas e retorna URL de pagamento; externalReference = pacote_&lt;quantidade&gt;. |
| 3 | Webhook Asaas: ao confirmar pagamento, calcular creditos_finais e creditar. |
| 4 | Créditos iniciais no cadastro (variável de ambiente ou valor fixo). |
| 5 | Página “Comprar créditos” no frontend (input de quantidade ou pacotes sugeridos). |

---

## 7. Métricas sugeridas

- Receita por compra de créditos.
- Créditos vendidos vs. créditos consumidos (uso).
- Conversão: cadastro → primeira compra.
- Custo médio de API por crédito para validar margem (R$ 0,25/crédito).

---

*Estratégia: apenas compra de créditos a R$ 0,25/crédito, com +20% de bônus em compras acima de 300 créditos.*
