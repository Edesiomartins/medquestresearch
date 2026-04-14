'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';

import Sidebar from '@/app/components/ui/sidebar';
import HelpAssistant from '@/app/components/ui/HelpAssistant';
import { useAuth } from '@/app/lib/hooks/useAuth';

const GLOSSARY: Array<{ sigla: string; significado: string }> = [
  { sigla: 'PRISMA', significado: 'Preferred Reporting Items for Systematic Reviews and Meta-Analyses; diretriz de transparência para revisões sistemáticas.' },
  { sigla: 'PICO', significado: 'Paciente/População, Intervenção, Comparador e Outcome (desfecho); estrutura para formular pergunta clínica.' },
  { sigla: 'SMD', significado: 'Standardized Mean Difference (diferença média padronizada), usada em desfechos contínuos.' },
  { sigla: 'RR', significado: 'Risk Ratio (razão de risco), compara riscos entre grupo intervenção e comparador.' },
  { sigla: 'OR', significado: 'Odds Ratio (razão de chances), compara odds/chances entre grupos.' },
  { sigla: 'IC95%', significado: 'Intervalo de confiança de 95%; faixa de plausibilidade da estimativa de efeito.' },
  { sigla: 'I²', significado: 'Percentual da heterogeneidade entre estudos não explicada pelo acaso.' },
  { sigla: 'tau²', significado: 'Variância entre estudos em modelos de efeitos aleatórios.' },
  { sigla: 'DL', significado: 'DerSimonian-Laird, método clássico para estimar heterogeneidade em efeitos aleatórios.' },
  { sigla: 'REML', significado: 'Restricted Maximum Likelihood; método para estimar tau² com boa robustez.' },
  { sigla: 'PM', significado: 'Paule-Mandel; método alternativo para estimativa da heterogeneidade (tau²).' },
  { sigla: 'Egger', significado: 'Teste estatístico para investigar assimetria no funnel plot (possível viés de publicação).' },
  { sigla: 'Begg', significado: 'Teste de correlação para avaliar viés de publicação.' },
];

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

            <article id="glossario" className="rounded-xl border border-slate-200 bg-white p-5">
              <h2 className="mb-2 text-lg font-semibold text-slate-800">Glossário completo de siglas</h2>
              <p className="mb-3 text-sm text-slate-600">
                Use esta tabela para interpretar os termos estatísticos e metodológicos exibidos no app.
              </p>
              <div className="overflow-x-auto">
                <table className="min-w-full text-sm">
                  <thead>
                    <tr className="text-left text-slate-500">
                      <th className="border-b pb-2 pr-3">Sigla</th>
                      <th className="border-b pb-2">Significado</th>
                    </tr>
                  </thead>
                  <tbody>
                    {GLOSSARY.map((item) => (
                      <tr key={item.sigla} className="border-b border-slate-100 align-top">
                        <td className="py-2 pr-3 font-semibold text-slate-800">{item.sigla}</td>
                        <td className="py-2 text-slate-700">{item.significado}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </article>
          </section>

          <HelpAssistant token={token} />
        </div>
      </main>
    </div>
  );
}

