'use client';

import { useState } from 'react';

interface ExplicarModalProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: (trecho: string, nivel: string) => void;
}

export default function ExplicarModal({ isOpen, onClose, onConfirm }: ExplicarModalProps) {
  const [trecho, setTrecho] = useState('');
  const [nivel, setNivel] = useState('graduação');

  if (!isOpen) return null;

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (trecho.trim()) {
      onConfirm(trecho.trim(), nivel);
      setTrecho('');
      onClose();
    }
  };

  return (
    <div 
      className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50"
      onClick={onClose}
      onMouseDown={(e) => e.stopPropagation()}
    >
      <div 
        className="bg-white rounded-xl shadow-2xl max-w-md w-full mx-4 p-6 select-text"
        onClick={(e) => e.stopPropagation()}
        onMouseDown={(e) => e.stopPropagation()}
        style={{ userSelect: 'text' }}
      >
        <h2 className="text-2xl font-bold text-mq-slate-800 mb-4">
          Explicar Conteúdo
        </h2>
        <p className="text-sm text-mq-slate-600 mb-6">
          Digite o termo, conceito ou trecho específico que deseja que seja explicado.
        </p>

        <form onSubmit={handleSubmit}>
          <div className="mb-4">
            <label htmlFor="trecho" className="block text-sm font-medium text-mq-slate-700 mb-2">
              Termo ou conteúdo a explicar *
            </label>
            <textarea
              id="trecho"
              value={trecho}
              onChange={(e) => setTrecho(e.target.value)}
              placeholder="Ex: 'metodologia do estudo', 'resultados principais', 'conceito X'..."
              className="w-full px-4 py-2 border border-mq-slate-300 rounded-lg focus:ring-2 focus:ring-mq-blue-500 focus:border-mq-blue-500 outline-none resize-none"
              rows={3}
              required
            />
          </div>

          <div className="mb-6">
            <label htmlFor="nivel" className="block text-sm font-medium text-mq-slate-700 mb-2">
              Nível de explicação
            </label>
            <select
              id="nivel"
              value={nivel}
              onChange={(e) => setNivel(e.target.value)}
              className="w-full px-4 py-2 border border-mq-slate-300 rounded-lg focus:ring-2 focus:ring-mq-blue-500 focus:border-mq-blue-500 outline-none"
            >
              <option value="leigo">Leigo</option>
              <option value="graduação">Graduação</option>
              <option value="pós-graduação">Pós-graduação</option>
              <option value="especialista">Especialista</option>
            </select>
          </div>

          <div className="flex gap-3 justify-end">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-mq-slate-700 bg-mq-slate-100 rounded-lg hover:bg-mq-slate-200 transition-colors"
            >
              Cancelar
            </button>
            <button
              type="submit"
              disabled={!trecho.trim()}
              className="px-4 py-2 bg-mq-blue-600 text-white rounded-lg hover:bg-mq-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              Explicar
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

