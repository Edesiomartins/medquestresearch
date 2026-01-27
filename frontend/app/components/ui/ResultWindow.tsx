// app/components/ui/ResultWindow.tsx
'use client';

import { useState, useEffect, useCallback, useRef } from 'react';
import ChatInterface from './ChatInterface';

export interface ResultWindowData {
  id: string;
  tipo: string;
  titulo: string;
  resultado: string | null;
  loading: boolean;
  timestamp: number;
  textoArtigo?: string; // Para contexto do chat
  modoConfiguracao?: boolean; // Se true, mostra formulário de configuração
  parametrosConfiguracao?: {
    trecho?: string;
    nivel?: string;
    focoAnalise?: string;
  };
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
  token?: string; // Token para autenticação no chat
  onUpdateResult?: (newResult: string) => void; // Callback para atualizar resultado
  onExecute?: (parametros: { trecho?: string; nivel?: string; focoAnalise?: string }) => void; // Callback para executar análise
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
  token,
  onUpdateResult,
  onExecute,
}: ResultWindowProps) {
  const [showChat, setShowChat] = useState(false);
  
  // Estados para formulários inline
  const [trecho, setTrecho] = useState(windowData.parametrosConfiguracao?.trecho || '');
  const [nivel, setNivel] = useState(windowData.parametrosConfiguracao?.nivel || 'graduação');
  const [focoAnalise, setFocoAnalise] = useState(windowData.parametrosConfiguracao?.focoAnalise || 'geral');
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
  
  // Verificar se resultado está completo (não está processando e não é erro)
  const resultadoCompleto = !windowData.loading && windowData.resultado && !isError && !isProcessing;

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
          {/* Botão de Chat (apenas quando resultado está completo) */}
          {resultadoCompleto && token && (
            <button
              onClick={(e) => {
                e.stopPropagation();
                setShowChat(!showChat);
              }}
              className={`p-1 transition-colors ${
                showChat 
                  ? 'text-[#2563eb] bg-blue-50 rounded' 
                  : 'text-slate-400 hover:text-[#2563eb]'
              }`}
              title="Abrir/Fechar Chat"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
              </svg>
            </button>
          )}
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
      <div className="flex flex-col" style={{ maxHeight: 'calc(80vh - 60px)' }}>
        {windowData.modoConfiguracao ? (
          // Modo de configuração (formulário inline)
          <div className="overflow-y-auto flex-1 p-4">
            {windowData.tipo === 'explicar' ? (
              // Formulário para Explicar
              <div className="space-y-4">
                <div>
                  <label htmlFor="trecho" className="block text-sm font-medium text-slate-700 mb-2">
                    Termo ou conteúdo a explicar *
                  </label>
                  <textarea
                    id="trecho"
                    value={trecho}
                    onChange={(e) => setTrecho(e.target.value)}
                    placeholder="Ex: 'metodologia do estudo', 'resultados principais', 'conceito X'..."
                    className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-[#2563eb] focus:border-[#2563eb] outline-none resize-none"
                    rows={3}
                  />
                </div>
                <div>
                  <label htmlFor="nivel" className="block text-sm font-medium text-slate-700 mb-2">
                    Nível de explicação
                  </label>
                  <select
                    id="nivel"
                    value={nivel}
                    onChange={(e) => setNivel(e.target.value)}
                    className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-[#2563eb] focus:border-[#2563eb] outline-none"
                  >
                    <option value="leigo">Leigo</option>
                    <option value="graduação">Graduação</option>
                    <option value="pós-graduação">Pós-graduação</option>
                    <option value="especialista">Especialista</option>
                  </select>
                </div>
                <div className="flex gap-3 justify-end pt-2">
                  <button
                    onClick={onClose}
                    className="px-4 py-2 text-slate-700 bg-slate-100 rounded-lg hover:bg-slate-200 transition-colors"
                  >
                    Cancelar
                  </button>
                  <button
                    onClick={() => {
                      if (trecho.trim() && onExecute) {
                        onExecute({ trecho: trecho.trim(), nivel });
                      }
                    }}
                    disabled={!trecho.trim()}
                    className="px-4 py-2 bg-[#2563eb] text-white rounded-lg hover:bg-[#1d4ed8] disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                  >
                    Explicar
                  </button>
                </div>
              </div>
            ) : windowData.tipo === 'critica' ? (
              // Formulário para Análise Crítica
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-3">
                    Escolha o Método de Análise Crítica *
                  </label>
                  <div className="grid grid-cols-1 gap-3 max-h-[400px] overflow-y-auto">
                    {[
                      { id: 'metodologia', nome: 'Metodologia', descricao: 'Avalia o desenho do estudo, métodos utilizados e adequação metodológica', icon: '🔬' },
                      { id: 'validade', nome: 'Validade Interna e Externa', descricao: 'Analisa a validade das conclusões dentro e fora do contexto do estudo', icon: '✅' },
                      { id: 'confiabilidade', nome: 'Confiabilidade', descricao: 'Verifica a consistência e reprodutibilidade dos resultados', icon: '📊' },
                      { id: 'vieses', nome: 'Vieses e Limitações', descricao: 'Identifica possíveis vieses de seleção, informação, confusão e outras limitações', icon: '⚠️' },
                      { id: 'amostra', nome: 'Amostragem e Tamanho Amostral', descricao: 'Avalia a representatividade da amostra e poder estatístico', icon: '👥' },
                      { id: 'estatistica', nome: 'Análise Estatística', descricao: 'Revisa métodos estatísticos, testes utilizados e interpretação dos dados', icon: '📈' },
                      { id: 'etico', nome: 'Aspectos Éticos', descricao: 'Examina questões éticas, consentimento informado e aprovação de comitês', icon: '⚖️' },
                      { id: 'relevancia', nome: 'Relevância Clínica/Científica', descricao: 'Avalia a importância prática e científica dos achados', icon: '🎯' },
                      { id: 'geral', nome: 'Análise Geral', descricao: 'Análise crítica abrangente cobrindo todos os aspectos principais', icon: '📚' },
                    ].map((metodo) => (
                      <button
                        key={metodo.id}
                        onClick={() => setFocoAnalise(metodo.id)}
                        className={`p-4 rounded-lg border-2 text-left transition-all ${
                          focoAnalise === metodo.id
                            ? 'border-[#2563eb] bg-[#eff6ff] shadow-md'
                            : 'border-slate-200 bg-white hover:border-slate-300 hover:bg-slate-50'
                        }`}
                      >
                        <div className="flex items-start gap-3">
                          <span className="text-2xl">{metodo.icon}</span>
                          <div className="flex-1">
                            <h3 className="font-semibold text-slate-800 mb-1 text-sm">
                              {metodo.nome}
                            </h3>
                            <p className="text-xs text-slate-600">
                              {metodo.descricao}
                            </p>
                          </div>
                          {focoAnalise === metodo.id && (
                            <div className="text-[#2563eb]">
                              <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                              </svg>
                            </div>
                          )}
                        </div>
                      </button>
                    ))}
                  </div>
                </div>
                <div className="flex gap-3 justify-end pt-2">
                  <button
                    onClick={onClose}
                    className="px-4 py-2 text-slate-700 bg-slate-100 rounded-lg hover:bg-slate-200 transition-colors"
                  >
                    Cancelar
                  </button>
                  <button
                    onClick={() => {
                      if (onExecute) {
                        onExecute({ focoAnalise });
                      }
                    }}
                    className="px-6 py-2 bg-[#2563eb] text-white rounded-lg hover:bg-[#1d4ed8] transition-colors font-medium"
                  >
                    Confirmar Análise
                  </button>
                </div>
              </div>
            ) : null}
          </div>
        ) : !showChat ? (
          // Modo de visualização de resultado
          <div className="overflow-y-auto flex-1 p-4">
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
        ) : (
          // Modo de chat
          <div className="flex-1" style={{ minHeight: '400px', maxHeight: 'calc(80vh - 60px)' }}>
            <ChatInterface
              initialMessage={windowData.resultado || undefined}
              tipoAnalise={windowData.tipo}
              textoArtigo={windowData.textoArtigo}
              token={token || ''}
              onNewResponse={(newResponse) => {
                // Atualizar resultado quando houver nova resposta do chat
                if (onUpdateResult) {
                  onUpdateResult(newResponse);
                }
              }}
              disabled={!token}
            />
          </div>
        )}
      </div>
    </div>
  );
}

