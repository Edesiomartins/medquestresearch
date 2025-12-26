'use client';

import { useState } from 'react';

interface CriticaModalProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: (focoAnalise: string) => void;
}

// Os 9 métodos de análise crítica científica
const METODOS_ANALISE = [
  {
    id: 'metodologia',
    nome: 'Metodologia',
    descricao: 'Avalia o desenho do estudo, métodos utilizados e adequação metodológica',
    icon: '🔬'
  },
  {
    id: 'validade',
    nome: 'Validade Interna e Externa',
    descricao: 'Analisa a validade das conclusões dentro e fora do contexto do estudo',
    icon: '✅'
  },
  {
    id: 'confiabilidade',
    nome: 'Confiabilidade',
    descricao: 'Verifica a consistência e reprodutibilidade dos resultados',
    icon: '📊'
  },
  {
    id: 'vieses',
    nome: 'Vieses e Limitações',
    descricao: 'Identifica possíveis vieses de seleção, informação, confusão e outras limitações',
    icon: '⚠️'
  },
  {
    id: 'amostra',
    nome: 'Amostragem e Tamanho Amostral',
    descricao: 'Avalia a representatividade da amostra e poder estatístico',
    icon: '👥'
  },
  {
    id: 'estatistica',
    nome: 'Análise Estatística',
    descricao: 'Revisa métodos estatísticos, testes utilizados e interpretação dos dados',
    icon: '📈'
  },
  {
    id: 'etico',
    nome: 'Aspectos Éticos',
    descricao: 'Examina questões éticas, consentimento informado e aprovação de comitês',
    icon: '⚖️'
  },
  {
    id: 'relevancia',
    nome: 'Relevância Clínica/Científica',
    descricao: 'Avalia a importância prática e científica dos achados',
    icon: '🎯'
  },
  {
    id: 'geral',
    nome: 'Análise Geral',
    descricao: 'Análise crítica abrangente cobrindo todos os aspectos principais',
    icon: '📚'
  }
];

export default function CriticaModal({ isOpen, onClose, onConfirm }: CriticaModalProps) {
  const [focoSelecionado, setFocoSelecionado] = useState<string>('geral');

  if (!isOpen) return null;

  const handleConfirm = () => {
    onConfirm(focoSelecionado);
    setFocoSelecionado('geral'); // Reset para próxima vez
  };

  const handleCancel = () => {
    setFocoSelecionado('geral');
    onClose();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
      <div className="bg-white rounded-lg shadow-xl max-w-3xl w-full mx-4 max-h-[90vh] overflow-y-auto">
        <div className="p-6">
          <h2 className="text-2xl font-bold text-[#0c3d66] mb-4">
            Escolha o Método de Análise Crítica
          </h2>
          <p className="text-slate-600 mb-6">
            Selecione um dos 9 métodos científicos de análise crítica para aplicar ao artigo:
          </p>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-3 mb-6">
            {METODOS_ANALISE.map((metodo) => (
              <button
                key={metodo.id}
                onClick={() => setFocoSelecionado(metodo.id)}
                className={`p-4 rounded-lg border-2 text-left transition-all ${
                  focoSelecionado === metodo.id
                    ? 'border-[#2563eb] bg-[#eff6ff] shadow-md'
                    : 'border-slate-200 bg-white hover:border-slate-300 hover:bg-slate-50'
                }`}
              >
                <div className="flex items-start gap-3">
                  <span className="text-2xl">{metodo.icon}</span>
                  <div className="flex-1">
                    <h3 className="font-semibold text-slate-800 mb-1">
                      {metodo.nome}
                    </h3>
                    <p className="text-sm text-slate-600">
                      {metodo.descricao}
                    </p>
                  </div>
                  {focoSelecionado === metodo.id && (
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

          <div className="flex gap-3 justify-end">
            <button
              onClick={handleCancel}
              className="px-4 py-2 text-slate-600 bg-slate-100 rounded-lg hover:bg-slate-200 transition-colors"
            >
              Cancelar
            </button>
            <button
              onClick={handleConfirm}
              className="px-6 py-2 bg-[#2563eb] text-white rounded-lg hover:bg-[#1d4ed8] transition-colors font-medium"
            >
              Confirmar Análise
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

