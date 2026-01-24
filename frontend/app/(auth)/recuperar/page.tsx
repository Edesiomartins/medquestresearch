"use client";

import Link from "next/link";
import Image from "next/image";

export default function RecuperarPage() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-[#075985] to-[#0284c7] p-4 sm:p-6 lg:p-8">
      <div className="w-full max-w-md bg-white rounded-xl shadow-2xl p-8 sm:p-10">
        <div className="text-center mb-8">
          <div className="mx-auto mb-6 flex justify-center">
            <Image
              src="/logo-medquestresearch.png"
              alt="MedQuestResearch"
              width={120}
              height={120}
              className="object-contain"
            />
          </div>
          <h1 className="text-2xl font-bold text-[#075985] mb-2">
            Recuperar senha
          </h1>
          <p className="text-gray-600 text-sm">
            Em breve você poderá redefinir sua senha por e-mail.
          </p>
        </div>

        <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg text-center text-sm text-blue-800 mb-6">
          Entre em contato com o suporte para redefinir sua senha.
        </div>

        <Link
          href="/login"
          className="block w-full py-3 text-center rounded-lg font-semibold text-white bg-[#0284c7] hover:bg-[#075985] transition-colors"
        >
          Voltar ao login
        </Link>
      </div>
    </div>
  );
}
