'use client';

import { usePathname } from 'next/navigation';
import { useState, useEffect } from 'react';
import './globals.css';

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const [mounted, setMounted] = useState(false);
  const pathname = usePathname();

  // Garantir que o componente está montado no cliente
  useEffect(() => {
    setMounted(true);
  }, []);

  // Usa pathname do hook (apenas no cliente após montar)
  const currentPath = mounted ? (pathname || '') : '';
  const pathnameStr = String(currentPath).trim().toLowerCase();
  
  // Lista de rotas de autenticação
  const authRoutes = ['/login', '/register', '/esqueci-senha'];
  
  // Verifica se é rota de autenticação (exata ou sub-rota) - apenas após montar
  const isAuthRoute = mounted && authRoutes.some(route => 
    pathnameStr === route || pathnameStr.startsWith(route + '/')
  );

  // Durante SSR ou antes de montar, renderizar estrutura padrão
  // A lógica de rota será aplicada após montar no cliente
  return (
    <html lang="pt-BR">
      <body className="bg-slate-50 text-slate-800">
        {children}
      </body>
    </html>
  );
}
