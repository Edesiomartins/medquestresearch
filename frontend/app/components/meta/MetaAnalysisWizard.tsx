'use client';

import { useMemo, useState } from 'react';

import { analyzeMeta, exportMetaDocx, exportMetaZip, reviewMetaStudies, uploadMetaFiles } from '@/app/lib/meta-api';
import type { MetaAnalysisResponse, StudyExtraction } from '@/app/types/meta';

import ArticleWriterPanel from './ArticleWriterPanel';
import EffectsTablePanel from './EffectsTablePanel';
import ExtractionReviewTable from './ExtractionReviewTable';
import ForestPlotViewer from './ForestPlotViewer';
import FunnelPlotViewer from './FunnelPlotViewer';
import MetaStatsSummary from './MetaStatsSummary';
import MetaStepper from './MetaStepper';
import PublicationBiasPanel from './PublicationBiasPanel';
import PrismaFlowPanel from './PrismaFlowPanel';
import SensitivityAnalysisPanel from './SensitivityAnalysisPanel';
import StudySelectionTable from './StudySelectionTable';
import StudyUploadPanel from './StudyUploadPanel';
import SubgroupResultsPanel from './SubgroupResultsPanel';

interface MetaAnalysisWizardProps {
  token: string;
}

type WizardStep = 'upload' | 'review' | 'analysis' | 'results';

