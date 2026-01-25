"use client";

import Link from "next/link";
import Image from "next/image";
import RegisterForm from "@/app/components/ui/RegisterForm";

export default function RegisterPage() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-linear-to-br from-[#075985] to-[#0284c7] p-4 sm:p-6 lg:p-8">
      <div className="w-full max-w-md bg-white rounded-xl shadow-2xl p-8 sm:p-10 lg:p-12 animate-fade-in-up">
        {/* Logo e título — igual ao login */}
        <div className="text-center mb-8">
          <div className="mx-auto mb-6 flex justify-center items-center">
            <Image
              src="/logo-medquestresearch.png"
              alt="MedQuestResearch Logo"
              width={150}
              height={150}
              priority
              unoptimized
              className="object-contain w-auto h-auto max-w-[150px] max-h-[150px]"
            />
          </div>
          <h1 className="text-3xl font-extrabold text-[#075985] mb-2">
            Criar conta
          </h1>
          <p className="text-md text-gray-600">
            Cadastre-se para usar o MedQuest Research
          </p>
        </div>

        <RegisterForm />

        {/* Link para login — mesmo padrão do login */}
        <div className="text-center mt-8">
          <p className="text-gray-600">
            Já tem conta?{" "}
            <Link href="/login" className="text-[#0284c7] font-semibold hover:underline transition-colors duration-200">
              Entrar
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
