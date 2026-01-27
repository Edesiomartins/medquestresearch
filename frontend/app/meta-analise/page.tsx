'use client';

import dynamic from 'next/dynamic';

const MetaAnaliseClient = dynamic(() => import('./MetaAnaliseClient'), {
  ssr: false,
  loading: () => (
    <div className="flex items-center justify-center min-h-screen bg-mq-blue-900 text-white">
      <div className="animate-pulse-blue text-2xl">⏳ MedquestResearch carregando...</div>
    </div>
  ),
});

export default function Page() {
  return <MetaAnaliseClient />;
}
