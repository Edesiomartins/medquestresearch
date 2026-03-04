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
  resultado_pt?: string; // Versão em português do texto extraído (tradução quando aplicável)
  token?: string;
  usuario?: any;
  creditos?: number;
  request_id?: number;
  status?: string;
  detalhes?: string;
  artigos?: any[]; // Artigos encontrados (para metanálise)
  total_artigos?: number; // Total de artigos encontrados
  resumo_analises?: {
    escore_medio?: number;
    pontuacao_prisma_media?: number;
    artigos_por_qualidade?: { excelente?: number; boa?: number; regular?: number; baixa?: number };
  }; // Resumo PRISMA (upload artigos metanálise)
}

export interface ExplicarConceitoResponse extends ApiResponse {
  resultado?: string;
}

// ============================================
// Autenticação e usuário
// ============================================

export async function login(email: string, senha: string): Promise<ApiResponse> {
  const response = await fetch(getApiUrl(API_ENDPOINTS.LOGIN), {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, senha }),
  });
  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    return { erro: data.erro || data.detail || `Erro ${response.status}` };
  }
  return data;
}

export async function cadastro(nome: string, email: string, senha: string): Promise<ApiResponse> {
  const response = await fetch(getApiUrl(API_ENDPOINTS.CADASTRO), {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ nome, email, senha }),
  });
  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    return { erro: data.erro || data.detail || `Erro ${response.status}` };
  }
  return data;
}

export async function getCreditos(token: string): Promise<ApiResponse> {
  const response = await authenticatedFetch(API_ENDPOINTS.CREDITOS, { method: 'GET' }, token);
  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    return { erro: data.erro || data.detail || `Erro ${response.status}` };
  }
  return data;
}

// Função genérica para chamadas de API
async function apiCall<T = any>(
  endpoint: string,
  method: 'GET' | 'POST' = 'POST',
  body?: any,
  token?: string,
  timeout: number = 300000
): Promise<T> {
  const options: RequestInit = {
    method,
    headers: {
      'Content-Type': 'application/json',
    },
  };

  if (body) {
    options.body = JSON.stringify(body);
  }

  const response = await authenticatedFetch(endpoint, options, token, timeout);

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ erro: `Erro ${response.status}` }));
    throw new Error(errorData.erro || `Erro ${response.status}`);
  }

  return await response.json();
}

// Função para polling de status de jobs assíncronos
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

      // Se o job estiver completo, retornar o resultado e artigos (se houver)
      if (response.status === 'done' && response.resultado) {
        return { 
          resultado: response.resultado,
          artigos: response.artigos,
          total_artigos: response.total_artigos
        };
      }

      // Se o job falhou, retornar o erro
      if (response.status === 'failed' || response.status === 'error') {
        return { erro: response.erro || response.detalhes || 'Erro ao processar' };
      }

      // Se ainda está processando, aguardar antes da próxima tentativa
      await new Promise(resolve => setTimeout(resolve, intervalMs));
    } catch (error: any) {
      // Se for timeout, continuar tentando (não retornar erro)
      if (error.message && error.message.includes('Timeout')) {
        await new Promise(resolve => setTimeout(resolve, intervalMs));
        continue;
      }
      return { erro: error.message || 'Erro ao verificar status do job' };
    }
  }
}

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

export async function traduzirTexto(token: string, texto: string): Promise<ApiResponse> {
  try {
    const response = await fetch(getApiUrl(API_ENDPOINTS.TRADUCAO), {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
      },
      body: JSON.stringify({ texto }),
    });
    const data = await response.json().catch(() => ({}));
    if (!response.ok) {
      return { erro: (data as any).detail || data.erro || `Erro ${response.status}` };
    }
    return data;
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

// ============================================
// Funções de Estrutura
// ============================================

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
// Função Metanálise (PRISMA Compliance)
// ============================================

export interface MetaAnaliseParams {
  tema?: string; // Tema agora é opcional (novo fluxo usa upload de artigos)
  etapa?: string; // 1=PICO+Busca, 2=Extração, 3=Redação, 4=Verificação
  texto_artigo?: string; // Opcional - usado apenas nas etapas 2-4
  json_extracao?: string | object;
  estilo?: string; // 'Vancouver' ou 'ABNT'
  manuscrito?: string;
  artigos_analisados?: any; // Artigos analisados (novo fluxo)
}

export async function metaAnalysis(
  token: string,
  params: MetaAnaliseParams
): Promise<ApiResponse> {
  // Converter json_extracao para string se for objeto
  const body: any = {
    tema: params.tema || '', // Tema agora é opcional
    etapa: params.etapa || '1',
    texto_artigo: params.texto_artigo || null, // Opcional
    json_extracao: typeof params.json_extracao === 'object' 
      ? JSON.stringify(params.json_extracao) 
      : params.json_extracao,
    estilo: params.estilo || 'Vancouver',
    manuscrito: params.manuscrito,
  };
  
  // Adicionar artigos analisados se fornecido (novo fluxo)
  if (params.artigos_analisados) {
    body.artigos_analisados = typeof params.artigos_analisados === 'object'
      ? JSON.stringify(params.artigos_analisados)
      : params.artigos_analisados;
  }

  return callAsyncApi(API_ENDPOINTS.META_ANALYSIS, token, body, 300000);
}

// ============================================
// Função Upload Múltiplo de Artigos (Metanálise)
// ============================================

export async function uploadArtigosMetanalise(
  token: string,
  files: File[]
): Promise<ApiResponse> {
  if (files.length === 0) {
    return { erro: 'Nenhum arquivo selecionado' };
  }
  
  if (files.length > 15) {
    return { erro: 'Máximo de 15 artigos permitidos' };
  }

  const formData = new FormData();
  // FastAPI espera múltiplos arquivos com o mesmo nome 'files'
  files.forEach((file) => {
    formData.append('files', file);
  });

  const headers: Record<string, string> = {};
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  try {
    const response = await fetch(
      getApiUrl('/genapi/meta_analysis/upload_articles'),
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
// Função Chat Follow-up (Interação com respostas)
// ============================================

export interface ChatFollowUpParams {
  tipo_analise: string;
  texto_artigo?: string;
  mensagem: string;
  historico?: Array<{ role: 'user' | 'assistant'; content: string }>;
}

export async function chatFollowUp(
  token: string,
  params: ChatFollowUpParams
): Promise<ApiResponse> {
  return apiCall(
    API_ENDPOINTS.CHAT_FOLLOWUP,
    'POST',
    {
      tipo_analise: params.tipo_analise,
      texto_artigo: params.texto_artigo,
      mensagem: params.mensagem,
      historico: params.historico || [],
    },
    token
  );
}
