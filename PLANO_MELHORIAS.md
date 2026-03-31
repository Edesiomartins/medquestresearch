# Plano de Melhorias — MedquestResearch

> **Para o Cursor:** Implemente as tarefas em ordem. Cada seção contém contexto, arquivos envolvidos, e o que exatamente deve ser feito. Não altere arquitetura estável sem necessidade. Prefira patches mínimos e verificáveis.

---

## Sumário de Prioridades

| # | Categoria | Impacto | Risco | Status |
|---|-----------|---------|-------|--------|
| 1 | Segurança: senha com bcrypt | Alto | Baixo | ⬜ |
| 2 | Estabilidade: jobs em threads | Alto | Médio | ⬜ |
| 3 | UX: feedback de erros no frontend | Médio | Baixo | ⬜ |
| 4 | Backend: créditos insuficientes (429 fix) | Alto | Baixo | ⬜ |
| 5 | Frontend: ResultPanel refinamento | Médio | Baixo | ⬜ |
| 6 | Meta-análise: nova etapa de escrita | Alto | Médio | ⬜ |
| 7 | Meta-análise: geração do artigo completo | Alto | Médio | ⬜ |
| 8 | Segurança: rate limiting persistente | Médio | Baixo | ⬜ |
| 9 | Migrations: schema versionado | Médio | Baixo | ⬜ |

---

## FASE 1 — Correções Críticas de Segurança e Estabilidade

### Tarefa 1.1 — Hash de senhas com bcrypt

**Problema:** Atualmente as senhas são armazenadas com SHA256 simples, sem salt. Isso é inseguro e vulnerável a ataques de dicionário e rainbow tables.

**Arquivo:** `backend/auth.py`

**O que fazer:**
1. Adicionar `bcrypt` ao `requirements.txt`
2. Substituir a função de hash atual por `bcrypt.hashpw(senha.encode(), bcrypt.gensalt())`
3. Substituir a verificação por `bcrypt.checkpw(senha.encode(), hash_armazenado)`
4. Criar migration de senhas: na primeira vez que o usuário logar com senha antiga (SHA256), re-hash com bcrypt e salvar

**Código de referência:**
```python
# requirements.txt — adicionar:
bcrypt==4.1.3

# backend/auth.py — substituir funções:
import bcrypt

def hash_senha(senha: str) -> str:
    return bcrypt.hashpw(senha.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

def verificar_senha(senha: str, hash_armazenado: str) -> bool:
    # Compatibilidade retroativa: detectar SHA256 antigo (hex de 64 chars)
    if len(hash_armazenado) == 64 and all(c in "0123456789abcdef" for c in hash_armazenado):
        import hashlib
        return hashlib.sha256(senha.encode()).hexdigest() == hash_armazenado
    return bcrypt.checkpw(senha.encode("utf-8"), hash_armazenado.encode("utf-8"))
```

**Após o login com hash antigo, re-hash no banco:**
```python
# Em backend/api.py, na rota POST /genapi/login, após verificar senha com sucesso:
if len(usuario["senha_hash"]) == 64:  # ainda é SHA256
    novo_hash = hash_senha(dados.senha)
    conn.execute("UPDATE usuarios SET senha_hash = %s WHERE id = %s", (novo_hash, usuario["id"]))
```

**Teste:** Login com usuário existente deve continuar funcionando. Novo hash deve ter ~60 chars (bcrypt).

---

### Tarefa 1.2 — Persistência de jobs em caso de restart

**Problema:** Jobs são executados em `threading.Thread(..., daemon=True)`. Se o servidor reiniciar (Railway reinicia ao deploy), todos os jobs em `status='processing'` ficam presos para sempre.

**Arquivo:** `backend/api.py`, `backend/research_jobs.py`

**O que fazer:**
1. Na inicialização da aplicação (evento `startup`), buscar todos os jobs com `status='processing'` mais antigos que 10 minutos e marcá-los como `failed` com mensagem explicativa
2. Adicionar campo `started_at` na tabela `research_jobs` para controle de timeout

