'use client';

import type { ArticleSections } from '@/app/types/meta';

interface ArticleWriterPanelProps {
  sections: ArticleSections;
}

export default function ArticleWriterPanel({ sections }: ArticleWriterPanelProps) {
  const entries = Object.entries(sections).filter(([, value]) => value);
  if (entries.length === 0) return null;
  return (
    <section className="rounded-xl border border-slate-200 bg-white p-5">
      <h3 className="mb-3 text-lg font-semibold text-slate-800">Manuscrito gerado</h3>
      <div className="space-y-4">
        {entries.map(([section, content]) => (
          <article key={section} className="rounded border border-slate-200 p-3">
            <h4 className="mb-2 text-sm font-semibold uppercase text-slate-700">{section}</h4>
            <p className="whitespace-pre-wrap text-sm text-slate-700">{content}</p>
          </article>
        ))}
      </div>
    </section>
  );
}

