'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import Image from 'next/image';

interface Usuario {
  id?: string;
  nome?: string;
  email?: string;
}

interface SidebarProps {
  usuario: Usuario | null;
  creditos: number;
  onLogout: () => void;
  onRefreshCreditos?: () => void;
}

export default function Sidebar({
  usuario,
  creditos,
  onLogout,
  onRefreshCreditos,
}: SidebarProps) {
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) {
    return (
      <aside className="fixed left-0 top-0 h-screen w-64 bg-linear-to-br from-[#0c3d66] to-[#0ea5e9] text-white flex flex-col shadow-lg">
        <div className="p-6 border-b border-[#0369a1]/50 flex flex-col items-center gap-4">
          <div className="w-20 h-20 bg-white/10 rounded animate-pulse" />
          <div className="h-6 w-32 bg-white/10 rounded animate-pulse" />
        </div>
        <div className="p-6">
          <div className="h-4 w-24 bg-white/10 rounded mb-2 animate-pulse" />
          <div className="h-4 w-32 bg-white/10 rounded animate-pulse" />
        </div>
        <div className="p-6 border-t border-[#0369a1]/50">
          <div className="h-12 bg-white/10 rounded animate-pulse" />
        </div>
      </aside>
    );
  }

  return (
    <aside className="fixed left-0 top-0 h-screen w-64 bg-linear-to-br from-[#0c3d66] to-[#0ea5e9] text-white flex flex-col shadow-lg">
      {/* TOPO - Logo e Título */}
      <div className="p-6 border-b border-[#0369a1]/50 flex flex-col items-center gap-4">
        <Image
          src="/logo-medquestresearch.png"
          alt="MedQuestResearch"
          width={80}
          height={80}
          priority
          className="object-contain"
        />
        <span className="text-xl font-bold text-white">MedquestResearch</span>
      </div>

      {/* INFO USUÁRIO */}
      <div className="p-6">
        <div>
          <p className="text-blue-200 text-sm">Usuário</p>
          <p className="font-medium text-white truncate" title={usuario?.nome || usuario?.email}>
            {usuario?.nome || usuario?.email}
          </p>
        </div>
      </div>

      {/* CRÉDITOS */}
      <div className="px-6 pb-4">
        <div className="bg-[#0369a1]/30 rounded-lg p-4">
          <p className="text-blue-200 text-xs mb-1">Créditos disponíveis</p>
          <p className="font-bold text-2xl text-white">{creditos}</p>
        </div>
      </div>

      {/* LINKS: Comprar créditos, Atualizar dados */}
      <div className="flex-1 px-6 space-y-3">
        <Link
          href="/planos"
          className="block w-full text-center py-3 rounded-lg text-sm font-semibold text-[#0c3d66] bg-white hover:bg-slate-100 shadow-md transition-colors border border-white/30"
        >
          Comprar créditos
        </Link>
        <Link
          href="/perfil"
          className="block w-full text-center py-2.5 rounded-lg text-sm font-semibold text-white border border-white/40 bg-white/5 hover:bg-white/10 hover:border-white/70 transition-colors"
        >
          Atualizar dados
        </Link>
        {(usuario?.email || '').trim().toLowerCase() === 'prof.edesio@gmail.com' && (
          <Link
            href="/admin"
            className="block w-full text-center py-2 text-amber-200 hover:text-amber-100 text-sm font-medium transition-colors"
          >
            Admin (métricas)
          </Link>
        )}
      </div>

      {/* RODAPÉ - Logout */}
      <div className="p-6 border-t border-[#0369a1]/50">
        <button
          onClick={onLogout}
          className="w-full bg-[#0369a1] hover:bg-[#075985] transition-colors py-3 rounded-lg text-sm font-medium text-white shadow-md"
        >
          Sair
        </button>
      </div>
    </aside>
  );
}
