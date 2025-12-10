'use client';

import { useState } from 'react';
import { useAuth } from '@/app/lib/hooks/useAuth';

export default function LoginForm({ onSuccess }: { onSuccess: () => void }) {
  const { login, loading, erro } = useAuth();
  const [email, setEmail] = useState('');
  const [senha, setSenha] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const success = await login(email, senha);
    if (success) {
      onSuccess();
    }
  };

  return (
    <div className="flex items-center justify-center min-h-screen bg-gradient-blue-subtle">
      <form
        onSubmit={handleSubmit}
        className="card-elevated w-full max-w-md animate-fade-in-up"
      >
        <h2 className="text-3xl font-bold text-blue-900 mb-6 text-center">
          🔐 Login MedQuest
        </h2>
        {erro && (
          <div className="mb-4 p-4 bg-red-50 border border-red-300 rounded-lg">
            <p className="text-red-700 text-sm">❌ {erro}</p>
          </div>
        )}
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-semibold text-slate-700 mb-2">
              Email
            </label>
            <input
              type="email"
              placeholder="seu@email.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              className="input"
            />
          </div>
          <div>
            <label className="block text-sm font-semibold text-slate-700 mb-2">
              Senha
            </label>
            <input
              type="password"
              placeholder="••••••••"
              value={senha}
              onChange={(e) => setSenha(e.target.value)}
              required
              className="input"
            />
          </div>
          <button
            type="submit"
            disabled={loading}
            className="btn btn-primary w-full"
          >
            {loading ? '⏳ Autenticando...' : '🔓 Entrar'}
          </button>
        </div>
        <p className="text-center text-sm text-slate-600 mt-4">
          Não tem conta?{' '}
          <a href="#" className="text-blue-600 hover:text-blue-700 font-semibold">
            Cadastre-se
          </a>
        </p>
      </form>
    </div>
  );
}

