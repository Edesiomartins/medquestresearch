// app/page.tsx
'use client';

import { useState, useEffect, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/app/lib/hooks/useAuth';
import {
  explicarConceito,
  structureMapper,
  structureVisualizer,
  verificarFatos,
  pesquisarPerspectiva,
  analisarCritica,
  uploadPdf,
} from '@/app/lib/api';
import ToolCard from '@/app/components/ui/ToolCard';
import ResultPanel from '@/app/components/ui/ResultPanel';
import ResultWindowsManager from '@/app/components/ui/ResultWindowsManager';
import { ResultWindowData } from '@/app/components/ui/ResultWindow';
import Sidebar from '@/app/components/ui/sidebar';
import Image from 'next/image'; // Para a logo na seção de upload

export default function Home() {
  // 1. Todos os useState
  const [textoArtigo, setTextoArtigo] = useState<string | null>(null);
  const [loadingResultado, setLoadingResultado] = useState(false);
  const [tituloResultado, setTituloResultado] = useState('');
  const [resultadoAtual, setResultadoAtual] = useState<string | null>(null); // Para mostrar texto do PDF
  const [isDragging, setIsDragging] = useState(false); // Para feedback visual de drag & drop
  const [uploadProgress, setUploadProgress] = useState(0); // Para barra de progresso de upload
  const [uploadError, setUploadError] = useState<string | null>(null); // Para erros de upload
  const [cardAtivo, setCardAtivo] = useState<string | null>(null); // Para controlar qual card está ativo
  const [resultWindows, setResultWindows] = useState<Map<string, ResultWindowData>>(() => new Map()); // Sistema de janelas

  // 2. useRouter
  const router = useRouter();

  // 3. useAuth
  const { token, usuario, creditos, loading, logout } = useAuth();

  // 4. Todos os useEffect (2 total)
  // Effect 1: Redirecionar se não autenticado
  useEffect(() => {
    if (!loading && !token) {
      router.replace('/login');
    }
  }, [loading, token, router]);

  // Effect 2: Limpar erro/progresso de upload após um tempo
  useEffect(() => {
    if (uploadError || uploadProgress === 100) {
      const timer = setTimeout(() => {
        setUploadError(null);
        setUploadProgress(0);
      }, 5000); // Limpa após 5 segundos
      return () => clearTimeout(timer);
    }
  }, [uploadError, uploadProgress]);

  // 5. Todos os useCallback (5 total: handleUpload, handleDragOver, handleDragLeave, handleDrop, runAnalise)

  // Callback 1: Lógica principal de upload
  const handleUpload = useCallback(async (file: File) => {
    if (!token) {
      setUploadError("Usuário não autenticado.");
      return;
    }
    if (!file) {
      setUploadError("Nenhum arquivo selecionado.");
      return;
    }
    if (!['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'].includes(file.type)) {
      setUploadError("Formato de arquivo inválido. Apenas PDF e DOCX são permitidos.");
      return;
    }

    setLoadingResultado(true);
    setTituloResultado('MedquestResearch processando arquivo...');
    setResultadoAtual(null);
    setUploadProgress(0);
    setUploadError(null);

    try {
      // Assumindo que uploadPdf em api.ts lida com o upload real
      // Para progresso, precisaríamos de um fetch customizado ou uma biblioteca que o suporte.
      // Por enquanto, simularemos o progresso.
      setUploadProgress(50); // Simula progresso inicial

      const res = await uploadPdf(token, file);

      if (res.erro) {
        setUploadError(res.erro);
        setResultadoAtual(res.erro);
        setTituloResultado('Erro ao processar arquivo');
      } else {
        setTextoArtigo(res.resultado || '');
        setResultadoAtual(res.resultado || 'Arquivo processado com sucesso!');
      setTituloResultado('Texto extraído do arquivo');
        setUploadProgress(100); // Simula conclusão
      }
    } catch (err: any) {
      console.error("Erro no upload:", err);
      setUploadError(`Falha ao enviar arquivo: ${err.message || 'Erro desconhecido'}`);
      setResultadoAtual(`Falha ao enviar arquivo: ${err.message || 'Erro desconhecido'}`);
      setTituloResultado('Erro');
    } finally {
      setLoadingResultado(false);
    }
  }, [token]);

  // Callback 2: Evento de arrastar sobre
  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  // Callback 3: Evento de arrastar para fora
  const handleDragLeave = useCallback(() => {
    setIsDragging(false);
  }, []);

  // Callback 4: Evento de soltar
  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    const file = e.dataTransfer.files[0];
    if (file) {
      handleUpload(file);
    }
  }, [handleUpload]);

  // Função para obter texto contextual por tipo de análise
  const textoProcessando = useCallback((tipo: string): string => {
    switch (tipo) {
      case 'structure_visualizer':
        return 'Extraindo a estrutura do artigo…';
      case 'structure_mapper':
        return 'Mapeando a organização lógica do estudo…';
      case 'fatos':
        return 'Verificando afirmações e evidências…';
      case 'perspectiva':
        return 'Executando análise científica comparativa…';
      case 'critica':
        return 'Aplicando leitura crítica aprofundada…';
      case 'explicar':
        return 'Explicando conceitos e trechos específicos…';
      default:
        return 'Processando análise…';
    }
  }, []);

  // Callback 5: Executar análise
  const runAnalise = useCallback(async (tipo: string, trecho?: string, nivel?: string) => {
    if (!textoArtigo || !token) {
      setResultadoAtual('Por favor, faça upload de um arquivo primeiro.');
      setTituloResultado('Aviso');
      return;
    }

    // 1. Destacar card
    setCardAtivo(tipo);

    // 2. Criar ou atualizar janela para este tipo de análise
    const windowId = `${tipo}_${Date.now()}`;
    const titulos: Record<string, string> = {
      explicar: 'Explicação do Conteúdo',
      structure_mapper: 'Mapeamento de Estrutura',
      structure_visualizer: 'Visualização de Estrutura',
      fatos: 'Verificação de Fatos',
      perspectiva: 'Perspectivas Científicas',
      critica: 'Análise Crítica',
    };

    const textoContextual = textoProcessando(tipo);
    const textoProcessandoCompleto = `⏳ Análise em andamento\n\n${textoContextual}\n\nEstamos processando o artigo.\nEste tipo de análise pode levar alguns minutos.\n\nVocê pode aguardar ou continuar usando a plataforma.`;

    // Criar janela inicial com estado de processamento
    const novaJanela: ResultWindowData = {
      id: windowId,
      tipo,
      titulo: titulos[tipo] || 'Resultado',
      resultado: textoProcessandoCompleto,
      loading: true,
      timestamp: Date.now(),
      textoArtigo: textoArtigo || undefined, // Adicionar texto do artigo para contexto do chat
    };

    setResultWindows(prev => new Map(prev).set(windowId, novaJanela));

    try {
      let res;
      switch (tipo) {
        case 'explicar':
          // Abrir janela em modo de configuração se não tiver trecho
          if (!trecho) {
            setResultWindows(prev => {
              const next = new Map(prev);
              const janela = next.get(windowId);
              if (janela) {
                next.set(windowId, {
                  ...janela,
                  modoConfiguracao: true,
                  resultado: null,
                  loading: false,
                });
              }
              return next;
            });
            return;
          }
          res = await explicarConceito(token, textoArtigo, trecho, nivel || 'graduação');
          break;
        case 'structure_mapper':
          res = await structureMapper(token, textoArtigo);
          break;
        case 'structure_visualizer':
          res = await structureVisualizer(token, textoArtigo);
          break;
        case 'fatos':
          res = await verificarFatos(token, textoArtigo);
          break;
        case 'perspectiva':
          res = await pesquisarPerspectiva(token, textoArtigo);
          break;
        case 'critica':
          // Abrir janela em modo de configuração
          setResultWindows(prev => {
            const next = new Map(prev);
            const janela = next.get(windowId);
            if (janela) {
              next.set(windowId, {
                ...janela,
                modoConfiguracao: true,
                resultado: null,
                loading: false,
              });
            }
            return next;
          });
          return;
        default:
          throw new Error('Tipo de análise não reconhecido');
      }

      // 3. Atualizar janela com resultado
      setResultWindows(prev => {
        const next = new Map(prev);
        const janela = next.get(windowId);
        if (janela) {
      if (res.erro) {
            next.set(windowId, {
              ...janela,
              resultado: `❌ Ocorreu um erro durante a análise.\n\nDetalhes técnicos:\n${res.erro}`,
              loading: false,
            });
          } else if (res.resultado) {
            next.set(windowId, {
              ...janela,
              resultado: res.resultado,
              loading: false,
            });
      } else {
            next.set(windowId, {
              ...janela,
              resultado: 'Análise concluída com sucesso!',
              loading: false,
            });
      }
        }
        return next;
      });
    } catch (error: any) {
      setResultWindows(prev => {
        const next = new Map(prev);
        const janela = next.get(windowId);
        if (janela) {
          next.set(windowId, {
            ...janela,
            resultado: `❌ Ocorreu um erro durante a análise.\n\nDetalhes técnicos:\n${error.message || 'Erro desconhecido'}`,
            loading: false,
          });
        }
        return next;
      });
    } finally {
      setCardAtivo(null);
    }
  }, [token, textoArtigo, textoProcessando]);

  // Callback para atualizar janela
  const handleUpdateWindow = useCallback((id: string, updates: Partial<ResultWindowData>) => {
    setResultWindows(prev => {
      const next = new Map(prev);
      const janela = next.get(id);
      if (janela) {
        next.set(id, { ...janela, ...updates });
    }
      return next;
    });
  }, []);

  // Callback para fechar janela
  const handleCloseWindow = useCallback((id: string) => {
    setResultWindows(prev => {
      const next = new Map(prev);
      next.delete(id);
      return next;
    });
  }, []);

  // Callback para executar análise a partir do formulário inline
  const handleExecute = useCallback(async (windowId: string, parametros: { trecho?: string; nivel?: string; focoAnalise?: string }) => {
    if (!textoArtigo || !token) {
      setResultadoAtual('Por favor, faça upload de um arquivo primeiro.');
      setTituloResultado('Aviso');
      return;
    }

    const janela = resultWindows.get(windowId);
    if (!janela) return;

    // Atualizar janela para modo de processamento
    setResultWindows(prev => {
      const next = new Map(prev);
      const janelaAtual = next.get(windowId);
      if (janelaAtual) {
        const nomesFoco: Record<string, string> = {
          metodologia: 'Metodologia',
          validade: 'Validade Interna e Externa',
          confiabilidade: 'Confiabilidade',
          vieses: 'Vieses e Limitações',
          amostra: 'Amostragem e Tamanho Amostral',
          estatistica: 'Análise Estatística',
          etico: 'Aspectos Éticos',
          relevancia: 'Relevância Clínica/Científica',
          geral: 'Análise Geral'
        };

        let textoProcessando = '⏳ Análise em andamento\n\n';
        if (janelaAtual.tipo === 'explicar') {
          textoProcessando += `Explicando: "${parametros.trecho}"\n\n`;
        } else if (janelaAtual.tipo === 'critica') {
          textoProcessando += `Aplicando análise crítica: ${nomesFoco[parametros.focoAnalise || 'geral'] || 'Análise Crítica'}…\n\n`;
        }
        textoProcessando += 'Estamos processando o artigo.\nEste tipo de análise pode levar alguns minutos.\n\nVocê pode aguardar ou continuar usando a plataforma.';

        next.set(windowId, {
          ...janelaAtual,
          modoConfiguracao: false,
          loading: true,
          resultado: textoProcessando,
          parametrosConfiguracao: parametros,
        });
      }
      return next;
    });

    try {
      let res;
      if (janela.tipo === 'explicar' && parametros.trecho) {
        res = await explicarConceito(token, textoArtigo, parametros.trecho, parametros.nivel || 'graduação');
      } else if (janela.tipo === 'critica' && parametros.focoAnalise) {
        res = await analisarCritica(token, textoArtigo, parametros.focoAnalise);
      } else {
        return;
      }

      // Atualizar janela com resultado
      setResultWindows(prev => {
        const next = new Map(prev);
        const janelaAtual = next.get(windowId);
        if (janelaAtual) {
          if (res.erro) {
            next.set(windowId, {
              ...janelaAtual,
              resultado: `❌ Ocorreu um erro durante a análise.\n\nDetalhes técnicos:\n${res.erro}`,
              loading: false,
              modoConfiguracao: false,
            });
          } else {
            const nomesFoco: Record<string, string> = {
              metodologia: 'Metodologia',
              validade: 'Validade Interna e Externa',
              confiabilidade: 'Confiabilidade',
              vieses: 'Vieses e Limitações',
              amostra: 'Amostragem e Tamanho Amostral',
              estatistica: 'Análise Estatística',
              etico: 'Aspectos Éticos',
              relevancia: 'Relevância Clínica/Científica',
              geral: 'Análise Geral'
            };

            let titulo = janelaAtual.titulo;
            if (janelaAtual.tipo === 'critica' && parametros.focoAnalise) {
              titulo = `Análise Crítica - ${nomesFoco[parametros.focoAnalise] || 'Geral'}`;
            }

            next.set(windowId, {
              ...janelaAtual,
              titulo,
              resultado: res.resultado || 'Análise concluída',
              loading: false,
              modoConfiguracao: false,
            });
          }
        }
        return next;
      });
      setCardAtivo(null);
    } catch (error: any) {
      setResultWindows(prev => {
        const next = new Map(prev);
        const janelaAtual = next.get(windowId);
        if (janelaAtual) {
          next.set(windowId, {
            ...janelaAtual,
            resultado: `❌ Erro: ${error.message || 'Erro desconhecido'}`,
            loading: false,
            modoConfiguracao: false,
          });
        }
        return next;
      });
      setCardAtivo(null);
    }
  }, [textoArtigo, token, resultWindows]);

  // Callback para quando o usuário confirmar no modal de análise crítica (mantido para compatibilidade, mas não será usado)
  const handleCriticaConfirm = useCallback(async (focoAnalise: string) => {
    if (!textoArtigo || !token) {
      setResultadoAtual('Por favor, faça upload de um arquivo primeiro.');
      setTituloResultado('Aviso');
      return;
    }

    // Mapear foco para nome amigável
    const nomesFoco: Record<string, string> = {
      metodologia: 'Metodologia',
      validade: 'Validade Interna e Externa',
      confiabilidade: 'Confiabilidade',
      vieses: 'Vieses e Limitações',
      amostra: 'Amostragem e Tamanho Amostral',
      estatistica: 'Análise Estatística',
      etico: 'Aspectos Éticos',
      relevancia: 'Relevância Clínica/Científica',
      geral: 'Análise Geral'
    };

    // Criar janela para análise crítica
    const windowId = `critica_${Date.now()}`;
    const textoProcessandoCompleto = `⏳ Análise em andamento\n\nAplicando análise crítica: ${nomesFoco[focoAnalise] || 'Análise Crítica'}…\n\nEstamos processando o artigo.\nEste tipo de análise pode levar alguns minutos.\n\nVocê pode aguardar ou continuar usando a plataforma.`;

    const novaJanela: ResultWindowData = {
      id: windowId,
      tipo: 'critica',
      titulo: `Análise Crítica - ${nomesFoco[focoAnalise] || 'Geral'}`,
      resultado: textoProcessandoCompleto,
      loading: true,
      timestamp: Date.now(),
      textoArtigo: textoArtigo || undefined, // Adicionar texto do artigo para contexto do chat
    };

    setResultWindows(prev => new Map(prev).set(windowId, novaJanela));
    setCardAtivo('critica');
    setShowCriticaModal(false);

    try {
      const res = await analisarCritica(token, textoArtigo, focoAnalise);

      // Atualizar janela com resultado
      setResultWindows(prev => {
        const next = new Map(prev);
        const janela = next.get(windowId);
        if (janela) {
          if (res.erro) {
            next.set(windowId, {
              ...janela,
              resultado: `❌ Ocorreu um erro durante a análise.\n\nDetalhes técnicos:\n${res.erro}`,
              loading: false,
            });
          } else {
            next.set(windowId, {
              ...janela,
              resultado: res.resultado || 'Análise concluída',
              loading: false,
            });
          }
        }
        return next;
      });
      setCardAtivo(null);
    } catch (error: any) {
      setResultWindows(prev => {
        const next = new Map(prev);
        const janela = next.get(windowId);
        if (janela) {
          next.set(windowId, {
            ...janela,
            resultado: `❌ Erro: ${error.message || 'Erro desconhecido'}`,
            loading: false,
          });
        }
        return next;
      });
      setCardAtivo(null);
    }
  }, [textoArtigo, token]);

  // Estado de carregamento inicial da autenticação
  if (loading || !token) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-mq-blue-900 text-white">
        <div className="animate-pulse-blue text-2xl">⏳ MedquestResearch carregando...</div>
      </div>
    );
  }

  return (
    <div className="flex min-h-screen bg-mq-slate-50">
      {/* Componente Sidebar */}
      <Sidebar usuario={usuario} creditos={creditos} onLogout={logout} />

      {/* Estrutura principal da dashboard */}
      <div className="ml-64 flex-1 flex"> {/* ml-64 para compensar a largura da sidebar */}
        {/* COLUNA AÇÕES */}
        <div className="w-1/2 p-8 space-y-8 overflow-y-auto border-r border-mq-slate-200">
          {/* COMECE AGORA - Seção de Upload */}
          <div className="card-elevated p-6">
            <h2 className="text-2xl font-bold text-mq-slate-800 mb-4">Comece agora</h2>
            <p className="text-base text-mq-slate-600 mb-6">
              Envie um artigo científico (PDF ou DOCX) e escolha o tipo de análise.
            </p>

            {/* Área de Drag & Drop */}
            <div
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onDrop={handleDrop}
              className={`
                relative flex flex-col items-center justify-center p-8 border-2 border-dashed rounded-xl
                transition-all duration-300
                ${isDragging ? 'border-mq-blue-500 bg-mq-blue-50' : 'border-mq-slate-300 hover:border-mq-blue-400 bg-white'}
              `}
            >
              <input
                id="file-upload"
                type="file"
                accept=".pdf,.docx"
                onChange={(e) => {
                  const file = e.target.files?.[0];
                  if (file) handleUpload(file);
                }}
                className="absolute inset-0 opacity-0 cursor-pointer"
              />
               <div className="text-center">
                 <div className="flex justify-center mb-3">
                   <Image 
                     src="/logo-medquestresearch.png" 
                     alt="Upload" 
                     width={64} 
                     height={64} 
                     className="opacity-70"
                   />
                 </div>
                 <p className="text-lg font-semibold text-mq-slate-700">
                   Arraste e solte seu arquivo aqui
                 </p>
                <p className="text-sm text-mq-slate-500 mt-1">
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
              <div className="mt-4 p-3 bg-red-50 border border-red-300 rounded-lg flex items-center gap-2">
                <span className="text-red-600 text-xl">❌</span>
                <p className="text-red-700 text-sm">{uploadError}</p>
              </div>
            )}
            {uploadProgress === 100 && !uploadError && (
              <div className="mt-4 p-3 bg-green-50 border border-green-300 rounded-lg flex items-center gap-2">
                <span className="text-green-600 text-xl">✅</span>
                <p className="text-green-700 text-sm">Arquivo enviado com sucesso!</p>
              </div>
            )}
          </div>

          {/* GRID FINAL — FERRAMENTAS */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {/* 1️⃣ Visualizar estrutura */}
            <ToolCard
              title="Visualizar estrutura"
              description="Visualize a estrutura do artigo em formato de mapa"
              icon="🗺️"
              disabled={!textoArtigo}
              active={cardAtivo === "structure_visualizer"}
              onClick={() => runAnalise("structure_visualizer")}
            />

            {/* 2️⃣ Mapear estrutura */}
            <ToolCard
              title="Mapear estrutura"
              description="Identifique seções, organização lógica e tipo de estudo do artigo"
              icon="🧠"
              disabled={!textoArtigo}
              active={cardAtivo === "structure_mapper"}
              onClick={() => runAnalise("structure_mapper")}
            />

            {/* 3️⃣ Verificar fatos */}
            <ToolCard
              title="Verificar fatos"
              description="Cheque afirmações e evidências apresentadas no artigo"
              icon="✓"
              disabled={!textoArtigo}
              active={cardAtivo === "fatos"}
              onClick={() => runAnalise("fatos")}
            />

            {/* 4️⃣ Explicar conteúdo */}
            <ToolCard
              title="Explicar conteúdo"
              description="Compreenda conceitos e trechos específicos do artigo com explicações claras"
              icon="📚"
              disabled={!textoArtigo}
              active={cardAtivo === "explicar"}
              onClick={() => runAnalise("explicar")}
            />

            {/* 5️⃣ Perspectivas científicas */}
            <ToolCard
              title="Perspectivas científicas"
              description="Compare o artigo com outras evidências e estudos relacionados"
              icon="🌍"
              disabled={!textoArtigo}
              active={cardAtivo === "perspectiva"}
              onClick={() => runAnalise("perspectiva")}
            />

            {/* 6️⃣ Análise crítica */}
            <ToolCard
              title="Análise crítica"
              description="Aplique leitura crítica usando 9 métodos científicos de análise"
              icon="🔬"
              disabled={!textoArtigo}
              active={cardAtivo === "critica"}
              onClick={() => runAnalise("critica")}
            />
          </div>

          {/* Link para Meta-Análise */}
          <div className="mt-6 card-elevated p-6">
            <div className="flex items-center justify-between">
              <div className="flex-1">
                <h3 className="text-lg font-bold text-[#0c3d66] mb-2">
                  📑 Meta-Análise PRISMA
                </h3>
                <p className="text-sm text-slate-600 mb-4">
                  Crie revisões sistemáticas e meta-análises completas. O sistema realiza buscas automáticas 
                  na literatura (PubMed, LILACS, Cochrane) e executa todas as etapas do protocolo PRISMA.
                </p>
              </div>
              <button
                onClick={() => router.push('/meta-analise')}
                className="px-6 py-3 bg-[#2563eb] text-white rounded-lg hover:bg-[#1d4ed8] transition-colors font-medium ml-4"
              >
                Acessar Meta-Análise
              </button>
            </div>
          </div>
        </div>

        {/* COLUNA RESULTADO - Mostra texto do PDF */}
        <div className="w-1/2 p-8 overflow-y-auto">
          <ResultPanel
            loading={loadingResultado}
            titulo={tituloResultado}
            resultado={resultadoAtual}
          />
        </div>
      </div>

      {/* Sistema de Janelas em Cascata */}
      <ResultWindowsManager
        windows={resultWindows}
        onUpdateWindow={handleUpdateWindow}
        onCloseWindow={handleCloseWindow}
        token={token || undefined}
        onExecute={handleExecute}
      />
    </div>
  );
}