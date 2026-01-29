'use client';

import { useState } from 'react';

export interface Artigo {
  pmid?: string;
  title: string;
  authors?: string[];
  year?: string;
  abstract?: string;
  doi?: string;
}

interface ArticleSelectorProps {
  artigos: Artigo[];
  totalArtigos?: number;
  tema: string;
  onArtigosSelecionados?: (artigosSelecionados: Artigo[]) => void;
}

export default function ArticleSelector({ 
  artigos, 
  totalArtigos,
  tema,
  onArtigosSelecionados 
}: ArticleSelectorProps) {
  const [artigosSelecionados, setArtigosSelecionados] = useState<Set<string>>(new Set());
  const [filtroTexto, setFiltroTexto] = useState('');
  const [expandido, setExpandido] = useState<Set<string>>(new Set());

  const toggleSelecao = (pmid: string | undefined, title: string) => {
    const id = pmid || title;
    const novosSelecionados = new Set(artigosSelecionados);
    
    if (novosSelecionados.has(id)) {
      novosSelecionados.delete(id);
    } else {
      novosSelecionados.add(id);
    }
    
    setArtigosSelecionados(novosSelecionados);
    
    // Notificar componente pai
    if (onArtigosSelecionados) {
      const artigosSelecionadosArray = artigos.filter(a => {
        const artigoId = a.pmid || a.title;
        return novosSelecionados.has(artigoId);
      });
      onArtigosSelecionados(artigosSelecionadosArray);
    }
  };

  const toggleExpandir = (id: string) => {
    const novosExpandidos = new Set(expandido);
    if (novosExpandidos.has(id)) {
      novosExpandidos.delete(id);
    } else {
      novosExpandidos.add(id);
    }
    setExpandido(novosExpandidos);
  };

  const selecionarTodos = () => {
    const todosIds = new Set(artigos.map(a => a.pmid || a.title));
    setArtigosSelecionados(todosIds);
    
    if (onArtigosSelecionados) {
      onArtigosSelecionados(artigos);
    }
  };

  const deselecionarTodos = () => {
    setArtigosSelecionados(new Set());
    if (onArtigosSelecionados) {
      onArtigosSelecionados([]);
    }
  };

  // Filtrar artigos pelo texto de busca
  const artigosFiltrados = artigos.filter(artigo => {
    if (!filtroTexto) return true;
    const busca = filtroTexto.toLowerCase();
    return (
      artigo.title?.toLowerCase().includes(busca) ||
      artigo.abstract?.toLowerCase().includes(busca) ||
      artigo.authors?.some(a => a.toLowerCase().includes(busca)) ||
      artigo.year?.includes(busca)
    );
  });

  if (artigos.length === 0) {
    return (
      <div className="p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
        <p className="text-sm text-yellow-800">
          Nenhum artigo encontrado para o tema: <strong>{tema}</strong>
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Cabeçalho com estatísticas */}
      <div className="flex items-center justify-between p-4 bg-blue-50 border border-blue-200 rounded-lg">
        <div>
          <h3 className="text-lg font-semibold text-blue-900 mb-1">
            Artigos Encontrados - PRISMA Check
          </h3>
          <p className="text-sm text-blue-700">
            <strong>Tema:</strong> {tema}
          </p>
          <p className="text-sm text-blue-700 mt-1">
            {artigosFiltrados.length} de {totalArtigos || artigos.length} artigos exibidos
            {artigosSelecionados.size > 0 && (
              <span className="ml-2 font-semibold">
                • {artigosSelecionados.size} selecionado{artigosSelecionados.size > 1 ? 's' : ''}
              </span>
            )}
          </p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={selecionarTodos}
            className="px-3 py-1.5 text-xs bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
          >
            Selecionar Todos
          </button>
          <button
            onClick={deselecionarTodos}
            className="px-3 py-1.5 text-xs bg-slate-200 text-slate-700 rounded hover:bg-slate-300 transition-colors"
          >
            Limpar Seleção
          </button>
        </div>
      </div>

      {/* Barra de busca */}
      <div className="relative">
        <input
          type="text"
          value={filtroTexto}
          onChange={(e) => setFiltroTexto(e.target.value)}
          placeholder="Buscar artigos por título, autor, ano ou resumo..."
          className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
        />
        {filtroTexto && (
          <button
            onClick={() => setFiltroTexto('')}
            className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600"
          >
            ✕
          </button>
        )}
      </div>

      {/* Lista de artigos */}
      <div className="space-y-3 max-h-[600px] overflow-y-auto">
        {artigosFiltrados.map((artigo, index) => {
          const artigoId = artigo.pmid || artigo.title;
          const estaSelecionado = artigosSelecionados.has(artigoId);
          const estaExpandido = expandido.has(artigoId);

          return (
            <div
              key={artigoId || index}
              className={`border-2 rounded-lg p-4 transition-all ${
                estaSelecionado
                  ? 'border-blue-500 bg-blue-50 shadow-md'
                  : 'border-slate-200 bg-white hover:border-slate-300'
              }`}
            >
              {/* Cabeçalho do artigo */}
              <div className="flex items-start gap-3">
                {/* Checkbox de seleção */}
                <input
                  type="checkbox"
                  checked={estaSelecionado}
                  onChange={() => toggleSelecao(artigo.pmid, artigo.title)}
                  className="mt-1 w-5 h-5 text-blue-600 border-slate-300 rounded focus:ring-blue-500"
                />

                {/* Conteúdo do artigo */}
                <div className="flex-1 min-w-0">
                  {/* Título */}
                  <h4 className="font-semibold text-slate-900 mb-2 text-sm leading-snug">
                    {artigo.title}
                  </h4>

                  {/* Metadados */}
                  <div className="flex flex-wrap items-center gap-3 text-xs text-slate-600 mb-2">
                    {artigo.authors && artigo.authors.length > 0 && (
                      <span>
                        <strong>Autores:</strong> {artigo.authors.slice(0, 3).join(', ')}
                        {artigo.authors.length > 3 && ` et al.`}
                      </span>
                    )}
                    {artigo.year && (
                      <span>
                        <strong>Ano:</strong> {artigo.year}
                      </span>
                    )}
                    {artigo.pmid && (
                      <span>
                        <strong>PMID:</strong> {artigo.pmid}
                      </span>
                    )}
                    {artigo.doi && (
                      <span>
                        <strong>DOI:</strong>{' '}
                        <a
                          href={`https://doi.org/${artigo.doi}`}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-blue-600 hover:underline"
                        >
                          {artigo.doi}
                        </a>
                      </span>
                    )}
                  </div>

                  {/* Abstract (expandível) */}
                  {artigo.abstract && (
                    <div className="mt-2">
                      <button
                        onClick={() => toggleExpandir(artigoId)}
                        className="text-xs text-blue-600 hover:text-blue-800 font-medium flex items-center gap-1"
                      >
                        {estaExpandido ? 'Ocultar' : 'Mostrar'} Resumo
                        <svg
                          className={`w-4 h-4 transition-transform ${estaExpandido ? 'rotate-180' : ''}`}
                          fill="none"
                          stroke="currentColor"
                          viewBox="0 0 24 24"
                        >
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                        </svg>
                      </button>
                      {estaExpandido && (
                        <p className="mt-2 text-xs text-slate-700 leading-relaxed bg-slate-50 p-3 rounded border border-slate-200">
                          {artigo.abstract}
                        </p>
                      )}
                    </div>
                  )}

                  {/* Links */}
                  <div className="mt-2 flex gap-2">
                    {artigo.pmid && (
                      <a
                        href={`https://pubmed.ncbi.nlm.nih.gov/${artigo.pmid}`}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-xs text-blue-600 hover:text-blue-800 underline"
                      >
                        Ver no PubMed
                      </a>
                    )}
                    {artigo.doi && (
                      <a
                        href={`https://doi.org/${artigo.doi}`}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-xs text-blue-600 hover:text-blue-800 underline"
                      >
                        Ver DOI
                      </a>
                    )}
                  </div>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {artigosFiltrados.length === 0 && filtroTexto && (
        <div className="text-center py-8 text-slate-500">
          <p>Nenhum artigo encontrado com o filtro "{filtroTexto}"</p>
        </div>
      )}
    </div>
  );
}
