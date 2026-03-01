-- Histórico de créditos: compras e consumo por módulo (auditoria, dashboard, antifraude)
-- No DBeaver: selecione TODO o script (Ctrl+A) e execute (Ctrl+Enter).

CREATE TABLE IF NOT EXISTS public.historico_creditos (
  id SERIAL PRIMARY KEY,
  usuario_id INTEGER NOT NULL REFERENCES public.usuarios(id),
  tipo VARCHAR(20) NOT NULL CHECK (tipo IN ('compra', 'consumo')),
  modulo VARCHAR(64) NULL,
  quantidade INTEGER NOT NULL DEFAULT 1,
  custo_total INTEGER NOT NULL DEFAULT 0,
  criado_em TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_historico_creditos_usuario_id ON public.historico_creditos(usuario_id);
CREATE INDEX IF NOT EXISTS idx_historico_creditos_tipo ON public.historico_creditos(tipo);
CREATE INDEX IF NOT EXISTS idx_historico_creditos_modulo ON public.historico_creditos(modulo);
CREATE INDEX IF NOT EXISTS idx_historico_creditos_criado_em ON public.historico_creditos(criado_em);

COMMENT ON TABLE public.historico_creditos IS 'Auditoria de créditos: compras (Asaas) e consumo por módulo (pdf, explicar, etc.)';
