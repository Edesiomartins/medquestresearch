import './globals.css';
import FloatingHelpWidget from '@/app/components/ui/FloatingHelpWidget';

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="pt-BR">
      <body className="bg-slate-50 text-slate-800">
        {children}
        <FloatingHelpWidget />
      </body>
    </html>
  );
}
