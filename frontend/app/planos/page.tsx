'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { getApiUrl, API_ENDPOINTS } from '@/app/lib/api-config';
import { useAuth } from '@/app/lib/hooks/useAuth';

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

const USO_CREDITOS = [
  { icon: '📄', label: 'Upload PDF/DOCX', creditos: 3 },
  { icon: '💡', label: 'Explicar conteúdo / Verificar fatos', creditos: 5 },
  { icon: '🔍', label: 'Análise crítica', creditos: 7 },
  { icon: '🌍', label: 'Perspectivas científicas', creditos: 10 },
  { icon: '📊', label: 'Metanálise (por etapa)', creditos: 12 },
  { icon: '📑', label: 'Upload + análise PRISMA por artigo', creditos: 15 },
];

export default function PlanosPage() {
  const { token } = useAuth();
  const [pacotes, setPacotes] = useState<Pacote[]>([]);
  const [regra, setRegra] = useState<Regra | null>(null);
  const [loading, setLoading] = useState(true);
  const [erro, setErro] = useState<string | null>(null);
  const [checkoutPacoteId, setCheckoutPacoteId] = useState<string | null>(null);
  const [checkoutErro, setCheckoutErro] = useState<string | null>(null);

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

  const handleComprar = async (pacote: Pacote) => {
    if (!token) {
      window.location.href = '/login?redirect=/planos';
      return;
    }
    setCheckoutErro(null);
    setCheckoutPacoteId(pacote.id);
    try {
      const res = await fetch(getApiUrl(API_ENDPOINTS.CHECKOUT_CREDITOS), {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ quantidade: pacote.quantidade }),
      });
      const data = await res.json().catch(() => ({}));
      if (!res.ok) {
        const msg = typeof data.detail === 'string'
          ? data.detail
          : (data.detail?.message || data.detail || 'Erro ao gerar pagamento.');
        setCheckoutErro(msg);
        return;
      }
      const url = data.invoiceUrl ?? data.url;
      if (url) window.open(url, '_blank', 'noopener,noreferrer');
      else setCheckoutErro('Link de pagamento não retornado.');
    } catch (e: unknown) {
      setCheckoutErro(e instanceof Error ? e.message : 'Erro de conexão.');
    } finally {
      setCheckoutPacoteId(null);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-50 via-white to-slate-50">
      {/* Header */}
      <header className="sticky top-0 z-10 border-b border-slate-200/80 bg-white/90 backdrop-blur-sm">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 py-4 flex items-center justify-between">
          <Link
            href="/"
            className="text-lg font-bold text-[#0c3d66] hover:text-[#0ea5e9] transition-colors"
          >
            MedQuestResearch
          </Link>
          <div className="flex items-center gap-3">
            {token ? (
              <Link
                href="/"
                className="text-slate-600 hover:text-[#0c3d66] text-sm font-medium"
              >
                Voltar ao app
              </Link>
            ) : (
              <>
                <Link
                  href="/login"
                  className="text-slate-600 hover:text-[#0c3d66] text-sm font-medium"
                >
                  Entrar
                </Link>
                <Link
                  href="/register"
                  className="bg-[#0c3d66] hover:bg-[#0a3352] text-white px-4 py-2 rounded-lg text-sm font-medium shadow-sm transition-colors"
                >
                  Cadastrar
                </Link>
              </>
            )}
          </div>
        </div>
      </header>

      <main className="max-w-5xl mx-auto px-4 sm:px-6 py-10 sm:py-14">
        {/* Hero */}
        <section className="text-center mb-12 sm:mb-16">
          <h1 className="text-3xl sm:text-4xl font-bold text-[#0c3d66] mb-3 tracking-tight">
            Comprar créditos
          </h1>
          <p className="text-slate-600 text-lg max-w-2xl mx-auto">
            Use créditos para análises de artigos, metanálise PRISMA, explicações e mais.
            Compre a quantidade que precisar.
          </p>
          {regra && (
            <div className="mt-6 inline-flex items-center gap-2 px-4 py-2 rounded-full bg-[#0c3d66]/10 border border-[#0c3d66]/20 text-[#0c3d66] text-sm font-medium">
              <span>R$ 0,25/crédito</span>
              <span className="text-slate-400">•</span>
              <span>
                +{regra.bonus_percentual ?? 20}% bônus acima de {regra.bonus_acima_de ?? 300} créditos
              </span>
            </div>
          )}
        </section>

        {erro && (
          <div className="mb-8 p-4 bg-red-50 border border-red-200 text-red-700 rounded-xl text-sm">
            {erro}
          </div>
        )}

        {checkoutErro && (
          <div className="mb-8 p-4 bg-amber-50 border border-amber-200 text-amber-800 rounded-xl text-sm">
            {checkoutErro}
          </div>
        )}

        {loading && (
          <div className="flex flex-col items-center justify-center py-20 text-slate-500">
            <div className="w-10 h-10 border-2 border-[#0c3d66]/30 border-t-[#0c3d66] rounded-full animate-spin mb-4" />
            <p>Carregando pacotes...</p>
          </div>
        )}

        {!loading && pacotes.length > 0 && (
          <>
            {/* Pacotes */}
            <section className="mb-16">
              <h2 className="text-xl font-semibold text-slate-800 mb-6">
                Escolha um pacote
              </h2>
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
                {pacotes.map((pacote) => {
                  const temBonus = pacote.creditos_entregues > pacote.quantidade;
                  const isLoading = checkoutPacoteId === pacote.id;
                  return (
                    <div
                      key={pacote.id}
                      className={`relative rounded-2xl border-2 bg-white p-6 shadow-sm transition-all duration-200 hover:shadow-md ${
                        pacote.destaque
                          ? 'border-[#0c3d66] shadow-[0_0_0_1px_rgba(12,61,102,0.08)]'
                          : 'border-slate-200 hover:border-slate-300'
                      }`}
                    >
                      {pacote.destaque && (
                        <div className="absolute -top-2.5 left-1/2 -translate-x-1/2">
                          <span className="inline-block px-3 py-0.5 rounded-full bg-[#0c3d66] text-white text-xs font-semibold">
                            Melhor custo-benefício
                          </span>
                        </div>
                      )}
                      <div className="pt-1">
                        <h3 className="text-lg font-bold text-[#0c3d66]">
                          {pacote.nome}
                        </h3>
                        <div className="mt-3 flex items-baseline gap-2">
                          <span className="text-2xl font-bold text-slate-800">
                            {pacote.creditos_entregues}
                          </span>
                          <span className="text-slate-500 text-sm">créditos</span>
                          {temBonus && (
                            <span className="text-xs font-medium text-emerald-600 bg-emerald-50 px-1.5 py-0.5 rounded">
                              +bônus
                            </span>
                          )}
                        </div>
                        <p className="mt-1 text-slate-600 text-sm">
                          {formatarPreco(pacote.preco_reais)}
                          {temBonus && (
                            <span className="text-slate-400 ml-1">
                              ({formatarPreco(pacote.preco_reais / pacote.creditos_entregues)}/crédito)
                            </span>
                          )}
                        </p>
                        <button
                          onClick={() => handleComprar(pacote)}
                          disabled={isLoading}
                          className="mt-5 w-full py-3 rounded-xl font-medium text-sm transition-colors disabled:opacity-60 disabled:cursor-not-allowed bg-[#0c3d66] hover:bg-[#0a3352] text-white shadow-sm"
                        >
                          {isLoading
                            ? 'Gerando pagamento...'
                            : token
                              ? 'Ver opções de pagamento'
                              : 'Entrar para comprar'}
                        </button>
                      </div>
                    </div>
                  );
                })}
              </div>
            </section>

            {/* Uso dos créditos */}
            <section className="rounded-2xl border border-slate-200 bg-white p-6 sm:p-8 shadow-sm">
              <h2 className="text-xl font-semibold text-slate-800 mb-5">
                Como funcionam os créditos?
              </h2>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                {USO_CREDITOS.map((item) => (
                  <div
                    key={item.label}
                    className="flex items-center gap-4 p-3 rounded-xl bg-slate-50/80 border border-slate-100"
                  >
                    <span className="text-2xl" aria-hidden>
                      {item.icon}
                    </span>
                    <div className="min-w-0">
                      <p className="font-medium text-slate-800 text-sm">
                        {item.label}
                      </p>
                      <p className="text-slate-500 text-xs">
                        {item.creditos} créditos
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </section>
          </>
        )}
      </main>
    </div>
  );
}
