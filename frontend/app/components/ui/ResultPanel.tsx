// app/components/ui/ResultPanel.tsx
'use client';

import { useState } from 'react';
import ChatInterface from './ChatInterface';
import ArticleSelector, { Artigo } from './ArticleSelector';

interface ResultPanelProps {
  loading: boolean;
  titulo: string;
  resultado: string | null;
  tipoAnalise?: string;
  textoArtigo?: string;
  token?: string;
  onUpdateResult?: (newResult: string | null) => void;
  modoConfiguracao?: boolean;
  etapasMetanalise?: Array<{ etapa: number; titulo: string; resultado: string; loading: boolean }>;
  onExecute?: (parametros: { trecho?: string; nivel?: string; focoAnalise?: string; temaMetanalise?: string }) => void;
  artigosEncontrados?: Artigo[];
  totalArtigos?: number;
  temaMetanalise?: string;
}

export default function ResultPanel({ 
  loading, 
  titulo, 
  resultado,
  tipoAnalise,
  textoArtigo,
  token,
  onUpdateResult,
  modoConfiguracao = false,
  etapasMetanalise = [],
  onExecute,
  artigosEncontrados = [],
  totalArtigos = 0,
  temaMetanalise = '',
}: ResultPanelProps) {
  const [showChat, setShowChat] = useState(false);
  const [trecho, setTrecho] = useState('');
  const [nivel, setNivel] = useState('graduação');
  const [focoAnalise, setFocoAnalise] = useState('geral');
  const [temaInput, setTemaInput] = useState(''); // Estado local para o input do formulário

  // Modo de configuração - mostrar formulário inline (mantendo texto do PDF visível abaixo)
  if (modoConfiguracao && tipoAnalise) {
    if (tipoAnalise === 'explicar') {
      return (
        <div className="card-elevated flex flex-col h-full">
          <h2 className="text-2xl font-bold text-[#0c3d66] mb-4">Explicar Conteúdo</h2>
          <p className="text-sm text-slate-600 mb-4">
            Digite o termo, conceito ou trecho específico que deseja que seja explicado.
          </p>
          <div className="space-y-4 mb-6">
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
                onClick={() => {
                  if (onUpdateResult) {
                    onUpdateResult(null);
                  }
                }}
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
          {/* Mostrar texto do PDF abaixo do formulário se existir */}
          {resultado && (
            <div className="mt-6 pt-6 border-t border-slate-200">
              <h3 className="text-lg font-semibold text-slate-700 mb-2">Texto do Artigo (Referência)</h3>
              <div className="whitespace-pre-wrap text-xs text-slate-600 bg-slate-50 p-3 rounded-lg border border-slate-200 overflow-y-auto max-h-[300px] font-sans leading-relaxed">
                {resultado}
              </div>
            </div>
          )}
        </div>
      );
    } else if (tipoAnalise === 'critica') {
      return (
        <div className="card-elevated flex flex-col h-full">
          <h2 className="text-2xl font-bold text-[#0c3d66] mb-4">Análise Crítica</h2>
          <p className="text-sm text-slate-600 mb-4">
            Selecione um dos 9 métodos científicos de análise crítica para aplicar ao artigo.
          </p>
          <div className="space-y-4 mb-6">
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
                onClick={() => {
                  if (onUpdateResult) {
                    onUpdateResult(null);
                  }
                }}
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
          {/* Mostrar texto do PDF abaixo do formulário se existir */}
          {resultado && (
            <div className="mt-6 pt-6 border-t border-slate-200">
              <h3 className="text-lg font-semibold text-slate-700 mb-2">Texto do Artigo (Referência)</h3>
              <div className="whitespace-pre-wrap text-xs text-slate-600 bg-slate-50 p-3 rounded-lg border border-slate-200 overflow-y-auto max-h-[300px] font-sans leading-relaxed">
                {resultado}
              </div>
            </div>
          )}
        </div>
      );
    } else if (tipoAnalise === 'meta-analise') {
      return (
        <div className="card-elevated flex flex-col h-full">
          <h2 className="text-2xl font-bold text-[#0c3d66] mb-4">Metanálise PRISMA</h2>
          <p className="text-sm text-slate-600 mb-4">
            Digite o tema da metanálise que deseja realizar. O sistema executará automaticamente todas as 4 etapas:
            estruturação PICO e busca na literatura, extração de dados, redação técnica (PRISMA) e verificação final.
          </p>
          <div className="space-y-4 mb-6">
            <div>
              <label htmlFor="temaMetanalise" className="block text-sm font-medium text-slate-700 mb-2">
                Tema da Metanálise *
              </label>
              <textarea
                id="temaMetanalise"
                value={temaInput}
                onChange={(e) => setTemaInput(e.target.value)}
                placeholder="Ex: 'Eficácia da terapia X no tratamento da condição Y', 'Efeitos da intervenção Z em pacientes com doença W'..."
                className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-[#2563eb] focus:border-[#2563eb] outline-none resize-none"
                rows={4}
              />
            </div>
            <div className="flex gap-3 justify-end pt-2">
              <button
                onClick={() => {
                  if (onUpdateResult) {
                    onUpdateResult(null);
                  }
                  setTemaInput(''); // Limpar input ao cancelar
                }}
                className="px-4 py-2 text-slate-700 bg-slate-100 rounded-lg hover:bg-slate-200 transition-colors"
              >
                Cancelar
              </button>
              <button
                onClick={() => {
                  if (temaInput.trim() && onExecute) {
                    onExecute({ temaMetanalise: temaInput.trim() });
                    setTemaInput(''); // Limpar input após iniciar
                  }
                }}
                disabled={!temaInput.trim()}
                className="px-4 py-2 bg-[#2563eb] text-white rounded-lg hover:bg-[#1d4ed8] disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                Iniciar Metanálise
              </button>
            </div>
          </div>
          {/* Mostrar texto do PDF abaixo do formulário se existir */}
          {resultado && (
            <div className="mt-6 pt-6 border-t border-slate-200">
              <h3 className="text-lg font-semibold text-slate-700 mb-2">Texto do Artigo (Referência)</h3>
              <div className="whitespace-pre-wrap text-xs text-slate-600 bg-slate-50 p-3 rounded-lg border border-slate-200 overflow-y-auto max-h-[300px] font-sans leading-relaxed">
                {resultado}
              </div>
            </div>
          )}
        </div>
      );
    }
  }

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
  if (resultado && !showChat) {
    // Se for metanálise e tiver etapas, mostrar progresso das etapas também
    const mostrarEtapas = tipoAnalise === 'meta-analise' && etapasMetanalise.length > 0;
    
    return (
      <div className="card-elevated flex flex-col h-full">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-2xl font-bold text-[#0c3d66]">{titulo}</h2>
          {token && tipoAnalise && tipoAnalise !== 'meta-analise' && (
            <button
              onClick={() => setShowChat(true)}
              className="px-4 py-2 bg-[#2563eb] text-white rounded-lg hover:bg-[#1d4ed8] transition-colors flex items-center gap-2 text-sm"
              title="Abrir Chat Interativo"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
              </svg>
              Chat
            </button>
          )}
        </div>
        {mostrarEtapas && (
          <div className="mb-4 space-y-2">
            {etapasMetanalise.map((etapa) => (
              <div
                key={etapa.etapa}
                className={`p-3 rounded-lg border-2 ${
                  etapa.loading
                    ? 'border-blue-300 bg-blue-50'
                    : etapa.resultado.startsWith('❌')
                    ? 'border-red-300 bg-red-50'
                    : 'border-green-300 bg-green-50'
                }`}
              >
                <div className="flex items-center gap-2 mb-1">
                  <span className="font-semibold text-sm text-slate-700">{etapa.titulo}</span>
                  {etapa.loading && (
                    <div className="animate-spin h-4 w-4 border-2 border-blue-500 border-t-transparent rounded-full"></div>
                  )}
                  {!etapa.loading && !etapa.resultado.startsWith('❌') && (
                    <span className="text-green-600">✓</span>
                  )}
                  {!etapa.loading && etapa.resultado.startsWith('❌') && (
                    <span className="text-red-600">✗</span>
                  )}
                </div>
                {!etapa.loading && (
                  <div className="text-xs text-slate-600 mt-1 line-clamp-2">
                    {etapa.resultado.substring(0, 100)}...
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
        
        {/* Mostrar seletor de artigos após etapa 1 completa */}
        {tipoAnalise === 'meta-analise' && 
         artigosEncontrados && 
         artigosEncontrados.length > 0 && 
         etapasMetanalise.some(e => e.etapa === 1 && !e.loading && !e.resultado.startsWith('❌')) && (
          <div className="mb-6">
            <ArticleSelector
              artigos={artigosEncontrados}
              totalArtigos={totalArtigos}
              tema={temaMetanalise}
              onArtigosSelecionados={(selecionados) => {
                // Opcional: salvar artigos selecionados para uso nas próximas etapas
                console.log('Artigos selecionados:', selecionados);
              }}
            />
          </div>
        )}
        
        <div className="prose max-w-none flex-1 overflow-hidden flex flex-col">
          <div className="whitespace-pre-wrap text-sm text-slate-700 bg-slate-50 p-4 rounded-lg border border-slate-200 overflow-x-auto font-sans leading-relaxed wrap-break-word overflow-y-auto flex-1">
            {resultado}
          </div>
        </div>
      </div>
    );
  }

  // Modo de chat
  if (resultado && showChat && token && tipoAnalise) {
    return (
      <div className="card-elevated flex flex-col h-full">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-2xl font-bold text-[#0c3d66]">{titulo} - Chat</h2>
          <button
            onClick={() => setShowChat(false)}
            className="px-4 py-2 text-slate-600 bg-slate-100 rounded-lg hover:bg-slate-200 transition-colors text-sm"
          >
            Voltar ao Resultado
          </button>
        </div>
        <div className="flex-1 min-h-0">
          <ChatInterface
            initialMessage={resultado}
            tipoAnalise={tipoAnalise}
            textoArtigo={textoArtigo}
            token={token}
            onNewResponse={(newResponse) => {
              if (onUpdateResult) {
                onUpdateResult(newResponse);
              }
            }}
            disabled={!token}
          />
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