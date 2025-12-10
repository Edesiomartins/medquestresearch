/**
 * Cliente API centralizado - Usa api-config.ts como base
 * 
 * Este arquivo exporta funções específicas da API usando a configuração
 * centralizada de api-config.ts
 */

import { authenticatedFetch, API_ENDPOINTS } from './api-config';

// Tipos de resposta da API
export interface ApiResponse<T = any> {
  data?: T;
  erro?: string;
  resultado?: string;
  token?: string;
  usuario?: any;
  creditos?: number;
}

export interface ExplicarConceitoResponse extends ApiResponse {
  resultado?: string;
}

// Função genérica para chamadas de API
async function apiCall<T = any>(
  endpoint: string,
  method: 'GET' | 'POST' = 'POST',
  body?: any,
  token?: string
): Promise<ApiResponse<T>> {
  try {
    const response = await authenticatedFetch(
      endpoint,
      {
        method,
        body: body ? JSON.stringify(body) : undefined,
      },
      token
    );

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ erro: `Erro ${response.status}` }));
      return { erro: errorData.erro || `Erro ${response.status}` };
    }

    return await response.json();
  } catch (error: any) {
    return { erro: `Erro de conexão: ${error.message || 'Erro desconhecido'}` };
  }
}

// ============================================
// Funções de Autenticação
// ============================================

export async function login(email: string, senha: string): Promise<ApiResponse> {
  return apiCall(API_ENDPOINTS.LOGIN, 'POST', { email, senha });
}

export async function cadastro(nome: string, email: string, senha: string): Promise<ApiResponse> {
  return apiCall(API_ENDPOINTS.CADASTRO, 'POST', { nome, email, senha });
}

export async function getCreditos(token: string): Promise<ApiResponse> {
  return apiCall(API_ENDPOINTS.CREDITOS, 'GET', undefined, token);
}

// ============================================
// Funções de IA - Versões Antigas
// ============================================

export async function explicarConceito(
  token: string,
  texto_artigo: string,
  trecho: string,
  nivel: string = 'graduação'
): Promise<ExplicarConceitoResponse> {
  return apiCall<ExplicarConceitoResponse>(
    API_ENDPOINTS.EXPLICAR,
    'POST',
    { texto_artigo, trecho, nivel },
    token
  );
}

export async function analisarCritica(
  token: string,
  texto_artigo: string
): Promise<ApiResponse> {
  return apiCall(API_ENDPOINTS.CRITICA, 'POST', { texto_artigo }, token);
}

export async function verificarFatos(
  token: string,
  texto_artigo: string
): Promise<ApiResponse> {
  return apiCall(API_ENDPOINTS.FATOS, 'POST', { texto_artigo }, token);
}

export async function pesquisarPerspectiva(
  token: string,
  texto_artigo: string
): Promise<ApiResponse> {
  return apiCall(API_ENDPOINTS.PERSPECTIVA, 'POST', { texto_artigo }, token);
}

export async function gerarMapa(
  token: string,
  texto_artigo: string
): Promise<ApiResponse> {
  return apiCall(API_ENDPOINTS.MAPA, 'POST', { texto_artigo }, token);
}

export async function uploadPdf(token: string, file: File): Promise<ApiResponse> {
  try {
    const formData = new FormData();
    formData.append('file', file);

    const response = await authenticatedFetch(
      API_ENDPOINTS.PDF,
      {
        method: 'POST',
        body: formData,
      },
      token
    );

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ erro: `Erro ${response.status}` }));
      return { erro: errorData.erro || `Erro ${response.status}` };
    }

    return await response.json();
  } catch (error: any) {
    return { erro: `Erro: ${error.message || 'Erro desconhecido'}` };
  }
}

// ============================================
// Funções Research - Versões Novas (Recomendadas)
// ============================================

export async function explainConcept(
  token: string,
  texto_artigo: string,
  trecho: string,
  nivel: string = 'graduação'
): Promise<ExplicarConceitoResponse> {
  return apiCall<ExplicarConceitoResponse>(
    API_ENDPOINTS.EXPLAIN_CONCEPT,
    'POST',
    { texto_artigo, trecho, nivel },
    token
  );
}

export async function criticalAnalysis(
  token: string,
  texto_artigo: string
): Promise<ApiResponse> {
  return apiCall(API_ENDPOINTS.CRITICAL_ANALYSIS, 'POST', { texto_artigo }, token);
}

export async function factChecker(
  token: string,
  texto_artigo: string
): Promise<ApiResponse> {
  return apiCall(API_ENDPOINTS.FACT_CHECKER, 'POST', { texto_artigo }, token);
}

export async function perspectiveResearch(
  token: string,
  texto_artigo: string
): Promise<ApiResponse> {
  return apiCall(API_ENDPOINTS.PERSPECTIVE_RESEARCH, 'POST', { texto_artigo }, token);
}

