// app/components/ui/ResultWindowsManager.tsx
'use client';

import { useState, useCallback } from 'react';
import ResultWindow, { ResultWindowData } from './ResultWindow';

interface ResultWindowsManagerProps {
  windows: Map<string, ResultWindowData>;
  onUpdateWindow: (id: string, updates: Partial<ResultWindowData>) => void;
  onCloseWindow: (id: string) => void;
}

export default function ResultWindowsManager({
  windows,
  onUpdateWindow,
  onCloseWindow,
}: ResultWindowsManagerProps) {
  const [activeWindowId, setActiveWindowId] = useState<string | null>(null);
  const [minimizedWindows, setMinimizedWindows] = useState<Set<string>>(() => new Set());
  const [windowZIndices, setWindowZIndices] = useState<Map<string, number>>(() => new Map());

  // Calcular z-index baseado na ordem de criação e janela ativa
  const getZIndex = useCallback((windowId: string) => {
    if (!windowZIndices.has(windowId)) {
      // Primeira vez: atribuir z-index baseado na ordem
      const baseZIndex = 1000 + Array.from(windows.keys()).indexOf(windowId);
      setWindowZIndices(prev => new Map(prev).set(windowId, baseZIndex));
      return baseZIndex;
    }
    return windowZIndices.get(windowId) || 1000;
  }, [windows, windowZIndices]);

  const handleActivate = useCallback((windowId: string) => {
    setActiveWindowId(windowId);
    // Trazer para frente: aumentar z-index
    const currentZIndex = getZIndex(windowId);
    const maxZIndex = Math.max(...Array.from(windowZIndices.values()), 1000);
    const newZIndex = maxZIndex + 1;
    setWindowZIndices(prev => new Map(prev).set(windowId, newZIndex));
  }, [getZIndex, windowZIndices]);

  const handleMinimize = useCallback((windowId: string) => {
    setMinimizedWindows(prev => new Set(prev).add(windowId));
  }, []);

  const handleMaximize = useCallback((windowId: string) => {
    setMinimizedWindows(prev => {
      const next = new Set(prev);
      next.delete(windowId);
      return next;
    });
    handleActivate(windowId);
  }, [handleActivate]);

  const handleClose = useCallback((windowId: string) => {
    onCloseWindow(windowId);
    setMinimizedWindows(prev => {
      const next = new Set(prev);
      next.delete(windowId);
      return next;
    });
    setWindowZIndices(prev => {
      const next = new Map(prev);
      next.delete(windowId);
      return next;
    });
    if (activeWindowId === windowId) {
      setActiveWindowId(null);
    }
  }, [onCloseWindow, activeWindowId]);

  // Ordenar janelas por z-index (maior primeiro = no topo)
  const sortedWindows = Array.from(windows.entries()).sort((a, b) => {
    const zA = getZIndex(a[0]);
    const zB = getZIndex(b[0]);
    return zB - zA;
  });

  return (
    <>
      {sortedWindows.map(([windowId, windowData], index) => (
        <ResultWindow
          key={windowId}
          window={windowData}
          zIndex={getZIndex(windowId)}
          isActive={activeWindowId === windowId}
          onActivate={() => handleActivate(windowId)}
          onClose={() => handleClose(windowId)}
          onMinimize={() => handleMinimize(windowId)}
          onMaximize={() => handleMaximize(windowId)}
          isMinimized={minimizedWindows.has(windowId)}
          windowIndex={index}
        />
      ))}
    </>
  );
}

