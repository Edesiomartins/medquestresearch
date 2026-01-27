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
    
    // ✅ Acessar window global apenas no cliente (renomeado para evitar conflito)
    if (typeof window !== 'undefined') {
      setPosition({
        x: Math.random() * (window.innerWidth - 400),
        y: Math.random() * (window.innerHeight - 300),
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
      <div className="border-t border-slate-200 p-3 bg-slate-50 rounded-b-lg text-xs text-slate-500">
        {new Date(windowData.timestamp).toLocaleTimeString('pt-BR')}
      </div>
    </div>
  );
}
