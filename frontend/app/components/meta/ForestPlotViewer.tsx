'use client';

interface ForestPlotViewerProps {
  svg?: string | null;
}

export default function ForestPlotViewer({ svg }: ForestPlotViewerProps) {
  if (!svg) return null;
  return (
    <section className="rounded-xl border border-slate-200 bg-white p-5">
      <h3 className="mb-3 text-lg font-semibold text-slate-800">Forest plot</h3>
      <div className="overflow-x-auto" dangerouslySetInnerHTML={{ __html: svg }} />
    </section>
  );
}

