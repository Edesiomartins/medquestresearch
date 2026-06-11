import { API_BASE_URL } from './api-config';
import type { EffectMeasure, MetaAnalysisResponse, MetaModel, MetaUploadResponse, StudyExtraction } from '@/app/types/meta';

function withAuth(token: string): HeadersInit {
  return {
    Authorization: `Bearer ${token}`,
  };
}

export async function uploadMetaFiles(token: string, files: File[]): Promise<MetaUploadResponse> {
  const formData = new FormData();
  files.forEach((file) => formData.append('files', file));
  const response = await fetch(`${API_BASE_URL}/api/meta/upload`, {
    method: 'POST',
    headers: withAuth(token),
    body: formData,
  });
  if (!response.ok) {
    const payload = await response.json().catch(() => ({}));
    throw new Error(payload.detail || payload.erro || `Erro ${response.status}`);
  }
  return response.json();
}

export async function reviewMetaStudies(
  token: string,
  projectId: string,
  studies: StudyExtraction[],
): Promise<MetaUploadResponse> {
  const response = await fetch(`${API_BASE_URL}/api/meta/review`, {
    method: 'POST',
    headers: {
      ...withAuth(token),
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      project_id: projectId,
      studies,
    }),
  });
  if (!response.ok) {
    const payload = await response.json().catch(() => ({}));
    throw new Error(payload.detail || payload.erro || `Erro ${response.status}`);
  }
  return response.json();
}

export async function analyzeMeta(
  token: string,
  body: {
    project_id: string;
    question: string;
    effect_measure: EffectMeasure;
    model_used: MetaModel;
    studies: StudyExtraction[];
    generate_article?: boolean;
  },
): Promise<MetaAnalysisResponse> {
  const response = await fetch(`${API_BASE_URL}/api/meta/analyze`, {
    method: 'POST',
    headers: {
      ...withAuth(token),
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(body),
  });
  if (!response.ok) {
    const payload = await response.json().catch(() => ({}));
    throw new Error(payload.detail || payload.erro || `Erro ${response.status}`);
  }
  return response.json();
}

export async function exportMetaDocx(
  token: string,
  body: {
    project_id: string;
    question: string;
    effect_measure: EffectMeasure;
    model_used: MetaModel;
    studies: StudyExtraction[];
    generate_article?: boolean;
  },
): Promise<Blob> {
  const response = await fetch(`${API_BASE_URL}/api/meta/export/docx`, {
    method: 'POST',
    headers: {
      ...withAuth(token),
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(body),
  });
  if (!response.ok) {
    const payload = await response.json().catch(() => ({}));
    throw new Error(payload.detail || payload.erro || `Erro ${response.status}`);
  }
  return response.blob();
}

export async function exportMetaZip(
  token: string,
  body: {
    project_id: string;
    question: string;
    effect_measure: EffectMeasure;
    model_used: MetaModel;
    studies: StudyExtraction[];
    generate_article?: boolean;
  },
): Promise<Blob> {
  const response = await fetch(`${API_BASE_URL}/api/meta/export/zip`, {
    method: 'POST',
    headers: {
      ...withAuth(token),
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(body),
  });
  if (!response.ok) {
    const payload = await response.json().catch(() => ({}));
    throw new Error(payload.detail || payload.erro || `Erro ${response.status}`);
  }
  return response.blob();
}

