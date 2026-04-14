'use client';

import type { MetaAnalysisResponse } from '@/app/types/meta';

interface MetaStatsSummaryProps {
  result: MetaAnalysisResponse;
}

export default function MetaStatsSummary({ result }: MetaStatsSummaryProps) {
  if (!result.pooled_result || !result.heterogeneity) return null;
  const pooled = result.pooled_result;
  const heterogeneity = result.heterogeneity;

  return (
    <section className="rounded-xl border border-slate-200 bg-white p-5">
      <h3 className="mb-3 text-lg font-semibold text-slate-800">Resumo estatístico</h3>
      <div className="grid grid-cols-2 gap-3 text-sm md:grid-cols-4">
        <div className="rounded border p-2">Modelo: {pooled.model}</div>
        <div className="rounded border p-2">Efeito: {pooled.effect.toFixed(4)}</div>
        <div className="rounded border p-2">IC95%: {pooled.ci_low.toFixed(4)} a {pooled.ci_high.toFixed(4)}</div>
        <div className="rounded border p-2">p global: {pooled.p_value.toExponential(2)}</div>
        <div className="rounded border p-2">I²: {heterogeneity.I2.toFixed(2)}%</div>
        <div className="rounded border p-2">tau²: {heterogeneity.tau2.toFixed(4)}</div>
        <div className="rounded border p-2">Q: {heterogeneity.Q.toFixed(3)}</div>
        <div className="rounded border p-2">p heterogeneity: {heterogeneity.p_heterogeneity.toExponential(2)}</div>
      </div>
    </section>
  );
}

