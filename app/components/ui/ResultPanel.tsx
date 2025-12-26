// app/components/ui/ResultPanel.tsx
'use client';

interface ResultPanelProps {
  loading: boolean;
  titulo: string;
  resultado: string | null;
}

export default function ResultPanel({ loading, titulo, resultado }: ResultPanelProps) {
  // Estado: processing - mostrar spinner e texto contextual
  if (loading && resultado && resultado.includes('⏳ Análise em andamento')) {
    return (
      <div className="card-elevated">
        <div className="py-8">
          <div className="text-center mb-6">
            <div className="animate-pulse-blue text-4xl mb-4">⏳</div>
            <div className="whitespace-pre-wrap text-base text-slate-700 font-sans leading-relaxed">
              {resultado}
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Estado: error - mostrar erro formatado
  if (resultado && resultado.startsWith('❌')) {
    return (
      <div className="card-elevated">
        <h2 className="text-2xl font-bold text-red-600 mb-4">{titulo}</h2>
        <div className="prose max-w-none">
          <div className="whitespace-pre-wrap text-sm text-red-700 bg-red-50 p-4 rounded-lg border border-red-200 overflow-x-auto font-sans leading-relaxed">
            {resultado}
          </div>
        </div>
      </div>
    );
  }

  // Estado: done - mostrar resultado no painel direito (sem alert)
  if (resultado) {
    return (
      <div className="card-elevated">
        <h2 className="text-2xl font-bold text-[#0c3d66] mb-4">{titulo}</h2>
        <div className="prose max-w-none">
          <div className="whitespace-pre-wrap text-sm text-slate-700 bg-slate-50 p-4 rounded-lg border border-slate-200 overflow-x-auto font-sans leading-relaxed break-words overflow-y-auto max-h-[calc(100vh-200px)]">
            {resultado}
          </div>
        </div>
      </div>
    );
  }

  // Estado inicial - nenhum resultado
  return (
    <div className="card-elevated">
      <div className="text-center py-12 text-slate-500">
        <p className="text-lg mb-2">📋 Nenhum resultado ainda</p>
        <p className="text-sm">Faça upload de um arquivo e escolha uma análise</p>
      </div>
    </div>
  );
}