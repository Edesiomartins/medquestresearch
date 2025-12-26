// app/components/ui/ToolCard.tsx
'use client';

interface ToolCardProps {
  title: string;
  description: string;
  icon: string;
  disabled?: boolean;
  active?: boolean;
  onClick: () => void;
}

export default function ToolCard({ title, description, icon, disabled = false, active = false, onClick }: ToolCardProps) {
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className={`
        card text-left w-full transition-all
        ${active ? 'border-2 border-[#2563eb] bg-[#eff6ff]' : ''}
        ${disabled 
          ? 'opacity-50 cursor-not-allowed' 
          : 'hover:shadow-lg hover:scale-105 cursor-pointer'
        }
      `}
    >
      <div className="flex items-start gap-4">
        <span className="text-3xl shrink-0">{icon}</span>
        <div className="flex-1">
          <h3 className="text-lg font-bold text-[#0c3d66] mb-1">{title}</h3>
          <p className="text-sm text-slate-600">{description}</p>
        </div>
      </div>
    </button>
  );
}