export default function MetaAnalysisWizard({ token }: MetaAnalysisWizardProps) {
  const [step, setStep] = useState<WizardStep>('upload');
  const [projectId, setProjectId] = useState<string>('');
  const [question, setQuestion] = useState('');
  const [effectMeasure, setEffectMeasure] = useState<'SMD' | 'log_RR' | 'log_OR'>('SMD');
  const [model, setModel] = useState<'fixed' | 'random_DL' | 'random_REML' | 'random_PM'>('random_REML');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [studies, setStudies] = useState<StudyExtraction[]>([]);
  const [reviewNotes, setReviewNotes] = useState<string[]>([]);
  const [result, setResult] = useState<MetaAnalysisResponse | null>(null);

  const steps = useMemo(
    () => [
      { key: 'upload', label: 'A. Ingestão' },
      { key: 'review', label: 'B-C. Extração/Revisão' },
      { key: 'analysis', label: 'D-F. Modelagem/Pooling' },
      { key: 'results', label: 'G-H. Síntese/Manuscrito' },
    ],
    [],
  );

  const handleUpload = async (files: File[]) => {
    setLoading(true);
    setError(null);
    try {
      const payload = await uploadMetaFiles(token, files);
      setProjectId(payload.project_id);
      setStudies(payload.studies);
      setReviewNotes(payload.notes || []);
      setStep('review');
    } catch (uploadError: any) {
      setError(uploadError.message || 'Falha no upload.');
    } finally {
      setLoading(false);
    }
  };

  const handleReview = async () => {
    setLoading(true);
    setError(null);
    try {
      const payload = await reviewMetaStudies(token, projectId, studies);
      setStudies(payload.studies);
      setReviewNotes(payload.notes || []);
      setStep('analysis');
    } catch (reviewError: any) {
      setError(reviewError.message || 'Falha ao salvar revisão.');
    } finally {
      setLoading(false);
    }
  };

  const handleAnalyze = async () => {
    setLoading(true);
    setError(null);
    const includedCount = studies.filter((row) => row.included).length;
    if (includedCount < 2) {
      setError('Inclua pelo menos 2 estudos na revisão para executar metanálise.');
      setLoading(false);
      return;
    }
    try {
      const payload = await analyzeMeta(token, {
        project_id: projectId,
        question,
        effect_measure: effectMeasure,
        model_used: model,
        studies,
        generate_article: true,
      });
      setResult(payload);
      setStep('results');
    } catch (analysisError: any) {
      setError(analysisError.message || 'Falha na análise.');
    } finally {
      setLoading(false);
    }
  };

  const handleExportDocx = async () => {
    if (!projectId || !studies.length) return;
    setLoading(true);
    setError(null);
    try {
      const blob = await exportMetaDocx(token, {
        project_id: projectId,
        question,
        effect_measure: effectMeasure,
        model_used: model,
        studies,
        generate_article: true,
      });
      const url = URL.createObjectURL(blob);
      const anchor = document.createElement('a');
      anchor.href = url;
      anchor.download = `meta_analise_${projectId}.docx`;
      document.body.appendChild(anchor);
      anchor.click();
      anchor.remove();
      URL.revokeObjectURL(url);
    } catch (exportError: any) {
      setError(exportError.message || 'Falha ao exportar DOCX.');
    } finally {
      setLoading(false);
    }
  };

  const handleExportZip = async () => {
    if (!projectId || !studies.length) return;
    setLoading(true);
    setError(null);
    try {
      const blob = await exportMetaZip(token, {
        project_id: projectId,
        question,
        effect_measure: effectMeasure,
        model_used: model,
        studies,
        generate_article: true,
      });
      const url = URL.createObjectURL(blob);
      const anchor = document.createElement('a');
      anchor.href = url;
      anchor.download = `submission_${projectId}.zip`;
      document.body.appendChild(anchor);
      anchor.click();
      anchor.remove();
      URL.revokeObjectURL(url);
    } catch (exportError: any) {
      setError(exportError.message || 'Falha ao exportar ZIP.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-5">
      <MetaStepper steps={steps} activeKey={step} />

      {error && <div className="rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-700">{error}</div>}

      {step === 'upload' && <StudyUploadPanel loading={loading} onUpload={handleUpload} />}

      {step === 'review' && (
        <div className="space-y-4">
          {reviewNotes.length > 0 && (
            <div className="rounded-lg border border-amber-200 bg-amber-50 p-3 text-xs text-amber-900">
              {reviewNotes.map((note, index) => (
                <p key={index}>- {note}</p>
              ))}
            </div>
          )}
          <ExtractionReviewTable studies={studies} onChange={setStudies} />
          <StudySelectionTable studies={studies} />
          <button
            type="button"
            onClick={handleReview}
            disabled={loading}
            className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white"
          >
            Confirmar revisão e avançar
          </button>
        </div>
      )}

      {step === 'analysis' && (
        <section className="rounded-xl border border-slate-200 bg-white p-5">
          <h3 className="mb-3 text-lg font-semibold text-slate-800">Configuração da metanálise</h3>
          <div className="grid grid-cols-1 gap-3 md:grid-cols-3">
            <input
              value={question}
              onChange={(event) => setQuestion(event.target.value)}
              placeholder="Pergunta clínica / questão da revisão"
              className="rounded-lg border border-slate-300 px-3 py-2 text-sm md:col-span-3"
            />
            <select value={effectMeasure} onChange={(event) => setEffectMeasure(event.target.value as any)} className="rounded-lg border border-slate-300 px-3 py-2 text-sm">
              <option value="SMD">SMD (Hedges g)</option>
              <option value="log_RR">log RR</option>
              <option value="log_OR">log OR</option>
            </select>
            <select value={model} onChange={(event) => setModel(event.target.value as any)} className="rounded-lg border border-slate-300 px-3 py-2 text-sm">
              <option value="fixed">Fixed</option>
              <option value="random_DL">Random DL</option>
              <option value="random_REML">Random REML</option>
              <option value="random_PM">Random Paule-Mandel</option>
            </select>
            <button type="button" onClick={handleAnalyze} disabled={loading} className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white">
              {loading ? 'Executando análise...' : 'Executar metanálise'}
            </button>
          </div>
        </section>
      )}

      {step === 'results' && result && (
        <div className="space-y-4">
          {result.warnings.length > 0 && (
            <div className="rounded-lg border border-amber-200 bg-amber-50 p-3 text-xs text-amber-900">
              {result.warnings.map((warning, index) => (
                <p key={index}>- {warning}</p>
              ))}
            </div>
          )}
          <div className="flex justify-end">
            <div className="flex gap-2">
              <button
                type="button"
                onClick={handleExportDocx}
                disabled={loading}
                className="rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white disabled:opacity-50"
              >
                Exportar em DOCX
              </button>
              <button
                type="button"
                onClick={handleExportZip}
                disabled={loading}
                className="rounded-lg bg-emerald-600 px-4 py-2 text-sm font-medium text-white disabled:opacity-50"
              >
                Exportar pacote ZIP
              </button>
            </div>
          </div>
          <MetaStatsSummary result={result} />
          <EffectsTablePanel rows={result.effects_table} />
          <PrismaFlowPanel prisma={result.prisma} />
          <PublicationBiasPanel data={result.publication_bias} />
          <SubgroupResultsPanel data={result.subgroups} />
          <ForestPlotViewer svg={result.forest_plot_svg} />
          <FunnelPlotViewer svg={result.funnel_plot_svg} />
          <SensitivityAnalysisPanel data={result.leave_one_out} />
          <ArticleWriterPanel sections={result.article_sections} />
        </div>
      )}
    </div>
  );
}