**Código de referência:**
```python
# backend/api.py — adicionar evento de startup:
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Recuperar jobs travados do restart anterior
    conn = get_connection()
    try:
        conn.execute("""
            UPDATE research_jobs
            SET status = 'failed',
                resultado = 'Processamento interrompido por reinicialização do servidor. Tente novamente.'
            WHERE status = 'processing'
              AND criado_em < NOW() - INTERVAL '10 minutes'
        """)
        conn.commit()
    finally:
        conn.close()
    yield

app = FastAPI(lifespan=lifespan)
```

**Teste:** Criar um job, reiniciar o servidor, verificar se o job aparece como `failed` com a mensagem correta.

---

### Tarefa 1.3 — Correção do erro 429 / créditos insuficientes

**Problema:** O commit `fix 429` sugere que ainda há inconsistências no tratamento de créditos. Verificar o fluxo completo de débito.

**Arquivo:** `backend/services/credit_service.py`, `backend/api.py`

**O que fazer:**
1. Garantir que `HTTP 402` (não 429) é retornado quando créditos são insuficientes
2. O status 429 deve ser reservado para rate limit
3. Verificar se o frontend trata `402` e exibe mensagem "Créditos insuficientes — adquira mais créditos"
4. No frontend, ao receber `402`, exibir botão direto para `/planos`

**Frontend — `frontend/app/lib/api.ts`:**
```typescript
// Ao fazer requisição de análise, tratar 402 explicitamente:
if (response.status === 402) {
  return {
    error: true,
    message: 'Créditos insuficientes. Adquira mais créditos para continuar.',
    redirect: '/planos'
  };
}
```

**Frontend — `frontend/app/page.tsx`:**
```tsx
// Após receber erro de análise, verificar se é 402:
if (resultado?.redirect) {
  // Mostrar toast/alert com link para /planos
  setUploadError('Créditos insuficientes. Clique aqui para adquirir mais.');
}
```

---

## FASE 2 — Melhorias de UX e Frontend

### Tarefa 2.1 — Feedback de erros claro no ResultPanel

**Problema:** Erros de LLM, timeout e outros aparecem de forma genérica ou não aparecem. O usuário não sabe o que aconteceu.

**Arquivo:** `frontend/app/components/ui/ResultPanel.tsx`

**O que fazer:**
1. Quando `resultado` contém uma mensagem de erro (começa com "Erro", "❌", ou o job tem `status='failed'`), exibir em box vermelho com ícone
2. Exibir botão "Tentar novamente" que chama `onRunAnalysis`
3. Exibir timestamp do erro

**Código de referência:**
```tsx
// Detectar erro no resultado:
const isErro = resultado?.startsWith('Erro') || resultado?.startsWith('❌') || resultado?.includes('falhou');

// Renderizar box de erro:
{isErro && (
  <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-4">
    <p className="text-red-700 font-medium">⚠️ Falha no processamento</p>
    <p className="text-red-600 text-sm mt-1">{resultado}</p>
    {onRunAnalysis && (
      <button onClick={onRunAnalysis} className="mt-3 btn-secondary text-sm">
        Tentar novamente
      </button>
    )}
  </div>
)}
```

---

### Tarefa 2.2 — Indicador de progresso durante polling

**Problema:** O usuário vê apenas "processando" sem nenhuma indicação de quanto tempo leva ou em que etapa está.

**Arquivo:** `frontend/app/page.tsx`, `frontend/app/components/ui/ResultPanel.tsx`

**O que fazer:**
1. Ao iniciar um job, registrar o timestamp de início
2. Exibir contador de tempo decorrido enquanto `loading = true`
3. Exibir mensagem dinâmica por tipo de análise (ex: "Lendo artigo...", "Consultando modelos de IA...", "Gerando análise crítica...")

