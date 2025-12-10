'use client';

import { useState } from 'react';
import { login } from '@/lib/api';

export default function LoginForm({ onLoginSuccess }: { onLoginSuccess: (token: string) => void }) {
  const [email, setEmail] = useState('');
  const [senha, setSenha] = useState('');
  const [loading, setLoading] = useState(false);
  const [erro, setErro] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setErro('');

    const res = await login(email, senha);
    if (res.erro) {
      setErro(res.erro);
    } else {
      localStorage.setItem('token', res.token!);
      onLoginSuccess(res.token!);
    }
    setLoading(false);
  };

  return (
    <form onSubmit={handleSubmit} className="analysis-card" style={{ maxWidth: '400px', margin: '0 auto' }}>
      <h2 className="card-title">Login MedQuest Research</h2>
      {erro && <p style={{ color: 'red' }}>{erro}</p>}
      <input
        type="email"
        placeholder="Email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        required
        style={{ width: '100%', padding: '10px', marginBottom: '10px', borderRadius: '4px', border: '1px solid #ccc' }}
      />
      <input
        type="password"
        placeholder="Senha"
        value={senha}
        onChange={(e) => setSenha(e.target.value)}
        required
        style={{ width: '100%', padding: '10px', marginBottom: '10px', borderRadius: '4px', border: '1px solid #ccc' }}
      />
      <button type="submit" className="card-button" disabled={loading}>
        {loading ? 'Autenticando...' : 'Entrar'}
      </button>
    </form>
  );
}