// app/page.tsx
'use client';

import { useState, useEffect, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/app/lib/hooks/useAuth';
import {
  analisarCritica,
  uploadPdf,
  traduzirTexto,
  metaAnalysis,
  uploadArtigosMetanalise,
  obterJob,
} from '@/app/lib/api';
import ResultPanel from '@/app/components/ui/ResultPanel';
import TextWindow from '@/app/components/ui/TextWindow';
import Sidebar from '@/app/components/ui/sidebar';

export default function Home() {
  // 1. Todos os useState
  const [mounted, setMounted] = useState(false);
  const [textoArtigo, setTextoArtigo] = useState<string | null>(null);
  const [textoArtigoPt, setTextoArtigoPt] = useState<string | null>(null);
  const [loadingResultado, setLoadingResultado] = useState(false);
  const [tituloResultado, setTituloResultado] = useState('');
  const [resultadoAtual, setResultadoAtual] = useState<string | null>(null); // Para mostrar texto do PDF
  const [isDragging, setIsDragging] = useState(false); // Para feedback visual de drag & drop
  const [uploadProgress, setUploadProgress] = useState(0); // Para barra de progresso de upload
  const [uploadError, setUploadError] = useState<string | null>(null); // Para erros de upload
  const [cardAtivo, setCardAtivo] = useState<string | null>(null); // Para controlar qual card está ativo
  const [modoConfiguracao, setModoConfiguracao] = useState(false); // Para mostrar formulário de configuração no ResultPanel
  const [etapasMetanalise, setEtapasMetanalise] = useState<Array<{ etapa: number; titulo: string; resultado: string; loading: boolean }>>([]); // Para armazenar etapas da metanálise
  const [artigosEncontrados, setArtigosEncontrados] = useState<any[]>([]); // Artigos encontrados na busca
  const [totalArtigos, setTotalArtigos] = useState(0); // Total de artigos encontrados
  const [temaMetanaliseAtual, setTemaMetanaliseAtual] = useState(''); // Tema atual da metanálise
  const [arquivosMetanalise, setArquivosMetanalise] = useState<File[]>([]); // Arquivos selecionados para metanálise
  const [analisesPrisma, setAnalisesPrisma] = useState<any[]>([]); // Análises PRISMA dos artigos
  const [loadingTraduzir, setLoadingTraduzir] = useState(false);
  const [traduzirErro, setTraduzirErro] = useState<string | null>(null);

  // 2. useRouter
  const router = useRouter();

  // 3. useAuth
  const { token, usuario, creditos, loading, logout, refreshCreditos } = useAuth();

  const handleJobSelectFromSidebar = useCallback(async (job: { id: number; modulo: string; status: string; resultado?: string; project_id?: number }) => {
    if (!token) return;
    const detalhe = await obterJob(token, job.id);
    const modulo = (job.modulo || '').toLowerCase();
    const mapaModulo: Record<string, string> = {
      critica: 'critica',
      meta_analise: 'meta-analise',
      escrever_artigo: 'meta-analise',
    };
    const legados = ['explicar', 'fatos', 'mapa', 'structure_mapper', 'structure_visualizer'];
    const card = mapaModulo[modulo] || (legados.includes(modulo) ? 'critica' : 'meta-analise');
    setCardAtivo(card);
    setModoConfiguracao(false);
    setLoadingResultado(false);
    setTituloResultado(`Job #${job.id} — ${modulo.split('_').join(' ')}`);
    setResultadoAtual((detalhe.resultado as string) || (detalhe.erro as string) || job.resultado || 'Sem resultado para este job.');
  }, [token]);

  // Callbacks que precisam vir antes de useEffect/handleUpload (runAnalise é usado em handleUpload)
  const runAnalise = useCallback(async (tipo: string) => {
    if (!token) {
      setResultadoAtual('Usuário não autenticado.');
      setTituloResultado('Aviso');
      return;
    }
    setCardAtivo(tipo);
    if (tipo === 'critica') {
      // Sempre abrir o painel de escolha do método; o texto do PDF pode vir depois do upload.
      setModoConfiguracao(true);
      setTituloResultado('Análise Crítica');
      setLoadingResultado(false);
      setResultadoAtual(null);
      return;
    }
    if (tipo === 'meta-analise') {
      router.push('/meta-analise');
      return;
    }
    setCardAtivo(null);
  }, [token]);

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
    // Se estiver em modo metanálise, não fazer upload único
    if (cardAtivo === 'meta-analise') {
      return;
    }

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

      if (res.redirect === '/planos') {
        const msg = res.erro || 'Créditos insuficientes. Clique para adquirir mais créditos.';
        setUploadError(msg);
        setTituloResultado('Créditos insuficientes');
        router.push('/planos');
      } else if (res.erro) {
        setUploadError(res.erro);
        setTituloResultado('Erro ao processar arquivo');
      } else {
        setTextoArtigo(res.resultado || '');
        setTextoArtigoPt(null); // Tradução sob demanda pelo botão
        setTraduzirErro(null);
        setUploadProgress(100); // Simula conclusão
        setResultadoAtual(null);
        setTituloResultado('');
        // Garantir que o painel de configuração (ex.: métodos de análise crítica) continue visível após o upload
        if (cardAtivo === 'critica') {
          setModoConfiguracao(true);
        }
      }
    } catch (err: any) {
      console.error("Erro no upload:", err);
      setUploadError(`Falha ao enviar arquivo: ${err.message || 'Erro desconhecido'}`);
      setTituloResultado('Erro');
    } finally {
      setLoadingResultado(false);
    }
  }, [token, cardAtivo, router]);

  const handleTraduzir = useCallback(async () => {
    if (!token || !textoArtigo) return;
    setLoadingTraduzir(true);
    setTraduzirErro(null);
    try {
      const res = await traduzirTexto(token, textoArtigo);
      if (res.erro) setTraduzirErro(res.erro);
      else setTextoArtigoPt(res.resultado_pt ?? null);
    } finally {
      setLoadingTraduzir(false);
    }
  }, [token, textoArtigo]);

  // Callback para apenas selecionar arquivos (sem upload) - metanálise
  const handleSelecionarArquivos = useCallback((files: File[]) => {
    // Apenas salvar arquivos selecionados, sem fazer upload
    setArquivosMetanalise(files);
    setUploadError(null);
  }, []);

  // Callback para iniciar análise PRISMA (upload e análise) - metanálise
  const handleIniciarAnalisePrisma = useCallback(async () => {
    const files = arquivosMetanalise;
    
    if (!token) {
      setUploadError("Usuário não autenticado.");
      return;
    }
    if (files.length === 0) {
      setUploadError("Nenhum arquivo selecionado.");
      return;
    }
    if (files.length > 25) {
      setUploadError("Máximo de 25 artigos permitidos.");
      return;
    }

    // Validar formatos
    const formatosInvalidos = files.filter(f => 
      !['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'].includes(f.type)
    );
    if (formatosInvalidos.length > 0) {
      setUploadError("Formato de arquivo inválido. Apenas PDF e DOCX são permitidos.");
      return;
    }

    setLoadingResultado(true);
    setTituloResultado('Analisando artigos com PRISMA...');
    setResultadoAtual(null);
    setUploadProgress(0);
    setUploadError(null);

    try {
      setUploadProgress(10);
      const res = await uploadArtigosMetanalise(token, files);

      if (res.redirect === '/planos') {
        const msg = res.erro || 'Créditos insuficientes. Clique para adquirir mais créditos.';
        setUploadError(msg);
        setTituloResultado('Créditos insuficientes');
        setUploadProgress(0);
        router.push('/planos');
      } else if (res.erro) {
        setUploadError(res.erro);
        setTituloResultado('Erro ao processar artigos');
        setUploadProgress(0);
      } else {
        // Salvar análises PRISMA
        if (res.artigos && Array.isArray(res.artigos)) {
          setAnalisesPrisma(res.artigos);
          setArtigosEncontrados(res.artigos);
          setTotalArtigos(res.total_artigos || res.artigos.length);
        }
        
        // Exibir resumo das análises
        const resumo = res.resumo_analises || {};
        const textoResumo = `
📊 ANÁLISE PRISMA CONCLUÍDA

Total de artigos analisados: ${res.total_artigos || res.artigos?.length || 0}

📈 Estatísticas:
- Escore médio de qualidade: ${resumo.escore_medio?.toFixed(2) || 'N/A'}/10
- Pontuação PRISMA média: ${resumo.pontuacao_prisma_media?.toFixed(2) || 'N/A'}/14

📋 Distribuição por qualidade:
- Excelente (9-10): ${resumo.artigos_por_qualidade?.excelente || 0} artigos
- Boa (7-8): ${resumo.artigos_por_qualidade?.boa || 0} artigos
- Regular (5-6): ${resumo.artigos_por_qualidade?.regular || 0} artigos
- Baixa (<5): ${resumo.artigos_por_qualidade?.baixa || 0} artigos

✅ Os artigos foram analisados e estão prontos para a próxima etapa.
        `.trim();
        
        setResultadoAtual(textoResumo);
        setTituloResultado('Análise PRISMA - Artigos Processados');
        setUploadProgress(100);
      }
    } catch (err: any) {
      console.error("Erro no upload múltiplo:", err);
      setUploadError(`Falha ao processar artigos: ${err.message || 'Erro desconhecido'}`);
      setTituloResultado('Erro');
      setUploadProgress(0);
    } finally {
      setLoadingResultado(false);
    }
  }, [token, arquivosMetanalise, router]);

  // Callback para upload múltiplo (metanálise) - DEPRECATED, usar handleIniciarAnalisePrisma
  const handleUploadMultiplo = useCallback(async (files: File[]) => {
    if (!token) {
      setUploadError("Usuário não autenticado.");
      return;
    }
    if (files.length === 0) {
      setUploadError("Nenhum arquivo selecionado.");
      return;
    }
    if (files.length > 25) {
      setUploadError("Máximo de 25 artigos permitidos.");
      return;
    }

    // Validar formatos
    const formatosInvalidos = files.filter(f => 
      !['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'].includes(f.type)
    );
    if (formatosInvalidos.length > 0) {
      setUploadError("Formato de arquivo inválido. Apenas PDF e DOCX são permitidos.");
      return;
    }

    // Esta função não deve ser chamada diretamente - usar handleIniciarAnalisePrisma
    // Mantida apenas para compatibilidade
    setArquivosMetanalise(files);
    setLoadingResultado(true);
    setTituloResultado('Analisando artigos com PRISMA...');
    setResultadoAtual(null);
    setUploadProgress(0);
    setUploadError(null);

    try {
      setUploadProgress(10);
      const res = await uploadArtigosMetanalise(token, files);

      if (res.redirect === '/planos') {
        const msg = res.erro || 'Créditos insuficientes. Clique para adquirir mais créditos.';
        setUploadError(msg);
        setTituloResultado('Créditos insuficientes');
        setUploadProgress(0);
        router.push('/planos');
      } else if (res.erro) {
        setUploadError(res.erro);
        setTituloResultado('Erro ao processar artigos');
        setUploadProgress(0);
      } else {
        // Salvar análises PRISMA
        if (res.artigos && Array.isArray(res.artigos)) {
          setAnalisesPrisma(res.artigos);
          setArtigosEncontrados(res.artigos);
          setTotalArtigos(res.total_artigos || res.artigos.length);
        }
        
        // Exibir resumo das análises
        const resumo = res.resumo_analises || {};
        const textoResumo = `
📊 ANÁLISE PRISMA CONCLUÍDA

Total de artigos analisados: ${res.total_artigos || res.artigos?.length || 0}

📈 Estatísticas:
- Escore médio de qualidade: ${resumo.escore_medio?.toFixed(2) || 'N/A'}/10
- Pontuação PRISMA média: ${resumo.pontuacao_prisma_media?.toFixed(2) || 'N/A'}/14

📋 Distribuição por qualidade:
- Excelente (9-10): ${resumo.artigos_por_qualidade?.excelente || 0} artigos
- Boa (7-8): ${resumo.artigos_por_qualidade?.boa || 0} artigos
- Regular (5-6): ${resumo.artigos_por_qualidade?.regular || 0} artigos
- Baixa (<5): ${resumo.artigos_por_qualidade?.baixa || 0} artigos

✅ Os artigos foram analisados e estão prontos para a próxima etapa.
        `.trim();
        
        setResultadoAtual(textoResumo);
        setTituloResultado('Análise PRISMA - Artigos Processados');
        setUploadProgress(100);
      }
    } catch (err: any) {
      console.error("Erro no upload múltiplo:", err);
      setUploadError(`Falha ao processar artigos: ${err.message || 'Erro desconhecido'}`);
      setTituloResultado('Erro');
      setUploadProgress(0);
    } finally {
      setLoadingResultado(false);
    }
  }, [token, router]);

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
    
      // Se estiver em modo metanálise, aceitar múltiplos arquivos (apenas selecionar)
      if (cardAtivo === 'meta-analise') {
        const files = Array.from(e.dataTransfer.files);
        if (files.length > 0) {
          if (files.length > 25) {
            setUploadError('Máximo de 25 artigos permitidos');
            return;
          }
          handleSelecionarArquivos(files);
        }
      } else {
        // Modo normal: arquivo único (upload automático)
        const file = e.dataTransfer.files[0];
        if (file) {
          handleUpload(file);
        }
      }
    }, [handleUpload, handleSelecionarArquivos, cardAtivo]);

  // Callback para executar análise a partir do formulário inline no ResultPanel
  const handleExecute = useCallback(async (parametros: { trecho?: string; nivel?: string; focoAnalise?: string; temaMetanalise?: string }) => {
    if (!token || !cardAtivo) {
      setResultadoAtual('Por favor, faça upload de um arquivo primeiro.');
      setTituloResultado('Aviso');
      return;
    }

    const tipo = cardAtivo;
    const titulos: Record<string, string> = {
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
      setArtigosEncontrados([]); // Limpar artigos anteriores
      setTotalArtigos(0);
      setTemaMetanaliseAtual(parametros.temaMetanalise);
      setLoadingResultado(true);
      
      const nomesEtapa: Record<string, string> = {
        '1': 'Etapa 1: Estruturação PICO e Busca na Literatura',
        '2': 'Etapa 2: Extração de Dados',
        '3': 'Etapa 3: Redação Técnica (PRISMA)',
      };

      const estilo = 'Vancouver';
      let resultadoAcumulado = '';

      for (let etapa = 1; etapa <= 3; etapa++) {
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

          // Se for etapa 1 e tiver artigos na resposta, salvar
          if (etapa === 1 && res.artigos && Array.isArray(res.artigos)) {
            setArtigosEncontrados(res.artigos);
            setTotalArtigos(res.total_artigos || res.artigos.length);
            setTemaMetanaliseAtual(parametros.temaMetanalise || '');
          }

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
      return;
    }

    // Para outros tipos de análise, verificar se precisa de textoArtigo
    if (!textoArtigo && tipo !== 'meta-analise') {
      setResultadoAtual('Por favor, faça upload de um arquivo primeiro.');
      setTituloResultado('Aviso');
      return;
    }

    // Garantir que textoArtigo não é null para análise crítica
    if (tipo === 'critica' && !textoArtigo) {
      setResultadoAtual('Por favor, faça upload de um arquivo primeiro.');
      setTituloResultado('Aviso');
      setModoConfiguracao(false);
      setCardAtivo(null);
      return;
    }

    // Mostrar estado de processamento
    let textoProc = '⏳ Análise em andamento\n\n';
    if (tipo === 'critica' && parametros.focoAnalise) {
      textoProc += `Aplicando análise crítica: ${nomesFoco[parametros.focoAnalise] || 'Análise Crítica'}…\n\n`;
    }
    textoProc += 'Estamos processando o artigo.\nEste tipo de análise pode levar alguns minutos.\n\nVocê pode aguardar ou continuar usando a plataforma.';

    setResultadoAtual(textoProc);
    setTituloResultado(titulos[tipo] || 'Processando...');
    setLoadingResultado(true);
    setModoConfiguracao(false);

    try {
      let res;
      if (tipo === 'critica' && parametros.focoAnalise && textoArtigo) {
        res = await analisarCritica(token, textoArtigo, parametros.focoAnalise);
      } else {
        return;
      }

      // Atualizar ResultPanel com resultado
      if (res.redirect === '/planos') {
        const msg = res.erro || 'Créditos insuficientes. Clique para adquirir mais créditos.';
        setUploadError(msg);
        setResultadoAtual(`❌ ${msg}`);
        setTituloResultado('Créditos insuficientes');
        setLoadingResultado(false);
        router.push('/planos');
      } else if (res.erro) {
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
        await refreshCreditos();
      }
    } catch (error: any) {
      setResultadoAtual(`❌ Erro: ${error.message || 'Erro desconhecido'}`);
      setTituloResultado('Erro');
      setLoadingResultado(false);
    }
  }, [textoArtigo, token, cardAtivo, router, refreshCreditos]);

  // Continuar para Etapas 2, 3 e 4 da metanálise (após análise PRISMA dos artigos)
  const handleContinuarEtapasMetanalise = useCallback(async (tema?: string) => {
    if (!token || !analisesPrisma?.length) {
      setResultadoAtual('Nenhum artigo analisado. Faça o upload e inicie a análise PRISMA primeiro.');
      setTituloResultado('Aviso');
      return;
    }
    setLoadingResultado(true);
    setEtapasMetanalise([]);
    if (tema?.trim()) setTemaMetanaliseAtual(tema.trim());

    const nomesEtapa: Record<string, string> = {
      '2': 'Etapa 2: Extração de Dados',
      '3': 'Etapa 3: Redação Técnica (PRISMA)',
    };
    const estilo = 'Vancouver';
    let resultadoAcumulado = '';

    for (let etapa = 2; etapa <= 3; etapa++) {
      const etapaStr = etapa.toString();
      const tituloEtapa = nomesEtapa[etapaStr] || `Etapa ${etapa}`;

      setEtapasMetanalise(prev => [...prev, {
        etapa,
        titulo: tituloEtapa,
        resultado: `⏳ Processando ${tituloEtapa}...`,
        loading: true,
      }]);

      try {
        const res = await metaAnalysis(token, {
          tema: tema?.trim() || '',
          etapa: etapaStr,
          texto_artigo: '',
          estilo,
          artigos_analisados: analisesPrisma,
        });

        const resultadoEtapa = res.erro
          ? `❌ Erro: ${res.erro}`
          : (res.resultado || 'Etapa concluída');

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

        resultadoAcumulado += `\n\n${'='.repeat(60)}\n${tituloEtapa}\n${'='.repeat(60)}\n\n${resultadoEtapa}`;
        setResultadoAtual(resultadoAcumulado.trim());
        setTituloResultado('Metanálise PRISMA - Em Progresso');

        if (etapa < 4) await new Promise((resolve) => setTimeout(resolve, 1000));
      } catch (error: any) {
        const erroMsg = `❌ Erro na ${tituloEtapa}: ${error.message || 'Erro desconhecido'}`;
        setEtapasMetanalise(prev => {
          const novasEtapas = [...prev];
          const index = novasEtapas.findIndex(e => e.etapa === etapa);
          if (index !== -1) {
            novasEtapas[index] = { ...novasEtapas[index], resultado: erroMsg, loading: false };
          }
          return novasEtapas;
        });
        resultadoAcumulado += `\n\n${'='.repeat(60)}\n${tituloEtapa}\n${'='.repeat(60)}\n\n${erroMsg}`;
        setResultadoAtual(resultadoAcumulado.trim());
      }
    }

    setTituloResultado('Metanálise PRISMA - Concluída');
    setLoadingResultado(false);
  }, [token, analisesPrisma]);

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
      <Sidebar
        usuario={usuario}
        creditos={creditos}
        onLogout={logout}
        token={token || undefined}
        onJobSelect={handleJobSelectFromSidebar}
      />

      {/* Área principal: grid de cards ou modal tela inteira */}
      <main className="ml-64 flex-1 min-h-screen p-6">
        {cardAtivo === null ? (
          /* Grid de cards - cada card abre o modal da análise */
          <div>
            <h1 className="text-2xl font-bold text-[#0c3d66] mb-6">Análises disponíveis</h1>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-6 max-w-3xl">
              {[
                { icon: '🔬', label: 'Análise crítica', tipo: 'critica' },
                { icon: '📑', label: 'Metanálise PRISMA', tipo: 'meta-analise' },
              ].map((modulo) => (
                <button
                  key={modulo.tipo}
                  onClick={() => {
                    setCardAtivo(modulo.tipo);
                    runAnalise(modulo.tipo);
                  }}
                  className="flex flex-col items-center justify-center p-8 rounded-xl border-2 border-slate-200 bg-white hover:border-[#0c3d66] hover:bg-[#0c3d66]/5 hover:shadow-lg transition-all text-left w-full group"
                >
                  <span className="text-4xl mb-3 group-hover:scale-110 transition-transform">{modulo.icon}</span>
                  <span className="font-semibold text-slate-800 text-center">{modulo.label}</span>
                  <span className="text-sm text-slate-500 mt-1">Clique para abrir</span>
                </button>
              ))}
            </div>
          </div>
        ) : (
          /* Modal tela inteira: upload (esquerda) + resultados (direita) */
          <div className="fixed inset-0 z-50 bg-white flex flex-col" style={{ left: '16rem' }}>
            <div className="flex items-center justify-between px-6 py-4 border-b border-slate-200 bg-slate-50">
              <h2 className="text-xl font-bold text-[#0c3d66]">
                {{
                  critica: 'Análise crítica',
                  'meta-analise': 'Metanálise PRISMA',
                }[cardAtivo] || cardAtivo}
              </h2>
              <button
                type="button"
                onClick={() => setCardAtivo(null)}
                className="px-4 py-2 rounded-lg text-slate-700 bg-slate-200 hover:bg-slate-300 transition-colors font-medium"
              >
                Fechar
              </button>
            </div>
            <div className="flex-1 flex min-h-0">
              <div className="w-1/2 p-6 border-r border-slate-200 overflow-hidden flex flex-col">
                <TextWindow
                  texto={textoArtigo}
                  textoPt={textoArtigoPt}
                  loading={loadingResultado && uploadProgress > 0 && uploadProgress < 100}
                  uploadProgress={uploadProgress}
                  uploadError={uploadError}
                  onTraduzir={handleTraduzir}
                  loadingTraduzir={loadingTraduzir}
                  traduzirErro={traduzirErro}
                  onDragOver={handleDragOver}
                  onDragLeave={handleDragLeave}
                  onDrop={handleDrop}
                  onFileSelect={handleUpload}
                  modoMetanalise={cardAtivo === 'meta-analise'}
                  onFilesSelect={handleSelecionarArquivos}
                  onIniciarAnalise={handleIniciarAnalisePrisma}
                  arquivosSelecionados={arquivosMetanalise}
                  analisandoArtigos={loadingResultado && uploadProgress > 0}
                />
              </div>
              <div className="w-1/2 p-6 overflow-hidden flex flex-col">
                <ResultPanel
                  artigosEncontrados={artigosEncontrados}
                  totalArtigos={totalArtigos}
                  temaMetanalise={temaMetanaliseAtual}
                  loading={loadingResultado}
                  titulo={tituloResultado}
                  resultado={resultadoAtual}
                  tipoAnalise={cardAtivo || undefined}
                  textoArtigo={textoArtigo || undefined}
                  token={token || undefined}
                  modoConfiguracao={modoConfiguracao}
                  etapasMetanalise={etapasMetanalise}
                  mostrarBotaoContinuarEtapas={cardAtivo === 'meta-analise' && artigosEncontrados.length > 0 && etapasMetanalise.length === 0}
                  onContinuarEtapasMetanalise={handleContinuarEtapasMetanalise}
                  onRunAnalysis={cardAtivo ? () => runAnalise(cardAtivo) : undefined}
                  onUpdateResult={(newResult) => {
                    if (newResult === null) {
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
        )}
      </main>
    </div>
  );
}