**Código de referência:**
```tsx
// No ResultPanel, enquanto loading:
const [elapsed, setElapsed] = useState(0);
useEffect(() => {
  if (!loading) { setElapsed(0); return; }
  const interval = setInterval(() => setElapsed(e => e + 1), 1000);
  return () => clearInterval(interval);
}, [loading]);

// Renderizar:
{loading && (
  <div className="flex flex-col items-center gap-3 py-8">
    <div className="animate-spin h-8 w-8 border-4 border-blue-500 border-t-transparent rounded-full" />
    <p className="text-slate-600">{titulo}</p>
    <p className="text-slate-400 text-sm">{elapsed}s decorridos</p>
  </div>
)}
```

---

### Tarefa 2.3 — Sidebar com histórico de jobs recentes

**Problema:** O usuário não tem acesso fácil aos jobs anteriores sem reprocessar tudo.

**Arquivo:** `frontend/app/components/ui/sidebar.tsx`, `frontend/app/lib/api.ts`

**O que fazer:**
1. Adicionar seção "Histórico Recente" na sidebar
2. Buscar `GET /genapi/jobs` ao montar a sidebar
3. Exibir os últimos 5 jobs com: tipo de análise, status (✅/❌/⏳), data
4. Ao clicar em um job, carregar o resultado no painel principal

**Endpoint já existe:** `GET /genapi/jobs` retorna lista de jobs do usuário.

---

## FASE 3 — Melhoria da Meta-Análise: Etapa de Escrita do Artigo

Esta é a principal feature nova. O objetivo é adicionar após as 4 etapas atuais de meta-análise uma **Etapa 5: Redação do Artigo Científico**, que usa todos os dados extraídos para gerar um artigo completo no formato IMRAD, seguindo as diretrizes PRISMA 2020.

### Visão Geral do Novo Fluxo

```
Upload PDFs (Etapa 0)
    ↓
Etapa 1: Estruturação PICO + Busca
    ↓
Etapa 2: Extração de Dados
    ↓
Etapa 3: Redação Técnica (PRISMA)
    ↓
Etapa 4: Verificação Final
    ↓
[NOVO] Etapa 5: Escrita do Artigo Científico
    ↓ (seções geradas individualmente)
    ├── Título + Resumo estruturado
    ├── Introdução (contexto, lacuna, objetivo)
    ├── Métodos (protocolo, critérios, extração)
    ├── Resultados (com dados estatísticos)
    ├── Discussão (interpretação, limitações)
    └── Referências + Tabelas/Figuras PRISMA
    ↓
[NOVO] Download como .txt ou .docx
```

---

### Tarefa 3.1 — Backend: nova rota para escrita do artigo

**Arquivo:** `backend/api.py`, `backend/meta_analysis.py`

**O que criar:**

**Rota nova:** `POST /genapi/meta_analysis/escrever_artigo`

```python
# Payload esperado:
{
  "project_id": "uuid-do-projeto",       # para buscar dados já processados
  "tema": "Eficácia de X em Y",
  "secao": "introducao" | "metodos" | "resultados" | "discussao" | "resumo" | "completo",
  "estilo_referencia": "Vancouver" | "ABNT" | "APA",
  "idioma": "pt" | "en",
  "instrucoes_adicionais": ""            # campo livre para o pesquisador personalizar
}
```

**Lógica:**
1. Buscar `analysis_json` e `dados_extras` do projeto no banco (`research_jobs` com `project_id` e `modulo='meta_analysis'`)
2. Buscar `evidence_graph` do projeto na tabela `evidence_graphs`
3. Construir contexto consolidado com todos os dados das etapas 1-4
4. Chamar LLM com prompt especializado por seção
5. Retornar resultado via sistema de jobs (polling)

**Custo de créditos:** 15 créditos para artigo completo, 5 por seção individual.

---

### Tarefa 3.2 — Backend: função de escrita em `meta_analysis.py`

**Arquivo:** `backend/meta_analysis.py`

**Adicionar função:**

