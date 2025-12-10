/**
 * Configuração centralizada da API do MedQuestResearch
 * 
 * Esta configuração garante que todas as chamadas de API usem o prefixo correto
 * baseado no ambiente (desenvolvimento/produção).
 */

// URL base da API - ajuste conforme necessário
// Em produção (PythonAnywhere): usa o prefixo /genapi configurado no WSGI.PY
// Em desenvolvimento local: pode usar http://localhost:5000 ou a URL do PythonAnywhere
const getApiBaseUrl = (): string => {
  // Se estiver definida uma variável de ambiente, use ela
  if (typeof window !== 'undefined' && process.env.NEXT_PUBLIC_API_URL) {
    return process.env.NEXT_PUBLIC_API_URL;
  }
  
  // Em produção (Vercel), aponta para o PythonAnywhere com prefixo /genapi
  if (process.env.NODE_ENV === 'production') {
    return 'https://dredesiomartins.pythonanywhere.com/genapi';
  }
  
  // Em desenvolvimento, pode apontar para localhost ou PythonAnywhere
  return 'https://dredesiomartins.pythonanywhere.com/genapi';
};

export const API_BASE_URL = getApiBaseUrl();

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
} as const;

// Função helper para construir URLs completas
export const getApiUrl = (endpoint: string): string => {
  return `${API_BASE_URL}${endpoint}`;
};

// Configuração padrão para fetch requests
export const defaultFetchOptions: RequestInit = {
  headers: {
    'Content-Type': 'application/json',
  },
};

// Função helper para fazer requisições autenticadas
export const authenticatedFetch = async (
  endpoint: string,
  options: RequestInit = {},
  token?: string
): Promise<Response> => {
  const headers: Record<string, string> = {
    ...(defaultFetchOptions.headers as Record<string, string>),
    ...(options.headers as Record<string, string>),
  };

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  return fetch(getApiUrl(endpoint), {
    ...defaultFetchOptions,
    ...options,
    headers,
  });
};

