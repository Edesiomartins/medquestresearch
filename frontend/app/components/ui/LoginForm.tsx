// app/components/ui/LoginForm.tsx
'use client';

import { useState } from 'react';
import { useAuth } from '@/app/lib/hooks/useAuth';

export default function LoginForm() {
  const { login, loading, erro } = useAuth();
  const [email, setEmail] = useState('');
  const [senha, setSenha] = useState('');
  const [emailError, setEmailError] = useState<string | null>(null);
  const [senhaError, setSenhaError] = useState<string | null>(null);

  // Função de validação de email
  const validateEmail = (email: string) => {
    if (!email) return "Email é obrigatório.";
    if (!/\S+@\S+\.\S+/.test(email)) return "Email inválido.";
    return null;
  };

  // Função de validação de senha
  const validateSenha = (senha: string) => {
    if (!senha) return "Senha é obrigatória.";
    if (senha.length < 6) return "A senha deve ter no mínimo 6 caracteres.";
    return null;
  };

  // Handler para mudança no campo de email com validação em tempo real
  const handleEmailChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newEmail = e.target.value;
    setEmail(newEmail);
    setEmailError(validateEmail(newEmail));
  };

  // Handler para mudança no campo de senha com validação em tempo real
  const handleSenhaChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newSenha = e.target.value;
    setSenha(newSenha);
    setSenhaError(validateSenha(newSenha));
  };

  // Handler para o envio do formulário
  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    // Validação final antes de enviar
    const emailValidation = validateEmail(email);
    const senhaValidation = validateSenha(senha);

    setEmailError(emailValidation);
    setSenhaError(senhaValidation);

    if (emailValidation || senhaValidation) {
      return; // Impede o envio se houver erros de validação
    }

    const ok = await login(email, senha);
    if (ok) {
      window.location.href = "/"; // Redireciona em caso de sucesso
    }
  }

  return (
    <form
      onSubmit={handleSubmit}
      className="space-y-6 animate-fade-in-up" // Animação de entrada para o formulário
    >
      {/* Mensagem de erro geral da API */}
      {erro && (
        <div className="p-3 bg-red-50 border border-red-300 text-red-700 rounded-lg text-sm">
          ❌ {erro}
          {((erro || "").toLowerCase().includes("conexão") ||
            (erro || "").toLowerCase().includes("cross-origin") ||
            (erro || "").toLowerCase().includes("network") ||
            (erro || "").toLowerCase().includes("fetch")) && (
            <p className="mt-2 text-xs">
              A API pode estar indisponível. Verifique se o backend está no ar (/, /health no domínio da API).
            </p>
          )}
        </div>
      )}

      {/* Campo de Email */}
      <div>
        <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-2">
          Email
        </label>
        <div className="relative">
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            {/* Ícone de Email (SVG) */}
            <svg className="h-5 w-5 text-gray-400" fill="currentColor" viewBox="0 0 20 20">
              <path d="M2.003 5.884L10 9.882l7.997-3.998A2 2 0 0016 4H4a2 2 0 00-1.997 1.884z"></path>
              <path d="M18 8.118l-8 4-8-4V14a2 2 0 002 2h12a2 2 0 002-2V8.118z"></path>
            </svg>
          </div>
          <input
            id="email"
            type="email"
            placeholder="seu@email.com"
            value={email}
            onChange={handleEmailChange}
            required
            className={`input-field pl-10 ${emailError ? 'border-red-500 focus:border-red-500' : (email && !emailError ? 'border-green-500 focus:border-green-500' : 'border-gray-300 focus:border-[#0284c7]')}`}
            aria-invalid={emailError ? "true" : "false"}
            aria-describedby="email-error"
          />
        </div>
        {emailError && (
          <p id="email-error" className="mt-2 text-sm text-red-600 animate-fade-in">
            {emailError}
          </p>
        )}
      </div>

      {/* Campo de Senha */}
      <div>
        <label htmlFor="senha" className="block text-sm font-medium text-gray-700 mb-2">
          Senha
        </label>
        <div className="relative">
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            {/* Ícone de Senha (SVG) */}
            <svg className="h-5 w-5 text-gray-400" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M18 8H2V6h16v2zm0 4H2v-2h16v2zm-5 4H2v-2h11v2z" clipRule="evenodd"></path>
            </svg>
          </div>
          <input
            id="senha"
            type="password"
            placeholder="••••••••"
            value={senha}
            onChange={handleSenhaChange}
            required
            className={`input-field pl-10 ${senhaError ? 'border-red-500 focus:border-red-500' : (senha && !senhaError ? 'border-green-500 focus:border-green-500' : 'border-gray-300 focus:border-[#0284c7]')}`}
            aria-invalid={senhaError ? "true" : "false"}
            aria-describedby="senha-error"
          />
        </div>
        {senhaError && (
          <p id="senha-error" className="mt-2 text-sm text-red-600 animate-fade-in">
            {senhaError}
          </p>
        )}
      </div>

      {/* Botão de Enviar */}
      <button
        type="submit"
        className="w-full py-3 px-4 rounded-lg font-semibold text-white bg-[#0284c7] hover:bg-[#075985] focus:outline-none focus:ring-2 focus:ring-[#0284c7] focus:ring-opacity-50 transition-all duration-300 ease-in-out disabled:opacity-60 disabled:cursor-not-allowed disabled:hover:bg-[#0284c7]"
      >
        {loading ? '⏳ Autenticando...' : '🔓 Entrar'}
      </button>
    </form>
  );
}