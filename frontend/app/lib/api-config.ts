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
// IMPORTANTE: Corrigir URL antiga se estiver configurada incorretamente
let apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL || 'https://medquestresearch-api.up.railway.app';

// Correção automática: substituir URL antiga pela correta
if (apiBaseUrl.includes('medquest-research-api')) {
  console.error('🚨 ERRO: URL antiga detectada! Corrigindo automaticamente...');
  console.error('❌ URL antiga:', apiBaseUrl);
  apiBaseUrl = apiBaseUrl.replace('medquest-research-api', 'medquestresearch-api');
  console.warn('✅ URL corrigida para:', apiBaseUrl);
  console.warn('⚠️ ATENÇÃO: Corrija a variável NEXT_PUBLIC_API_BASE_URL no Railway e faça um novo build!');
}

export const API_BASE_URL = apiBaseUrl;

// Log da URL sendo usada (apenas em desenvolvimento)
if (typeof window !== 'undefined' && process.env.NODE_ENV === 'development') {
  console.log('🔗 API Base URL configurada:', API_BASE_URL);
}

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
  ADICIONAR_CREDITOS: '/genapi/admin/adicionar-creditos',
  LISTAR_CUSTOS: '/genapi/admin/custos',
  METRICAS_CREDITOS: '/genapi/admin/metricas-creditos',
  CHECKOUT_CREDITOS: '/genapi/checkout/creditos',
  PERFIL: '/genapi/perfil',
  PLANOS: '/genapi/planos',
  PACOTES: '/genapi/pacotes',
  
  // Rotas de IA (versões antigas - mantidas para compatibilidade)
  EXPLICAR: '/genapi/explicar',
  CRITICA: '/genapi/critica',
  FATOS: '/genapi/fatos',
  MAPA: '/genapi/mapa',
  PDF: '/genapi/pdf',
  TRADUCAO: '/genapi/traducao',
  
  // Rotas Research (novas - recomendadas)
  CRITICAL_ANALYSIS: '/genapi/critical_analysis',
  EXPLAIN_CONCEPT: '/genapi/explain_concept',
  FACT_CHECKER: '/genapi/fact_checker',
  META_ANALYSIS: '/genapi/meta_analysis',
  META_ANALYSE: '/genapi/meta_analise', // Alias para compatibilidade
  
  // Rotas de status de jobs assíncronos
  JOB_STATUS: '/genapi/job',
  JOBS: '/genapi/jobs',
  
  // Chat e interação
  CHAT_FOLLOWUP: '/genapi/chat-followup',
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

