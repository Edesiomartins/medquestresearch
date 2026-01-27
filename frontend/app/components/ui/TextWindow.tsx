// app/components/ui/TextWindow.tsx
'use client';

import { useMemo } from 'react';

interface TextWindowProps {
  texto: string | null;
  loading: boolean;
  uploadProgress: number;
  uploadError: string | null;
  onDragOver: (e: React.DragEvent) => void;
  onDragLeave: (e: React.DragEvent) => void;
  onDrop: (e: React.DragEvent) => void;
  onFileSelect: (file: File) => void;
}

// Função para consolidar texto removendo separadores de chunks
function consolidarTexto(texto: string | null): string | null {
  if (!texto) return null;
  
  // Remover marcadores de chunk comuns
  let textoConsolidado = texto
    // Remover marcadores explícitos de chunk
    .replace(/\n\[Chunk final resumido\]/g, '')
    .replace(/\[Chunk \d+\]/g, '')
    .replace(/---+\s*Chunk\s*\d+\s*---+/gi, '')
    .replace(/===+\s*Chunk\s*\d+\s*===+/gi, '')
    // Remover múltiplas quebras de linha consecutivas (mais de 2)
    .replace(/\n{3,}/g, '\n\n')
    // Remover espaços em branco excessivos no início/fim de linhas
    .split('\n')
    .map(linha => linha.trim())
    .join('\n')
    // Remover linhas vazias excessivas novamente após trim
    .replace(/\n{3,}/g, '\n\n')
    // Garantir que parágrafos sejam separados por apenas uma quebra de linha
    .replace(/([.!?])\n\n+/g, '$1\n\n')
    .trim();
  
  return textoConsolidado;
}

export default function TextWindow({
  texto,
  loading,
  uploadProgress,
  uploadError,
  onDragOver,
  onDragLeave,
  onDrop,
  onFileSelect,
}: TextWindowProps) {
  // Consolidar texto removendo separadores de chunks
  const textoConsolidado = useMemo(() => consolidarTexto(texto), [texto]);
  return (
    <div className="card-elevated flex flex-col h-full">
      <h2 className="text-2xl font-bold text-[#0c3d66] mb-4">Texto Extraído</h2>
      
      {!texto ? (
        <div className="flex-1 flex flex-col items-center justify-center">
          {/* Área de Upload */}
          <div
            onDragOver={onDragOver}
            onDragLeave={onDragLeave}
            onDrop={onDrop}
            className={`
              relative flex flex-col items-center justify-center p-12 border-2 border-dashed rounded-xl
              transition-all duration-300 w-full max-w-md
              ${uploadProgress > 0 ? 'border-mq-blue-500 bg-mq-blue-50' : 'border-mq-slate-300 hover:border-mq-blue-400 bg-white'}
            `}
          >
            <input
              id="file-upload"
              type="file"
              accept=".pdf,.docx"
              onChange={(e) => {
                const file = e.target.files?.[0];
                if (file) onFileSelect(file);
              }}
              className="absolute inset-0 opacity-0 cursor-pointer"
            />
            <div className="text-center">
              <div className="text-6xl mb-4">📄</div>
              <p className="text-lg font-semibold text-mq-slate-700 mb-2">
                Arraste e solte seu arquivo aqui
              </p>
              <p className="text-sm text-mq-slate-500">
                ou <span className="text-mq-blue-600 font-medium cursor-pointer hover:underline">clique para selecionar</span>
              </p>
              <p className="text-xs text-mq-slate-400 mt-2">
                (PDF, DOCX - máximo 10MB)
              </p>
            </div>

            {/* Progresso de Upload */}
            {uploadProgress > 0 && uploadProgress < 100 && (
              <div className="absolute bottom-0 left-0 w-full h-2 bg-mq-blue-200 rounded-b-xl overflow-hidden">
                <div
                  className="h-full bg-mq-blue-500 transition-all duration-300 ease-out"
                  style={{ width: `${uploadProgress}%` }}
                ></div>
              </div>
            )}
            {uploadProgress === 100 && (
              <div className="absolute bottom-0 left-0 w-full h-2 bg-green-500 rounded-b-xl"></div>
            )}
          </div>

          {/* Feedback de Upload */}
          {uploadError && (
            <div className="mt-4 p-3 bg-red-50 border border-red-300 rounded-lg flex items-center gap-2 max-w-md">
              <span className="text-red-600 text-xl">❌</span>
              <p className="text-red-700 text-sm">{uploadError}</p>
            </div>
          )}
          {uploadProgress === 100 && !uploadError && (
            <div className="mt-4 p-3 bg-green-50 border border-green-300 rounded-lg flex items-center gap-2 max-w-md">
              <span className="text-green-600 text-xl">✅</span>
              <p className="text-green-700 text-sm">Arquivo enviado com sucesso!</p>
            </div>
          )}
        </div>
      ) : (
        <div className="flex-1 overflow-hidden flex flex-col">
          {loading ? (
            <div className="flex-1 flex items-center justify-center">
              <div className="text-center">
                <div className="animate-pulse-blue text-4xl mb-4">⏳</div>
                <p className="text-slate-600">Processando arquivo...</p>
              </div>
            </div>
          ) : (
            <div className="flex-1 overflow-y-auto">
              <div className="whitespace-pre-wrap text-sm text-slate-700 bg-slate-50 p-4 rounded-lg border border-slate-200 font-sans leading-relaxed wrap-break-word">
                {textoConsolidado}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
