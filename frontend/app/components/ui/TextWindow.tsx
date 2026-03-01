// app/components/ui/TextWindow.tsx
'use client';

import { useMemo, useEffect, useState, useRef } from 'react';

interface TextWindowProps {
  texto: string | null;
  textoPt?: string | null; // Versão em português (após clicar em Traduzir texto)
  loading: boolean;
  uploadProgress: number;
  uploadError: string | null;
  onTraduzir?: () => void;
  loadingTraduzir?: boolean;
  traduzirErro?: string | null;
  onDragOver: (e: React.DragEvent) => void;
  onDragLeave: (e: React.DragEvent) => void;
  onDrop: (e: React.DragEvent) => void;
  onFileSelect: (file: File) => void;
  modoMetanalise?: boolean;
  onFilesSelect?: (files: File[]) => void;
  onIniciarAnalise?: () => void;
  arquivosSelecionados?: File[];
  analisandoArtigos?: boolean;
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
  textoPt = null,
  loading,
  uploadProgress,
  uploadError,
  onTraduzir,
  loadingTraduzir = false,
  traduzirErro = null,
  onDragOver,
  onDragLeave,
  onDrop,
  onFileSelect,
  modoMetanalise = false,
  onFilesSelect,
  onIniciarAnalise,
  arquivosSelecionados = [],
  analisandoArtigos = false,
}: TextWindowProps) {
  const [mounted, setMounted] = useState(false);
  const [abaTexto, setAbaTexto] = useState<'original' | 'pt'>('original');
  const fileInputRef = useRef<HTMLInputElement>(null);
  const textoConsolidadoPt = useMemo(() => {
    if (!mounted || !textoPt) return textoPt;
    return consolidarTexto(textoPt);
  }, [textoPt, mounted]);

  // Garantir que o componente está montado no cliente
  useEffect(() => {
    setMounted(true);
  }, []);

  // Consolidar texto removendo separadores de chunks (apenas no cliente)
  const textoConsolidado = useMemo(() => {
    if (!mounted || !texto) return texto;
    return consolidarTexto(texto);
  }, [texto, mounted]);
  return (
    <div className="card-elevated flex flex-col h-full">
      <h2 className="text-2xl font-bold text-[#0c3d66] mb-4">
        {modoMetanalise ? 'Upload de Artigos - Metanálise PRISMA' : 'Texto Extraído'}
      </h2>
      
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
              ref={fileInputRef}
              id="file-upload"
              type="file"
              accept=".pdf,.docx"
              multiple={modoMetanalise}
              onChange={(e) => {
                const files = e.target.files;
                if (modoMetanalise && files && files.length > 0) {
                  // Modo metanálise: apenas selecionar arquivos (não fazer upload ainda)
                  const fileArray = Array.from(files);
                  if (fileArray.length > 15) {
                    alert('Máximo de 15 artigos permitidos');
                    e.target.value = ''; // Limpar seleção
                    return;
                  }
                  if (onFilesSelect) {
                    onFilesSelect(fileArray);
                  }
                } else if (files && files[0]) {
                  // Modo normal: arquivo único (upload automático)
                  onFileSelect(files[0]);
                }
                // Limpar input para permitir selecionar os mesmos arquivos novamente
                e.target.value = '';
              }}
              className={modoMetanalise ? 'hidden' : 'absolute inset-0 opacity-0 cursor-pointer'}
              aria-hidden={modoMetanalise}
            />
            <div className={`text-center ${modoMetanalise ? 'pointer-events-none' : ''}`}>
              <div className="text-6xl mb-4">{modoMetanalise ? '📚' : '📄'}</div>
              <p className="text-lg font-semibold text-mq-slate-700 mb-2">
                {modoMetanalise 
                  ? 'Arraste e solte seus artigos aqui (máx. 15)'
                  : 'Arraste e solte seu arquivo aqui'
                }
              </p>
              <p className="text-sm text-mq-slate-500">
                {modoMetanalise 
                  ? 'Ou use o botão abaixo para selecionar arquivos'
                  : 'ou clique para selecionar'
                }
              </p>
              <p className="text-xs text-mq-slate-400 mt-2">
                {modoMetanalise 
                  ? '(PDF, DOCX - máximo 15 artigos)'
                  : '(PDF, DOCX - máximo 10MB)'
                }
              </p>
            </div>
            {modoMetanalise && (
              <div className="mt-4 flex flex-col items-center gap-3 pointer-events-auto">
                <button
                  type="button"
                  onClick={() => fileInputRef.current?.click()}
                  className="px-5 py-2.5 rounded-lg font-medium text-white bg-[#0c3d66] hover:bg-[#0a3255] transition-colors"
                >
                  Selecionar arquivos
                </button>
              </div>
            )}
            {modoMetanalise && arquivosSelecionados.length > 0 && (
                <div className="mt-4 w-full max-w-md mx-auto space-y-3">
                  <div className="p-3 bg-blue-50 border border-blue-200 rounded-lg">
                    <p className="text-sm font-semibold text-blue-900 mb-2">
                      {arquivosSelecionados.length} artigo{arquivosSelecionados.length > 1 ? 's' : ''} selecionado{arquivosSelecionados.length > 1 ? 's' : ''}:
                    </p>
                    <div className="text-xs text-blue-700 space-y-1 max-h-32 overflow-y-auto">
                      {arquivosSelecionados.map((file, idx) => (
                        <div key={idx} className="truncate">• {file.name}</div>
                      ))}
                    </div>
                  </div>
                  
                  {/* Botão para iniciar análise */}
                  <button
                    onClick={() => {
                      if (onIniciarAnalise) {
                        onIniciarAnalise();
                      }
                    }}
                    disabled={analisandoArtigos || arquivosSelecionados.length === 0}
                    className={`
                      w-full px-6 py-3 rounded-lg font-semibold text-white
                      transition-all duration-200
                      ${analisandoArtigos || arquivosSelecionados.length === 0
                        ? 'bg-slate-400 cursor-not-allowed'
                        : 'bg-[#2563eb] hover:bg-[#1d4ed8] shadow-md hover:shadow-lg'
                      }
                      flex items-center justify-center gap-2
                    `}
                  >
                    {analisandoArtigos ? (
                      <>
                        <div className="animate-spin h-5 w-5 border-2 border-white border-t-transparent rounded-full"></div>
                        <span>Analisando artigos...</span>
                      </>
                    ) : (
                      <>
                        <span>🔬</span>
                        <span>Iniciar Análise PRISMA</span>
                      </>
                    )}
                  </button>
                </div>
              )}

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
                <>
                  {texto && !modoMetanalise && (
                    <div className="flex flex-wrap items-center gap-2 mb-3">
                      {textoPt != null ? (
                        <div className="flex gap-1 border-b border-slate-200 pb-2">
                          <button
                            type="button"
                            onClick={() => setAbaTexto('original')}
                            className={`px-3 py-1.5 rounded-t text-sm font-medium transition-colors ${
                              abaTexto === 'original'
                                ? 'bg-[#0c3d66] text-white'
                                : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                            }`}
                          >
                            Original
                          </button>
                          <button
                            type="button"
                            onClick={() => setAbaTexto('pt')}
                            className={`px-3 py-1.5 rounded-t text-sm font-medium transition-colors ${
                              abaTexto === 'pt'
                                ? 'bg-[#0c3d66] text-white'
                                : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                            }`}
                          >
                            Português
                          </button>
                        </div>
                      ) : (
                        <>
                          <button
                            type="button"
                            onClick={onTraduzir}
                            disabled={loadingTraduzir}
                            className="px-4 py-2 rounded-lg text-sm font-medium bg-[#0c3d66] text-white hover:bg-[#0a3255] disabled:opacity-60 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
                          >
                            {loadingTraduzir ? (
                              <>
                                <span className="inline-block w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                                Traduzir texto...
                              </>
                            ) : (
                              <>Traduzir texto</>
                            )}
                          </button>
                          {traduzirErro && (
                            <p className="text-sm text-red-600">{traduzirErro}</p>
                          )}
                        </>
                      )}
                    </div>
                  )}
                  <div className="flex-1 overflow-y-auto">
                    <div className="whitespace-pre-wrap text-sm text-slate-700 bg-slate-50 p-4 rounded-lg border border-slate-200 font-sans leading-relaxed wrap-break-word">
                      {abaTexto === 'pt' && textoConsolidadoPt != null ? textoConsolidadoPt : textoConsolidado}
                    </div>
                  </div>
                </>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
