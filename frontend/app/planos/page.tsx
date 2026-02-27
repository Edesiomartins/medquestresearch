'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { getApiUrl } from '@/app/lib/api-config';
import { API_ENDPOINTS } from '@/app/lib/api-config';

interface Pacote {
  id: string;
  nome: string;
  quantidade: number;
  creditos_entregues: number;
  preco_reais: number;
  destaque?: boolean;
}

interface Regra {
  preco_por_credito_reais?: number;
  bonus_acima_de?: number;
  bonus_percentual?: number;
}

export default function PlanosPage() {
  const [pacotes, setPacotes] = useState<Pacote[]>([]);
  const [regra, setRegra] = useState<Regra | null>(null);
  const [loading, setLoading] = useState(true);
  const [erro, setErro] = useState<string | null>(null);

  useEffect(() => {
    const carregar = async () => {
      try {
        const resPacotes = await fetch(getApiUrl(API_ENDPOINTS.PACOTES));
        if (resPacotes.ok) {
          const data = await resPacotes.json();
          setPacotes(data.pacotes || []);
          setRegra(data.regra || null);
        }
      } catch (e: unknown) {
        setErro(e instanceof Error ? e.message : 'Erro ao carregar preços.');
      } finally {
        setLoading(false);
      }
    };
    carregar();
  }, []);

  const formatarPreco = (valor: number) =>
    valor.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });

  return (
    <div className="min-h-screen bg-mq-slate-50">
      <header className="bg-[#0c3d66] text-white shadow-md">
        <div className="max-w-6xl mx-auto px-6 py-4 flex items-center justify-between">
          <Link href="/" className="text-xl font-bold text-white hover:opacity-90">
            MedQuestResearch
          </Link>
          <div className="flex gap-4">
            <Link href="/login" className="text-blue-200 hover:text-white text-sm">
              Entrar
            </Link>
            <Link href="/register" className="bg-white/20 hover:bg-white/30 px-4 py-2 rounded-lg text-sm font-medium">
              Cadastrar
            </Link>
          </div>
        </div>
      </header>

      <main className="max-w-6xl mx-auto px-6 py-12">
        <h1 className="text-3xl font-bold text-[#0c3d66] mb-2">Comprar créditos</h1>
        <p className="text-slate-600 mb-4">
          Use créditos para análises de artigos, metanálise PRISMA, explicações e mais. Compre a quantidade que precisar.
        </p>

        {regra && (
          <div className="mb-8 p-4 bg-[#0c3d66]/10 border border-[#0c3d66]/30 rounded-xl">
            <p className="text-slate-700 font-medium">
              R$ 0,25 por crédito. Compras acima de {regra.bonus_acima_de ?? 300} créditos ganham{' '}
              <strong>{regra.bonus_percentual ?? 20}%</strong> de bônus.
            </p>
          </div>
        )}

        {loading && (
          <div className="text-center py-12 text-slate-500">Carregando...</div>
        )}
        {erro && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-6">
            {erro}
          </div>
        )}

        {!loading && (
          <>
            <section>
              <h2 className="text-xl font-semibold text-[#0c3d66] mb-4">Pacotes de créditos</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {pacotes.map((pacote) => (
                  <div
                    key={pacote.id}
                    className={`bg-white border-2 rounded-xl p-5 shadow-sm hover:border-[#0c3d66]/40 transition-colors ${
                      pacote.destaque ? 'border-[#0c3d66] ring-2 ring-[#0c3d66]/20' : 'border-slate-200'
                    }`}
                  >
                    {pacote.destaque && (
                      <span className="text-xs font-semibold text-[#0c3d66] bg-[#0c3d66]/10 px-2 py-0.5 rounded">
                        +20% bônus
                      </span>
                    )}
                    <h3 className="text-lg font-bold text-[#0c3d66] mt-1">{pacote.nome}</h3>
                    <p className="text-xl font-bold text-slate-800 mt-1">
                      {pacote.creditos_entregues} créditos
                      {pacote.creditos_entregues > pacote.quantidade && (
                        <span className="text-sm font-normal text-green-600 ml-1">
                          (compra de {pacote.quantidade})
                        </span>
                      )}
                    </p>
                    <p className="text-slate-600 text-sm">{formatarPreco(pacote.preco_reais)}</p>
                    <button
                      disabled
                      className="mt-4 w-full py-2 rounded-lg bg-slate-200 text-slate-500 text-sm font-medium cursor-not-allowed"
                    >
                      Em breve
                    </button>
                  </div>
                ))}
              </div>
            </section>

            <div className="mt-12 p-6 bg-slate-100 rounded-xl text-slate-600 text-sm">
              <p className="font-medium text-slate-700 mb-2">Como funcionam os créditos?</p>
              <ul className="list-disc list-inside space-y-1">
                <li>Upload de PDF/DOCX: 3 créditos por arquivo</li>
                <li>Explicar conteúdo / Verificar fatos: 5 créditos</li>
                <li>Análise crítica: 7 créditos</li>
                <li>Perspectivas científicas: 10 créditos</li>
                <li>Metanálise (por etapa): 12 créditos</li>
                <li>Upload + análise PRISMA por artigo: 15 créditos</li>
              </ul>
            </div>
          </>
        )}
      </main>
    </div>
  );
}
