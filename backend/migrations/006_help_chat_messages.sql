-- Migration 006: histórico persistente do chatbot de ajuda por usuário

CREATE TABLE IF NOT EXISTS public.help_chat_messages (
    id BIGSERIAL PRIMARY KEY,
    usuario_id BIGINT NOT NULL REFERENCES public.usuarios(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant')),
    content TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_help_chat_messages_usuario_created
ON public.help_chat_messages (usuario_id, created_at DESC);

COMMENT ON TABLE public.help_chat_messages
IS 'Histórico do chatbot de ajuda, vinculado ao usuário autenticado.';

