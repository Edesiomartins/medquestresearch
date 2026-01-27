# Erro de Hidratação React #310 - Módulo Metanálise

## Informações do Erro

**Erro:** `Uncaught Error: Minified React error #310`  
**Localização:** Módulo Metanálise (`/meta-analise`)  
**Tipo:** Erro de Hidratação (Hydration Mismatch)  
**Referência:** https://react.dev/errors/310

## Stack Trace Completo do Console

```
Uncaught Error: Minified React error #310; visit https://react.dev/errors/310 for the full message or use the non-minified dev environment for full errors and additional helpful warnings.
    NextJS 43
30ea11065999f7ac.js:1:64560
    NextJS 40
    AsyncFunctionNext self-hosted:780
    (assíncrono: async)
    I NextJS
    forEach self-hosted:145
    NextJS 2
```

## Versões das Dependências

### Next.js
- **Versão:** 16.1.0 (Turbopack)

### React
- **Versão:** 19.2.1
- **React DOM:** 19.2.1

### Outras Dependências Relevantes
- TypeScript
- Tailwind CSS

## Código do Componente Principal

### Arquivo: `frontend/app/meta-analise/page.tsx`

```typescript
'use client';

import { useState, useCallback, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/app/lib/hooks/useAuth';
import { metaAnalysis } from '@/app/lib/api';
import Sidebar from '@/app/components/ui/sidebar';
import ResultWindowsManager from '@/app/components/ui/ResultWindowsManager';
import { ResultWindowData } from '@/app/components/ui/ResultWindow';

export default function MetaAnalisePage() {
  const router = useRouter();
  const { token, usuario, creditos, loading, logout } = useAuth();
  const [tema, setTema] = useState('');
  const [etapaAtual, setEtapaAtual] = useState<string | null>(null);
  const [resultWindows, setResultWindows] = useState<Map<string, ResultWindowData>>(new Map);
  const [executando, setExecutando] = useState(false);
  const [mounted, setMounted] = useState(false);

  // Garantir que o componente está montado no cliente
  useEffect(() => {
    setMounted(true);
  }, []);

  // Redirecionar se não autenticado
  useEffect(() => {
    if (!loading && !token && mounted) {
      router.replace('/login');
    }
  }, [loading, token, router, mounted]);

  if (!mounted || loading || !token) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-mq-blue-900 text-white">
        <div className="animate-pulse-blue text-2xl">⏳ MedquestResearch carregando...</div>
      </div>
    );
  }

  const executarEtapa = useCallback(async (etapa: string, temaTexto: string, estilo: string = 'Vancouver') => {
    if (!token || !temaTexto.trim()) {
      return;
    }

    setExecutando(true);
    const windowId = `meta_analise_etapa_${etapa}_${Date.now()}`;
    
    const nomesEtapa: Record<string, string> = {
      '1': 'Etapa 1: Estruturação PICO e Busca na Literatura',
      '2': 'Etapa 2: Extração de Dados',
      '3': 'Etapa 3: Redação Técnica (PRISMA)',
      '4': 'Etapa 4: Verificação Final'
    };

    const novaJanela: ResultWindowData = {
      id: windowId,
      tipo: 'meta_analise',
      titulo: nomesEtapa[etapa] || `Etapa ${etapa}`,
      resultado: `⏳ Processando ${nomesEtapa[etapa]}...\n\nAguarde enquanto processamos sua metanálise.`,
      loading: true,
      timestamp: Date.now(),
    };

    setResultWindows(prev => new Map(prev).set(windowId, novaJanela));
    setEtapaAtual(etapa);

    try {
      const res = await metaAnalysis(token, {
        tema: temaTexto,
        etapa,
        texto_artigo: '',
        estilo,
      });

      if (res.erro) {
        setResultWindows(prev => {
          const next = new Map(prev);
          const janela = next.get(windowId);
          if (janela) {
            next.set(windowId, {
              ...janela,
              resultado: `❌ Erro: ${res.erro}`,
              loading: false,
            });
          }
          return next;
        });
      } else if (res.resultado) {
        setResultWindows(prev => {
          const next = new Map(prev);
          const janela = next.get(windowId);
          if (janela) {
            next.set(windowId, {
              ...janela,
              resultado: res.resultado || 'Etapa concluída',
              loading: false,
            });
          }
          return next;
        });
      }
    } catch (error: any) {
      setResultWindows(prev => {
        const next = new Map(prev);
        const janela = next.get(windowId);
        if (janela) {
          next.set(windowId, {
            ...janela,
            resultado: `❌ Erro: ${error.message || 'Erro desconhecido'}`,
            loading: false,
          });
        }
        return next;
      });
    } finally {
      setExecutando(false);
      setEtapaAtual(null);
    }
  }, [token]);

  const executarTodasEtapas = useCallback(async () => {
    if (!tema.trim() || !token) return;

    const estilo = 'Vancouver';
    
    for (let etapa = 1; etapa <= 4; etapa++) {
      await executarEtapa(etapa.toString(), tema, estilo);
      if (etapa < 4) {
        await new Promise(resolve => setTimeout(resolve, 2000));
      }
    }
  }, [tema, token, executarEtapa]);

  const handleUpdateWindow = useCallback((id: string, updates: Partial<ResultWindowData>) => {
    setResultWindows(prev => {
      const next = new Map(prev);
      const janela = next.get(id);
      if (janela) {
        next.set(id, { ...janela, ...updates });
      }
      return next;
    });
  }, []);

  const handleCloseWindow = useCallback((id: string) => {
    setResultWindows(prev => {
      const next = new Map(prev);
      next.delete(id);
      return next;
    });
  }, []);

  return (
    <div className="flex min-h-screen bg-mq-slate-50">
      <Sidebar 
        usuario={usuario} 
        creditos={creditos} 
        onLogout={logout}
        onModuleClick={undefined}
      />
      
      <div className="ml-64 flex-1 p-8">
        <div className="max-w-4xl mx-auto">
          <h1 className="text-3xl font-bold text-[#0c3d66] mb-2">
            Metanálise PRISMA
          </h1>
          <p className="text-slate-600 mb-8">
            Crie revisões sistemáticas e metanálises seguindo o protocolo PRISMA 2020.
            O sistema executará buscas na literatura (PubMed, LILACS, Cochrane) e guiará você através das etapas.
          </p>

          {/* Formulário de Tema */}
          <div className="card-elevated p-6 mb-8">
            <h2 className="text-xl font-bold text-[#0c3d66] mb-4">
              Iniciar Metanálise
            </h2>
            
            <div className="mb-4">
              <label htmlFor="tema" className="block text-sm font-medium text-slate-700 mb-2">
                Tema da Revisão Sistemática *
              </label>
              <textarea
                id="tema"
                value={tema}
                onChange={(e) => setTema(e.target.value)}
                placeholder="Ex: Eficácia da intervenção X em pacientes com condição Y"
                className="w-full px-4 py-3 border border-slate-300 rounded-lg focus:ring-2 focus:ring-[#2563eb] focus:border-[#2563eb] outline-none resize-none"
                rows={3}
                disabled={executando}
              />
              <p className="text-xs text-slate-500 mt-2">
                Descreva o tema da sua revisão sistemática. O sistema realizará buscas automáticas na literatura.
              </p>
            </div>

            <div className="flex gap-3">
              <button
                onClick={() => executarEtapa('1', tema)}
                disabled={!tema.trim() || executando}
                className="px-6 py-3 bg-[#2563eb] text-white rounded-lg hover:bg-[#1d4ed8] transition-colors font-medium disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {executando && etapaAtual === '1' ? 'Processando...' : 'Iniciar Etapa 1 (PICO + Busca)'}
              </button>
              
              <button
                onClick={executarTodasEtapas}
                disabled={!tema.trim() || executando}
                className="px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors font-medium disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {executando ? 'Executando Todas as Etapas...' : 'Executar Todas as Etapas'}
              </button>
            </div>
          </div>

          {/* Informações sobre as Etapas */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8">
            {/* Cards de informações das etapas */}
          </div>
        </div>
      </div>

      {/* Sistema de Janelas - apenas renderizar se houver janelas e componente estiver montado */}
      {mounted && resultWindows.size > 0 && (
        <ResultWindowsManager
          windows={resultWindows}
          onUpdateWindow={handleUpdateWindow}
          onCloseWindow={handleCloseWindow}
          token={token || undefined}
        />
      )}
    </div>
  );
}
```

