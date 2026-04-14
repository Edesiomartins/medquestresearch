'use client';

import type { PublicationBiasResult } from '@/app/types/meta';

interface PublicationBiasPanelProps {
  data?: PublicationBiasResult;
}

export default function PublicationBiasPanel({ data }: PublicationBiasPanelProps) {
  if (!data) return null;
  return (
    <section className="rounded-xl border border-slate-200 bg-white p-5">
      <h3 className="mb-3 text-lg font-semibold text-slate-800">Viés de publicação</h3>
      <div className="grid grid-cols-1 gap-3 text-sm md:grid-cols-3">
        <div className="rounded border p-2">Egger p: {data.egger_p ?? 'N/D'}</div>
        <div className="rounded border p-2">Begg p: {data.begg_p ?? 'N/D'}</div>
        <div className="rounded border p-2">Interpretação: {data.interpretation || 'N/D'}</div>
      </div>
    </section>
  );
}

