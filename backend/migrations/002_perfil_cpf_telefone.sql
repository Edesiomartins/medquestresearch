-- Perfil do usuário: CPF e telefone para criação de cliente no Asaas
-- Execute no PostgreSQL (ex.: Railway).

ALTER TABLE usuarios
ADD COLUMN IF NOT EXISTS cpf VARCHAR(14) NULL,
ADD COLUMN IF NOT EXISTS telefone VARCHAR(20) NULL;

COMMENT ON COLUMN usuarios.cpf IS 'CPF do usuário (pode ser formatado, ex.: 123.456.789-09). Usado ao criar cliente no Asaas.';
COMMENT ON COLUMN usuarios.telefone IS 'Telefone com DDD (ex.: (62) 99999-9999). Usado ao criar cliente no Asaas.';
