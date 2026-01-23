/**
 * Configuração centralizada da API do MedQuestResearch
 * 
 * Esta configuração garante que todas as chamadas de API usem a URL correta
 * baseado no ambiente (desenvolvimento/produção).
 * 
 * PRODUÇÃO (Railway):
 *   NEXT_PUBLIC_API_BASE_URL=https://medquest-research-api.up.railway.app
 *   → Usa a URL do Railway diretamente
 * 
 * DESENVOLVIMENTO (.env.local):
 *   NEXT_PUBLIC_API_BASE_URL=https://medquest-research-api.up.railway.app
 *   → Ou use a URL do Railway também em desenvolvimento
 *   → Ou http://localhost:5000 para desenvolvimento local
 */

// URL base da API - OBRIGATÓRIA (Railway)
// Fallback para a URL de produção se não estiver configurada
export const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'https://medquest-research-api.up.railway.app';

if (!API_BASE_URL) {
  console.warn('⚠️ NEXT_PUBLIC_API_BASE_URL não configurado. Usando URL padrão do Railway.');
}

// Endpoints da API
export const API_ENDPOINTS = {
  // Rotas básicas
  PING: '/ping',
  
  // Rotas de usuário
  CADASTRO: '/cadastro',
  LOGIN: '/login',
  CREDITOS: '/creditos',
  
  // Rotas de IA (versões antigas - mantidas para compatibilidade)
  EXPLICAR: '/explicar',
  CRITICA: '/critica',
  FATOS: '/fatos',
  PERSPECTIVA: '/perspectiva',
  MAPA: '/mapa',
  PDF: '/pdf',
  
  // Rotas Research (novas - recomendadas)
  CRITICAL_ANALYSIS: '/critical_analysis',
  EXPLAIN_CONCEPT: '/explain_concept',
  FACT_CHECKER: '/fact_checker',
  PERSPECTIVE_RESEARCH: '/perspective_research',
  
  // Rotas de status de jobs assíncronos
  JOB_STATUS: '/job',
  JOBS: '/jobs',
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

