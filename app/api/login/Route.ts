import { NextRequest, NextResponse } from 'next/server';
import { getApiUrl, API_ENDPOINTS } from '@/app/lib/api-config';

export async function POST(req: NextRequest) {
  try {
    const body = await req.json();  // { email, senha }
    const res = await fetch(getApiUrl(API_ENDPOINTS.LOGIN), {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    });

    if (!res.ok) {
      const err = await res.json();
      return NextResponse.json({ erro: err.erro || 'Falha no login' }, { status: res.status });
    }

    const data = await res.json();
    return NextResponse.json({ token: data.token, usuario: data.usuario });
  } catch (error) {
    return NextResponse.json({ erro: 'Erro de conexão' }, { status: 500 });
  }
}