'use client';

import type { StudyExtraction } from '@/app/types/meta';

interface StudySelectionTableProps {
  studies: StudyExtraction[];
}

export default function StudySelectionTable({ studies }: StudySelectionTableProps) {
  return (
    <section className="rounded-xl border border-slate-200 bg-white p-5">
      <h3 className="mb-3 text-lg font-semibold text-slate-800">Estudos elegíveis</h3>
      <div className="overflow-x-auto">
        <table className="min-w-full text-sm">
          <thead>
            <tr className="text-left text-slate-500">
              <th className="pb-2">Study ID</th>
              <th className="pb-2">Citação</th>
              <th className="pb-2">Ano</th>
              <th className="pb-2">Incluído</th>
            </tr>
          </thead>
          <tbody>
            {studies.map((study) => (
              <tr key={study.study_id} className="border-t border-slate-100">
                <td className="py-2 pr-3">{study.study_id}</td>
                <td className="py-2 pr-3">{study.citation}</td>
                <td className="py-2 pr-3">{study.year ?? '-'}</td>
                <td className="py-2">{study.included ? 'Sim' : 'Não'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}

