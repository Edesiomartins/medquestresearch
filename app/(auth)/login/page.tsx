// app/(auth)/login/page.tsx
"use client";

import Link from "next/link";
import Image from "next/image";
import LoginForm from "@/app/components/ui/LoginForm";

export default function LoginPage() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-linear-to-br from-[#075985] to-[#0284c7] p-4 sm:p-6 lg:p-8 animate-fade-in">
      <div className="w-full max-w-md bg-white rounded-xl shadow-2xl p-8 sm:p-10 lg:p-12 animate-slide-up">
        {/* Logo e Seção de Boas-Vindas */}
        <div className="text-center mb-8">
          <div className="mx-auto mb-6 flex justify-center items-center">
            {/* Logo MedQuestResearch */}
            <Image
              src="/logo-medquestresearch.png"
              alt="MedQuestResearch Logo"
              width={150}
              height={150}
              priority
              unoptimized
              className="object-contain w-auto h-auto max-w-[150px] max-h-[150px]"
              onError={(e) => {
                // Fallback se a imagem não carregar
                console.error('Erro ao carregar logo');
              }}
            />
          </div>
          <h1 className="text-3xl font-extrabold text-[#075985] mb-2">
            Bem-vindo ao MedQuestResearch
          </h1>
          <p className="text-md text-gray-600">
            Sua plataforma inteligente para análise científica e médica.
          </p>
        </div>

        {/* Componente do Formulário de Login */}
        <LoginForm />

        {/* Links para Recuperar Senha e Criar Conta */}
        <div className="text-center mt-8 space-y-3 text-sm">
          <Link href="/recuperar" className="text-[#0284c7] hover:underline font-medium transition-colors duration-200">
            Esqueceu sua senha?
          </Link>

          <p className="text-gray-600">
            Ainda não tem conta?{" "}
            <Link href="/register" className="text-[#0284c7] font-semibold hover:underline transition-colors duration-200">
              Criar conta
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}