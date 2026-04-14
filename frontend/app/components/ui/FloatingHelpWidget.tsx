'use client';

import { useEffect, useMemo, useState } from 'react';
import { usePathname } from 'next/navigation';

import { clearHelpChatHistory, getHelpChatHistory, helpChat, HelpChatMessage } from '@/app/lib/api';

export default function FloatingHelpWidget() {
  const pathname = usePathname();
  const hiddenRoutes = useMemo(() => ['/login', '/register', '/recuperar'], []);
  const shouldHide = hiddenRoutes.some((route) => pathname?.startsWith(route));

  const [open, setOpen] = useState(false);
  const [token, setToken] = useState<string | null>(null);
  const [messages, setMessages] = useState<HelpChatMessage[]>([
    {
      role: 'assistant',
      content:
        'Olá! Sou o assistente do MedquestResearch. Posso te ajudar com metanálise, warnings, siglas e exportações.',
    },
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (typeof window === 'undefined') return;
    const localToken = localStorage.getItem('token');
    setToken(localToken);
  }, []);

  useEffect(() => {
    if (!open || !token) return;
    (async () => {
      const history = await getHelpChatHistory(token, 80);
      if (history.data?.messages && history.data.messages.length > 0) {
        setMessages(history.data.messages);
      }
    })();
  }, [open, token]);

  const send = async () => {
    const message = input.trim();
    if (!message || !token || loading) return;
    setError(null);

    const optimistic = [...messages, { role: 'user' as const, content: message }];
    setMessages(optimistic);
    setInput('');
    setLoading(true);

    const response = await helpChat(token, message, optimistic);
    if (response.erro || !response.data?.answer) {
      setError(response.erro || 'Falha ao obter resposta do assistente.');
      setLoading(false);
      return;
    }

    setMessages((prev) => [...prev, { role: 'assistant', content: response.data!.answer }]);
    setLoading(false);
  };

  const clear = async () => {
    if (!token) return;
    setLoading(true);
    setError(null);
    const response = await clearHelpChatHistory(token);
    if (response.erro) {
      setError(response.erro);
      setLoading(false);
      return;
    }
    setMessages([
      {
        role: 'assistant',
        content: 'Histórico limpo. Como posso ajudar agora?',
      },
    ]);
    setLoading(false);
  };

  if (shouldHide || !token) return null;

  return (
    <>
      {open && (
        <div className="fixed inset-0 z-100 bg-black/25" onClick={() => setOpen(false)}>
          <div
            className="absolute bottom-24 right-6 w-[360px] max-w-[calc(100vw-2rem)] rounded-2xl border border-slate-200 bg-white shadow-2xl"
            onClick={(event) => event.stopPropagation()}
          >
            <div className="flex items-center justify-between rounded-t-2xl bg-blue-600 px-4 py-3 text-white">
              <p className="text-sm font-semibold">Assistente de Ajuda</p>
              <button type="button" onClick={() => setOpen(false)} className="text-xs font-medium text-blue-100 hover:text-white">
                Fechar
              </button>
            </div>
            <div className="h-80 space-y-2 overflow-y-auto bg-slate-50 p-3">
              {messages.map((message, index) => (
                <div
                  key={`${message.role}-${index}`}
                  className={`rounded-lg p-2 text-sm ${
                    message.role === 'assistant' ? 'bg-white text-slate-700' : 'bg-blue-100 text-blue-900'
                  }`}
                >
                  <p className="mb-1 text-[10px] font-semibold uppercase">{message.role}</p>
                  <p className="whitespace-pre-wrap">{message.content}</p>
                </div>
              ))}
              {loading && <p className="text-xs text-slate-500">Assistente está respondendo...</p>}
              {error && <p className="text-xs text-red-600">{error}</p>}
            </div>
            <div className="space-y-2 border-t border-slate-200 p-3">
              <div className="flex gap-2">
                <input
                  value={input}
                  onChange={(event) => setInput(event.target.value)}
                  placeholder="Digite sua dúvida..."
                  className="flex-1 rounded border border-slate-300 px-3 py-2 text-sm"
                  onKeyDown={(event) => {
                    if (event.key === 'Enter') {
                      event.preventDefault();
                      send();
                    }
                  }}
                />
                <button
                  type="button"
                  onClick={send}
                  disabled={loading || !input.trim()}
                  className="rounded bg-blue-600 px-3 py-2 text-sm font-medium text-white disabled:opacity-50"
                >
                  Enviar
                </button>
              </div>
              <button
                type="button"
                onClick={clear}
                disabled={loading}
                className="w-full rounded bg-slate-200 px-3 py-2 text-xs font-medium text-slate-700 disabled:opacity-50"
              >
                Limpar histórico
              </button>
            </div>
          </div>
        </div>
      )}

      <button
        type="button"
        onClick={() => setOpen((prev) => !prev)}
        className="fixed bottom-6 right-6 z-110 h-14 w-14 rounded-full bg-blue-600 text-white shadow-xl transition hover:bg-blue-700"
        aria-label="Abrir chat de ajuda"
      >
        <span className="text-2xl">💬</span>
      </button>
    </>
  );
}

