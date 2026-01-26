// app/components/ui/Sidebar.tsx
'use client';

import Image from 'next/image';
import Link from 'next/link';

interface Usuario {
  id?: string;
  nome?: string;
  email?: string;
}

interface SidebarProps {
  usuario: Usuario | null;
  creditos: number;
  onLogout: () => void;
}

export default function Sidebar({ usuario, creditos, onLogout }: SidebarProps) {
  return (
    <aside className="fixed left-0 top-0 h-screen w-64 bg-linear-to-br from-[#0c3d66] to-[#0ea5e9] text-white flex flex-col justify-between shadow-lg">
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
      <div className="p-6 space-y-4 grow">
        <div>
          <p className="text-blue-200 text-sm">Usuário</p>
          <p className="font-medium text-white">{usuario?.nome || usuario?.email}</p>
        </div>
        <div>
          <p className="text-blue-200 text-sm">Créditos</p>
          <p className="font-bold text-2xl text-white">{creditos}</p>
        </div>
        {/* Links de Navegação */}
        <nav className="mt-8 space-y-2">
          <Link href="/" className="flex items-center gap-3 p-2 rounded-lg hover:bg-[#0369a1] transition-colors text-white">
            <span className="text-xl">🏠</span>
            <span className="font-medium">Dashboard</span>
          </Link>
          <Link href="/meta-analise" className="flex items-center gap-3 p-2 rounded-lg hover:bg-[#0369a1] transition-colors text-white">
            <span className="text-xl">📑</span>
            <span className="font-medium">Meta-Análise PRISMA</span>
          </Link>
        </nav>
      </div>
      
      {/* LOGOUT */}
      <div className="p-6 border-t border-[#0369a1]/50">
        <button
          onClick={onLogout}
          className="w-full bg-[#0369a1] hover:bg-[#075985] transition-colors py-3 rounded-lg text-sm font-medium text-white shadow-md"
        >
          Logout
        </button>
      </div>
    </aside>
  );
}