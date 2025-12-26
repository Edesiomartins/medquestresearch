'use client';

import { useState } from 'react';
import { useAnalysis } from '@/app/lib/hooks/useAnalysis';

export default function ExplicarForm({ token }: { token: string }) {
  const { explicar, loading, erro, resultado } = useAnalysis(token);
  const [texto, setTexto] = useState('');
  const [trecho, setTrecho] = useState('');
  const [nivel, setNivel] = useState<'graduação' | 'mestrado' | 'doutorado'>('graduação');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await explicar({ texto_artigo: texto, trecho, nivel });
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label className="block text-sm font-semibold text-slate-700 mb-2">
          📚 Texto do Artigo
        </label>
        <textarea
          placeholder="Cole o texto do artigo científico aqui..."
          value={texto}
          onChange={(e) => setTexto(e.target.value)}
          required
          className="input h-32 resize-none"
        />
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-semibold text-slate-700 mb-2">
            🔍 Conceito/Trecho
          </label>
          <input
            type="text"
            placeholder="Ex: machine learning"
            value={trecho}
            onChange={(e) => setTrecho(e.target.value)}
            required
            className="input"
          />
        </div>
        <div>
          <label className="block text-sm font-semibold text-slate-700 mb-2">
            📖 Nível
          </label>
          <select
            value={nivel}
            onChange={(e) => setNivel(e.target.value as any)}
            className="input"
          >
            <option value="graduação">Graduação</option>
            <option value="mestrado">Mestrado</option>
            <option value="doutorado">Doutorado</option>
          </select>
        </div>
      </div>
      {erro && (
        <div className="p-4 bg-red-50 border border-red-300 rounded-lg">
          <p className="text-red-700 text-sm">❌ {erro}</p>
        </div>
      )}
      <button
        type="submit"
        disabled={loading}
        className="btn btn-primary w-full"
      >
        {loading ? '⏳ MedquestResearch analisando...' : '🔍 Explicar Conceito'}
      </button>
      {resultado && (
        <div className="p-4 bg-blue-50 border-l-4 border-blue-500 rounded-lg animate-fade-in-up">
          <h4 className="font-semibold text-blue-900 mb-2">✅ Resultado:</h4>
          <p className="text-slate-700 whitespace-pre-wrap text-sm">{resultado}</p>
        </div>
      )}
    </form>
  );
}

