/**
 * Configuração centralizada da API do MedQuestResearch
 *
 * PRODUÇÃO (Railway):
 *   NEXT_PUBLIC_API_BASE_URL=https://medquestresearch-api.up.railway.app
 *
 * DESENVOLVIMENTO (.env.local):
 *   NEXT_PUBLIC_API_BASE_URL=https://medquestresearch-api.up.railway.app
 *   → Ou http://localhost:5000 para desenvolvimento local
 */

// URL base da API (Railway)
export const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'https://medquestresearch-api.up.railway.app';

if (!API_BASE_URL) {
  console.warn('⚠️ NEXT_PUBLIC_API_BASE_URL não configurado. Usando URL padrão do Railway.');
}

// Endpoints da API
export const API_ENDPOINTS = {
  // Rotas básicas
  PING: '/ping',
  
  // Rotas de usuário
  CADASTRO: '/genapi/cadastro',
  LOGIN: '/genapi/login',
  CREDITOS: '/genapi/creditos',
  
  // Rotas de IA (versões antigas - mantidas para compatibilidade)
  EXPLICAR: '/genapi/explicar',
  CRITICA: '/genapi/critica',
  FATOS: '/genapi/fatos',
  PERSPECTIVA: '/genapi/perspectiva',
  MAPA: '/genapi/mapa',
  PDF: '/genapi/pdf',
  
  // Rotas Research (novas - recomendadas)
  CRITICAL_ANALYSIS: '/genapi/critical_analysis',
  EXPLAIN_CONCEPT: '/genapi/explain_concept',
  FACT_CHECKER: '/genapi/fact_checker',
  PERSPECTIVE_RESEARCH: '/genapi/perspective_research',
  META_ANALYSIS: '/genapi/meta_analise',
  META_ANALYSE: '/genapi/meta_analysis', // Alias
  
  // Rotas de status de jobs assíncronos
  JOB_STATUS: '/genapi/job',
  JOBS: '/genapi/jobs',
} as const;

// Função helper para construir URLs completas
export function getApiUrl(path: string): string {
  // Remove barra duplicada se houver
  const baseUrl = API_BASE_URL.endsWith('/') ? API_BASE_URL.slice(0, -1) : API_BASE_URL;
  const cleanPath = path.startsWith('/') ? path : `/${path}`;
  
  return `${baseUrl}${cleanPath}`;
}

// Configuração padrão para fetch requests
export const defaultFetchOptions: RequestInit = {
  headers: {
    'Content-Type': 'application/json',
  },
};

// Função helper para fazer requisições autenticadas com timeout
export const authenticatedFetch = async (
  endpoint: string,
  options: RequestInit = {},
  token?: string,
  timeout: number = 300000 // 5 minutos (300 segundos) para processamento de IA
): Promise<Response> => {
  const headers: Record<string, string> = {
    ...(defaultFetchOptions.headers as Record<string, string>),
    ...(options.headers as Record<string, string>),
  };

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  // Criar AbortController para timeout
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeout);

  try {
    const response = await fetch(getApiUrl(endpoint), {
      ...defaultFetchOptions,
      ...options,
      headers,
      signal: controller.signal,
    });
    
    clearTimeout(timeoutId);
    return response;
  } catch (error: any) {
    clearTimeout(timeoutId);
    if (error.name === 'AbortError') {
      throw new Error(`Timeout: A requisição demorou mais de ${timeout / 1000} segundos`);
    }
    throw error;
  }
};

