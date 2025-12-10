'use client';

import { useState } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import './globals.css';

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const pathname = usePathname();

  const menuItems = [
    { label: 'Dashboard', href: '/', icon: '📊' },
    { label: 'Explicar', href: '/explicar', icon: '📚' },
    { label: 'Crítica', href: '/critica', icon: '🔍' },
    { label: 'Fatos', href: '/fatos', icon: '✓' },
    { label: 'Perspectiva', href: '/perspectiva', icon: '🌍' },
    { label: 'PDF', href: '/pdf', icon: '📄' },
  ];

  return (
    <html lang="pt-BR">
      <body className="bg-slate-50 text-slate-800">
        <div className="flex min-h-screen">
          {/* Sidebar */}
          <aside
            className={`fixed left-0 top-0 h-screen bg-gradient-blue text-white transition-all duration-300 z-50 ${
              sidebarOpen ? 'w-64' : 'w-20'
            } overflow-y-auto`}
          >
            {/* Logo */}
            <div className="flex items-center justify-between p-4 border-b border-blue-400">
              {sidebarOpen && (
                <h1 className="text-xl font-bold">MedQuest</h1>
              )}
              <button
                onClick={() => setSidebarOpen(!sidebarOpen)}
                className="p-2 hover:bg-blue-600 rounded-lg transition-colors"
                title={sidebarOpen ? 'Fechar' : 'Abrir'}
              >
                {sidebarOpen ? '◀' : '▶'}
              </button>
            </div>
            {/* Menu Items */}
            <nav className="p-4 space-y-2">
              {menuItems.map((item) => (
                <Link
                  key={item.href}
                  href={item.href}
                  className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-all duration-200 ${
                    pathname === item.href
                      ? 'bg-blue-500 shadow-lg'
                      : 'hover:bg-blue-600'
                  }`}
                  title={!sidebarOpen ? item.label : ''}
                >
                  <span className="text-xl shrink-0">{item.icon}</span>
                  {sidebarOpen && (
                    <span className="text-sm font-medium">{item.label}</span>
                  )}
                </Link>
              ))}
            </nav>
            {/* Footer Info */}
            {sidebarOpen && (
              <div className="absolute bottom-0 left-0 right-0 p-4 border-t border-blue-400 bg-blue-900/50">
                <p className="text-xs text-blue-100">
                  © 2024 MedQuest Research
                </p>
              </div>
            )}
          </aside>
          {/* Main Content */}
          <div
            className={`flex-1 flex flex-col transition-all duration-300 ${
              sidebarOpen ? 'ml-64' : 'ml-20'
            }`}
          >
            {/* Header */}
            <header className="sticky top-0 z-40 bg-white border-b border-blue-200 shadow-sm">
              <div className="flex items-center justify-between px-6 py-4">
                <h1 className="text-2xl font-bold text-gradient-blue">
                  MedQuest Research
                </h1>
                <div className="flex items-center gap-4">
                  <span className="text-sm text-slate-600">
                    👤 Usuário
                  </span>
                  <button className="btn btn-primary text-sm">
                    Logout
                  </button>
                </div>
              </div>
            </header>
            {/* Page Content */}
            <main className="flex-1 overflow-auto bg-slate-50 p-6">
              <div className="max-w-7xl mx-auto">
                {children}
              </div>
            </main>
            {/* Footer */}
            <footer className="bg-white border-t border-blue-200 px-6 py-4 text-center text-sm text-slate-600">
              <p>MedQuest Research © 2024 | Análise Científica com IA</p>
            </footer>
          </div>
        </div>
      </body>
    </html>
  );
}
