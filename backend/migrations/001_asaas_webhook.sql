-- Webhook Asaas: coluna em usuarios + tabela pagamentos
-- Execute no PostgreSQL vinculado ao projeto (ex: Railway).

-- 1) Coluna para vincular usuário ao cliente Asaas (preencher ao criar cobrança)
ALTER TABLE usuarios
ADD COLUMN IF NOT EXISTS asaas_customer_id VARCHAR(64) NULL;

COMMENT ON COLUMN usuarios.asaas_customer_id IS 'ID do cliente no Asaas (ex: cus_000143719698). Preenchido ao criar primeira cobrança.';

-- 2) Tabela de pagamentos para idempotência e histórico
CREATE TABLE IF NOT EXISTS pagamentos (
  id SERIAL PRIMARY KEY,
  usuario_id INTEGER NOT NULL REFERENCES usuarios(id),
  payment_asaas_id VARCHAR(64) NOT NULL UNIQUE,
  referencia VARCHAR(255) NULL,
  valor NUMERIC(12,2) NULL,
  evento VARCHAR(64) NOT NULL,
  creditos_adicionados INTEGER NOT NULL DEFAULT 0,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_pagamentos_usuario_id ON pagamentos(usuario_id);
CREATE INDEX IF NOT EXISTS idx_pagamentos_payment_asaas_id ON pagamentos(payment_asaas_id);

COMMENT ON TABLE pagamentos IS 'Pagamentos recebidos via Asaas (webhook). payment_asaas_id evita processar o mesmo pagamento duas vezes.';
