'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { useAuth } from '@/app/lib/hooks/useAuth';
import LoginForm from '@/app/components/LoginForm';
import ExplicarForm from '@/app/components/ExplicarForm';

export default function Home() {
  const { token, usuario, creditos, loading, logout } = useAuth();
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted || loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-pulse-blue text-2xl">⏳ Carregando...</div>
      </div>
    );
  }

  return (
    <div className="space-y-6 animate-fade-in-up">
      {!token ? (
        <LoginForm onSuccess={() => window.location.reload()} />
      ) : (
        <>
          {/* Welcome Card */}
          <div className="card-elevated bg-gradient-blue-subtle border-blue-300">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-2xl font-bold text-blue-900 mb-2">
                  Bem-vindo, {usuario?.nome || usuario?.email}! 👋
                </h2>
                <p className="text-blue-700">
                  Você tem <span className="font-bold text-blue-900">{creditos}</span> créditos disponíveis
                </p>
              </div>
              <button
                onClick={logout}
                className="btn btn-primary"
              >
                🚪 Logout
              </button>
            </div>
          </div>

          {/* Features Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {/* Explicar Card */}
            <div className="card hover:shadow-lg">
              <div className="text-4xl mb-3">📚</div>
              <h3 className="text-lg font-bold text-blue-900 mb-2">Explicar Conceito</h3>
              <p className="text-slate-600 text-sm mb-4">
                Entenda conceitos complexos de artigos científicos com explicações claras
              </p>
              <Link href="/explicar" className="btn btn-primary-light text-sm">
                Começar →
              </Link>
            </div>

            {/* Crítica Card */}
            <div className="card hover:shadow-lg">
              <div className="text-4xl mb-3">🔍</div>
              <h3 className="text-lg font-bold text-blue-900 mb-2">Análise Crítica</h3>
              <p className="text-slate-600 text-sm mb-4">
                Análise profunda e crítica de artigos científicos
              </p>
              <Link href="/critica" className="btn btn-primary-light text-sm">
                Começar →
              </Link>
            </div>

            {/* Fatos Card */}
            <div className="card hover:shadow-lg">
              <div className="text-4xl mb-3">✓</div>
              <h3 className="text-lg font-bold text-blue-900 mb-2">Verificar Fatos</h3>
              <p className="text-slate-600 text-sm mb-4">
                Valide afirmações e fatos com base em evidências científicas
              </p>
              <Link href="/fatos" className="btn btn-primary-light text-sm">
                Começar →
              </Link>
            </div>

            {/* Perspectiva Card */}
            <div className="card hover:shadow-lg">
              <div className="text-4xl mb-3">🌍</div>
              <h3 className="text-lg font-bold text-blue-900 mb-2">Pesquisar Perspectivas</h3>
              <p className="text-slate-600 text-sm mb-4">
                Explore diferentes perspectivas sobre um tópico
              </p>
              <Link href="/perspectiva" className="btn btn-primary-light text-sm">
                Começar →
              </Link>
            </div>

            {/* PDF Card */}
            <div className="card hover:shadow-lg">
              <div className="text-4xl mb-3">📄</div>
              <h3 className="text-lg font-bold text-blue-900 mb-2">Analisar PDF</h3>
              <p className="text-slate-600 text-sm mb-4">
                Faça upload de PDFs científicos para análise automática
              </p>
              <Link href="/pdf" className="btn btn-primary-light text-sm">
                Começar →
              </Link>
            </div>

            {/* Dashboard Card */}
            <div className="card hover:shadow-lg">
              <div className="text-4xl mb-3">📊</div>
              <h3 className="text-lg font-bold text-blue-900 mb-2">Histórico</h3>
              <p className="text-slate-600 text-sm mb-4">
                Veja seu histórico de análises e resultados anteriores
              </p>
              <Link href="/historico" className="btn btn-primary-light text-sm">
                Começar →
              </Link>
            </div>
          </div>

          {/* Quick Start Section */}
          <div className="card-elevated">
            <h3 className="text-xl font-bold text-blue-900 mb-4">🚀 Comece Agora</h3>
            <ExplicarForm token={token} />
          </div>
        </>
      )}
    </div>
  );
}
