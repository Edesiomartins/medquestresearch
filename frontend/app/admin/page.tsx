'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { getApiUrl, API_ENDPOINTS } from '@/app/lib/api-config';
import { useAuth } from '@/app/lib/hooks/useAuth';

const ADMIN_EMAIL = 'prof.edesio@gmail.com';

interface Resumo {
  compras: { registros: number; total_creditos: number };
  consumo: { registros: number; total_creditos: number };
}

interface ModuloRow {
  modulo: string;
  qtd_registros: number;
  total_creditos: number;
}

interface Registro {
  id: number;
  usuario_id: number;
  email: string | null;
  nome: string | null;
  tipo: string;
  modulo: string | null;
  quantidade: number;
  custo_total: number;
  criado_em: string;
}

export default function AdminPage() {
  const { token, usuario, loading: authLoading } = useAuth();
  const router = useRouter();
  const [metricas, setMetricas] = useState<{
    resumo?: Resumo;
    por_modulo?: ModuloRow[];
    ultimos_registros?: Registro[];
  } | null>(null);
  const [loading, setLoading] = useState(true);
  const [erro, setErro] = useState<string | null>(null);

  const isAdmin = (usuario?.email || '').trim().toLowerCase() === ADMIN_EMAIL;

  useEffect(() => {
    if (!authLoading && !token) {
      router.replace('/login');
      return;
    }
    if (authLoading || !token) return;
    if (!isAdmin) {
      router.replace('/');
      return;
    }
    const carregar = async () => {
      try {
        const res = await fetch(getApiUrl(API_ENDPOINTS.METRICAS_CREDITOS), {
          headers: { Authorization: `Bearer ${token}` },
        });
        if (res.status === 403) {
          router.replace('/');
          return;
        }
        if (res.ok) {
          const data = await res.json();
          setMetricas(data);
        } else {
          setErro('Erro ao carregar métricas.');
        }
      } catch (e: unknown) {
        setErro(e instanceof Error ? e.message : 'Erro de conexão.');
      } finally {
        setLoading(false);
      }
    };
    carregar();
  }, [token, authLoading, isAdmin, router]);

  if (authLoading || (token && !isAdmin)) {
    return null;
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-50 via-white to-slate-50">
      <header className="sticky top-0 z-10 border-b border-slate-200/80 bg-white/90 backdrop-blur-sm">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 py-4 flex items-center justify-between">
          <Link href="/" className="text-lg font-bold text-[#0c3d66] hover:text-[#0ea5e9] transition-colors">
            MedQuestResearch
          </Link>
          <div className="flex items-center gap-3">
            <span className="text-slate-500 text-sm">Admin</span>
            <Link href="/" className="text-slate-600 hover:text-[#0c3d66] text-sm font-medium">
              Voltar
            </Link>
          </div>
        </div>
      </header>

      <main className="max-w-5xl mx-auto px-4 sm:px-6 py-10">
        <h1 className="text-2xl sm:text-3xl font-bold text-[#0c3d66] mb-2">
          Dashboard – Métricas de créditos
        </h1>
        <p className="text-slate-600 mb-8">
          Auditoria, uso por módulo e controle. Acesso restrito ao administrador.
        </p>

        {erro && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 text-red-700 rounded-xl text-sm">
            {erro}
          </div>
        )}

        {loading && (
          <div className="flex justify-center py-20">
            <div className="w-10 h-10 border-2 border-[#0c3d66]/30 border-t-[#0c3d66] rounded-full animate-spin" />
          </div>
        )}

        {!loading && metricas && (
          <>
            {/* Resumo */}
            <section className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-10">
              <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
                <h2 className="text-sm font-medium text-slate-500 mb-1">Compras</h2>
                <p className="text-2xl font-bold text-[#0c3d66]">
                  {metricas.resumo?.compras?.total_creditos ?? 0} créditos
                </p>
                <p className="text-slate-500 text-sm mt-1">
                  {metricas.resumo?.compras?.registros ?? 0} registro(s)
                </p>
              </div>
              <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
                <h2 className="text-sm font-medium text-slate-500 mb-1">Consumo</h2>
                <p className="text-2xl font-bold text-amber-600">
                  {metricas.resumo?.consumo?.total_creditos ?? 0} créditos
                </p>
                <p className="text-slate-500 text-sm mt-1">
                  {metricas.resumo?.consumo?.registros ?? 0} registro(s)
                </p>
              </div>
            </section>

            {/* Uso por módulo */}
            <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm mb-10">
              <h2 className="text-xl font-semibold text-slate-800 mb-4">Uso por módulo</h2>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-slate-200 text-left text-slate-600">
                      <th className="pb-2 pr-4">Módulo</th>
                      <th className="pb-2 pr-4">Registros</th>
                      <th className="pb-2">Créditos</th>
                    </tr>
                  </thead>
                  <tbody>
                    {(metricas.por_modulo || []).map((row) => (
                      <tr key={row.modulo} className="border-b border-slate-100">
                        <td className="py-2 pr-4 font-medium">{row.modulo}</td>
                        <td className="py-2 pr-4">{row.qtd_registros}</td>
                        <td className="py-2">{row.total_creditos}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </section>

            {/* Últimos registros */}
            <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
              <h2 className="text-xl font-semibold text-slate-800 mb-4">Últimos registros (auditoria)</h2>
              <div className="overflow-x-auto max-h-96 overflow-y-auto">
                <table className="w-full text-sm">
                  <thead className="sticky top-0 bg-white">
                    <tr className="border-b border-slate-200 text-left text-slate-600">
                      <th className="pb-2 pr-2">Data</th>
                      <th className="pb-2 pr-2">Usuário</th>
                      <th className="pb-2 pr-2">Tipo</th>
                      <th className="pb-2 pr-2">Módulo</th>
                      <th className="pb-2 pr-2">Qtd</th>
                      <th className="pb-2">Créditos</th>
                    </tr>
                  </thead>
                  <tbody>
                    {(metricas.ultimos_registros || []).map((r) => (
                      <tr key={r.id} className="border-b border-slate-100">
                        <td className="py-1.5 pr-2 text-slate-500 whitespace-nowrap">
                          {r.criado_em ? new Date(r.criado_em).toLocaleString('pt-BR') : '-'}
                        </td>
                        <td className="py-1.5 pr-2">{r.email || r.nome || r.usuario_id}</td>
                        <td className="py-1.5 pr-2">{r.tipo}</td>
                        <td className="py-1.5 pr-2">{r.modulo ?? '-'}</td>
                        <td className="py-1.5 pr-2">{r.quantidade}</td>
                        <td className="py-1.5">{r.custo_total}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </section>
          </>
        )}
      </main>
    </div>
  );
}
