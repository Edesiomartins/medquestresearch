'use client';

import type { PrismaPanelData } from '@/app/types/meta';

interface PrismaFlowPanelProps {
  prisma: PrismaPanelData;
}

export default function PrismaFlowPanel({ prisma }: PrismaFlowPanelProps) {
  return (
    <section className="rounded-xl border border-slate-200 bg-white p-5">
      <h3 className="mb-3 text-lg font-semibold text-slate-800">Fluxo PRISMA</h3>
      <div className="grid grid-cols-2 gap-3 text-sm md:grid-cols-4">
        <div className="rounded border p-2">Identificados: {prisma.identified}</div>
        <div className="rounded border p-2">Triados: {prisma.screened}</div>
        <div className="rounded border p-2">Elegíveis: {prisma.eligible}</div>
        <div className="rounded border p-2">Incluídos: {prisma.included}</div>
      </div>
      {prisma.excluded_reasons.length > 0 && (
        <ul className="mt-3 list-disc pl-5 text-xs text-slate-600">
          {prisma.excluded_reasons.map((item) => (
            <li key={`${item.study_id}-${item.reason}`}>
              {item.study_id}: {item.reason}
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}

