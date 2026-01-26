'use client';

import { useState, useRef, useEffect } from 'react';

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: number;
}

interface ChatInterfaceProps {
  initialMessage?: string;
  tipoAnalise: string;
  textoArtigo?: string;
  token: string;
  onNewResponse?: (response: string) => void;
  disabled?: boolean;
}

export default function ChatInterface({
  initialMessage,
  tipoAnalise,
  textoArtigo,
  token,
  onNewResponse,
  disabled = false,
}: ChatInterfaceProps) {
  const [messages, setMessages] = useState<ChatMessage[]>(() => {
    if (initialMessage) {
      return [{
        id: 'initial',
        role: 'assistant' as const,
        content: initialMessage,
        timestamp: Date.now(),
      }];
    }
    return [];
  });
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  // Scroll para a última mensagem
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Adicionar mensagem inicial quando mudar
  useEffect(() => {
    if (initialMessage && messages.length === 0) {
      setMessages([{
        id: 'initial',
        role: 'assistant',
        content: initialMessage,
        timestamp: Date.now(),
      }]);
    }
  }, [initialMessage]);

  const sendMessage = async () => {
    if (!input.trim() || isLoading || disabled) return;

    const userMessage: ChatMessage = {
      id: `user-${Date.now()}`,
      role: 'user',
      content: input.trim(),
      timestamp: Date.now(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      // Importar função de API
      const { chatFollowUp } = await import('@/app/lib/api');
      
      // Chamar API para processar a mensagem de follow-up
      const response = await chatFollowUp(token, {
        tipo_analise: tipoAnalise,
        texto_artigo: textoArtigo || '',
        mensagem: userMessage.content,
        historico: messages.map(m => ({
          role: m.role,
          content: m.content,
        })),
      });

      if (response.erro) {
        throw new Error(response.erro);
      }

      const assistantMessage: ChatMessage = {
        id: `assistant-${Date.now()}`,
        role: 'assistant',
        content: response.resultado || response.resposta || 'Resposta recebida',
        timestamp: Date.now(),
      };

      setMessages(prev => [...prev, assistantMessage]);
      
      // Notificar componente pai sobre nova resposta
      if (onNewResponse) {
        onNewResponse(assistantMessage.content);
      }
    } catch (error: any) {
      const errorMessage: ChatMessage = {
        id: `error-${Date.now()}`,
        role: 'assistant',
        content: `❌ Erro ao processar mensagem: ${error.message || 'Erro desconhecido'}`,
        timestamp: Date.now(),
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
      inputRef.current?.focus();
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="flex flex-col h-full border-t border-slate-200">
      {/* Área de mensagens */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-slate-50">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-[80%] rounded-lg px-4 py-2 ${
                message.role === 'user'
                  ? 'bg-[#2563eb] text-white'
                  : 'bg-white border border-slate-200 text-slate-700'
              }`}
            >
              <div className="whitespace-pre-wrap text-sm leading-relaxed">
                {message.content}
              </div>
              <div
                className={`text-xs mt-1 ${
                  message.role === 'user' ? 'text-blue-100' : 'text-slate-400'
                }`}
              >
                {new Date(message.timestamp).toLocaleTimeString('pt-BR', {
                  hour: '2-digit',
                  minute: '2-digit',
                })}
              </div>
            </div>
          </div>
        ))}
        
        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-white border border-slate-200 rounded-lg px-4 py-2">
              <div className="flex items-center gap-2">
                <div className="animate-pulse">💭</div>
                <span className="text-sm text-slate-500">Processando...</span>
              </div>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      {/* Área de input */}
      <div className="p-4 border-t border-slate-200 bg-white">
        <div className="flex gap-2">
          <textarea
            ref={inputRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Digite sua mensagem... (Enter para enviar, Shift+Enter para nova linha)"
            className="flex-1 px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-[#2563eb] focus:border-[#2563eb] outline-none resize-none text-sm"
            rows={2}
            disabled={isLoading || disabled}
          />
          <button
            onClick={sendMessage}
            disabled={!input.trim() || isLoading || disabled}
            className="px-4 py-2 bg-[#2563eb] text-white rounded-lg hover:bg-[#1d4ed8] disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center justify-center"
            title="Enviar mensagem (Enter)"
          >
            {isLoading ? (
              <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
            ) : (
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
              </svg>
            )}
          </button>
        </div>
        <p className="text-xs text-slate-500 mt-2">
          💡 Você pode fazer perguntas ou pedir melhorias na análise
        </p>
      </div>
    </div>
  );
}
