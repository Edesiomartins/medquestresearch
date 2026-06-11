'use client';

import { useState } from 'react';

interface StudyUploadPanelProps {
  loading: boolean;
  onUpload: (files: File[]) => Promise<void>;
}

export default function StudyUploadPanel({ loading, onUpload }: StudyUploadPanelProps) {
  const [files, setFiles] = useState<File[]>([]);

  return (
    <section className="rounded-xl border border-slate-200 bg-white p-5">
      <h3 className="mb-3 text-lg font-semibold text-slate-800">Ingestão de estudos</h3>
      <p className="mb-4 text-sm text-slate-600">
        Envie múltiplos PDFs/DOCX. A IA extrai automaticamente PICO, desenho e dados numéricos dos
        desfechos de cada artigo para sua revisão — a extração pode levar até ~1 minuto por artigo.
      </p>
      <input
        type="file"
        multiple
        accept=".pdf,.docx"
        onChange={(event) => setFiles(Array.from(event.target.files || []))}
        className="mb-4 block w-full text-sm"
      />
      <button
        type="button"
        disabled={loading || files.length === 0}
        onClick={() => onUpload(files)}
        className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white disabled:opacity-50"
      >
        {loading ? 'Processando upload...' : `Upload e extração (${files.length})`}
      </button>
    </section>
  );
}

