'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';

import Sidebar from '@/app/components/ui/sidebar';
import HelpAssistant from '@/app/components/ui/HelpAssistant';
import { useAuth } from '@/app/lib/hooks/useAuth';

export default function ManualPage() {
  const router = useRouter();
  const { token, usuario, creditos, loading, logout } = useAuth();

  useEffect(() => {
    if (!loading && !token) {
      router.replace('/login');
    }
  }, [loading, token, router]);

  if (loading || !token) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-mq-blue-900 text-white">
        <p className="text-xl">Carregando manual...</p>
      </div>
    );
  }

  return (
    <div className="flex min-h-screen bg-slate-50">
      <Sidebar usuario={usuario} creditos={creditos} onLogout={logout} token={token} />
      <main className="ml-64 flex-1 p-6">
        <header className="mb-4 flex items-start justify-between gap-3">
          <div>
            <h1 className="text-2xl font-bold text-[#0c3d66]">Manual do Usuário</h1>
            <p className="text-sm text-slate-600">
              Guia de funcionalidades do webapp e suporte com chatbot de ajuda.
            </p>
          </div>
          <button
            type="button"
            onClick={() => router.push('/')}
            className="rounded-lg bg-slate-200 px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-300"
          >
            Voltar ao dashboard
          </button>
        </header>

        <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
          <section className="space-y-4 lg:col-span-2">
            <article className="rounded-xl border border-slate-200 bg-white p-5">
              <h2 className="mb-2 text-lg font-semibold text-slate-800">Fluxo principal do app</h2>
              <ul className="list-disc space-y-1 pl-5 text-sm text-slate-700">
                <li>A. Ingestão de artigos em PDF/DOCX</li>
                <li>B-C. Extração estruturada + revisão humana</li>
                <li>D-F. Configuração da metanálise e pooling estatístico</li>
                <li>G-H. Síntese narrativa, manuscrito e exportações</li>
              </ul>
            </article>

            <article className="rounded-xl border border-slate-200 bg-white p-5">
              <h2 className="mb-2 text-lg font-semibold text-slate-800">Como resolver warnings comuns</h2>
              <p className="mb-2 text-sm text-slate-700">
                Se aparecer “Pooling quantitativo indisponível por falta de dados completos”, volte para B-C e revise os campos numéricos dos outcomes.
              </p>
              <ul className="list-disc space-y-1 pl-5 text-sm text-slate-700">
                <li>Para SMD: preencher mean/sd/total em intervenção e comparador.</li>
                <li>Para log RR/log OR: preencher events/total em intervenção e comparador.</li>
                <li>Manter pelo menos 2 estudos incluídos e aptos para pooling.</li>
              </ul>
            </article>

            <article className="rounded-xl border border-slate-200 bg-white p-5">
              <h2 className="mb-2 text-lg font-semibold text-slate-800">Exportações</h2>
              <ul className="list-disc space-y-1 pl-5 text-sm text-slate-700">
                <li>DOCX: manuscrito consolidado.</li>
                <li>ZIP de submissão: DOCX + JSON + CSV + plots SVG + narrativa + README.</li>
              </ul>
            </article>
          </section>

          <HelpAssistant token={token} />
        </div>
      </main>
    </div>
  );
}

