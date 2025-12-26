export default function AuthLayout({ children }: { children: React.ReactNode }) {
  // Layout do grupo (auth) - apenas retorna children sem wrapper HTML/Body
  // O HTML/Body já está no layout raiz (app/layout.tsx)
  return <>{children}</>;
}
  