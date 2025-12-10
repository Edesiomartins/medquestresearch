import { NextRequest, NextResponse } from 'next/server';
import { getApiUrl, API_ENDPOINTS } from '@/app/lib/api-config';

export async function POST(req: NextRequest) {
  try {
    const formData = await req.formData();
    const token = formData.get('token') as string;
    const file = formData.get('file') as File;

    if (!token || !file) {
      return NextResponse.json(
        { erro: 'Token e arquivo PDF são obrigatórios' },
        { status: 400 }
      );
    }

    // Cria FormData para enviar ao backend
    const backendFormData = new FormData();
    backendFormData.append('file', file);

    const res = await fetch(getApiUrl(API_ENDPOINTS.PDF), {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
      },
      body: backendFormData,
    });

    if (!res.ok) {
      const err = await res.json();
      return NextResponse.json(
        { erro: err.erro || 'Falha no upload' },
        { status: res.status }
      );
    }

    return NextResponse.json(await res.json());
  } catch (error) {
    console.error('Erro pdf:', error);
    return NextResponse.json(
      { erro: 'Erro de conexão' },
      { status: 500 }
    );
  }
}