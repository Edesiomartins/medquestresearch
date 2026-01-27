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
  metaAnalysis,
} from '@/app/lib/api';
import ResultPanel from '@/app/components/ui/ResultPanel';
import TextWindow from '@/app/components/ui/TextWindow';
import Sidebar from '@/app/components/ui/sidebar';

export default function Home() {
  // 1. Todos os useState
  const [mounted, setMounted] = useState(false);
  const [textoArtigo, setTextoArtigo] = useState<string | null>(null);
  const [loadingResultado, setLoadingResultado] = useState(false);
  const [tituloResultado, setTituloResultado] = useState('');
  const [resultadoAtual, setResultadoAtual] = useState<string | null>(null); // Para mostrar texto do PDF
  const [isDragging, setIsDragging] = useState(false); // Para feedback visual de drag & drop
  const [uploadProgress, setUploadProgress] = useState(0); // Para barra de progresso de upload
  const [uploadError, setUploadError] = useState<string | null>(null); // Para erros de upload
  const [cardAtivo, setCardAtivo] = useState<string | null>(null); // Para controlar qual card está ativo
  const [modoConfiguracao, setModoConfiguracao] = useState(false); // Para mostrar formulário de configuração no ResultPanel
  const [etapasMetanalise, setEtapasMetanalise] = useState<Array<{ etapa: number; titulo: string; resultado: string; loading: boolean }>>([]); // Para armazenar etapas da metanálise

  // 2. useRouter
  const router = useRouter();

  // 3. useAuth
  const { token, usuario, creditos, loading, logout } = useAuth();

  // Garantir que o componente está montado no cliente
  useEffect(() => {
    setMounted(true);
  }, []);

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
        setTituloResultado('Erro ao processar arquivo');
      } else {
        setTextoArtigo(res.resultado || '');
        // Não atualizar resultadoAtual aqui - o texto será mostrado na janela esquerda (TextWindow)
        setUploadProgress(100); // Simula conclusão
      }
    } catch (err: any) {
      console.error("Erro no upload:", err);
      setUploadError(`Falha ao enviar arquivo: ${err.message || 'Erro desconhecido'}`);
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
    // Metanálise não precisa de textoArtigo - funciona apenas com tema
    if (tipo !== 'meta-analise' && (!textoArtigo || !token)) {
      setResultadoAtual('Por favor, faça upload de um arquivo primeiro.');
      setTituloResultado('Aviso');
      return;
    }
    
    if (!token) {
      setResultadoAtual('Usuário não autenticado.');
      setTituloResultado('Aviso');
      return;
    }

    // 1. Destacar card
    setCardAtivo(tipo);

    const titulos: Record<string, string> = {
      explicar: 'Explicação do Conteúdo',
      structure_mapper: 'Mapeamento de Estrutura',
      structure_visualizer: 'Visualização de Estrutura',
      fatos: 'Verificação de Fatos',
      perspectiva: 'Perspectivas Científicas',
      critica: 'Análise Crítica',
      'meta-analise': 'Metanálise PRISMA',
    };

    // 2. Verificar se precisa de configuração ANTES de processar
    if (tipo === 'explicar' && !trecho) {
      // Mostrar formulário de configuração no ResultPanel
      setModoConfiguracao(true);
      setTituloResultado('Explicar Conteúdo');
      // NÃO limpar resultadoAtual - manter texto do PDF visível
      setLoadingResultado(false);
      return;
    }

    if (tipo === 'critica') {
      // Mostrar formulário de configuração no ResultPanel
      setModoConfiguracao(true);
      setTituloResultado('Análise Crítica');
      // NÃO limpar resultadoAtual - manter texto do PDF visível
      setLoadingResultado(false);
      return;
    }

    if (tipo === 'meta-analise') {
      // Mostrar formulário de configuração no ResultPanel para pedir o tema
      setModoConfiguracao(true);
      setTituloResultado('Metanálise PRISMA');
      setEtapasMetanalise([]); // Limpar etapas anteriores
      // NÃO limpar resultadoAtual - manter texto do PDF visível
      setLoadingResultado(false);
      return;
    }

    // 3. Para análises que não requerem configuração, mostrar estado de processamento
    setModoConfiguracao(false);
    const textoContextual = textoProcessando(tipo);
    const textoProcessandoCompleto = `⏳ Análise em andamento\n\n${textoContextual}\n\nEstamos processando o artigo.\nEste tipo de análise pode levar alguns minutos.\n\nVocê pode aguardar ou continuar usando a plataforma.`;
    setResultadoAtual(textoProcessandoCompleto);
    setTituloResultado(titulos[tipo] || 'Processando...');
    setLoadingResultado(true);

    try {
      let res;
      switch (tipo) {
        case 'explicar':
          res = await explicarConceito(token, textoArtigo, trecho!, nivel || 'graduação');
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
        default:
          throw new Error('Tipo de análise não reconhecido');
      }

      // 4. Atualizar ResultPanel com resultado
      setModoConfiguracao(false);
      if (res.erro) {
        setResultadoAtual(`❌ Ocorreu um erro durante a análise.\n\nDetalhes técnicos:\n${res.erro}`);
        setTituloResultado('Erro na Análise');
        setLoadingResultado(false);
      } else if (res.resultado) {
        setResultadoAtual(res.resultado);
        setTituloResultado(titulos[tipo] || 'Resultado');
        setLoadingResultado(false);
      } else {
        setResultadoAtual('Análise concluída com sucesso!');
        setTituloResultado(titulos[tipo] || 'Resultado');
        setLoadingResultado(false);
      }
    } catch (error: any) {
      setModoConfiguracao(false);
      setResultadoAtual(`❌ Ocorreu um erro durante a análise.\n\nDetalhes técnicos:\n${error.message || 'Erro desconhecido'}`);
      setTituloResultado('Erro');
      setLoadingResultado(false);
    } finally {
      setCardAtivo(null);
    }
  }, [token, textoArtigo, textoProcessando]);

  // Callback para executar análise a partir do formulário inline no ResultPanel
  const handleExecute = useCallback(async (parametros: { trecho?: string; nivel?: string; focoAnalise?: string; temaMetanalise?: string }) => {
    if (!token || !cardAtivo) {
      setResultadoAtual('Por favor, faça upload de um arquivo primeiro.');
      setTituloResultado('Aviso');
      return;
    }

    const tipo = cardAtivo;
    const titulos: Record<string, string> = {
      explicar: 'Explicação do Conteúdo',
      structure_mapper: 'Mapeamento de Estrutura',
      structure_visualizer: 'Visualização de Estrutura',
      fatos: 'Verificação de Fatos',
      perspectiva: 'Perspectivas Científicas',
      critica: 'Análise Crítica',
      'meta-analise': 'Metanálise PRISMA',
    };

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

    // Caso especial: Metanálise - executar todas as etapas sequencialmente
    if (tipo === 'meta-analise' && parametros.temaMetanalise) {
      setModoConfiguracao(false);
      setEtapasMetanalise([]);
      setLoadingResultado(true);
      
      const nomesEtapa: Record<string, string> = {
        '1': 'Etapa 1: Estruturação PICO e Busca na Literatura',
        '2': 'Etapa 2: Extração de Dados',
        '3': 'Etapa 3: Redação Técnica (PRISMA)',
        '4': 'Etapa 4: Verificação Final',
      };

      const estilo = 'Vancouver';
      let resultadoAcumulado = '';

      for (let etapa = 1; etapa <= 4; etapa++) {
        const etapaStr = etapa.toString();
        const tituloEtapa = nomesEtapa[etapaStr] || `Etapa ${etapa}`;
        
        // Adicionar etapa inicial com loading
        setEtapasMetanalise(prev => [...prev, {
          etapa,
          titulo: tituloEtapa,
          resultado: `⏳ Processando ${tituloEtapa}...`,
          loading: true,
        }]);

        try {
          const res = await metaAnalysis(token, {
            tema: parametros.temaMetanalise,
            etapa: etapaStr,
            texto_artigo: textoArtigo || '',
            estilo,
          });

          const resultadoEtapa = res.erro 
            ? `❌ Erro: ${res.erro}`
            : (res.resultado || 'Etapa concluída');

          // Atualizar etapa com resultado
          setEtapasMetanalise(prev => {
            const novasEtapas = [...prev];
            const index = novasEtapas.findIndex(e => e.etapa === etapa);
            if (index !== -1) {
              novasEtapas[index] = {
                ...novasEtapas[index],
                resultado: resultadoEtapa,
                loading: false,
              };
            }
            return novasEtapas;
          });

          // Acumular resultado
          resultadoAcumulado += `\n\n${'='.repeat(60)}\n${tituloEtapa}\n${'='.repeat(60)}\n\n${resultadoEtapa}`;

          // Atualizar resultadoAtual com todas as etapas acumuladas
          setResultadoAtual(resultadoAcumulado.trim());
          setTituloResultado('Metanálise PRISMA - Em Progresso');

          // Aguardar um pouco entre etapas (exceto na última)
          if (etapa < 4) {
            await new Promise((resolve) => setTimeout(resolve, 1000));
          }
        } catch (error: any) {
          const erroMsg = `❌ Erro na ${tituloEtapa}: ${error.message || 'Erro desconhecido'}`;
          setEtapasMetanalise(prev => {
            const novasEtapas = [...prev];
            const index = novasEtapas.findIndex(e => e.etapa === etapa);
            if (index !== -1) {
              novasEtapas[index] = {
                ...novasEtapas[index],
                resultado: erroMsg,
                loading: false,
              };
            }
            return novasEtapas;
          });
          resultadoAcumulado += `\n\n${'='.repeat(60)}\n${tituloEtapa}\n${'='.repeat(60)}\n\n${erroMsg}`;
          setResultadoAtual(resultadoAcumulado.trim());
        }
      }

      setTituloResultado('Metanálise PRISMA - Concluída');
      setLoadingResultado(false);
      setCardAtivo(null);
      return;
    }

    // Para outros tipos de análise, verificar se precisa de textoArtigo
    if (!textoArtigo && tipo !== 'meta-analise') {
      setResultadoAtual('Por favor, faça upload de um arquivo primeiro.');
      setTituloResultado('Aviso');
      return;
    }

    // Mostrar estado de processamento
    let textoProcessando = '⏳ Análise em andamento\n\n';
    if (tipo === 'explicar' && parametros.trecho) {
      textoProcessando += `Explicando: "${parametros.trecho}"\n\n`;
    } else if (tipo === 'critica' && parametros.focoAnalise) {
      textoProcessando += `Aplicando análise crítica: ${nomesFoco[parametros.focoAnalise] || 'Análise Crítica'}…\n\n`;
    }
    textoProcessando += 'Estamos processando o artigo.\nEste tipo de análise pode levar alguns minutos.\n\nVocê pode aguardar ou continuar usando a plataforma.';

    setResultadoAtual(textoProcessando);
    setTituloResultado(titulos[tipo] || 'Processando...');
    setLoadingResultado(true);
    setModoConfiguracao(false);

    try {
      let res;
      if (tipo === 'explicar' && parametros.trecho) {
        res = await explicarConceito(token, textoArtigo!, parametros.trecho, parametros.nivel || 'graduação');
      } else if (tipo === 'critica' && parametros.focoAnalise) {
        res = await analisarCritica(token, textoArtigo!, parametros.focoAnalise);
      } else {
        return;
      }

      // Atualizar ResultPanel com resultado
      if (res.erro) {
        setResultadoAtual(`❌ Ocorreu um erro durante a análise.\n\nDetalhes técnicos:\n${res.erro}`);
        setTituloResultado('Erro na Análise');
        setLoadingResultado(false);
      } else {
        let titulo = titulos[tipo] || 'Resultado';
        if (tipo === 'critica' && parametros.focoAnalise) {
          titulo = `Análise Crítica - ${nomesFoco[parametros.focoAnalise] || 'Geral'}`;
        }

        setResultadoAtual(res.resultado || 'Análise concluída');
        setTituloResultado(titulo);
        setLoadingResultado(false);
      }
      setCardAtivo(null);
    } catch (error: any) {
      setResultadoAtual(`❌ Erro: ${error.message || 'Erro desconhecido'}`);
      setTituloResultado('Erro');
      setLoadingResultado(false);
      setCardAtivo(null);
    }
  }, [textoArtigo, token, cardAtivo]);


  // Estado de carregamento inicial da autenticação
  if (!mounted || loading || !token) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-mq-blue-900 text-white">
        <div className="animate-pulse-blue text-2xl">⏳ MedquestResearch carregando...</div>
      </div>
    );
  }

  return (
    <div className="flex min-h-screen bg-mq-slate-50">
      {/* Componente Sidebar */}
      <Sidebar 
        usuario={usuario} 
        creditos={creditos} 
        onLogout={logout}
        onModuleClick={runAnalise}
      />

      {/* Estrutura principal da dashboard - Duas janelas */}
      <div className="ml-64 flex-1 flex h-screen"> {/* ml-64 para compensar a largura da sidebar */}
        {/* JANELA ESQUERDA - Texto Extraído */}
        <div className="w-1/2 p-6 border-r border-mq-slate-200 overflow-hidden flex flex-col">
          <TextWindow
            texto={textoArtigo}
            loading={loadingResultado && uploadProgress > 0 && uploadProgress < 100}
            uploadProgress={uploadProgress}
            uploadError={uploadError}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            onFileSelect={handleUpload}
          />
        </div>

        {/* JANELA DIREITA - Resultados + Chat */}
        <div className="w-1/2 p-6 overflow-hidden flex flex-col">
          <ResultPanel
            loading={loadingResultado}
            titulo={tituloResultado}
            resultado={resultadoAtual}
            tipoAnalise={cardAtivo || undefined}
            textoArtigo={textoArtigo || undefined}
            token={token || undefined}
            modoConfiguracao={modoConfiguracao}
            etapasMetanalise={etapasMetanalise}
            onUpdateResult={(newResult) => {
              if (newResult === null) {
                // Cancelar configuração - restaurar texto do PDF se existir
                setModoConfiguracao(false);
                setCardAtivo(null);
                setEtapasMetanalise([]);
                if (textoArtigo) {
                  setResultadoAtual(textoArtigo);
                  setTituloResultado('Texto extraído do arquivo');
                } else {
                  setResultadoAtual(null);
                  setTituloResultado('');
                }
              } else {
                setResultadoAtual(newResult);
                setModoConfiguracao(false);
              }
            }}
            onExecute={handleExecute}
          />
        </div>
      </div>
    </div>
  );
}