```python
PROMPTS_SECAO = {
    "resumo": """
Você é um especialista em redação científica. Com base nos dados da meta-análise abaixo,
escreva um RESUMO ESTRUTURADO seguindo as diretrizes PRISMA 2020.

O resumo deve conter:
- Objetivo (1-2 frases)
- Critérios de elegibilidade
- Fontes de informação
- Método de síntese
- Resultados principais (com dados quantitativos)
- Limitações
- Conclusão
- Registro (se disponível)

Dados da meta-análise:
{contexto}

Escreva em {idioma}. Use linguagem científica formal. Máximo 350 palavras.
""",

    "introducao": """
Você é um especialista em redação de artigos de revisão sistemática.
Escreva a INTRODUÇÃO do artigo de meta-análise com base nos dados abaixo.

A introdução deve:
1. Contextualizar o problema clínico/científico (2-3 parágrafos)
2. Apresentar o que já se sabe e a lacuna do conhecimento
3. Justificar a necessidade da meta-análise
4. Declarar claramente o objetivo e a questão PICO

Dados disponíveis:
{contexto}

Escreva em {idioma}. Linguagem científica, sem bullet points, em prosa fluente.
""",

    "metodos": """
Você é um especialista em metodologia de revisões sistemáticas (Cochrane, PRISMA 2020).
Escreva a seção de MÉTODOS do artigo com base nos dados abaixo.

Inclua obrigatoriamente:
1. Protocolo e registro (se disponível)
2. Critérios de elegibilidade (inclusão e exclusão)
3. Fontes de informação e estratégia de busca
4. Processo de seleção de estudos
5. Extração de dados
6. Avaliação do risco de viés
7. Método de síntese estatística (modelo usado, heterogeneidade, I²)

Dados disponíveis:
{contexto}

Escreva em {idioma}. Linguagem científica, sem bullet points, em prosa fluente.
""",

    "resultados": """
Você é um especialista em bioestatística e revisões sistemáticas.
Escreva a seção de RESULTADOS do artigo com base nos dados abaixo.

Inclua obrigatoriamente:
1. Seleção dos estudos (fluxo PRISMA — quantos identificados, excluídos, incluídos)
2. Características dos estudos incluídos
3. Risco de viés dos estudos
4. Resultados das sínteses (com valores numéricos: RR, OR, SMD, IC 95%, I², p-valor)
5. Análises de sensibilidade (se disponíveis)

Dados disponíveis:
{contexto}

Escreva em {idioma}. Inclua os dados numéricos disponíveis. Linguagem científica.
""",

    "discussao": """
Você é um especialista em medicina baseada em evidências.
Escreva a seção de DISCUSSÃO do artigo com base nos dados abaixo.

Inclua obrigatoriamente:
1. Resumo dos principais achados
2. Comparação com literatura existente
3. Explicação para heterogeneidade (se presente)
4. Limitações do estudo (risco de viés, heterogeneidade, viés de publicação)
5. Implicações para prática clínica
6. Implicações para pesquisa futura
7. Conclusão final

Dados disponíveis:
{contexto}

Escreva em {idioma}. Linguagem científica, em prosa, sem bullet points.
""",
}

def montar_contexto_projeto(project_id: str, conn) -> str:
    """
    Busca todos os dados do projeto e monta um contexto consolidado para o LLM.
    """
    # Buscar todos os jobs do projeto
    rows = conn.execute("""
        SELECT modulo, resultado, dados_extras, analysis_json
        FROM research_jobs
        WHERE project_id = %s AND status = 'done'
        ORDER BY criado_em ASC
    """, (project_id,)).fetchall()

    partes = []
    for row in rows:
        if row["resultado"]:
            partes.append(f"=== {row['modulo'].upper()} ===\n{row['resultado'][:3000]}")

    # Buscar evidence graph
    graph_row = conn.execute("""
        SELECT graph_data FROM evidence_graphs WHERE project_id = %s
    """, (project_id,)).fetchone()

    if graph_row and graph_row["graph_data"]:
        import json
        graph = json.loads(graph_row["graph_data"]) if isinstance(graph_row["graph_data"], str) else graph_row["graph_data"]
        estudos = [n for n in graph.get("nodes", []) if n.get("type") == "Study"]
        if estudos:
            partes.append(f"=== ESTUDOS INCLUÍDOS ({len(estudos)}) ===")
            for e in estudos[:20]:  # Limitar para não exceder contexto
                partes.append(f"- {e.get('label', e.get('id', 'Estudo'))} | {e.get('year','')} | n={e.get('n','?')}")

    return "\n\n".join(partes)


async def escrever_secao_artigo(
    project_id: str,
    tema: str,
    secao: str,
    estilo_referencia: str = "Vancouver",
    idioma: str = "pt",
    instrucoes_adicionais: str = "",
    model: str = "nvidia/nemotron-nano-12b-v2-vl:free"
) -> str:
    """
    Gera uma seção do artigo científico usando os dados consolidados do projeto.
    """
    from database import get_connection

    conn = get_connection()
    try:
        contexto = montar_contexto_projeto(project_id, conn)
    finally:
        conn.close()

    if not contexto:
        return "Erro: Nenhum dado encontrado para o projeto. Execute as etapas 1-4 antes de gerar o artigo."

    idioma_texto = "português científico brasileiro" if idioma == "pt" else "scientific English"

    prompt_template = PROMPTS_SECAO.get(secao)
    if not prompt_template:
        return f"Seção '{secao}' não reconhecida."

    prompt = prompt_template.format(
        contexto=contexto[:6000],
        idioma=idioma_texto
    )

    if instrucoes_adicionais:
        prompt += f"\n\nInstruções adicionais do pesquisador: {instrucoes_adicionais}"

    prompt += f"\n\nEstilo de referência: {estilo_referencia}"

    resultado = await gerar_resposta(prompt, model=model, max_tokens=2000)
    return resultado
```

