'use client';

import type { SubgroupResult } from '@/app/types/meta';

interface SubgroupResultsPanelProps {
  data: SubgroupResult[];
}

export default function SubgroupResultsPanel({ data }: SubgroupResultsPanelProps) {
  if (!data.length) return null;
  return (
    <section className="rounded-xl border border-slate-200 bg-white p-5">
      <h3 className="mb-3 text-lg font-semibold text-slate-800">Análise por subgrupos</h3>
      <div className="overflow-x-auto">
        <table className="min-w-full text-xs">
          <thead>
            <tr className="text-left text-slate-500">
              <th className="pb-2">Subgrupo</th>
              <th className="pb-2">Efeito</th>
              <th className="pb-2">IC95%</th>
              <th className="pb-2">I²</th>
              <th className="pb-2">k</th>
            </tr>
          </thead>
          <tbody>
            {data.map((row) => (
              <tr key={row.subgroup} className="border-t border-slate-100">
                <td className="py-2">{row.subgroup}</td>
                <td className="py-2">{row.pooled_result.effect.toFixed(4)}</td>
                <td className="py-2">
                  {row.pooled_result.ci_low.toFixed(4)} a {row.pooled_result.ci_high.toFixed(4)}
                </td>
                <td className="py-2">{row.heterogeneity.I2.toFixed(2)}%</td>
                <td className="py-2">{row.pooled_result.k}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}

