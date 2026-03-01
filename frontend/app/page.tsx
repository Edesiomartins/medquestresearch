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
  uploadArtigosMetanalise,
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

      if (res.erro) {
        setUploadError(res.erro);
        setTituloResultado('Erro ao processar arquivo');
      } else {
        setTextoArtigo(res.resultado || '');
        setTextoArtigoPt(res.resultado_pt ?? null);
        setUploadProgress(100); // Simula conclusão
      }
    } catch (err: any) {
      console.error("Erro no upload:", err);
      setUploadError(`Falha ao enviar arquivo: ${err.message || 'Erro desconhecido'}`);
      setTituloResultado('Erro');
    } finally {
      setLoadingResultado(false);
    }
  }, [token, cardAtivo]);

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
    if (files.length > 15) {
      setUploadError("Máximo de 15 artigos permitidos.");
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

      if (res.erro) {
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
  }, [token, arquivosMetanalise]);

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
    if (files.length > 15) {
      setUploadError("Máximo de 15 artigos permitidos.");
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

      if (res.erro) {
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
    
      // Se estiver em modo metanálise, aceitar múltiplos arquivos (apenas selecionar)
      if (cardAtivo === 'meta-analise') {
        const files = Array.from(e.dataTransfer.files);
        if (files.length > 0) {
          if (files.length > 15) {
            setUploadError('Máximo de 15 artigos permitidos');
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
      // Novo fluxo: mostrar área de upload múltiplo no TextWindow
      setModoConfiguracao(false);
      setTituloResultado('Metanálise PRISMA - Upload de Artigos');
      setEtapasMetanalise([]); // Limpar etapas anteriores
      setTextoArtigo(null);
      setTextoArtigoPt(null);
      setArquivosMetanalise([]); // Limpar arquivos anteriores
      setAnalisesPrisma([]); // Limpar análises anteriores
      setResultadoAtual(null);
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

    // Garantir que textoArtigo não é null (já verificado acima, mas TypeScript precisa de confirmação)
    if (!textoArtigo) {
      setModoConfiguracao(false);
      setResultadoAtual('Por favor, faça upload de um arquivo primeiro.');
      setTituloResultado('Aviso');
      setLoadingResultado(false);
      setCardAtivo(null);
      return;
    }

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
      setArtigosEncontrados([]); // Limpar artigos anteriores
      setTotalArtigos(0);
      setTemaMetanaliseAtual(parametros.temaMetanalise);
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
      setCardAtivo(null);
      return;
    }

    // Para outros tipos de análise, verificar se precisa de textoArtigo
    if (!textoArtigo && tipo !== 'meta-analise') {
      setResultadoAtual('Por favor, faça upload de um arquivo primeiro.');
      setTituloResultado('Aviso');
      return;
    }

    // Garantir que textoArtigo não é null para tipos que precisam dele
    if ((tipo === 'explicar' || tipo === 'critica') && !textoArtigo) {
      setResultadoAtual('Por favor, faça upload de um arquivo primeiro.');
      setTituloResultado('Aviso');
      setModoConfiguracao(false);
      setCardAtivo(null);
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
      if (tipo === 'explicar' && parametros.trecho && textoArtigo) {
        res = await explicarConceito(token, textoArtigo, parametros.trecho, parametros.nivel || 'graduação');
      } else if (tipo === 'critica' && parametros.focoAnalise && textoArtigo) {
        res = await analisarCritica(token, textoArtigo, parametros.focoAnalise);
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
      '4': 'Etapa 4: Verificação Final',
    };
    const estilo = 'Vancouver';
    let resultadoAcumulado = '';

    for (let etapa = 2; etapa <= 4; etapa++) {
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
    setCardAtivo(null);
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
      {/* Componente Sidebar */}
      <Sidebar 
        usuario={usuario} 
        creditos={creditos} 
        onLogout={logout}
        onModuleClick={runAnalise}
      />

      {/* Estrutura principal da dashboard - Duas janelas */}
      <div className="ml-64 flex-1 flex h-screen"> {/* ml-64 para compensar a largura da sidebar */}
        {/* JANELA ESQUERDA - Texto Extraído / Upload de Artigos */}
        <div className="w-1/2 p-6 border-r border-mq-slate-200 overflow-hidden flex flex-col">
          <TextWindow
            texto={textoArtigo}
            textoPt={textoArtigoPt}
            loading={loadingResultado && uploadProgress > 0 && uploadProgress < 100}
            uploadProgress={uploadProgress}
            uploadError={uploadError}
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

        {/* JANELA DIREITA - Resultados + Chat */}
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