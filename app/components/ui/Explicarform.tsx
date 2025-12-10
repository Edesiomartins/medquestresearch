'use client';

import { useState } from 'react';
import { explicarConceito } from '@/lib/api';

export default function ExplicarForm({ token }: { token: string }) {
  const [texto, setTexto] = useState('');
  const [trecho, setTrecho] = useState('');
  const [nivel, setNivel] = useState('graduação');
  const [resultado, setResultado] = useState('');
  const [loading, setLoading] = useState(false);
  const [erro, setErro] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setErro('');
    setResultado('');

    const res = await explicarConceito(token, texto, trecho, nivel);
    if (res.erro) {
      setErro(res.erro);
    } else {
      setResultado(res.resultado || JSON.stringify(res));
    }
    setLoading(false);
  };

  return (
    <div className="analysis-card">
      <h2 className="card-title">Explicar Conceito</h2>
      <form onSubmit={handleSubmit}>
        <textarea
          placeholder="Cole o texto do artigo científico aqui..."
          value={texto}
          onChange={(e) => setTexto(e.target.value)}
          required
          style={{ width: '100%', height: '150px', padding: '10px', marginBottom: '10px', borderRadius: '4px', border: '1px solid #ccc' }}
        />
        <input
          type="text"
          placeholder="Conceito/trecho a explicar"
          value={trecho}
          onChange={(e) => setTrecho(e.target.value)}
          required
          style={{ width: '100%', padding: '10px', marginBottom: '10px', borderRadius: '4px', border: '1px solid #ccc' }}
        />
        <select
          value={nivel}
          onChange={(e) => setNivel(e.target.value)}
          style={{ width: '100%', padding: '10px', marginBottom: '10px', borderRadius: '4px', border: '1px solid #ccc' }}
        >
          <option value="graduação">Graduação</option>
          <option value="mestrado">Mestrado</option>
          <option value="doutorado">Doutorado</option>
        </select>
        <button type="submit" className="card-button" disabled={loading}>
          {loading ? 'Analisando...' : 'Explicar'}
        </button>
      </form>
      {erro && <p style={{ color: 'red', marginTop: '10px' }}>{erro}</p>}
      {resultado && <div className="result-area">{resultado}</div>}
    </div>
  );
}