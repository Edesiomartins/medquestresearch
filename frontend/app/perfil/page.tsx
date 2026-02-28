'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { getApiUrl, API_ENDPOINTS } from '@/app/lib/api-config';
import { useAuth } from '@/app/lib/hooks/useAuth';

interface Perfil {
  id: number;
  nome: string;
  email: string;
  cpf: string;
  telefone: string;
}

export default function PerfilPage() {
  const { token, loading: authLoading } = useAuth();
  const router = useRouter();
  const [perfil, setPerfil] = useState<Perfil | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [erro, setErro] = useState<string | null>(null);
  const [sucesso, setSucesso] = useState(false);

  const [nome, setNome] = useState('');
  const [email, setEmail] = useState('');
  const [cpf, setCpf] = useState('');
  const [telefone, setTelefone] = useState('');

  useEffect(() => {
    if (!authLoading && !token) {
      router.replace('/login');
      return;
    }
    if (!token) return;
    const carregar = async () => {
      try {
        const res = await fetch(getApiUrl(API_ENDPOINTS.PERFIL), {
          headers: { Authorization: `Bearer ${token}` },
        });
        if (res.ok) {
          const data = await res.json();
          setPerfil(data);
          setNome(data.nome ?? '');
          setEmail(data.email ?? '');
          setCpf(data.cpf ?? '');
          setTelefone(data.telefone ?? '');
        }
      } catch (e: unknown) {
        setErro(e instanceof Error ? e.message : 'Erro ao carregar perfil.');
      } finally {
        setLoading(false);
      }
    };
    carregar();
  }, [token, authLoading, router]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!token) return;
    setErro(null);
    setSucesso(false);
    setSaving(true);
    try {
      const res = await fetch(getApiUrl(API_ENDPOINTS.PERFIL), {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          nome: nome.trim() || undefined,
          email: email.trim() || undefined,
          cpf: cpf.trim() || undefined,
          telefone: telefone.trim() || undefined,
        }),
      });
      const data = await res.json().catch(() => ({}));
      if (!res.ok) {
        setErro(data.detail || 'Erro ao atualizar cadastro.');
        return;
      }
      setSucesso(true);
      setPerfil(data.usuario ? { ...perfil, ...data.usuario } : perfil);
    } catch (e: unknown) {
      setErro(e instanceof Error ? e.message : 'Erro de conexão.');
    } finally {
      setSaving(false);
    }
  };

  if (authLoading || (token && loading)) {
    return (
      <div className="min-h-screen bg-gradient-to-b from-slate-50 via-white to-slate-50 flex items-center justify-center">
        <div className="w-10 h-10 border-2 border-[#0c3d66]/30 border-t-[#0c3d66] rounded-full animate-spin" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-50 via-white to-slate-50">
      <header className="sticky top-0 z-10 border-b border-slate-200/80 bg-white/90 backdrop-blur-sm">
        <div className="max-w-2xl mx-auto px-4 sm:px-6 py-4 flex items-center justify-between">
          <Link
            href="/"
            className="text-lg font-bold text-[#0c3d66] hover:text-[#0ea5e9] transition-colors"
          >
            MedQuestResearch
          </Link>
          <Link
            href="/"
            className="text-slate-600 hover:text-[#0c3d66] text-sm font-medium"
          >
            Voltar ao app
          </Link>
        </div>
      </header>

      <main className="max-w-2xl mx-auto px-4 sm:px-6 py-10">
        <h1 className="text-2xl sm:text-3xl font-bold text-[#0c3d66] mb-2">
          Atualizar cadastro
        </h1>
        <p className="text-slate-600 mb-6">
          CPF e telefone são necessários para comprar créditos. Mantenha seus dados atualizados.
        </p>

        {erro && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 text-red-700 rounded-xl text-sm">
            {erro}
          </div>
        )}
        {sucesso && (
          <div className="mb-6 p-4 bg-emerald-50 border border-emerald-200 text-emerald-800 rounded-xl text-sm">
            Cadastro atualizado com sucesso.
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-5">
          <div>
            <label htmlFor="nome" className="block text-sm font-medium text-slate-700 mb-1">
              Nome
            </label>
            <input
              id="nome"
              type="text"
              value={nome}
              onChange={(e) => setNome(e.target.value)}
              className="w-full px-4 py-2.5 rounded-xl border border-slate-300 focus:ring-2 focus:ring-[#0c3d66]/30 focus:border-[#0c3d66]"
              placeholder="Seu nome"
            />
          </div>
          <div>
            <label htmlFor="email" className="block text-sm font-medium text-slate-700 mb-1">
              E-mail
            </label>
            <input
              id="email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full px-4 py-2.5 rounded-xl border border-slate-300 focus:ring-2 focus:ring-[#0c3d66]/30 focus:border-[#0c3d66]"
              placeholder="seu@email.com"
            />
          </div>
          <div>
            <label htmlFor="cpf" className="block text-sm font-medium text-slate-700 mb-1">
              CPF <span className="text-amber-600">*</span>
            </label>
            <input
              id="cpf"
              type="text"
              value={cpf}
              onChange={(e) => setCpf(e.target.value)}
              className="w-full px-4 py-2.5 rounded-xl border border-slate-300 focus:ring-2 focus:ring-[#0c3d66]/30 focus:border-[#0c3d66]"
              placeholder="000.000.000-00"
              maxLength={14}
            />
            <p className="mt-1 text-xs text-slate-500">Obrigatório para comprar créditos.</p>
          </div>
          <div>
            <label htmlFor="telefone" className="block text-sm font-medium text-slate-700 mb-1">
              Telefone (com DDD) <span className="text-amber-600">*</span>
            </label>
            <input
              id="telefone"
              type="text"
              value={telefone}
              onChange={(e) => setTelefone(e.target.value)}
              className="w-full px-4 py-2.5 rounded-xl border border-slate-300 focus:ring-2 focus:ring-[#0c3d66]/30 focus:border-[#0c3d66]"
              placeholder="(00) 00000-0000"
              maxLength={20}
            />
            <p className="mt-1 text-xs text-slate-500">Obrigatório para comprar créditos.</p>
          </div>
          <button
            type="submit"
            disabled={saving}
            className="w-full py-3 rounded-xl font-medium text-white bg-[#0c3d66] hover:bg-[#0a3352] disabled:opacity-60 transition-colors"
          >
            {saving ? 'Salvando...' : 'Salvar alterações'}
          </button>
        </form>

        <p className="mt-8 text-sm text-slate-500">
          <Link href="/planos" className="text-[#0c3d66] hover:underline">
            Comprar créditos
          </Link>
          {' · '}
          <Link href="/" className="text-[#0c3d66] hover:underline">
            Início
          </Link>
        </p>
      </main>
    </div>
  );
}
