'use client';

import { useState } from 'react';

interface MetaAnaliseModalProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: (etapa: string, tema?: string, estilo?: string) => void;
}

const ETAPAS_META_ANALISE = [
  {
    id: '1',
    nome: 'Etapa 1: Estruturação PICO e Protocolo',
    descricao: 'Gere a pergunta PICO, estratégia de busca e critérios de elegibilidade',
    icon: '📋'
  },
  {
    id: '2',
    nome: 'Etapa 2: Extração de Dados',
    descricao: 'Extraia dados dos artigos e crie tabela de evidências (JSON)',
    icon: '📊'
  },
  {
    id: '3',
    nome: 'Etapa 3: Redação Técnica (PRISMA)',
    descricao: 'Redija as seções: Métodos, Resultados e Discussão conforme PRISMA',
    icon: '✍️'
  },
  {
    id: '4',
    nome: 'Etapa 4: Verificação Final',
    descricao: 'Revisão final, formatação e verificação de conformidade PRISMA',
    icon: '✅'
  }
];

const ESTILOS_REFERENCIA = [
  { id: 'Vancouver', nome: 'Vancouver' },
  { id: 'ABNT', nome: 'ABNT' }
];

export default function MetaAnaliseModal({ isOpen, onClose, onConfirm }: MetaAnaliseModalProps) {
  const [etapaSelecionada, setEtapaSelecionada] = useState<string>('1');
  const [tema, setTema] = useState('');
  const [estilo, setEstilo] = useState<string>('Vancouver');

  if (!isOpen) return null;

  const handleConfirm = () => {
    onConfirm(etapaSelecionada, tema.trim() || undefined, estilo);
    setEtapaSelecionada('1');
    setTema('');
    setEstilo('Vancouver');
  };

  const handleCancel = () => {
    setEtapaSelecionada('1');
    setTema('');
    setEstilo('Vancouver');
    onClose();
  };

  return (
    <div 
      className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50"
      onClick={onClose}
      onMouseDown={(e) => e.stopPropagation()}
    >
      <div 
        className="bg-white rounded-lg shadow-xl max-w-3xl w-full mx-4 max-h-[90vh] overflow-y-auto select-text"
        onClick={(e) => e.stopPropagation()}
        onMouseDown={(e) => e.stopPropagation()}
        style={{ userSelect: 'text' }}
      >
        <div className="p-6">
          <h2 className="text-2xl font-bold text-[#0c3d66] mb-4">
            Meta-Análise - Configuração PRISMA
          </h2>
          <p className="text-slate-600 mb-6">
            Selecione a etapa do workflow de meta-análise que deseja executar:
          </p>

          {/* Seleção de Etapa */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-slate-700 mb-3">
              Etapa do Workflow *
            </label>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {ETAPAS_META_ANALISE.map((etapa) => (
                <button
                  key={etapa.id}
                  onClick={() => setEtapaSelecionada(etapa.id)}
                  className={`p-4 rounded-lg border-2 text-left transition-all ${
                    etapaSelecionada === etapa.id
                      ? 'border-[#2563eb] bg-[#eff6ff] shadow-md'
                      : 'border-slate-200 bg-white hover:border-slate-300 hover:bg-slate-50'
                  }`}
                >
                  <div className="flex items-start gap-3">
                    <span className="text-2xl">{etapa.icon}</span>
                    <div className="flex-1">
                      <h3 className="font-semibold text-slate-800 mb-1 text-sm">
                        {etapa.nome}
                      </h3>
                      <p className="text-xs text-slate-600">
                        {etapa.descricao}
                      </p>
                    </div>
                    {etapaSelecionada === etapa.id && (
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

          {/* Tema (opcional, principalmente para Etapa 1) */}
          {(etapaSelecionada === '1' || etapaSelecionada === '3') && (
            <div className="mb-6">
              <label htmlFor="tema" className="block text-sm font-medium text-slate-700 mb-2">
                Tema da Revisão {etapaSelecionada === '1' ? '*' : '(opcional)'}
              </label>
              <input
                id="tema"
                type="text"
                value={tema}
                onChange={(e) => setTema(e.target.value)}
                placeholder="Ex: Eficácia da intervenção X em pacientes com condição Y"
                className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-[#2563eb] focus:border-[#2563eb] outline-none"
                required={etapaSelecionada === '1'}
              />
            </div>
          )}

          {/* Estilo de Referência (para Etapa 3 e 4) */}
          {(etapaSelecionada === '3' || etapaSelecionada === '4') && (
            <div className="mb-6">
              <label htmlFor="estilo" className="block text-sm font-medium text-slate-700 mb-2">
                Estilo de Referência
              </label>
              <select
                id="estilo"
                value={estilo}
                onChange={(e) => setEstilo(e.target.value)}
                className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-[#2563eb] focus:border-[#2563eb] outline-none"
              >
                {ESTILOS_REFERENCIA.map((est) => (
                  <option key={est.id} value={est.id}>
                    {est.nome}
                  </option>
                ))}
              </select>
            </div>
          )}

          <div className="flex gap-3 justify-end">
            <button
              onClick={handleCancel}
              className="px-4 py-2 text-slate-600 bg-slate-100 rounded-lg hover:bg-slate-200 transition-colors"
            >
              Cancelar
            </button>
            <button
              onClick={handleConfirm}
              disabled={etapaSelecionada === '1' && !tema.trim()}
              className="px-6 py-2 bg-[#2563eb] text-white rounded-lg hover:bg-[#1d4ed8] transition-colors font-medium disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Iniciar Meta-Análise
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
