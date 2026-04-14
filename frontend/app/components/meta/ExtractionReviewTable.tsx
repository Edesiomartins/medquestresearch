'use client';

import type { StudyExtraction } from '@/app/types/meta';

interface ExtractionReviewTableProps {
  studies: StudyExtraction[];
  onChange: (next: StudyExtraction[]) => void;
}

export default function ExtractionReviewTable({ studies, onChange }: ExtractionReviewTableProps) {
  const toggleIncluded = (studyId: string) => {
    const next = studies.map((item) =>
      item.study_id === studyId
        ? {
            ...item,
            included: !item.included,
            exclusion_reason: item.included ? item.exclusion_reason || 'Excluído na revisão manual.' : undefined,
          }
        : item,
    );
    onChange(next);
  };

  const updateExclusionReason = (studyId: string, reason: string) => {
    const next = studies.map((item) =>
      item.study_id === studyId ? { ...item, exclusion_reason: reason } : item,
    );
    onChange(next);
  };

  const updateOutcomeNumericField = (
    studyId: string,
    outcomeId: string,
    field:
      | 'intervention_mean'
      | 'intervention_sd'
      | 'intervention_events'
      | 'intervention_total'
      | 'comparator_mean'
      | 'comparator_sd'
      | 'comparator_events'
      | 'comparator_total',
    value: string,
  ) => {
    const parsed = value.trim() === '' ? undefined : Number(value);
    const next = studies.map((study) => {
      if (study.study_id !== studyId) return study;
      return {
        ...study,
        outcomes: study.outcomes.map((outcome) =>
          outcome.outcome_id === outcomeId
            ? {
                ...outcome,
                [field]: Number.isNaN(parsed) ? undefined : parsed,
              }
            : outcome,
        ),
      };
    });
    onChange(next);
  };

  return (
    <section className="rounded-xl border border-slate-200 bg-white p-5">
      <h3 className="mb-3 text-lg font-semibold text-slate-800">Revisão humana da extração</h3>
      <p className="mb-4 text-sm text-slate-600">
        Ajuste quais estudos entram no pooling. Snippets e page hints ficam nos objetos para rastreabilidade.
      </p>
      <div className="space-y-3">
        {studies.map((study) => (
          <article key={study.study_id} className="rounded-lg border border-slate-200 p-3">
            <div className="flex items-start justify-between gap-3">
              <div>
                <p className="font-medium text-slate-900">{study.citation}</p>
                <p className="text-xs text-slate-500">{study.study_id}</p>
              </div>
              <button
                type="button"
                onClick={() => toggleIncluded(study.study_id)}
                className={`rounded px-3 py-1 text-xs font-semibold ${
                  study.included ? 'bg-emerald-100 text-emerald-800' : 'bg-red-100 text-red-800'
                }`}
              >
                {study.included ? 'Incluído' : 'Excluído'}
              </button>
            </div>
            <p className="mt-2 text-xs text-slate-600">
              Outcomes: {study.outcomes.map((outcome) => outcome.outcome_name).join(', ') || 'N/D'}
            </p>
            {!study.included && (
              <div className="mt-3">
                <label className="mb-1 block text-xs font-medium text-slate-600">Motivo da exclusão</label>
                <input
                  type="text"
                  value={study.exclusion_reason || ''}
                  onChange={(event) => updateExclusionReason(study.study_id, event.target.value)}
                  className="w-full rounded border border-slate-300 px-2 py-1 text-xs"
                  placeholder="Ex: dados incompletos para pooling"
                />
              </div>
            )}

            <div className="mt-3 space-y-3 rounded border border-slate-100 bg-slate-50 p-2">
              {study.outcomes.map((outcome) => (
                <div key={outcome.outcome_id} className="rounded border border-slate-200 bg-white p-2">
                  <p className="text-xs font-semibold text-slate-700">{outcome.outcome_name}</p>
                  <p className="mt-1 text-[11px] text-slate-500">
                    Tipo: {outcome.outcome_type} | Measure: {outcome.measure_type || 'N/D'}
                  </p>
                  <div className="mt-2 grid grid-cols-2 gap-2 text-xs md:grid-cols-4">
                    <input
                      type="number"
                      step="any"
                      placeholder="Mean intervenção"
                      value={outcome.intervention_mean ?? ''}
                      onChange={(event) =>
                        updateOutcomeNumericField(study.study_id, outcome.outcome_id, 'intervention_mean', event.target.value)
                      }
                      className="rounded border border-slate-300 px-2 py-1"
                    />
                    <input
                      type="number"
                      step="any"
                      placeholder="SD intervenção"
                      value={outcome.intervention_sd ?? ''}
                      onChange={(event) =>
                        updateOutcomeNumericField(study.study_id, outcome.outcome_id, 'intervention_sd', event.target.value)
                      }
                      className="rounded border border-slate-300 px-2 py-1"
                    />
                    <input
                      type="number"
                      step="1"
                      placeholder="Eventos intervenção"
                      value={outcome.intervention_events ?? ''}
                      onChange={(event) =>
                        updateOutcomeNumericField(study.study_id, outcome.outcome_id, 'intervention_events', event.target.value)
                      }
                      className="rounded border border-slate-300 px-2 py-1"
                    />
                    <input
                      type="number"
                      step="1"
                      placeholder="Total intervenção"
                      value={outcome.intervention_total ?? ''}
                      onChange={(event) =>
                        updateOutcomeNumericField(study.study_id, outcome.outcome_id, 'intervention_total', event.target.value)
                      }
                      className="rounded border border-slate-300 px-2 py-1"
                    />
                    <input
                      type="number"
                      step="any"
                      placeholder="Mean comparador"
                      value={outcome.comparator_mean ?? ''}
                      onChange={(event) =>
                        updateOutcomeNumericField(study.study_id, outcome.outcome_id, 'comparator_mean', event.target.value)
                      }
                      className="rounded border border-slate-300 px-2 py-1"
                    />
                    <input
                      type="number"
                      step="any"
                      placeholder="SD comparador"
                      value={outcome.comparator_sd ?? ''}
                      onChange={(event) =>
                        updateOutcomeNumericField(study.study_id, outcome.outcome_id, 'comparator_sd', event.target.value)
                      }
                      className="rounded border border-slate-300 px-2 py-1"
                    />
                    <input
                      type="number"
                      step="1"
                      placeholder="Eventos comparador"
                      value={outcome.comparator_events ?? ''}
                      onChange={(event) =>
                        updateOutcomeNumericField(study.study_id, outcome.outcome_id, 'comparator_events', event.target.value)
                      }
                      className="rounded border border-slate-300 px-2 py-1"
                    />
                    <input
                      type="number"
                      step="1"
                      placeholder="Total comparador"
                      value={outcome.comparator_total ?? ''}
                      onChange={(event) =>
                        updateOutcomeNumericField(study.study_id, outcome.outcome_id, 'comparator_total', event.target.value)
                      }
                      className="rounded border border-slate-300 px-2 py-1"
                    />
                  </div>
                  <div className="mt-2 grid grid-cols-1 gap-2 text-[11px] text-slate-600 md:grid-cols-2">
                    <div>
                      <p className="font-medium text-slate-700">Evidence snippets</p>
                      <ul className="list-disc pl-4">
                        {outcome.evidence_snippets.map((snippet, idx) => (
                          <li key={idx}>{snippet}</li>
                        ))}
                      </ul>
                    </div>
                    <div>
                      <p className="font-medium text-slate-700">Page hints</p>
                      <ul className="list-disc pl-4">
                        {outcome.page_hints.map((hint, idx) => (
                          <li key={idx}>{hint}</li>
                        ))}
                      </ul>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </article>
        ))}
      </div>
    </section>
  );
}

