'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { getApiUrl } from '@/app/lib/api-config';
import { API_ENDPOINTS } from '@/app/lib/api-config';

interface Plano {
  id: string;
  nome: string;
  creditos_mes: number;
  preco_reais: number;
  recorrente: boolean;
  descricao?: string;
  bonus?: string;
}

interface Pacote {
  id: string;
  nome: string;
  creditos: number;
  preco_reais: number;
  destaque?: boolean;
}

export default function PlanosPage() {
  const [planos, setPlanos] = useState<Plano[]>([]);
  const [pacotes, setPacotes] = useState<Pacote[]>([]);
  const [loading, setLoading] = useState(true);
  const [erro, setErro] = useState<string | null>(null);

  useEffect(() => {
    const carregar = async () => {
      try {
        const [resPlanos, resPacotes] = await Promise.all([
          fetch(getApiUrl(API_ENDPOINTS.PLANOS)),
          fetch(getApiUrl(API_ENDPOINTS.PACOTES)),
        ]);
        if (resPlanos.ok) {
          const data = await resPlanos.json();
          setPlanos(data.planos || []);
        }
        if (resPacotes.ok) {
          const data = await resPacotes.json();
          setPacotes(data.pacotes || []);
        }
      } catch (e: any) {
        setErro(e?.message || 'Erro ao carregar planos.');
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
        <h1 className="text-3xl font-bold text-[#0c3d66] mb-2">Planos e preços</h1>
        <p className="text-slate-600 mb-10">
          Use créditos para análises de artigos, metanálise PRISMA, explicações e mais. Escolha um plano ou compre créditos avulsos.
        </p>

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
            <section className="mb-12">
              <h2 className="text-xl font-semibold text-[#0c3d66] mb-4">Planos mensais</h2>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {planos.map((plano) => (
                  <div
                    key={plano.id}
                    className="bg-white border-2 border-slate-200 rounded-xl p-6 shadow-sm hover:border-[#0c3d66]/40 transition-colors"
                  >
                    <h3 className="text-lg font-bold text-[#0c3d66]">{plano.nome}</h3>
                    <p className="text-2xl font-bold text-slate-800 mt-2">
                      {formatarPreco(plano.preco_reais)}
                      <span className="text-sm font-normal text-slate-500">/mês</span>
                    </p>
                    <p className="text-slate-600 text-sm mt-1">
                      {plano.creditos_mes} créditos/mês
                      {plano.bonus && (
                        <span className="ml-1 text-green-600 font-medium">+{plano.bonus}</span>
                      )}
                    </p>
                    <p className="text-slate-500 text-sm mt-3">{plano.descricao}</p>
                    <button
                      disabled
                      className="mt-6 w-full py-3 rounded-lg bg-slate-200 text-slate-500 text-sm font-medium cursor-not-allowed"
                    >
                      Em breve
                    </button>
                  </div>
                ))}
              </div>
            </section>

            <section>
              <h2 className="text-xl font-semibold text-[#0c3d66] mb-4">Pacotes avulsos</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                {pacotes.map((pacote) => (
                  <div
                    key={pacote.id}
                    className={`bg-white border-2 rounded-xl p-5 shadow-sm hover:border-[#0c3d66]/40 transition-colors ${
                      pacote.destaque ? 'border-[#0c3d66] ring-2 ring-[#0c3d66]/20' : 'border-slate-200'
                    }`}
                  >
                    {pacote.destaque && (
                      <span className="text-xs font-semibold text-[#0c3d66] bg-[#0c3d66]/10 px-2 py-0.5 rounded">
                        Recomendado
                      </span>
                    )}
                    <h3 className="text-lg font-bold text-[#0c3d66] mt-1">{pacote.nome}</h3>
                    <p className="text-xl font-bold text-slate-800 mt-1">{pacote.creditos} créditos</p>
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