---

### Tarefa 3.3 — Backend: registrar rota na API

**Arquivo:** `backend/api.py`

**Adicionar após as rotas de meta-análise existentes:**

```python
class EscreverArtigoRequest(BaseModel):
    project_id: str
    tema: str
    secao: str = "completo"  # "resumo", "introducao", "metodos", "resultados", "discussao", "completo"
    estilo_referencia: str = "Vancouver"
    idioma: str = "pt"
    instrucoes_adicionais: str = ""

@app.post("/genapi/meta_analysis/escrever_artigo")
async def escrever_artigo_metanalise(
    dados: EscreverArtigoRequest,
    usuario=Depends(require_api_key)
):
    usuario_id = usuario["id"]

    # Verificar créditos
    custo = 15 if dados.secao == "completo" else 5
    creditos_disp = usuario["creditos"] - usuario["creditos_usados"]
    if creditos_disp < custo:
        raise HTTPException(status_code=402, detail=f"Créditos insuficientes. Necessário: {custo}, disponível: {creditos_disp}")

    # Verificar se o projeto pertence ao usuário
    conn = get_connection()
    try:
        projeto = conn.execute("""
            SELECT id FROM research_jobs
            WHERE project_id = %s AND usuario_id = %s
            LIMIT 1
        """, (dados.project_id, usuario_id)).fetchone()
        if not projeto:
            raise HTTPException(status_code=404, detail="Projeto não encontrado.")
    finally:
        conn.close()

    # Criar job
    entrada = {
        "project_id": dados.project_id,
        "tema": dados.tema,
        "secao": dados.secao,
        "estilo_referencia": dados.estilo_referencia,
        "idioma": dados.idioma,
        "instrucoes_adicionais": dados.instrucoes_adicionais,
    }
    job_id = criar_research_job(usuario_id, "escrever_artigo", entrada)
    debitar_creditos(usuario_id, "escrever_artigo", custo)

    # Executar em background thread
    def processar():
        if dados.secao == "completo":
            secoes = ["resumo", "introducao", "metodos", "resultados", "discussao"]
            partes = []
            for s in secoes:
                import asyncio
                loop = asyncio.new_event_loop()
                texto = loop.run_until_complete(
                    escrever_secao_artigo(
                        dados.project_id, dados.tema, s,
                        dados.estilo_referencia, dados.idioma, dados.instrucoes_adicionais
                    )
                )
                partes.append(f"## {s.upper()}\n\n{texto}")
            resultado = "\n\n---\n\n".join(partes)
        else:
            import asyncio
            loop = asyncio.new_event_loop()
            resultado = loop.run_until_complete(
                escrever_secao_artigo(
                    dados.project_id, dados.tema, dados.secao,
                    dados.estilo_referencia, dados.idioma, dados.instrucoes_adicionais
                )
            )
        atualizar_job(job_id, "done", resultado)

    threading.Thread(target=processar, daemon=True).start()

    return {"request_id": job_id, "status": "processing", "custo": custo}
```

