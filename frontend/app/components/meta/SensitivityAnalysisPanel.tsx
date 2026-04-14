'use client';

import type { LeaveOneOutResult } from '@/app/types/meta';

interface SensitivityAnalysisPanelProps {
  data: LeaveOneOutResult[];
}

export default function SensitivityAnalysisPanel({ data }: SensitivityAnalysisPanelProps) {
  if (!data.length) return null;
  return (
    <section className="rounded-xl border border-slate-200 bg-white p-5">
      <h3 className="mb-3 text-lg font-semibold text-slate-800">Análise de sensibilidade (leave-one-out)</h3>
      <div className="overflow-x-auto">
        <table className="min-w-full text-xs">
          <thead>
            <tr className="text-left text-slate-500">
              <th className="pb-2">Estudo removido</th>
              <th className="pb-2">Efeito</th>
              <th className="pb-2">IC95%</th>
              <th className="pb-2">I²</th>
              <th className="pb-2">Delta</th>
            </tr>
          </thead>
          <tbody>
            {data.map((row) => (
              <tr key={row.removed_study_id} className="border-t border-slate-100">
                <td className="py-2">{row.removed_study_id}</td>
                <td className="py-2">{row.pooled_effect.toFixed(4)}</td>
                <td className="py-2">{row.pooled_ci_low.toFixed(4)} a {row.pooled_ci_high.toFixed(4)}</td>
                <td className="py-2">{row.I2.toFixed(2)}%</td>
                <td className="py-2">{row.delta_effect.toFixed(4)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}

