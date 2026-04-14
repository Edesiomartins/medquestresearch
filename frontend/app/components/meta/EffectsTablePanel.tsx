'use client';

import type { EffectSizeRow } from '@/app/types/meta';

interface EffectsTablePanelProps {
  rows: EffectSizeRow[];
}

export default function EffectsTablePanel({ rows }: EffectsTablePanelProps) {
  if (!rows.length) return null;
  return (
    <section className="rounded-xl border border-slate-200 bg-white p-5">
      <h3 className="mb-3 text-lg font-semibold text-slate-800">Tabela de efeitos</h3>
      <div className="overflow-x-auto">
        <table className="min-w-full text-xs">
          <thead>
            <tr className="text-left text-slate-500">
              <th className="pb-2">Estudo</th>
              <th className="pb-2">Efeito</th>
              <th className="pb-2">SE</th>
              <th className="pb-2">IC95%</th>
              <th className="pb-2">Peso fixo</th>
              <th className="pb-2">Peso random</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((row) => (
              <tr key={`${row.study_id}-${row.effect}`} className="border-t border-slate-100">
                <td className="py-2">{row.citation}</td>
                <td className="py-2">{row.effect.toFixed(4)}</td>
                <td className="py-2">{row.standard_error.toFixed(4)}</td>
                <td className="py-2">
                  {row.ci_low.toFixed(4)} a {row.ci_high.toFixed(4)}
                </td>
                <td className="py-2">{row.weight_fixed?.toFixed(4) ?? '-'}</td>
                <td className="py-2">{row.weight_random?.toFixed(4) ?? '-'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}

