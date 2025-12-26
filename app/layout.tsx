'use client';

import { usePathname } from 'next/navigation';
import './globals.css';

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const pathname = usePathname();

  // Usa pathname do hook ou window.location como fallback (apenas no cliente)
  const currentPath = pathname || (typeof window !== 'undefined' ? window.location.pathname : '');
  const pathnameStr = String(currentPath).trim().toLowerCase();
  
  // Lista de rotas de autenticação
  const authRoutes = ['/login', '/register', '/esqueci-senha'];
  
  // Verifica se é rota de autenticação (exata ou sub-rota)
  const isAuthRoute = authRoutes.some(route => 
    pathnameStr === route || pathnameStr.startsWith(route + '/')
  );

  // 🔹 MODO AUTH: sem sidebar, sem header
  if (isAuthRoute) {
    return (
      <html lang="pt-BR">
        <body className="bg-slate-50 text-slate-800">
          {children}
        </body>
      </html>
    );
  }

  // 🔹 MODO DASHBOARD: a estrutura completa está no page.tsx
  return (
    <html lang="pt-BR">
      <body className="bg-slate-50 text-slate-800">
        {children}
      </body>
    </html>
  );
}
