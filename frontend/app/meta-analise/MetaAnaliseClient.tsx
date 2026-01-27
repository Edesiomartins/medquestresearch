'use client';

import { useState, useCallback, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/app/lib/hooks/useAuth';
import { metaAnalysis } from '@/app/lib/api';
import Sidebar from '@/app/components/ui/sidebar';
import ResultWindowsManager from '@/app/components/ui/ResultWindowsManager';
import { ResultWindowData } from '@/app/components/ui/ResultWindow';

export default function MetaAnaliseClient() {
  const router = useRouter();
  const { token, usuario, creditos, loading, logout } = useAuth();
  const [tema, setTema] = useState('');
  const [etapaAtual, setEtapaAtual] = useState<string | null>(null);
  
  // ✅ Usar objeto em vez de Map (mais estável)
  const [resultWindows, setResultWindows] = useState<Record<string, ResultWindowData>>({});
  
  const [executando, setExecutando] = useState(false);
  const [mounted, setMounted] = useState(false);

  // ✅ GARANTIR HIDRATAÇÃO CORRETA
  useEffect(() => {
    setMounted(true);
  }, []);

  // ✅ REDIRECIONAR SE NÃO AUTENTICADO
  useEffect(() => {
    if (!loading && !token && mounted) {
      router.replace('/login');
    }
  }, [loading, token, router, mounted]);

  if (!mounted || loading || !token) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-mq-blue-900 text-white">
        <div className="animate-pulse-blue text-2xl">⏳ MedquestResearch carregando...</div>
      </div>
    );
  }

  const executarEtapa = useCallback(
    async (etapa: string, temaTexto: string, estilo: string = 'Vancouver') => {
      if (!token || !temaTexto.trim()) {
        return;
      }

      setExecutando(true);
      
      // ✅ Gerar ID - está dentro de evento, então ok
      const timestamp = Date.now();
      const windowId = `meta_analise_etapa_${etapa}_${timestamp}`;

      const nomesEtapa: Record<string, string> = {
        '1': 'Etapa 1: Estruturação PICO e Busca na Literatura',
        '2': 'Etapa 2: Extração de Dados',
        '3': 'Etapa 3: Redação Técnica (PRISMA)',
        '4': 'Etapa 4: Verificação Final',
      };

      const novaJanela: ResultWindowData = {
        id: windowId,
        tipo: 'meta_analise',
        titulo: nomesEtapa[etapa] || `Etapa ${etapa}`,
        resultado: `⏳ Processando ${nomesEtapa[etapa]}...\n\nAguarde enquanto processamos sua metanálise.`,
        loading: true,
        timestamp,
      };

      // ✅ Onde você adiciona: usar objeto
      setResultWindows(prev => ({
        ...prev,
        [windowId]: novaJanela
      }));
      setEtapaAtual(etapa);

      try {
        const res = await metaAnalysis(token, {
          tema: temaTexto,
          etapa,
          texto_artigo: '',
          estilo,
        });

        if (res.erro) {
          // ✅ Onde você atualiza: usar objeto
          setResultWindows(prev => {
            const janela = prev[windowId];
            if (!janela) return prev;

            return {
              ...prev,
              [windowId]: { ...janela, resultado: `❌ Erro: ${res.erro}`, loading: false }
            };
          });
        } else if (res.resultado) {
          setResultWindows(prev => {
            const janela = prev[windowId];
            if (!janela) return prev;

            return {
              ...prev,
              [windowId]: { ...janela, resultado: res.resultado || 'Etapa concluída', loading: false }
            };
          });
        }
      } catch (error: any) {
        setResultWindows(prev => {
          const janela = prev[windowId];
          if (!janela) return prev;

          return {
            ...prev,
            [windowId]: { ...janela, resultado: `❌ Erro: ${error.message || 'Erro desconhecido'}`, loading: false }
          };
        });
      } finally {
        setExecutando(false);
        setEtapaAtual(null);
      }
    },
    [token]
  );

  const executarTodasEtapas = useCallback(async () => {
    if (!tema.trim() || !token) return;

    const estilo = 'Vancouver';

    for (let etapa = 1; etapa <= 4; etapa++) {
      await executarEtapa(etapa.toString(), tema, estilo);
      if (etapa < 4) {
        await new Promise((resolve) => setTimeout(resolve, 2000));
      }
    }
  }, [tema, token, executarEtapa]);

  const handleUpdateWindow = useCallback((id: string, updates: Partial<ResultWindowData>) => {
    // ✅ Onde você atualiza: usar objeto
    setResultWindows(prev => {
      const janela = prev[id];
      if (!janela) return prev;

      return {
        ...prev,
        [id]: { ...janela, ...updates }
      };
    });
  }, []);

  const handleCloseWindow = useCallback((id: string) => {
    // ✅ Onde remove: usar objeto
    setResultWindows(prev => {
      const next = { ...prev };
      delete next[id];
      return next;
    });
  }, []);

  return (
    <div className="flex min-h-screen bg-mq-slate-50">
      <Sidebar
        usuario={usuario}
        creditos={creditos}
        onLogout={logout}
        onModuleClick={undefined}
      />

      <div className="ml-64 flex-1 p-8">
        <div className="max-w-4xl mx-auto">
          <h1 className="text-3xl font-bold text-[#0c3d66] mb-2">
            Metanálise PRISMA
          </h1>
          <p className="text-slate-600 mb-8">
            Crie revisões sistemáticas e metanálises seguindo o protocolo PRISMA 2020.
            O sistema executará buscas na literatura (PubMed, LILACS, Cochrane) e guiará você através das etapas.
          </p>

          {/* Formulário de Tema */}
          <div className="card-elevated p-6 mb-8">
            <h2 className="text-xl font-bold text-[#0c3d66] mb-4">
              Iniciar Metanálise
            </h2>

            <div className="mb-4">
              <label htmlFor="tema" className="block text-sm font-medium text-slate-700 mb-2">
                Tema da Revisão Sistemática *
              </label>
              <textarea
                id="tema"
                value={tema}
                onChange={(e) => setTema(e.target.value)}
                placeholder="Ex: Eficácia da intervenção X em pacientes com condição Y"
                className="w-full px-4 py-3 border border-slate-300 rounded-lg focus:ring-2 focus:ring-[#2563eb] focus:border-[#2563eb] outline-none resize-none"
                rows={3}
                disabled={executando}
              />
              <p className="text-xs text-slate-500 mt-2">
                Descreva o tema da sua revisão sistemática. O sistema realizará buscas automáticas na literatura.
              </p>
            </div>

            <div className="flex gap-3">
              <button
                onClick={() => executarEtapa('1', tema)}
                disabled={!tema.trim() || executando}
                className="px-6 py-3 bg-[#2563eb] text-white rounded-lg hover:bg-[#1d4ed8] transition-colors font-medium disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {executando && etapaAtual === '1' ? 'Processando...' : 'Iniciar Etapa 1 (PICO + Busca)'}
              </button>

              <button
                onClick={executarTodasEtapas}
                disabled={!tema.trim() || executando}
                className="px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors font-medium disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {executando ? 'Executando Todas as Etapas...' : 'Executar Todas as Etapas'}
              </button>
            </div>
          </div>

          {/* Informações sobre as Etapas */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8">
            <div className="card p-4">
              <div className="flex items-start gap-3">
                <span className="text-2xl">📋</span>
                <div>
                  <h3 className="font-semibold text-slate-800 mb-1">Etapa 1: PICO + Busca</h3>
                  <p className="text-sm text-slate-600">
                    Gera pergunta PICO, estratégia de busca e realiza buscas em PubMed, LILACS e Cochrane.
                  </p>
                </div>
              </div>
            </div>

            <div className="card p-4">
              <div className="flex items-start gap-3">
                <span className="text-2xl">📊</span>
                <div>
                  <h3 className="font-semibold text-slate-800 mb-1">Etapa 2: Extração</h3>
                  <p className="text-sm text-slate-600">
                    Extrai dados dos artigos selecionados e cria tabela de evidências (JSON).
                  </p>
                </div>
              </div>
            </div>

            <div className="card p-4">
              <div className="flex items-start gap-3">
                <span className="text-2xl">✍️</span>
                <div>
                  <h3 className="font-semibold text-slate-800 mb-1">Etapa 3: Redação</h3>
                  <p className="text-sm text-slate-600">
                    Redige seções: Métodos, Resultados e Discussão conforme PRISMA.
                  </p>
                </div>
              </div>
            </div>

            <div className="card p-4">
              <div className="flex items-start gap-3">
                <span className="text-2xl">✅</span>
                <div>
                  <h3 className="font-semibold text-slate-800 mb-1">Etapa 4: Verificação</h3>
                  <p className="text-sm text-slate-600">
                    Revisão final, formatação e verificação de conformidade PRISMA.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* ✅ Onde renderiza: usar objeto */}
      {mounted && Object.keys(resultWindows).length > 0 && (
        <ResultWindowsManager
          windows={resultWindows}
          onUpdateWindow={handleUpdateWindow}
          onCloseWindow={handleCloseWindow}
          token={token || undefined}
        />
      )}
    </div>
  );
}
