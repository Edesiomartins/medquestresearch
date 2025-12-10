"use client";

import { useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
// import "./dashboard.css"; // arquivo opcional para ajustes extras - descomente se criar o arquivo

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const [open, setOpen] = useState(false);
  const pathname = usePathname();

  const menu = [
    { name: "Visão Geral", href: "/dashboard", icon: "📊" },
    { name: "Meus Artigos", href: "/dashboard/artigos", icon: "📄" },
    { name: "Análises", href: "/dashboard/analises", icon: "🔬" },
    { name: "Configurações", href: "/dashboard/config", icon: "⚙️" },
  ];

  return (
    <div className="flex min-h-screen bg-[var(--color-background)] text-[var(--color-text)]">

      {/* ===== SIDEBAR — Desktop ===== */}
      <aside className="
        hidden md:flex 
        w-64 flex-col 
        backdrop-blur-xl 
        bg-[rgba(0,56,99,0.55)]
        border-r border-[rgba(255,255,255,0.1)]
        text-white
        shadow-xl
      ">
        {/* Logo */}
        <div className="p-6 flex items-center gap-3 border-b border-[rgba(255,255,255,0.1)]">
          <div className="h-12 w-12 rounded-xl flex items-center justify-center bg-[var(--color-primary)] shadow-lg">
            <span className="text-white font-bold text-xl">MQ</span>
          </div>
          <div className="flex flex-col leading-tight">
            <span className="font-bold text-lg">MedQuest</span>
            <span className="text-[var(--color-accent)] text-sm font-semibold">Research</span>
          </div>
        </div>

        {/* Menu */}
        <nav className="flex-1 p-4 space-y-2">
          {menu.map((item) => {
            const active = pathname === item.href;
            return (
              <Link
                key={item.href}
                href={item.href}
                className={`
                  flex items-center gap-3 px-4 py-3 rounded-lg transition-all
                  ${active ? "bg-[rgba(255,255,255,0.15)] text-[var(--color-accent)] font-semibold" : "text-white/80 hover:bg-[rgba(255,255,255,0.1)] hover:text-white"}
                `}
              >
                <span className="text-xl">{item.icon}</span>
                {item.name}
              </Link>
            );
          })}
        </nav>

        {/* User */}
        <div className="p-4 border-t border-[rgba(255,255,255,0.1)]">
          <div className="flex items-center gap-3 p-3 rounded-lg hover:bg-[rgba(255,255,255,0.1)] cursor-pointer transition">
            <div className="w-10 h-10 rounded-full bg-[var(--color-accent)] flex items-center justify-center text-white font-bold">
              ED
            </div>
            <div>
              <p className="text-sm font-semibold">Dr. Edesio</p>
              <p className="text-xs opacity-80">Pesquisador</p>
            </div>
          </div>
        </div>
      </aside>

      {/* ===== SIDEBAR — Mobile ===== */}
      {open && (
        <div
          className="
            fixed inset-0 z-40 flex md:hidden 
            backdrop-blur-xl bg-[rgba(0,0,0,0.4)]
          "
          onClick={() => setOpen(false)}
        >
          <aside
            className="
              w-64 h-full bg-[rgba(0,56,99,0.55)] backdrop-blur-2xl text-white p-6 shadow-xl
            "
            onClick={(e) => e.stopPropagation()}
          >
            <div className="mb-8">
              <h2 className="text-xl font-semibold">Menu</h2>
            </div>

            <nav className="space-y-4">
              {menu.map((item) => (
                <Link
                  key={item.href}
                  href={item.href}
                  className="block text-white/90 hover:text-white font-medium"
                  onClick={() => setOpen(false)}
                >
                  {item.icon} {item.name}
                </Link>
              ))}
            </nav>
          </aside>
        </div>
      )}

      {/* ===== MAIN AREA ===== */}
      <div className="flex-1 flex flex-col">

        {/* TOPBAR */}
        <header
          className="
            h-16 flex items-center justify-between px-6
            backdrop-blur-xl bg-[rgba(255,255,255,0.6)]
            border-b border-[var(--color-border)]
            shadow-sm sticky top-0 z-20
          "
        >
          {/* Mobile toggle */}
          <button
            className="md:hidden p-2 text-[var(--color-primary)]"
            onClick={() => setOpen(true)}
          >
            ☰
          </button>

          <h1 className="text-xl font-bold text-[var(--color-primary)]">Dashboard</h1>

          <button className="hidden md:flex px-4 py-2 rounded-lg bg-[var(--color-primary)] text-white font-semibold shadow hover:bg-[var(--color-primary-hover)] transition">
            + Novo Artigo
          </button>
        </header>

        {/* CONTENT */}
        <main className="flex-1 p-8 overflow-y-auto">
          {children}
        </main>
      </div>
    </div>
  );
}
