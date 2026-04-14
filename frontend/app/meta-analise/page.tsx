'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';

import MetaAnalysisWizard from '@/app/components/meta/MetaAnalysisWizard';
import Sidebar from '@/app/components/ui/sidebar';
import { useAuth } from '@/app/lib/hooks/useAuth';

export default function MetaAnalisePage() {
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
        <p className="text-xl">Carregando módulo de metanálise...</p>
      </div>
    );
  }

  return (
    <div className="flex min-h-screen bg-slate-50">
      <Sidebar usuario={usuario} creditos={creditos} onLogout={logout} token={token} />
      <main className="ml-64 flex-1 p-6">
        <header className="mb-4 flex items-start justify-between gap-3">
          <div>
            <h1 className="text-2xl font-bold text-[#0c3d66]">Pipeline de Metanálise Científica</h1>
            <p className="text-sm text-slate-600">
              Fluxo estruturado com ingestão, revisão humana, modelagem estatística e redação por seções.
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
        <MetaAnalysisWizard token={token} />
      </main>
    </div>
  );
}
