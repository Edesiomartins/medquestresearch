"use client";

import { useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import "./globals.css";

export default function RootLayout({ children }: { children: React.ReactNode }) {
  const [aberto, setAberto] = useState(false);
  const pathname = usePathname();

  const menu = [
    { name: "Visão Geral", href: "/dashboard", icon: "📊" },
    { name: "Meus Artigos", href: "/dashboard/artigos", icon: "📄" },
    { name: "Análises", href: "/dashboard/analises", icon: "🔬" },
    { name: "Configurações", href: "/dashboard/config", icon: "⚙️" },
  ];

  return (
    <html lang="pt-BR">
      <body>
        <div className="dashboard-container">
          <aside className={`sidebar ${aberto ? '' : 'closed'}`}>
            {/* Logo */}
            <div className={`sidebar-logo ${aberto ? '' : 'closed'}`}>
              <span>MedQuest Research</span>
            </div>

            {/* Menu */}
            <nav>
              {menu.map((item) => {
                const active = pathname === item.href;
                return (
                  <Link
                    key={item.href}
                    href={item.href}
                    className={`menu-item ${active ? 'active' : ''}`}
                  >
                    <span className="menu-icon">{item.icon}</span>
                    <span className="menu-text">{item.name}</span>
                  </Link>
                );
              })}
            </nav>

            {/* Botão Toggle */}
            <button
              className="toggle-btn"
              onClick={() => setAberto(!aberto)}
              aria-label="Toggle sidebar"
            >
              {aberto ? '◀' : '▶'}
            </button>
          </aside>

          <div style={{ marginLeft: aberto ? '250px' : '60px', transition: 'margin-left 0.3s ease', minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
            <header className="header">
              <div className="header-logo">MedQuest Research</div>
              <nav className="header-nav">
                {/* Adicione links de navegação aqui se necessário */}
              </nav>
            </header>

            <main className="main-content">
              {children}
            </main>
          </div>
        </div>
      </body>
    </html>
  );
}
