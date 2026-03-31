-- Migration 005: adiciona started_at em research_jobs
-- Execute no PostgreSQL de produção (ex.: Railway) antes de remover compatibilidade temporária.

ALTER TABLE public.research_jobs
ADD COLUMN IF NOT EXISTS started_at TIMESTAMPTZ NULL;

-- Backfill compatível com schemas que usam created_at OU criado_em
DO $$
BEGIN
  IF EXISTS (
    SELECT 1
    FROM information_schema.columns
    WHERE table_schema = 'public'
      AND table_name = 'research_jobs'
      AND column_name = 'created_at'
  ) THEN
    EXECUTE '
      UPDATE public.research_jobs
      SET started_at = COALESCE(started_at, created_at, NOW())
      WHERE started_at IS NULL
    ';
  ELSIF EXISTS (
    SELECT 1
    FROM information_schema.columns
    WHERE table_schema = 'public'
      AND table_name = 'research_jobs'
      AND column_name = 'criado_em'
  ) THEN
    EXECUTE '
      UPDATE public.research_jobs
      SET started_at = COALESCE(started_at, criado_em, NOW())
      WHERE started_at IS NULL
    ';
  ELSE
    EXECUTE '
      UPDATE public.research_jobs
      SET started_at = COALESCE(started_at, NOW())
      WHERE started_at IS NULL
    ';
  END IF;
END $$;

CREATE INDEX IF NOT EXISTS idx_research_jobs_started_at
ON public.research_jobs (started_at);

COMMENT ON COLUMN public.research_jobs.started_at
IS 'Timestamp real de início do processamento do job para controle de timeout/recovery.';

-- Validação rápida pós-migration:
-- SELECT column_name, data_type
-- FROM information_schema.columns
-- WHERE table_schema = 'public'
--   AND table_name = 'research_jobs'
--   AND column_name = 'started_at';
--
-- SELECT COUNT(*) AS sem_started_at
-- FROM public.research_jobs
-- WHERE started_at IS NULL;
