'use client';

interface AnalysisCardProps {
  title: string;
  onClick: () => void;
}

export default function AnalysisCard({ title, onClick }: AnalysisCardProps) {
  return (
    <button
      onClick={onClick}
      className="card hover:shadow-lg text-left w-full transition-all hover:scale-105"
    >
      <h3 className="text-lg font-bold text-blue-900 mb-2">{title}</h3>
      <p className="text-slate-600 text-sm">Clique para executar</p>
    </button>
  );
}

