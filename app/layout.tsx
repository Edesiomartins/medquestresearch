import type { ReactNode } from "react";
import "./globals.css";

export const metadata = {
  title: "MedQuestResearch",
  description:
    "Plataforma inteligente de leitura crítica, análise científica e geração de conhecimento assistida por IA."
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="pt-BR">
      <body className="min-h-screen bg-slate-50 text-slate-900">
        {/* GRADIENTE PREMIUM */}
        <div className="hero-gradient min-h-screen">
          {/* HEADER PREMIUM */}
          <header className="border-b bg-white/70 backdrop-blur-md supports-[backdrop-filter]:bg-white/50">
            <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-4">
              {/* LOGO COM ÍCONE NOVO */}
              <div className="flex items-center gap-3">
                <div className="flex h-10 w-10 items-center justify-center rounded-full bg-gradient-to-br from-emerald-500 to-emerald-700 text-white text-lg font-bold shadow-md overflow-hidden">
                  <svg
                    viewBox="0 0 100 100"
                    className="w-6 h-6"
                    fill="none"
                    xmlns="http://www.w3.org/2000/svg"
                  >
                    {/* Nuvem com símbolo de pesquisa */}
                    <path
                      d="M50 20C35 20 25 30 25 45C25 55 32 63 42 65C42 75 48 85 50 85C52 85 58 75 58 65C68 63 75 55 75 45C75 30 65 20 50 20Z"
                      fill="white"
                    />
                    {/* Cruz de pesquisa/saúde */}
                    <path
                      d="M50 40V60M40 50H60"
                      stroke="currentColor"
                      strokeWidth="3"
                      strokeLinecap="round"
                    />
                  </svg>
                </div>

                <div className="flex flex-col leading-tight">
                  <span className="text-base font-semibold text-slate-900">
                    MedQuestResearch
                  </span>
                  <span className="text-xs text-slate-500">
                    Análise científica com IA — módulo premium
                  </span>
                </div>
              </div>

              {/* ÁREA DIREITA DO HEADER */}
              <div className="flex items-center gap-3">
                <button className="btn-outline hidden md:block">
                  Documentação
                </button>
                <button className="btn-primary">Entrar</button>
              </div>
            </div>
          </header>

          {/* CONTEÚDO PRINCIPAL */}
          <main className="mx-auto max-w-6xl px-4 py-10">{children}</main>
        </div>
      </body>
    </html>
  );
}