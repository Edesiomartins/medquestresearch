import { NextRequest, NextResponse } from 'next/server';
import { getApiUrl, API_ENDPOINTS } from '@/app/lib/api-config';

export async function POST(req: NextRequest) {
  try {
    const body = await req.json();
    const { token, texto_artigo, trecho, nivel } = body;

    if (!token || !texto_artigo || !trecho || !nivel) {
      return NextResponse.json(
        { erro: 'Token, texto_artigo, trecho e nivel são obrigatórios' },
        { status: 400 }
      );
    }

    const res = await fetch(getApiUrl(API_ENDPOINTS.EXPLICAR), {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ texto_artigo, trecho, nivel }),
    });

    if (!res.ok) {
      const err = await res.json();
      return NextResponse.json(
        { erro: err.erro || 'Falha na análise' },
        { status: res.status }
      );
    }

    return NextResponse.json(await res.json());
  } catch (error) {
    console.error('Erro explicar:', error);
    return NextResponse.json(
      { erro: 'Erro de conexão' },
      { status: 500 }
    );
  }
}