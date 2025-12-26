"use client";

import Link from "next/link";
import RegisterForm from "@/app/components/ui/RegisterForm";

export default function RegisterPage() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-linear-to-b from-mq-blue-50 to-white px-4">
      <div className="w-full max-w-md bg-white border border-blue-100 rounded-2xl shadow-lg p-8 animate-fade-in-up">
        {/* Logo */}
        <div className="text-center mb-8">
          <div className="mx-auto w-16 h-16 rounded-2xl flex items-center justify-center gradient-blue shadow-md">
            <span className="text-3xl text-white font-bold">MQ</span>
          </div>
          <h1 className="mt-4 text-2xl font-bold text-slate-900">
            Criar conta
          </h1>
          <p className="text-slate-600 text-sm mt-2">
            Cadastre-se para usar o MedQuest Research
          </p>
        </div>

        <RegisterForm />

        <p className="text-center text-sm text-slate-600 mt-6">
          Já tem conta?{" "}
          <Link href="/login" className="text-blue-700 font-semibold hover:underline">
            Entrar
          </Link>
        </p>
      </div>
    </div>
  );
}
