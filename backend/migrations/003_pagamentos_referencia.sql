-- Webhook passa a usar referencia para idempotência e INSERT com (usuario_id, referencia, valor, evento)
-- Execute no PostgreSQL (ex.: Railway).

ALTER TABLE pagamentos
ALTER COLUMN payment_asaas_id DROP NOT NULL;

-- Índice único em referencia para garantir idempotência por referência
CREATE UNIQUE INDEX IF NOT EXISTS idx_pagamentos_referencia ON pagamentos(referencia) WHERE referencia IS NOT NULL AND referencia != '';

COMMENT ON COLUMN pagamentos.referencia IS 'externalReference do Asaas. Usado para idempotência (evitar processar o mesmo pagamento duas vezes).';
