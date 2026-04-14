'use client';

interface FunnelPlotViewerProps {
  svg?: string | null;
}

export default function FunnelPlotViewer({ svg }: FunnelPlotViewerProps) {
  if (!svg) return null;
  return (
    <section className="rounded-xl border border-slate-200 bg-white p-5">
      <h3 className="mb-3 text-lg font-semibold text-slate-800">Funnel plot</h3>
      <div className="overflow-x-auto" dangerouslySetInnerHTML={{ __html: svg }} />
    </section>
  );
}