**Adicionar custo em `backend/credit_costs.py`:**
```python
DEFAULT_COSTS = {
    ...
    "escrever_artigo": 5,       # por seção
    "escrever_artigo_completo": 15,  # artigo completo
}
```

---

### Tarefa 3.4 — Frontend: nova UI para Etapa 5 na página de meta-análise

**Arquivo:** `frontend/app/meta-analise/MetaAnaliseClient.tsx`

**O que adicionar:**

1. Após as 4 etapas existentes, exibir painel "Etapa 5: Escrever Artigo Científico"
2. O painel só aparece quando `etapa 4` está concluída e `project_id` está disponível
3. Controles disponíveis:
   - Seletor de seção: Resumo / Introdução / Métodos / Resultados / Discussão / **Artigo Completo**
   - Seletor de estilo de referência: Vancouver / ABNT / APA
   - Seletor de idioma: Português / English
   - Campo texto livre "Instruções adicionais" (opcional)
   - Botão "Gerar seção" / "Gerar artigo completo"
4. Resultado exibido em nova janela no `ResultWindowsManager`
5. Botão de download do texto (.txt) ao lado do resultado

**Código de referência para adicionar no componente:**

```tsx
// Estado adicional:
const [projectId, setProjectId] = useState<string | null>(null);
const [secaoArtigo, setSecaoArtigo] = useState('completo');
const [estiloRef, setEstiloRef] = useState('Vancouver');
const [idiomaArtigo, setIdiomaArtigo] = useState('pt');
const [instrucoes, setInstrucoes] = useState('');
const [etapa4Concluida, setEtapa4Concluida] = useState(false);

// Ao concluir etapa 4, salvar project_id e marcar conclusão:
// (dentro de executarEtapa, quando etapa === '4' e res.ok):
// setEtapa4Concluida(true);
// setProjectId(res.project_id); // o backend deve retornar project_id

// Painel da Etapa 5:
{etapa4Concluida && projectId && (
  <div className="card-elevated mt-6">
    <h3 className="text-xl font-bold text-[#0c3d66] mb-4">
      Etapa 5 — Escrever Artigo Científico
    </h3>
    <p className="text-sm text-slate-500 mb-4">
      Gera um artigo científico completo a partir de todos os dados extraídos nas etapas anteriores.
    </p>

    <div className="grid grid-cols-2 gap-4 mb-4">
      <div>
        <label className="label-sm">Seção</label>
        <select value={secaoArtigo} onChange={e => setSecaoArtigo(e.target.value)} className="input-select">
          <option value="completo">Artigo Completo</option>
          <option value="resumo">Resumo Estruturado</option>
          <option value="introducao">Introdução</option>
          <option value="metodos">Métodos</option>
          <option value="resultados">Resultados</option>
          <option value="discussao">Discussão</option>
        </select>
      </div>
      <div>
        <label className="label-sm">Estilo de Referência</label>
        <select value={estiloRef} onChange={e => setEstiloRef(e.target.value)} className="input-select">
          <option value="Vancouver">Vancouver</option>
          <option value="ABNT">ABNT</option>
          <option value="APA">APA</option>
        </select>
      </div>
      <div>
        <label className="label-sm">Idioma</label>
        <select value={idiomaArtigo} onChange={e => setIdiomaArtigo(e.target.value)} className="input-select">
          <option value="pt">Português</option>
          <option value="en">English</option>
        </select>
      </div>
    </div>

    <textarea
      placeholder="Instruções adicionais (opcional): ex: 'Incluir análise de custo-efetividade', 'Focar em pacientes pediátricos'..."
      value={instrucoes}
      onChange={e => setInstrucoes(e.target.value)}
      className="input-textarea w-full mb-4"
      rows={3}
    />

    <button
      onClick={() => executarEscritaArtigo()}
      disabled={executando}
      className="btn-primary w-full"
    >
      {secaoArtigo === 'completo' ? '✍️ Gerar Artigo Completo (15 créditos)' : `✍️ Gerar ${secaoArtigo} (5 créditos)`}
    </button>
  </div>
)}
```

