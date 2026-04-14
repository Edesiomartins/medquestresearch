'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import Image from 'next/image';
import { listarJobs, obterJob, JobItem } from '@/app/lib/api';

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
  token?: string;
  onJobSelect?: (job: { id: number; modulo: string; status: string; resultado?: string; project_id?: number }) => void;
}

export default function Sidebar({
  usuario,
  creditos,
  onLogout,
  onRefreshCreditos,
  token,
  onJobSelect,
}: SidebarProps) {
  const [mounted, setMounted] = useState(false);
  const [jobsRecentes, setJobsRecentes] = useState<JobItem[]>([]);
  const [loadingJobs, setLoadingJobs] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  useEffect(() => {
    const carregarJobs = async () => {
      if (!token) return;
      setLoadingJobs(true);
      const res = await listarJobs(token);
      if (res.data?.jobs) {
        setJobsRecentes(res.data.jobs.slice(0, 5));
      } else {
        setJobsRecentes([]);
      }
      setLoadingJobs(false);
    };
    carregarJobs();
  }, [token, creditos]);

  const handleAbrirJob = async (job: JobItem) => {
    if (!token || !onJobSelect) return;
    const detalhe = await obterJob(token, job.id);
    onJobSelect({
      id: job.id,
      modulo: job.modulo,
      status: (detalhe.status as string) || job.status,
      resultado: detalhe.resultado || detalhe.erro || '',
      project_id: detalhe.project_id,
    });
  };

  const statusIcon = (status: string) => {
    if (status === 'done') return '✅';
    if (status === 'failed' || status === 'error') return '❌';
    return '⏳';
  };

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
      <div className="px-6 space-y-3">
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
        <Link
          href="/manual"
          className="block w-full text-center py-2.5 rounded-lg text-sm font-semibold text-white border border-white/40 bg-white/5 hover:bg-white/10 hover:border-white/70 transition-colors"
        >
          Manual e ajuda
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

      <div className="px-6 py-4">
        <p className="text-blue-200 text-xs mb-2">Histórico recente</p>
        <div className="space-y-2">
          {loadingJobs && <p className="text-[11px] text-blue-100/80">Carregando...</p>}
          {!loadingJobs && jobsRecentes.length === 0 && (
            <p className="text-[11px] text-blue-100/80">Sem jobs recentes.</p>
          )}
          {!loadingJobs &&
            jobsRecentes.map((job) => (
              <button
                key={job.id}
                type="button"
                onClick={() => handleAbrirJob(job)}
                className="w-full text-left px-2 py-2 rounded bg-white/10 hover:bg-white/20 transition-colors"
              >
                <p className="text-[11px] text-white truncate">
                  {statusIcon(job.status)} {job.modulo.split('_').join(' ')}
                </p>
                <p className="text-[10px] text-blue-100/80">
                  #{job.id} {job.created_at ? `• ${new Date(job.created_at).toLocaleDateString('pt-BR')}` : ''}
                </p>
              </button>
            ))}
        </div>
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
