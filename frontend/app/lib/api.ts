/**
 * Cliente API centralizado - Usa api-config.ts como base
 * 
 * Este arquivo exporta funções específicas da API usando a configuração
 * centralizada de api-config.ts
 */

import { authenticatedFetch, API_ENDPOINTS, API_BASE_URL, getApiUrl } from './api-config';

// Tipos de resposta da API
export interface ApiResponse<T = any> {
  data?: T;
  erro?: string;
  resultado?: string;
  token?: string;
  usuario?: any;
  creditos?: number;
  request_id?: number;
  status?: string;
  detalhes?: string;
}

export interface ExplicarConceitoResponse extends ApiResponse {
  resultado?: string;
}

// Função genérica para chamadas de API
async function apiCall<T = any>(
  endpoint: string,
  method: 'GET' | 'POST' = 'POST',
  body?: any,
  token?: string,
  timeout?: number // Timeout opcional em milissegundos
): Promise<ApiResponse<T>> {
  try {
    const response = await authenticatedFetch(
      endpoint,
      {
        method,
        body: body ? JSON.stringify(body) : undefined,
      },
      token,
      timeout // Passar timeout para authenticatedFetch
    );

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ erro: `Erro ${response.status}` }));
      return { erro: errorData.erro || `Erro ${response.status}` };
    }

    return await response.json();
  } catch (error: any) {
    // Tratar diferentes tipos de erro
    const errorMessage = error?.message || error?.toString() || 'Erro desconhecido';
    
    // Timeout não é erro em análise científica - removido
    
    if (errorMessage.includes('ECONNRESET') || 
        errorMessage.includes('socket hang up') || 
        errorMessage.includes('network') ||
        errorMessage.includes('fetch failed') ||
        error?.name === 'TypeError') {
      return { erro: 'Conexão interrompida. O servidor pode estar processando. Aguarde alguns segundos e tente novamente.' };
    }
    
    return { erro: `Erro de conexão: ${errorMessage}` };
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
// Função de Polling para Jobs Assíncronos
// ============================================

export async function pollJobStatus(
  token: string,
  jobId: number,
  intervalMs: number = 5000 // 5 segundos entre tentativas
): Promise<ApiResponse> {
  // Polling infinito - sem timeout, segue o ritmo do backend
  while (true) {
    try {
      const response = await apiCall<ApiResponse>(
        `${API_ENDPOINTS.JOB_STATUS}/${jobId}`,
        'GET',
        undefined,
        token,
        60000 // 60 segundos de timeout por requisição individual (aumentado para evitar timeout)
      );

      if (response.erro && response.status !== 'processing') {
        return response;
      }

      // Se o job estiver completo, retornar o resultado
      if (response.status === 'done' && response.resultado) {
        return { resultado: response.resultado };
      }

      // Se o job falhou, retornar o erro
      if (response.status === 'failed' || response.status === 'error') {
        return { erro: response.erro || response.detalhes || 'Erro ao processar' };
      }

      // Se ainda está processando, aguardar antes da próxima tentativa
      if (response.status === 'processing') {
        await new Promise(resolve => setTimeout(resolve, intervalMs));
        continue;
      }

      // Status desconhecido - continuar tentando
      await new Promise(resolve => setTimeout(resolve, intervalMs));
    } catch (error: any) {
      // Em caso de erro de rede, continuar tentando
      await new Promise(resolve => setTimeout(resolve, intervalMs));
    }
  }
}

// ============================================
// Função Helper para APIs Assíncronas
// ============================================

async function callAsyncApi(
  endpoint: string,
  token: string,
  body: any,
  timeout: number = 300000
): Promise<ApiResponse> {
  // Fazer a requisição inicial com timeout maior para garantir que recebemos o job_id
  // Mesmo que o processamento seja rápido, a criação do job pode demorar um pouco
  const initialResponse = await apiCall<ApiResponse>(
    endpoint,
    'POST',
    body,
    token,
    30000 // 30 segundos para receber o job_id (aumentado para evitar timeout prematuro)
  );

  // Se retornar erro direto, retornar
  if (initialResponse.erro) {
    // Se o erro for timeout, pode ser que o job já tenha sido criado e processado
    // Tentar verificar se há um job recente
    if (initialResponse.erro.includes('Timeout') || initialResponse.erro.includes('timeout')) {
      // Não retornar erro imediatamente, pode ser que o job já esteja pronto
      // O polling vai verificar isso
      console.warn('Timeout na criação do job, mas pode já estar processado');
    }
    return initialResponse;
  }

  // Se retornar request_id, significa que é assíncrono
  if (initialResponse.request_id && initialResponse.status === 'processing') {
    // Fazer polling do status (pode já estar completo se foi muito rápido)
    return await pollJobStatus(token, initialResponse.request_id);
  }

  // Se já retornar resultado direto (compatibilidade com versão antiga)
  if (initialResponse.resultado) {
    return initialResponse;
  }

  return { erro: 'Resposta inválida da API' };
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
  return callAsyncApi(
    API_ENDPOINTS.EXPLICAR,
    token,
    { texto_artigo, trecho, nivel },
    300000
  ) as Promise<ExplicarConceitoResponse>;
}

export async function analisarCritica(
  token: string,
  texto_artigo: string,
  foco_analise: string = "geral"
): Promise<ApiResponse> {
  return callAsyncApi(API_ENDPOINTS.CRITICA, token, { texto_artigo, foco_analise }, 300000);
}

export async function verificarFatos(
  token: string,
  texto_artigo: string
): Promise<ApiResponse> {
  return callAsyncApi(API_ENDPOINTS.FATOS, token, { texto_artigo }, 300000);
}

export async function pesquisarPerspectiva(
  token: string,
  texto_artigo: string
): Promise<ApiResponse> {
  return callAsyncApi(API_ENDPOINTS.PERSPECTIVA, token, { texto_artigo }, 300000);
}

export async function gerarMapa(
  token: string,
  texto_artigo: string
): Promise<ApiResponse> {
  return apiCall(API_ENDPOINTS.MAPA, 'POST', { texto_artigo }, token, 300000); // 5 minutos
}

export async function uploadPdf(token: string, file: File): Promise<ApiResponse> {
  try {
    const formData = new FormData();
    formData.append('file', file);

    // Para FormData, não devemos definir Content-Type manualmente
    // O browser define automaticamente com o boundary correto
    const headers: Record<string, string> = {};
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    const response = await fetch(
      getApiUrl(API_ENDPOINTS.PDF),
      {
        method: 'POST',
        headers,
        body: formData,
      }
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

export async function structureMapper(
  token: string,
  texto_artigo: string
): Promise<ApiResponse> {
  return callAsyncApi('/genapi/structure_mapper', token, { texto_artigo }, 300000);
}

export async function structureVisualizer(
  token: string,
  texto_artigo: string
): Promise<ApiResponse> {
  return callAsyncApi('/genapi/structure_visualizer', token, { texto_artigo }, 300000);
}

// ============================================
// Função Meta-Análise (PRISMA Compliance)
// ============================================

export interface MetaAnaliseParams {
  tema: string; // Tema é obrigatório agora
  etapa?: string; // 1=PICO+Busca, 2=Extração, 3=Redação, 4=Verificação
  texto_artigo?: string; // Opcional - usado apenas nas etapas 2-4
  json_extracao?: string | object;
  estilo?: string; // 'Vancouver' ou 'ABNT'
  manuscrito?: string;
}

export async function metaAnalysis(
  token: string,
  params: MetaAnaliseParams
): Promise<ApiResponse> {
  // Converter json_extracao para string se for objeto
  const body = {
    tema: params.tema, // Tema é obrigatório
    etapa: params.etapa || '1',
    texto_artigo: params.texto_artigo || null, // Opcional
    json_extracao: typeof params.json_extracao === 'object' 
      ? JSON.stringify(params.json_extracao) 
      : params.json_extracao,
    estilo: params.estilo || 'Vancouver',
    manuscrito: params.manuscrito,
  };

  return callAsyncApi(API_ENDPOINTS.META_ANALYSIS, token, body, 300000);
}

