"use client";

import { useState } from "react";
import { useAuth } from "@/app/lib/hooks/useAuth";

export default function RegisterForm() {
  const { register, loading, erro } = useAuth();
  const [nome, setNome] = useState("");
  const [email, setEmail] = useState("");
  const [senha, setSenha] = useState("");
  const [confirmarSenha, setConfirmarSenha] = useState("");
  const [erroLocal, setErroLocal] = useState<string | null>(null);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setErroLocal(null);

    if (!nome || !email || !senha) {
      setErroLocal("Preencha todos os campos.");
      return;
    }
    if (senha !== confirmarSenha) {
      setErroLocal("As senhas não conferem.");
      return;
    }

    const ok = await register(nome, email, senha);
    if (ok) {
      window.location.href = "/";
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {(erro || erroLocal) && (
        <div className="text-sm text-red-600 bg-red-50 border border-red-200 rounded-lg p-2">
          {erro || erroLocal}
        </div>
      )}

      <div>
        <label className="block text-sm font-medium text-slate-700 mb-1">
          Nome completo
        </label>
        <input
          type="text"
          value={nome}
          onChange={(e) => setNome(e.target.value)}
          className="input w-full"
          placeholder="Seu nome"
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-slate-700 mb-1">
          E-mail
        </label>
        <input
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          className="input w-full"
          placeholder="seu@email.com"
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-slate-700 mb-1">
          Senha
        </label>
        <input
          type="password"
          value={senha}
          onChange={(e) => setSenha(e.target.value)}
          className="input w-full"
          placeholder="••••••••"
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-slate-700 mb-1">
          Confirmar senha
        </label>
        <input
          type="password"
          value={confirmarSenha}
          onChange={(e) => setConfirmarSenha(e.target.value)}
          className="input w-full"
          placeholder="••••••••"
        />
      </div>

      <button
        type="submit"
        disabled={loading}
        className="btn btn-primary w-full"
      >
        {loading ? "Criando conta..." : "Criar conta"}
      </button>
    </form>
  );
}