## Componentes Relacionados

### 1. Sidebar (`frontend/app/components/ui/sidebar.tsx`)
- Usa `usePathname()` do Next.js
- Renderiza módulos de navegação
- Tem estado `mounted` para evitar problemas de hidratação

### 2. ResultWindowsManager (`frontend/app/components/ui/ResultWindowsManager.tsx`)
- Gerencia múltiplas janelas de resultado
- Usa `Map` e `Set` para estado
- Renderizado condicionalmente baseado em `mounted` e `resultWindows.size`

### 3. ResultWindow (`frontend/app/components/ui/ResultWindow.tsx`)
- Janela individual de resultado
- Usa `window.innerWidth` e `window.innerHeight` para posicionamento
- Tem estado `mounted` para evitar acesso a `window` durante SSR

## Possíveis Causas do Erro

1. **Diferença entre renderização no servidor e cliente:**
   - `usePathname()` pode retornar valores diferentes
   - `Date.now()` usado em `executarEtapa` pode causar diferenças
   - Acesso a `window` em componentes filhos

2. **Renderização condicional:**
   - `ResultWindowsManager` renderizado condicionalmente baseado em `mounted`
   - Sidebar renderiza módulos diferentes baseado em `mounted`

3. **Inicializadores de estado:**
   - `useState<Map>(new Map)` pode causar problemas
   - `useState<Set>(new Set)` pode causar problemas

## Correções Aplicadas

1. ✅ Adicionado estado `mounted` no componente principal
2. ✅ `ResultWindowsManager` só renderiza quando `mounted && resultWindows.size > 0`
3. ✅ Sidebar tem renderização de fallback quando não montado
4. ✅ `Sidebar` recebe `onModuleClick={undefined}` explicitamente
5. ✅ Componentes filhos (`ResultWindow`, `ResultWindowsManager`) têm proteção de hidratação

## Próximos Passos para Debug

1. **Executar em modo desenvolvimento:**
   ```bash
   npm run dev
   ```
   Isso mostrará o erro completo ao invés do erro minificado.

2. **Verificar console do navegador:**
   - Abrir DevTools (F12)
   - Verificar erros completos na aba Console
   - Verificar avisos de hidratação

3. **Verificar Network tab:**
   - Verificar se há requisições falhando
   - Verificar se há problemas de CORS

4. **Testar em modo produção:**
   ```bash
   npm run build
   npm run start
   ```

## Arquivos de Configuração Relevantes

- `frontend/next.config.js` ou `next.config.mjs`
- `frontend/tsconfig.json`
- `frontend/package.json`

## Ambiente

- **Plataforma:** Railway
- **URL de Produção:** https://medquestresearch.up.railway.app
- **URL da API:** https://medquestresearch-api.up.railway.app

## Notas Adicionais

- O erro ocorre especificamente no módulo de metanálise
- Outros módulos podem estar funcionando corretamente
- O erro pode estar relacionado à renderização do `Sidebar` ou `ResultWindowsManager`
- Verificar se há diferenças entre o HTML renderizado no servidor e no cliente
