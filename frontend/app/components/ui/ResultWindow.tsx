// app/components/ui/ResultWindow.tsx
'use client';

import { useState, useEffect, useCallback, useRef } from 'react';

export interface ResultWindowData {
  id: string;
  tipo: string;
  titulo: string;
  resultado: string | null;
  loading: boolean;
  timestamp: number;
}

interface ResultWindowProps {
  window: ResultWindowData;
  zIndex: number;
  isActive: boolean;
  onActivate: () => void;
  onClose: () => void;
  onMinimize: () => void;
  onMaximize: () => void;
  isMinimized: boolean;
  initialPosition?: { x: number; y: number };
  windowIndex?: number;
}

export default function ResultWindow({
  window: windowData,
  zIndex,
  isActive,
  onActivate,
  onClose,
  onMinimize,
  onMaximize,
  isMinimized,
  initialPosition,
  windowIndex = 0,
}: ResultWindowProps) {
  // Calcular posição inicial em cascata se não fornecida
  const getInitialPosition = useCallback(() => {
    if (initialPosition) return initialPosition;
    // Efeito cascata: cada janela deslocada 30px para direita e baixo
    const offset = windowIndex * 30;
    if (typeof window !== 'undefined') {
      return {
        x: window.innerWidth / 2 - 300 + offset,
        y: window.innerHeight / 2 - 200 + offset,
      };
    }
    return { x: 0, y: 0 };
  }, [initialPosition, windowIndex]);

  const [isDragging, setIsDragging] = useState(false);
  const [position, setPosition] = useState(() => {
    // Inicializar apenas no cliente
    if (typeof window !== 'undefined') {
      return getInitialPosition();
    }
    return { x: 0, y: 0 };
  });
  
  // Atualizar posição quando montar no cliente
  useEffect(() => {
    if (typeof window !== 'undefined' && !initialPosition) {
      setPosition(getInitialPosition());
    }
  }, [getInitialPosition, initialPosition]);
  const dragOffsetRef = useRef({ x: 0, y: 0 });

  const handleMouseDown = (e: React.MouseEvent) => {
    if (e.target instanceof HTMLElement && e.target.closest('button')) {
      return; // Não iniciar drag se clicou em um botão
    }
    setIsDragging(true);
    const rect = e.currentTarget.getBoundingClientRect();
    dragOffsetRef.current = {
      x: e.clientX - rect.left,
      y: e.clientY - rect.top,
    };
    onActivate();
  };

  const handleMouseMove = useCallback((e: MouseEvent) => {
    setPosition({
      x: e.clientX - dragOffsetRef.current.x,
      y: e.clientY - dragOffsetRef.current.y,
    });
  }, []);

  const handleMouseUp = useCallback(() => {
    setIsDragging(false);
  }, []);

  // Adicionar event listeners para drag
  useEffect(() => {
    if (isDragging) {
      window.addEventListener('mousemove', handleMouseMove);
      window.addEventListener('mouseup', handleMouseUp);
      return () => {
        window.removeEventListener('mousemove', handleMouseMove);
        window.removeEventListener('mouseup', handleMouseUp);
      };
    }
  }, [isDragging, handleMouseMove, handleMouseUp]);

  const getIcon = (tipo: string) => {
    const icons: Record<string, string> = {
      structure_visualizer: '🗺️',
      structure_mapper: '🧠',
      fatos: '✓',
      explicar: '📚',
      perspectiva: '🌍',
      critica: '🔬',
    };
    return icons[tipo] || '📋';
  };

  // Estado: processing
  const isProcessing = windowData.loading && windowData.resultado && windowData.resultado.includes('⏳ Análise em andamento');
  
  // Estado: error
  const isError = windowData.resultado && windowData.resultado.startsWith('❌');

  if (isMinimized) {
    return (
      <div
        className={`
          fixed bottom-4 left-4 bg-white rounded-lg shadow-lg border-2 cursor-pointer
          ${isActive ? 'border-[#2563eb]' : 'border-slate-300'}
          transition-all duration-200
        `}
        style={{ zIndex }}
        onClick={onActivate}
      >
        <div className="flex items-center gap-2 px-4 py-2">
          <span className="text-xl">{getIcon(windowData.tipo)}</span>
          <span className="text-sm font-semibold text-slate-700 truncate max-w-[200px]">
            {windowData.titulo}
          </span>
          <button
            onClick={(e) => {
              e.stopPropagation();
              onClose();
            }}
            className="ml-2 text-slate-400 hover:text-red-500 transition-colors"
          >
            ✕
          </button>
        </div>
      </div>
    );
  }

  return (
    <div
      className={`
        fixed bg-white rounded-lg shadow-2xl border-2 transition-all duration-200
        ${isActive ? 'border-[#2563eb]' : 'border-slate-300'}
        ${isDragging ? 'cursor-move' : 'cursor-default'}
      `}
      style={{
        zIndex,
        top: `${position.y}px`,
        left: `${position.x}px`,
        width: '600px',
        maxWidth: '90vw',
        maxHeight: '80vh',
      }}
      onMouseDown={handleMouseDown}
    >
      {/* Header da janela */}
      <div
        className={`
          flex items-center justify-between px-4 py-3 border-b
          ${isActive ? 'bg-[#eff6ff]' : 'bg-slate-50'}
        `}
      >
        <div className="flex items-center gap-2 flex-1 min-w-0">
          <span className="text-xl shrink-0">{getIcon(windowData.tipo)}</span>
          <h3 className="text-lg font-bold text-[#0c3d66] truncate">
            {windowData.titulo}
          </h3>
        </div>
        <div className="flex items-center gap-1 shrink-0">
          <button
            onClick={onMinimize}
            className="p-1 text-slate-400 hover:text-slate-600 transition-colors"
            title="Minimizar"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 12H4" />
            </svg>
          </button>
          <button
            onClick={onMaximize}
            className="p-1 text-slate-400 hover:text-slate-600 transition-colors"
            title="Maximizar"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5l-5-5m5 5v-4m0 4h-4" />
            </svg>
          </button>
          <button
            onClick={onClose}
            className="p-1 text-slate-400 hover:text-red-500 transition-colors"
            title="Fechar"
          >
            ✕
          </button>
        </div>
      </div>

      {/* Conteúdo da janela */}
      <div className="overflow-y-auto max-h-[calc(80vh-60px)] p-4">
        {isProcessing ? (
          <div className="text-center py-8">
            <div className="animate-pulse-blue text-4xl mb-4">⏳</div>
            <div className="whitespace-pre-wrap text-base text-slate-700 font-sans leading-relaxed">
              {windowData.resultado}
            </div>
          </div>
        ) : isError ? (
          <div className="prose max-w-none">
            <div className="whitespace-pre-wrap text-sm text-red-700 bg-red-50 p-4 rounded-lg border border-red-200 overflow-x-auto font-sans leading-relaxed">
              {windowData.resultado}
            </div>
          </div>
        ) : windowData.resultado ? (
          <div className="prose max-w-none">
            <div className="whitespace-pre-wrap text-sm text-slate-700 bg-slate-50 p-4 rounded-lg border border-slate-200 overflow-x-auto font-sans leading-relaxed break-words">
              {windowData.resultado}
            </div>
          </div>
        ) : (
          <div className="text-center py-8 text-slate-500">
            <p className="text-sm">Aguardando resultado...</p>
          </div>
        )}
      </div>
    </div>
  );
}

