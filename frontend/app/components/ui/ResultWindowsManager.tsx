'use client';

import { useEffect, useState } from 'react';
import ResultWindow from './ResultWindow';
import { ResultWindowData } from './ResultWindow';

interface ResultWindowsManagerProps {
  windows: Map<string, ResultWindowData>;
  onUpdateWindow: (id: string, updates: Partial<ResultWindowData>) => void;
  onCloseWindow: (id: string) => void;
  token?: string;
}

export default function ResultWindowsManager({
  windows,
  onUpdateWindow,
  onCloseWindow,
  token,
}: ResultWindowsManagerProps) {
  // ✅ Garantir que só renderiza no cliente
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) {
    return null;
  }

  // ✅ CORREÇÃO: Não duplicar 'id' - data já contém id
  const windowsArray = Array.from(windows.entries()).map(([, data]) => data);

  if (windowsArray.length === 0) {
    return null;
  }

  return (
    <div className="fixed bottom-0 right-0 p-4 space-y-4 max-h-screen overflow-y-auto">
      {windowsArray.map((window) => (
        <ResultWindow
          key={window.id}
          window={window}
          onUpdate={(updates) => onUpdateWindow(window.id, updates)}
          onClose={() => onCloseWindow(window.id)}
          token={token}
        />
      ))}
    </div>
  );
}