**Função de chamada à API:**
```tsx
const executarEscritaArtigo = useCallback(async () => {
  if (!token || !projectId || !tema.trim()) return;
  setExecutando(true);

  const windowId = `artigo_${secaoArtigo}_${Date.now()}`;
  const titulo = secaoArtigo === 'completo' ? 'Artigo Científico Completo' : `Artigo — ${secaoArtigo}`;

  setResultWindows(prev => ({
    ...prev,
    [windowId]: {
      id: windowId,
      tipo: 'escrever_artigo',
      titulo,
      resultado: `⏳ Gerando ${titulo}...\n\nAguarde enquanto o artigo é redigido com base nos dados extraídos.`,
      loading: true,
      timestamp: Date.now(),
    }
  }));

  try {
    const res = await fetch(`${API_BASE}/genapi/meta_analysis/escrever_artigo`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
      body: JSON.stringify({
        project_id: projectId,
        tema,
        secao: secaoArtigo,
        estilo_referencia: estiloRef,
        idioma: idiomaArtigo,
        instrucoes_adicionais: instrucoes,
      }),
    });

    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || 'Erro ao iniciar escrita');

    // Polling do job
    const jobId = data.request_id;
    const poll = setInterval(async () => {
      const jobRes = await fetch(`${API_BASE}/genapi/job/${jobId}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      const job = await jobRes.json();
      if (job.status === 'done' || job.status === 'failed') {
        clearInterval(poll);
        setResultWindows(prev => ({
          ...prev,
          [windowId]: { ...prev[windowId], resultado: job.resultado, loading: false }
        }));
        setExecutando(false);
      }
    }, 5000);

  } catch (err: any) {
    setResultWindows(prev => ({
      ...prev,
      [windowId]: { ...prev[windowId], resultado: `❌ Erro: ${err.message}`, loading: false }
    }));
    setExecutando(false);
  }
}, [token, projectId, tema, secaoArtigo, estiloRef, idiomaArtigo, instrucoes]);
```

---

### Tarefa 3.5 — Frontend: botão de download do artigo

**Arquivo:** `frontend/app/components/ui/ResultWindow.tsx`

**O que fazer:**
Quando o tipo da janela for `escrever_artigo` e o resultado estiver disponível, exibir botão de download:

```tsx
// Em ResultWindow.tsx, junto aos botões de ação:
{tipo === 'escrever_artigo' && resultado && !loading && (
  <button
    onClick={() => {
      const blob = new Blob([resultado], { type: 'text/plain;charset=utf-8' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `artigo_metanalise_${Date.now()}.txt`;
      a.click();
      URL.revokeObjectURL(url);
    }}
    className="btn-secondary text-sm"
  >
    ⬇️ Baixar artigo (.txt)
  </button>
)}
```

---

### Tarefa 3.6 — Backend: garantir que `project_id` é retornado nas etapas

**Problema:** Para o frontend saber o `project_id` do projeto em andamento, as rotas de meta-análise precisam retornar esse campo consistentemente.

**Arquivo:** `backend/api.py`

**O que verificar e corrigir:**
1. Na rota `POST /genapi/meta_analysis/upload_articles`, garantir que a resposta inclui `project_id`
2. Na rota `POST /genapi/meta_analise`, garantir que cada etapa retorna o mesmo `project_id`
3. No frontend `MetaAnaliseClient.tsx`, capturar e salvar o `project_id` retornado

**Exemplo de resposta esperada:**
```json
{
  "request_id": "job-uuid-123",
  "project_id": "proj-uuid-456",
  "status": "processing",
  "etapa": 1
}
```

---

## FASE 4 — Melhorias Menores e Qualidade

### Tarefa 4.1 — Rate limiting persistente com Redis (opcional, futuro)

**Quando implementar:** Apenas se a escala do produto exigir. Por enquanto, é suficiente garantir que os erros 429 exibem mensagem amigável no frontend.

**O que fazer agora (baixo risco):**
- Verificar que `slowapi` retorna JSON bem formatado no erro 429
- Frontend: tratar erro 429 com mensagem "Muitas requisições. Aguarde alguns instantes."

---

### Tarefa 4.2 — Limpeza de cache LLM antigo

**Problema:** `backend/cache_llm.py` não tem TTL, pode crescer indefinidamente.

**Arquivo:** `backend/cache_llm.py`

**O que fazer:**
1. Adicionar campo `timestamp` ao cache
2. Na função de busca, ignorar entradas com mais de 7 dias
3. Adicionar função `limpar_cache_antigo()` chamada no startup

---

### Tarefa 4.3 — Variáveis de ambiente documentadas

**Arquivo:** `backend/.env.example`

**O que fazer:**
Garantir que `.env.example` tem todos os campos necessários documentados, incluindo os novos para a Etapa 5:

```
# Custo da nova etapa de escrita (opcional, padrão: 5 por seção, 15 completo)
CREDIT_COST_ESCREVER_ARTIGO=5
CREDIT_COST_ESCREVER_ARTIGO_COMPLETO=15
```

---

## Checklist Final de Testes

Após implementar todas as tarefas, validar:

- [ ] Login com usuário existente continua funcionando (compatibilidade bcrypt)
- [ ] Cadastro de novo usuário cria hash bcrypt
- [ ] Job em `processing` ao reiniciar servidor vira `failed` com mensagem clara
- [ ] Erro de créditos insuficientes retorna HTTP 402 (não 429)
- [ ] Frontend exibe mensagem de erro clara com link para `/planos` ao receber 402
- [ ] Etapas 1-4 da meta-análise continuam funcionando
- [ ] `project_id` é retornado em todas as respostas de meta-análise
- [ ] Etapa 5 aparece após conclusão da etapa 4
- [ ] Geração de seção individual (ex: só "Métodos") funciona
- [ ] Geração de artigo completo funciona
- [ ] Download do artigo como `.txt` funciona
- [ ] Custo de créditos é debitado corretamente (5 por seção, 15 completo)
- [ ] Indicador de tempo decorrido aparece durante processamento
- [ ] Botão "Tentar novamente" funciona após falha

---

## Observações para o Cursor

1. **Não altere** `backend/database.py`, `backend/auth.py` (exceto onde indicado), `backend/gpt_engine.py` e `backend/model_router.py` — são estáveis
2. **Preserve** todos os endpoints existentes — não renomeie rotas
3. **Ao adicionar imports** em `meta_analysis.py`, mantenha o padrão try/except de importação relativa/absoluta já existente
4. **Ao editar** `MetaAnaliseClient.tsx`, mantenha o padrão de `Record<string, ResultWindowData>` já usado para as janelas
5. **Teste localmente** com `uvicorn backend.api:app --reload` antes de comitar
6. **Não crie** arquivos de documentação extras — este plano é suficiente
