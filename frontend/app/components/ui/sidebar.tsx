'use client';

import { useEffect, useState } from 'react';
import { usePathname, useRouter } from 'next/navigation';
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
  onModuleClick?: (tipo: string) => void;
}

export default function Sidebar({
  usuario,
  creditos,
  onLogout,
  onModuleClick,
}: SidebarProps) {
  // ✅ Garantir que só renderiza no cliente
  const [mounted, setMounted] = useState(false);
  const pathname = usePathname();
  const router = useRouter();

  useEffect(() => {
    setMounted(true);
  }, []);

  // Renderizar estrutura básica sempre, mas conteúdo dinâmico apenas quando montado
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
        <nav className="flex-1 px-3 pb-4">
          <div className="space-y-1">
            {[1, 2, 3, 4, 5, 6, 7].map((i) => (
              <div key={i} className="h-12 bg-white/10 rounded animate-pulse" />
            ))}
          </div>
        </nav>
        <div className="p-6 border-t border-[#0369a1]/50">
          <div className="h-12 bg-white/10 rounded animate-pulse" />
        </div>
      </aside>
    );
  }

  const modulos = [
    { href: '/', icon: '🗺️', label: 'Visualizar estrutura', tipo: 'structure_visualizer' },
    { href: '/', icon: '🧠', label: 'Mapear estrutura', tipo: 'structure_mapper' },
    { href: '/', icon: '✓', label: 'Verificar fatos', tipo: 'fatos' },
    { href: '/', icon: '📚', label: 'Explicar conteúdo', tipo: 'explicar' },
    { href: '/', icon: '🔬', label: 'Análise crítica', tipo: 'critica' },
    { href: '/', icon: '📑', label: 'Metanálise PRISMA', tipo: 'meta-analise' },
  ];

  // Determinar módulo ativo baseado na rota (apenas no cliente)
  const isModuloAtivo = (modulo: typeof modulos[0]) => {
    return pathname === '/';
  };

  // Handler para clicar em módulo
  const handleModuleClick = (modulo: typeof modulos[0], e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    
    if (!onModuleClick) {
      if (pathname !== '/') {
        router.push('/');
      }
      return;
    }
    
    if (pathname !== '/') {
      router.push('/');
      setTimeout(() => {
        onModuleClick(modulo.tipo);
      }, 300);
    } else {
      onModuleClick(modulo.tipo);
    }
  };

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
          <p className="font-medium text-white">{usuario?.nome || usuario?.email}</p>
        </div>
      </div>
      
      {/* NAVEGAÇÃO - MÓDULOS */}
      <nav className="flex-1 overflow-y-auto px-3 pb-4">
        <div className="space-y-1">
          {modulos.map((modulo) => {
            const isActive = isModuloAtivo(modulo);
            return (
              <button
                key={modulo.tipo}
                onClick={(e) => handleModuleClick(modulo, e)}
                className={`w-full flex items-center gap-3 p-3 rounded-lg transition-colors text-left ${
                  isActive 
                    ? 'bg-[#0369a1] text-white shadow-md' 
                    : 'hover:bg-[#0369a1]/50 text-white'
                }`}
              >
                <span className="text-xl">{modulo.icon}</span>
                <span className="font-medium text-sm">{modulo.label}</span>
              </button>
            );
          })}
        </div>
      </nav>
      
      {/* RODAPÉ - Créditos, Planos e Logout */}
      <div className="p-6 border-t border-[#0369a1]/50 space-y-4">
        {/* Créditos */}
        <div className="bg-[#0369a1]/30 rounded-lg p-4">
          <p className="text-blue-200 text-xs mb-1">Créditos Disponíveis</p>
          <p className="font-bold text-2xl text-white">{creditos}</p>
        </div>
        <Link
          href="/planos"
          className="block w-full text-center py-3 rounded-lg text-sm font-semibold text-[#0c3d66] bg-white hover:bg-slate-100 shadow-md transition-colors border border-white/30"
        >
          Comprar créditos
        </Link>
        <Link
          href="/perfil"
          className="block w-full text-center py-2 text-blue-200 hover:text-white text-sm font-medium transition-colors"
        >
          Atualizar cadastro
        </Link>
        {(usuario?.email || '').trim().toLowerCase() === 'prof.edesio@gmail.com' && (
          <Link
            href="/admin"
            className="block w-full text-center py-2 text-amber-200 hover:text-amber-100 text-sm font-medium transition-colors"
          >
            Admin (métricas)
          </Link>
        )}
        {/* Logout */}
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
