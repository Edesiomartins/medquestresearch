'use client';

import { useState } from 'react';

import { helpChat, HelpChatMessage } from '@/app/lib/api';

interface HelpAssistantProps {
  token: string;
}

export default function HelpAssistant({ token }: HelpAssistantProps) {
  const [messages, setMessages] = useState<HelpChatMessage[]>([
    {
      role: 'assistant',
      content:
        'Olá! Sou o assistente de ajuda do MedquestResearch. Posso explicar fluxos, warnings e como interpretar resultados.',
    },
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const send = async () => {
    const question = input.trim();
    if (!question || loading) return;
    setError(null);

    const nextMessages = [...messages, { role: 'user' as const, content: question }];
    setMessages(nextMessages);
    setInput('');
    setLoading(true);

    const response = await helpChat(token, question, nextMessages);
    if (response.erro || !response.data?.answer) {
      setError(response.erro || 'Falha ao obter resposta.');
      setLoading(false);
      return;
    }

    setMessages((prev) => [...prev, { role: 'assistant', content: response.data!.answer }]);
    setLoading(false);
  };

  return (
    <section className="rounded-xl border border-slate-200 bg-white p-5">
      <h3 className="mb-3 text-lg font-semibold text-slate-800">Chatbot de ajuda</h3>
      <p className="mb-3 text-xs text-slate-500">
        Motor OpenRouter free para dúvidas de uso e interpretação do sistema.
      </p>
      <div className="mb-3 h-72 space-y-2 overflow-y-auto rounded border border-slate-200 bg-slate-50 p-3">
        {messages.map((message, index) => (
          <div
            key={`${message.role}-${index}`}
            className={`rounded p-2 text-sm ${
              message.role === 'assistant' ? 'bg-white text-slate-700' : 'bg-blue-100 text-blue-900'
            }`}
          >
            <p className="mb-1 text-[11px] font-semibold uppercase">{message.role}</p>
            <p className="whitespace-pre-wrap">{message.content}</p>
          </div>
        ))}
        {loading && <p className="text-xs text-slate-500">Pensando...</p>}
      </div>
      {error && <p className="mb-2 text-xs text-red-600">{error}</p>}
      <div className="flex gap-2">
        <input
          value={input}
          onChange={(event) => setInput(event.target.value)}
          placeholder="Digite sua dúvida sobre o webapp..."
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
          className="rounded bg-blue-600 px-4 py-2 text-sm font-medium text-white disabled:opacity-50"
        >
          Enviar
        </button>
      </div>
    </section>
  );
}

