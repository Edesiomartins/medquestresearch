'use client';

import { useEffect, useState } from 'react';

export interface ResultWindowData {
  id: string;
  tipo: string;
  titulo: string;
  resultado: string;
  loading: boolean;
  timestamp: number;
}

interface ResultWindowProps {
  window: ResultWindowData;
  onUpdate: (updates: Partial<ResultWindowData>) => void;
  onClose: () => void;
  token?: string;
}

export default function ResultWindow({
  window: windowData,
  onUpdate,
  onClose,
  token,
}: ResultWindowProps) {
  // ✅ Garantir que só renderiza no cliente
  const [mounted, setMounted] = useState(false);
  const [position, setPosition] = useState({ x: 0, y: 0 });

  useEffect(() => {
    setMounted(true);
    
    // ✅ Usar posição fixa baseada no índice para evitar Math.random() que causa problemas de hidratação
    // Acessar window global apenas no cliente
    if (typeof window !== 'undefined') {
      // Posição fixa no canto inferior direito para evitar problemas de hidratação
      setPosition({
        x: Math.max(0, window.innerWidth - 420),
        y: Math.max(0, window.innerHeight - 350),
      });
    }
  }, []);

  if (!mounted) {
    return null;
  }

  return (
    <div
      className="fixed bg-white rounded-lg shadow-lg border border-slate-200 w-96 max-h-96 flex flex-col"
      style={{
        left: `${position.x}px`,
        top: `${position.y}px`,
      }}
    >
      {/* Header */}
      <div className="bg-linear-to-r from-[#0c3d66] to-[#1e5a96] text-white p-4 rounded-t-lg flex justify-between items-center">
        <h3 className="font-bold text-sm truncate">{windowData.titulo}</h3>
        <button
          onClick={onClose}
          className="text-white hover:bg-white/20 rounded px-2 py-1 transition-colors"
        >
          ✕
        </button>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-4 text-sm text-slate-700 whitespace-pre-wrap">
        {windowData.loading ? (
          <div className="flex items-center justify-center h-full">
            <div className="animate-spin">⏳</div>
          </div>
        ) : (
          windowData.resultado
        )}
      </div>

      {/* Footer */}
      <div className="border-t border-slate-200 p-3 bg-slate-50 rounded-b-lg text-xs text-slate-500 flex items-center justify-between gap-2">
        <span>{new Date(windowData.timestamp).toLocaleTimeString('pt-BR')}</span>
        {windowData.tipo === 'escrever_artigo' && windowData.resultado && !windowData.loading && (
          <button
            onClick={() => {
              const blob = new Blob([windowData.resultado], { type: 'text/plain;charset=utf-8' });
              const url = URL.createObjectURL(blob);
              const a = document.createElement('a');
              a.href = url;
              a.download = `artigo_metanalise_${Date.now()}.txt`;
              a.click();
              URL.revokeObjectURL(url);
            }}
            className="px-2 py-1 rounded bg-slate-200 hover:bg-slate-300 text-slate-700 transition-colors"
          >
            ⬇ Baixar .txt
          </button>
        )}
      </div>
    </div>
  );
}
