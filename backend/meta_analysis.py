# Tentar importação relativa primeiro, depois absoluta
import logging

try:
    from .gpt_engine import gerar_resposta
    from .chunker import estimate_tokens
    from .meta_stats import (
        Effect,
        effect_smd_hedges_g,
        effect_log_rr,
        effect_log_or,
        pool_effects,
        forest_plot_png,
    )
    from .services.evidence_graph_service import (
        carregar_evidence_graph_por_projeto,
        studies_for_outcome,
    )
    from .database import get_connection
    from .meta_detector import detectar_metaanalises_possiveis
except ImportError:
    try:
        from gpt_engine import gerar_resposta
        from chunker import estimate_tokens
        from meta_stats import (
            Effect,
            effect_smd_hedges_g,
            effect_log_rr,
            effect_log_or,
            pool_effects,
            forest_plot_png,
        )
        from services.evidence_graph_service import (
            carregar_evidence_graph_por_projeto,
            studies_for_outcome,
        )
        from database import get_connection
        from meta_detector import detectar_metaanalises_possiveis
    except ImportError:
        import backend.gpt_engine as gpt_engine
        import backend.chunker as chunker
        from backend.meta_stats import (  # type: ignore[reportMissingImports]
            Effect,
            effect_smd_hedges_g,
            effect_log_rr,
            effect_log_or,
            pool_effects,
            forest_plot_png,
        )
        import backend.services.evidence_graph_service as eg_service  # type: ignore[reportMissingImports]
        from backend.database import get_connection  # type: ignore[reportMissingImports]
        import backend.meta_detector as meta_detector  # type: ignore[reportMissingImports]

        gerar_resposta = gpt_engine.gerar_resposta
        detectar_metaanalises_possiveis = meta_detector.detectar_metaanalises_possiveis
        estimate_tokens = chunker.estimate_tokens
        carregar_evidence_graph_por_projeto = eg_service.carregar_evidence_graph_por_projeto
        studies_for_outcome = eg_service.studies_for_outcome

def _executar_metaanalises_dos_candidatos(graph: dict, model: str = "random_DL") -> list:
    """
    Para cada candidato retornado por detectar_metaanalises_possiveis, monta efeitos,
    chama pool_effects e opcionalmente forest_plot. Retorna lista de dicts por outcome.
    """
    candidatos = detectar_metaanalises_possiveis(graph)
    if not candidatos:
        return []
    studies = {n["id"]: n for n in (graph.get("nodes") or []) if n.get("type") == "Study"}
    resultados = []
    for idx, cand in enumerate(candidatos):
        items = cand.get("items", [])
        if len(items) < 2:
            continue
        efeitos = []
        try:
            for item in items:
                study_id = item.get("study_id", "")
                data = item.get("data", {})
                label = (studies.get(study_id) or {}).get("label", study_id)
                if cand["tipo"] == "continuous":
                    ef = effect_smd_hedges_g(
                        study_id,
                        label,
                        int(data.get("n_t", 0)),
                        float(data.get("mean_t", 0)),
                        float(data.get("sd_t", 0)),
                        int(data.get("n_c", 0)),
                        float(data.get("mean_c", 0)),
                        float(data.get("sd_c", 0)),
                    )
                else:
                    e_t = data.get("events_t", data.get("e_t", 0))
                    e_c = data.get("events_c", data.get("e_c", 0))
                    ef = effect_log_rr(
                        study_id,
                        label,
                        int(e_t),
                        int(data.get("n_t", 0)),
                        int(e_c),
                        int(data.get("n_c", 0)),
                    )
                ef.label = f"{label} ({cand.get('outcome_label', '')})"
                efeitos.append(ef)
            if not efeitos:
                continue
            pooled_pack = pool_effects(efeitos, model=model)
            scale = "exp" if cand["tipo"] == "binary" else "identity"
            forest_path = f"/tmp/forest_{cand.get('outcome_id', idx)}.png"
            fp = forest_plot_png(pooled_pack["pooled"], efeitos, forest_path, scale=scale)
            resultados.append({
                "outcome_label": cand.get("outcome_label"),
                "outcome_id": cand.get("outcome_id"),
                "tipo": cand["tipo"],
                "n_estudos": len(efeitos),
                "pooled": pooled_pack["pooled"],
                "effects": pooled_pack["effects"],
                "forest_plot": fp,
            })
        except Exception as e:
            logging.warning(f"[META_ANALYSIS] Candidato {cand.get('outcome_label')} falhou: {e}")
    return resultados


def gerar_meta_analise(tema: str = "", etapa: str = "1", dados_extras: dict = None, texto_artigo: str = None) -> dict:
    """
    Gera análise e criação de artigos de Metanálises seguindo protocolo PRISMA.
    
    Args:
        tema: Tema da revisão sistemática (obrigatório)
        etapa: Etapa do workflow (1=PICO+Busca, 2=Extração, 3=Redação, 4=Verificação)
        dados_extras: Dicionário com dados adicionais (json_extração, estilo, etc.)
        texto_artigo: Texto do(s) artigo(s) científico(s) - opcional, usado apenas nas etapas 2-4
    
    Returns:
        Dicionário com 'resultado' (resposta formatada da IA) e 'artigos' (lista de artigos encontrados, apenas na etapa 1)
    """
    # Limitar texto se fornecido
    if texto_artigo:
        texto_artigo = texto_artigo[:6000] if len(texto_artigo) > 6000 else texto_artigo
    else:
        texto_artigo = ""
    
    # Determinar qual prompt usar baseado na etapa
    # NOVO FLUXO: Etapa 1 agora é análise PRISMA dos artigos enviados (não busca)
    if etapa == "1" or etapa == "pico":
        # Se tiver artigos analisados em dados_extras, usar análise PRISMA
        if dados_extras and "artigos_analisados" in dados_extras:
            prompt = _criar_prompt_etapa1_com_artigos(dados_extras)
            resultados_busca = None
        else:
            # Fallback: busca tradicional (mantido para compatibilidade)
            prompt, resultados_busca = _criar_prompt_etapa1_com_busca(tema, dados_extras)
    elif etapa == "2" or etapa == "extracao":
        prompt = _criar_prompt_etapa2(texto_artigo, dados_extras)
        resultados_busca = None
    elif etapa == "3" or etapa == "redacao":
        prompt = _criar_prompt_etapa3(texto_artigo, dados_extras)
        resultados_busca = None
    elif etapa == "4" or etapa == "verificacao":
        prompt = _criar_prompt_etapa4(texto_artigo, dados_extras)
        resultados_busca = None
    elif etapa == "5" or etapa == "meta":
        # Etapa 5: metanálise numérica (meta_stats) + opcional metanálises automáticas a partir do Evidence Graph
        prompt = None
        resultados_busca = None

        estudos = (dados_extras or {}).get("extracted_studies_confirmed", [])
        outcome_mode = (dados_extras or {}).get("outcome_mode", "continuous")
        model = (dados_extras or {}).get("model", "random_DL")
        label = (dados_extras or {}).get("label", "Outcome")
        project_id = (dados_extras or {}).get("project_id")

        # Se houver project_id, carregar graph e tentar metanálises automáticas (candidatos do detector)
        graph = None
        if project_id is not None:
            try:
                conn = get_connection()
                try:
                    graph = carregar_evidence_graph_por_projeto(conn, int(project_id))
                finally:
                    conn.close()
            except Exception as e:
                logging.warning(f"[META_ANALYSIS] Falha ao carregar graph (project_id={project_id}): {e}")

        if graph and detectar_metaanalises_possiveis(graph):
            auto_resultados = _executar_metaanalises_dos_candidatos(graph, model=model)
            if auto_resultados:
                linhas = ["Metanálises automáticas (Evidence Graph):", ""]
                for r in auto_resultados:
                    p = r.get("pooled", {})
                    linhas.append(f"• {r.get('outcome_label', '')} ({r.get('tipo', '')}, n={r.get('n_estudos', 0)})")
                    linhas.append(f"  Efeito combinado: {p.get('mu')} [IC95%: {p.get('ci_low')}–{p.get('ci_high')}]")
                    linhas.append(f"  I²={p.get('I2')}%, Q={p.get('Q')}, p_heterogeneidade={p.get('p_heterogeneity')}")
                    linhas.append("")
                texto = "\n".join(linhas)
                return {
                    "resultado": texto,
                    "artigos": [],
                    "total_artigos": 0,
                    "metaanalises_automaticas": auto_resultados,
                }

        # Fluxo habitual: usar extracted_studies_confirmed e opcional filtro por outcome no graph
        outcome_label = (dados_extras or {}).get("outcome_label") or label
        if graph and outcome_label and estudos:
            try:
                study_labels_graph = set(studies_for_outcome(graph, outcome_label) or [])
                if study_labels_graph:
                    estudos_filtrados = []
                    for s in estudos:
                        lbl = str(
                            s.get("label")
                            or s.get("study")
                            or s.get("study_id")
                            or ""
                        ).strip()
                        if lbl in study_labels_graph:
                            estudos_filtrados.append(s)
                    if estudos_filtrados:
                        logging.warning(
                            f"[META_ANALYSIS] Etapa 5: filtrando estudos por Evidence Graph "
                            f"(outcome='{outcome_label}', antes={len(estudos)}, depois={len(estudos_filtrados)})"
                        )
                        estudos = estudos_filtrados
            except Exception as e:
                logging.warning(f"[META_ANALYSIS] Falha ao usar Evidence Graph na Etapa 5: {e}")

        efeitos = []
        for s in estudos:
            study_id = str(s.get("study_id") or s.get("id") or s.get("study") or "study")
            study_label = str(s.get("label") or s.get("study") or study_id)

            if outcome_mode == "continuous":
                ef = effect_smd_hedges_g(
                    study_id,
                    study_label,
                    int(s["n_t"]),
                    float(s["mean_t"]),
                    float(s["sd_t"]),
                    int(s["n_c"]),
                    float(s["mean_c"]),
                    float(s["sd_c"]),
                )
            elif outcome_mode == "rr":
                ef = effect_log_rr(
                    study_id,
                    study_label,
                    int(s["e_t"]),
                    int(s["n_t"]),
                    int(s["e_c"]),
                    int(s["n_c"]),
                )
            elif outcome_mode == "or":
                ef = effect_log_or(
                    study_id,
                    study_label,
                    int(s["e_t"]),
                    int(s["n_t"]),
                    int(s["e_c"]),
                    int(s["n_c"]),
                )
            else:
                raise ValueError("outcome_mode inválido. Use: continuous|rr|or")

            ef.label = f"{study_label} ({label})"
            efeitos.append(ef)

        pooled_pack = pool_effects(efeitos, model=model)

        forest_path = (dados_extras or {}).get("forest_path", "/tmp/forest_plot.png")
        scale = "exp" if outcome_mode in ("rr", "or") else "identity"
        fp = forest_plot_png(pooled_pack["pooled"], efeitos, forest_path, scale=scale)

        resultado = {
            "resultado": {
                "pooled": pooled_pack["pooled"],
                "effects": pooled_pack["effects"],
                "forest_plot": fp,
            },
            "artigos": [],
            "total_artigos": 0,
        }

        if (dados_extras or {}).get("gerar_texto_sugestao"):
            resumo_numeros = {
                "outcome_mode": outcome_mode,
                "model": model,
                "pooled": pooled_pack["pooled"],
            }
            import json as _json

            prompt_txt = f"""
Atue como redator científico. Gere uma SUGESTÃO curta para a seção de resultados da metanálise,
usando SOMENTE estes números (não invente nada):
{_json.dumps(resumo_numeros, ensure_ascii=False, indent=2)}
Escreva em português brasileiro, tom impessoal.
"""
            sugestao = gerar_resposta(prompt_txt, temperatura=0.3)
            resultado["resultado"]["texto_sugestao"] = sugestao

        return resultado
    else:
        # Etapa padrão
        if dados_extras and "artigos_analisados" in dados_extras:
            prompt = _criar_prompt_etapa1_com_artigos(dados_extras)
            resultados_busca = None
        else:
            prompt, resultados_busca = _criar_prompt_etapa1_com_busca(tema, dados_extras)
    
    # Gerar resposta com temperatura adequada para análise científica
    resposta = gerar_resposta(prompt, temperatura=0.7)
    
    # Retornar resultado e artigos (apenas na etapa 1)
    resultado = {
        'resultado': resposta
    }
    
    # Se for etapa 1, incluir artigos encontrados
    if (etapa == "1" or etapa == "pico") and resultados_busca:
        artigos_pubmed = resultados_busca.get('pubmed', {}).get('artigos', [])
        # Filtrar apenas artigos com detalhes completos (não apenas IDs)
        artigos_detalhados = [a for a in artigos_pubmed if isinstance(a, dict) and 'title' in a]
        resultado['artigos'] = artigos_detalhados
        resultado['total_artigos'] = resultados_busca.get('pubmed', {}).get('total', 0)
    else:
        resultado['artigos'] = []
        resultado['total_artigos'] = 0
    
    return resultado

def _criar_prompt_etapa1_com_busca(tema: str, dados_extras: dict = None) -> tuple:
    """
    Prompt para Etapa 1: Estruturação PICO, Protocolo e Busca na Literatura.
    
    Returns:
        Tupla (prompt_str, resultados_busca_dict)
    """
    try:
        from .literature_search import buscar_literatura, gerar_resumo_busca
    except ImportError:
        try:
            from literature_search import buscar_literatura, gerar_resumo_busca
        except ImportError:
            import backend.literature_search as literature_search
            buscar_literatura = literature_search.buscar_literatura
            gerar_resumo_busca = literature_search.gerar_resumo_busca
    
    # Realizar busca na literatura
    resultados_busca = buscar_literatura(tema)
    resumo_busca = gerar_resumo_busca(resultados_busca, tema)
    
    prompt = f"""
# PERSONA
Atue como um Especialista em Metodologia Científica especializado em Revisões Sistemáticas e Metanálises seguindo protocolo PRISMA.

# ETAPA 1: MAPEAMENTO PICO, PROTOCOLO E BUSCA NA LITERATURA

Tema da revisão: {tema}

# RESULTADOS DA BUSCA BIBLIOGRÁFICA

## Busca Realizada
Foram realizadas buscas nas seguintes bases de dados:
- PubMed: {resultados_busca.get('pubmed', {}).get('total', 0)} artigos encontrados
- LILACS: {resultados_busca.get('lilacs', {}).get('total', 0)} artigos encontrados
- Cochrane: Estratégia de busca gerada

## Resumo da Busca
{resumo_busca}

# TAREFA
Com base no tema fornecido e nos resultados da busca bibliográfica, você deve:

**Requisitos de rigor (obrigatório):**
- PICO deve ser reprodutível: população, intervenção, comparador e desfechos mensuráveis em uma frase de pergunta clínica.
- Critérios de inclusão/exclusão devem ser verificáveis a partir do título/resumo (evite adjetivos vagos como “bons estudos”).
- A estratégia de busca deve poder ser copiada para as bases (termos + operadores booleanos por linha).

1. **Gerar a pergunta estruturada PICO:**
   - P (Paciente/População): Quem?
   - I (Intervenção): O quê?
   - C (Comparação): Comparado com quê?
   - O (Outcome/Desfecho): Qual o resultado esperado?

2. **Definir critérios de inclusão/exclusão:**
   - Critérios de inclusão claros e objetivos
   - Critérios de exclusão específicos
   - Tipo de estudo (RCT, coorte, etc.)

3. **Criar estratégia de busca detalhada:**
   - Termos MeSH/DeCS para PubMed
   - Termos MeSH/DeCS para LILACS
   - Estratégia para Cochrane Library
   - Combinações booleanas (AND, OR, NOT)
   - Filtros de data, idioma, tipo de estudo

4. **Estabelecer protocolo de seleção:**
   - Processo de triagem (título/resumo, texto completo)
   - Critérios de elegibilidade
   - Resolução de conflitos entre revisores

# FORMATO DA RESPOSTA
Organize a resposta em seções claras:
- Pergunta PICO
- Critérios de Elegibilidade
- Estratégia de Busca (por base de dados)
- Protocolo de Seleção

IMPORTANTE: Responda SEMPRE em português brasileiro.
"""
    return prompt, resultados_busca

def _criar_prompt_etapa1_com_artigos(dados_extras: dict = None) -> str:
    """Prompt para Etapa 1: Estruturação PICO baseada nos artigos analisados (NOVO FLUXO)."""
    artigos_analisados = dados_extras.get("artigos_analisados", []) if dados_extras else []
    resumo_analises = dados_extras.get("resumo_analises", {}) if dados_extras else {}
    
    # Preparar resumo dos artigos para o prompt
    resumo_artigos = ""
    for idx, artigo in enumerate(artigos_analisados, 1):
        analise = artigo.get("analise_prisma", {})
        resumo_artigos += f"""
Artigo {idx}: {artigo.get("titulo", artigo.get("arquivo", "Sem título"))}
- Tipo de Estudo: {analise.get("tipo_estudo", "N/A")}
- Escore de Qualidade: {analise.get("escore_qualidade", 0)}/10
- Pontuação PRISMA: {analise.get("pontuacao_prisma", 0)}/14
- Risco de Viés: {analise.get("risco_vies", "N/A")}
- Recomendação: {analise.get("recomendacao", "N/A")}
- Pontos Fortes: {', '.join(analise.get("pontos_fortes", []))}
- Pontos Fracos: {', '.join(analise.get("pontos_fracos", []))}
"""
    
    prompt = f"""
# PERSONA
Atue como um Especialista em Metodologia Científica especializado em Revisões Sistemáticas e Metanálises seguindo protocolo PRISMA.

# ETAPA 1: MAPEAMENTO PICO E PROTOCOLO BASEADO NOS ARTIGOS ANALISADOS

# ARTIGOS ENVIADOS E ANALISADOS
Total de artigos analisados: {len(artigos_analisados)}

## Resumo das Análises PRISMA:
- Escore Médio de Qualidade: {resumo_analises.get("escore_medio", 0):.2f}/10
- Pontuação PRISMA Média: {resumo_analises.get("pontuacao_prisma_media", 0):.2f}/14
- Distribuição por Qualidade:
  * Excelente (9-10): {resumo_analises.get("artigos_por_qualidade", {}).get("excelente", 0)} artigos
  * Boa (7-8): {resumo_analises.get("artigos_por_qualidade", {}).get("boa", 0)} artigos
  * Regular (5-6): {resumo_analises.get("artigos_por_qualidade", {}).get("regular", 0)} artigos
  * Baixa (<5): {resumo_analises.get("artigos_por_qualidade", {}).get("baixa", 0)} artigos

## Detalhes dos Artigos:
{resumo_artigos}

# TAREFA
Com base nos artigos analisados e suas avaliações PRISMA, você deve:

1. **Gerar a pergunta estruturada PICO:**
   - P (Paciente/População): Quem? (baseado nos artigos analisados)
   - I (Intervenção): O quê? (baseado nos artigos analisados)
   - C (Comparação): Comparado com quê?
   - O (Outcome/Desfecho): Qual o resultado esperado?

2. **Definir critérios de inclusão/exclusão:**
   - Critérios de inclusão claros baseados nos artigos de alta qualidade
   - Critérios de exclusão específicos (artigos com escore < 5 devem ser excluídos)
   - Tipo de estudo predominante identificado

3. **Criar estratégia de seleção baseada nos escores:**
   - Artigos com escore >= 7: Incluir automaticamente
   - Artigos com escore 5-6: Incluir com ressalvas (justificar)
   - Artigos com escore < 5: Excluir (justificar)

4. **Estabelecer protocolo de seleção:**
   - Processo de triagem baseado nos escores PRISMA
   - Critérios de elegibilidade baseados na qualidade metodológica
   - Resolução de conflitos entre revisores

# FORMATO DA RESPOSTA
Organize a resposta em seções claras:
- Pergunta PICO (baseada nos artigos analisados)
- Critérios de Elegibilidade (baseados nos escores PRISMA)
- Estratégia de Seleção (por escore de qualidade)
- Protocolo de Seleção
- Recomendação de Artigos a Incluir/Excluir

IMPORTANTE: Responda SEMPRE em português brasileiro.
"""
    return prompt

def _criar_prompt_inicial(texto_artigo: str, dados_extras: dict = None) -> str:
    """Prompt inicial que pergunta sobre o estágio da pesquisa."""
    tema = dados_extras.get("tema", "") if dados_extras else ""
    
    prompt = f"""
# PERSONA
Atue como um Especialista em Metodologia Científica e Engenheiro de Prompt de IA. Seu objetivo é estruturar um aplicativo/workflow de escrita para Revisões Sistemáticas e Metanálises que siga rigorosamente o protocolo PRISMA (Preferred Reporting Items for Systematic Reviews and Meta-Analyses).

# DIRETRIZES DE SEGURANÇA (ANTI-ALUCINAÇÃO E PLÁGIO)
1. ZERO-KNOWLEDGE WRITING: Você não deve usar seu conhecimento interno para citar fatos. Use apenas os dados extraídos dos arquivos carregados.
2. VERBATIM CHECK: Toda citação direta deve ser sinalizada. A paráfrase deve ser técnica e original para garantir <5% de similaridade em softwares de plágio.
3. CITATION MAPPING: Cada parágrafo deve conter a referência (Autor, Ano) vinculada à base de dados fornecida.

# ESTRUTURA DO APLICATIVO (PIPELINE)
Você deve guiar o usuário através de 4 módulos sequenciais:

### Módulo 1: Estruturação PICO e Protocolo
- Entrada: Tema central.
- Saída: Pergunta PICO, estratégia de busca (MeSH/DeCS) para PubMed, Embase e Cochrane, e critérios de elegibilidade.

### Módulo 2: Extração de Dados e Tabela de Evidências
- Entrada: PDFs ou tabelas de dados brutos dos artigos selecionados.
- Processamento: Extrair N, intervenção, controle, desfechos e viés (Risk of Bias - Cochrane Tool).
- Saída: Tabela de características dos estudos padronizada.

### Módulo 3: Escrita Técnica (PRISMA Compliance)
- Fluxo de Redação:
  1. Introdução (Racional e Objetivos).
  2. Métodos (Estratégia de busca, seleção, extração e síntese estatística).
  3. Resultados (Fluxograma PRISMA e descrição dos estudos).
  4. Discussão (Limitações, força da evidência e conclusão).

### Módulo 4: Verificação e Revisão de Estilo
- Revisão gramatical acadêmica (Medical English ou ABNT/Vancouver).
- Verificação de consistência entre a tabela de dados e o texto escrito.

# FORMATO DA RESPOSTA
Inicie perguntando ao usuário: "Qual o tema da revisão e qual o estágio atual da sua pesquisa (Ideia, Busca de Artigos ou Extração de Dados)?"

{f"Tema fornecido: {tema}" if tema else ""}

Texto do(s) artigo(s) fornecido(s):
{texto_artigo}

IMPORTANTE: Responda SEMPRE em português brasileiro, mesmo que o artigo esteja em inglês.
"""
    return prompt

def _criar_prompt_etapa1(texto_artigo: str, dados_extras: dict = None) -> str:
    """Prompt para Etapa 1: Estruturação PICO e Protocolo."""
    tema = dados_extras.get("tema", "") if dados_extras else ""
    
    prompt = f"""
# PERSONA
Atue como um Especialista em Metodologia Científica especializado em Revisões Sistemáticas e Metanálises seguindo protocolo PRISMA.

# ETAPA 1: MAPEAMENTO PICO E CRITÉRIOS

Tema da revisão: {tema if tema else "Não especificado"}

Texto do(s) artigo(s):
{texto_artigo}

# TAREFA
1. Gere a pergunta estruturada PICO (Paciente, Intervenção, Comparação, Outcome).
2. Defina critérios de inclusão/exclusão baseados no protocolo fornecido.
3. Crie estratégia de busca com termos MeSH/DeCS para PubMed, Embase e Cochrane.
4. Estabeleça critérios de elegibilidade claros e objetivos.

# DIRETRIZES
- Use apenas informações presentes no texto fornecido.
- Se algum dado não estiver disponível, indique claramente.
- Formate a saída de forma estruturada e clara.

IMPORTANTE: Responda SEMPRE em português brasileiro, mesmo que o artigo esteja em inglês.
"""
    return prompt

def _criar_prompt_etapa2(texto_artigo: str, dados_extras: dict = None) -> str:
    """Prompt para Etapa 2: Extração de Dados e Tabela de Evidências."""
    prompt = f"""
# PERSONA
Atue como um Especialista em Extração de Dados para Revisões Sistemáticas e Metanálises.

# ETAPA 2: EXTRAÇÃO DE DADOS (DATA EXTRACTION)

Texto do(s) artigo(s):
{texto_artigo}

# TAREFA
Extraia os dados do(s) artigo(s) seguindo estritamente o esquema JSON fornecido abaixo. Se um valor numérico não for encontrado, use null. Não tente calcular valores ausentes. Extraia apenas o que está explicitamente escrito no texto para garantir 0% de alucinação nos dados brutos.

Além disso:
- retorne também um campo de nível superior "needs_user_confirmation": true
- para CADA outcome extraído, inclua:
  - "evidence_snippet": trecho EXATO (curto) do texto onde o número aparece
  - "page_hint": se houver indicação (ex: "Page 4" ou "Tabela 2"), senão "not_reported"

# ESQUEMA JSON DE EXTRAÇÃO (Standard de Ouro)
{{
  "study_metadata": {{
    "title": "string",
    "authors": "string",
    "year": "integer",
    "doi": "string",
    "study_design": "string (ex: RCT, Cohort, Case-Control)"
  }},
  "population": {{
    "total_sample_size": "integer",
    "intervention_group_n": "integer",
    "control_group_n": "integer",
    "age_mean": "number",
    "setting": "string (ex: Hospital, Community)"
  }},
  "outcomes": [
    {{
      "outcome_name": "string",
      "measure_type": "string (ex: Mean, Odds Ratio, Risk Ratio)",
      "intervention_results": {{
        "mean_or_event": "number",
        "sd_or_total": "number"
      }},
      "control_results": {{
        "mean_or_event": "number",
        "sd_or_total": "number"
      }},
      "p_value": "number",
      "confidence_interval": "string (ex: 95% CI 1.2-1.8)"
    }}
  ],
  "risk_of_bias": {{
    "tool_used": "string (ex: RoB 2, Newcastle-Ottawa)",
    "overall_score": "string (ex: Low, High, Some concerns)",
    "justification": "string"
  }}
}}

# INSTRUÇÕES
1. Crie uma tabela estruturada contendo: Autor/Ano, N total, Média/Evento em cada braço, Desfechos Primários e Avaliação de Viés.
2. Se houver múltiplos estudos, extraia cada um separadamente.
3. Valide se intervention_group_n + control_group_n == total_sample_size.
4. Se p_value < 0.05 mas confidence_interval cruza a linha de nulidade, sinalize inconsistência estatística.
5. Inclua no topo do objeto: "needs_user_confirmation": true para sinalizar que a extração deve ser revisada por um humano.

IMPORTANTE: Responda SEMPRE em português brasileiro, mesmo que o artigo esteja em inglês. Retorne o JSON estruturado seguido de uma tabela formatada para visualização.
"""
    return prompt

def _criar_prompt_etapa3(texto_artigo: str, dados_extras: dict = None) -> str:
    """Prompt para Etapa 3: Síntese Qualitativa e Redação (PRISMA Compliance)."""
    json_extracao = dados_extras.get("json_extracao", "") if dados_extras else ""
    
    prompt = f"""
# PERSONA
Atue como um Redator Científico Sênior especializado em Revisões Sistemáticas. Sua tarefa é redigir a seção de "Resultados" e "Discussão" baseando-se EXCLUSIVAMENTE no objeto JSON de extração de dados fornecido.

# INPUT DATA
JSON de Extração:
{json_extracao if json_extracao else "Não fornecido - use os dados do texto abaixo"}

Texto do(s) artigo(s):
{texto_artigo}

# REGRAS DE OURO (RIGOR CIENTÍFICO)
1. ANCORAGEM NUMÉRICA: Toda vez que mencionar um resultado, você deve citar os valores exatos do JSON (n, p-valor, IC 95%).
2. SÍNTESE, NÃO REPETIÇÃO: Não faça apenas uma lista. Compare os estudos. Agrupe estudos com resultados similares e contraste os que apresentaram discrepâncias.
3. ANTI-PLÁGIO: Utilize paráfrases técnicas. Em vez de "o estudo X disse Y", use "Observou-se uma tendência de [Desfecho] no grupo [Intervenção] em comparação ao [Controle] (Estudo X, Ano)".
4. VERIFICAÇÃO DE VIÉS: Integre os dados de 'risk_of_bias' na narrativa. Discuta como a qualidade metodológica de cada estudo pode ter influenciado os resultados encontrados.

# ESTRUTURA DA REDAÇÃO
1. CARACTERÍSTICAS DOS ESTUDOS: Descreva o perfil populacional médio e os desenhos de estudo encontrados.
2. SÍNTESE DOS DESFECHOS: Organize por subtemas (ex: Eficácia, Segurança, Marcadores Bioquímicos).
3. ANÁLISE DE HETEROGENEIDADE: Comente sobre as variações entre os estudos (diferenças de doses, idade, tempo de seguimento).
4. CONCLUSÃO PRELIMINAR: Resuma a força da evidência atual.

# RESTRIÇÕES DE OUTPUT
- Proibido usar adjetivos subjetivos (ex: "estudo maravilhoso", "resultado incrível"). Use termos neutros (ex: "estatisticamente significativo", "robusto", "limitado").
- Limite de alucinação: Se o JSON marcar um campo como `null`, você deve escrever que "não foram reportados dados sobre [X] neste conjunto de evidências".
- Estilo: Linguagem acadêmica formal (Medical English ou Português Acadêmico), tom impessoal.

# ETAPA 3: SÍNTESE ESTATÍSTICA E RESULTADOS
- Descreva os resultados para o Forest Plot (Heterogeneidade I², Valor de p, e Effect Size). 
- *Nota: Se o usuário não fornecer os cálculos, descreva qualitativamente os resultados seguindo o rigor estatístico.*

# ETAPA 4: REDAÇÃO CONFORME PRISMA
- Redija as seções: Métodos, Resultados e Discussão.

IMPORTANTE: Responda SEMPRE em português brasileiro, mesmo que o artigo esteja em inglês.
"""
    return prompt

def _criar_prompt_etapa4(texto_artigo: str, dados_extras: dict = None) -> str:
    """Prompt para Etapa 4: Verificação Final, Rigor PRISMA e Formatação."""
    json_extracao = dados_extras.get("json_extracao", "") if dados_extras else ""
    estilo = dados_extras.get("estilo", "Vancouver") if dados_extras else "Vancouver"
    manuscrito = dados_extras.get("manuscrito", texto_artigo) if dados_extras else texto_artigo
    
    prompt = f"""
# PERSONA
Atue como Editor-Chefe de um periódico médico de alto fator de impacto e Especialista em Normatização Científica. Sua missão é realizar a revisão final do manuscrito para garantir ZERO erros de formatação e integridade total dos dados.

# INPUT
1. Manuscrito gerado no Módulo 3:
{manuscrito}

2. JSON de extração original (para conferência):
{json_extracao if json_extracao else "Não fornecido"}

# TAREFA 1: CROSS-CHECK DE DADOS (ANTI-ALUCINAÇÃO FINAL)
- Compare cada número, porcentagem e p-valor presente no texto com o JSON original.
- Liste em uma tabela de "Divergências Encontradas" qualquer dado que não seja idêntico ao JSON. Se não houver divergências, escreva: "Dados 100% íntegros".

# TAREFA 2: CHECKLIST PRISMA 2020
- Analise o texto e verifique se os seguintes itens estão presentes e claros:
    - Elegibilidade (Critérios PICO).
    - Fontes de informação e estratégia de busca.
    - Processo de seleção e extração.
    - Avaliação do risco de viés (RoB).
    - Síntese dos resultados.

# TAREFA 3: FORMATAÇÃO DE REFERÊNCIAS E ESTILO
- Aplique o estilo {estilo} (VANCOUVER OU ABNT).
- Garanta que todas as citações no corpo do texto tenham uma correspondência na lista de referências final.
- Verifique o tom: O texto deve ser estritamente impessoal, em voz passiva (ex: "Observou-se" em vez de "Nós observamos").

# TAREFA 4: REVISÃO DE PLÁGIO (PARÁFRASE CIENTÍFICA)
- Identifique frases que possuam estrutura sintática muito comum ou repetitiva.
- Sugira melhorias para aumentar a sofisticação do "Medical English" ou do "Português Acadêmico", mantendo a precisão dos termos MeSH/DeCS.

# OUTPUT FINAL
1. Relatório de Erros/Inconsistências (se houver).
2. Versão Final do Manuscrito formatada e polida.
3. Declaração de conformidade com as normas PRISMA.

IMPORTANTE: Responda SEMPRE em português brasileiro, mesmo que o artigo esteja em inglês.
"""
    return prompt


PROMPTS_SECAO = {
    "resumo": """
Você é um especialista em redação científica. Com base nos dados da meta-análise abaixo,
escreva um RESUMO ESTRUTURADO seguindo as diretrizes PRISMA 2020.

O resumo deve conter:
- Objetivo
- Critérios de elegibilidade
- Fontes de informação
- Método de síntese
- Resultados principais (com dados quantitativos quando disponíveis)
- Limitações
- Conclusão

Dados da meta-análise:
{contexto}

Escreva em {idioma}. Use linguagem científica formal. Máximo 350 palavras.
""",
    "introducao": """
Você é um especialista em redação de artigos de revisão sistemática.
Escreva a INTRODUÇÃO do artigo de meta-análise com base nos dados abaixo.

A introdução deve:
1. Contextualizar o problema clínico/científico
2. Apresentar a lacuna de conhecimento
3. Justificar a necessidade da meta-análise
4. Declarar claramente o objetivo e a questão PICO

Dados disponíveis:
{contexto}

Escreva em {idioma}. Linguagem científica, sem bullets, em prosa fluente.
""",
    "metodos": """
Você é um especialista em metodologia de revisões sistemáticas (Cochrane, PRISMA 2020).
Escreva a seção de MÉTODOS do artigo com base nos dados abaixo.

Inclua:
1. Protocolo e registro (se disponível)
2. Critérios de elegibilidade
3. Fontes de informação e estratégia de busca
4. Processo de seleção de estudos
5. Extração de dados
6. Avaliação do risco de viés
7. Método de síntese estatística (modelo, heterogeneidade, I²)

Dados disponíveis:
{contexto}

Escreva em {idioma}. Linguagem científica, sem bullets, em prosa fluente.
""",
    "resultados": """
Você é um especialista em bioestatística e revisões sistemáticas.
Escreva a seção de RESULTADOS do artigo com base nos dados abaixo.

Inclua:
1. Seleção dos estudos (fluxo PRISMA)
2. Características dos estudos incluídos
3. Risco de viés dos estudos
4. Resultados das sínteses (valores numéricos disponíveis: RR/OR/SMD, IC95%, I², p-valor)
5. Análises de sensibilidade (se disponíveis)

Dados disponíveis:
{contexto}

Escreva em {idioma}. Linguagem científica formal.
""",
    "discussao": """
Você é um especialista em medicina baseada em evidências.
Escreva a seção de DISCUSSÃO do artigo com base nos dados abaixo.

Inclua:
1. Principais achados
2. Comparação com literatura
3. Possíveis explicações para heterogeneidade
4. Limitações do estudo
5. Implicações para prática clínica
6. Implicações para pesquisa futura
7. Conclusão final

Dados disponíveis:
{contexto}

Escreva em {idioma}. Linguagem científica formal, em prosa.
""",
}


def montar_contexto_projeto(project_id: int, conn) -> str:
    """
    Consolida dados de jobs concluídos e do evidence graph para uso na escrita do artigo.
    """
    rows = conn.execute(
        """
        SELECT modulo, resultado, dados_extras, analysis_json
        FROM research_jobs
        WHERE project_id = %s AND status = 'done'
        ORDER BY id ASC
        """,
        (project_id,),
    ).fetchall()

    partes = [f"PROJECT_ID: {project_id}"]
    for row in rows:
        modulo = row.get("modulo", "desconhecido")
        if row.get("resultado"):
            partes.append(f"=== MODULO: {modulo} ===\n{str(row['resultado'])[:3000]}")
        if row.get("analysis_json"):
            partes.append(f"=== ANALYSIS_JSON: {modulo} ===\n{str(row['analysis_json'])[:3000]}")
        if row.get("dados_extras"):
            partes.append(f"=== DADOS_EXTRAS: {modulo} ===\n{str(row['dados_extras'])[:3000]}")

    graph_row = conn.execute(
        "SELECT graph_data FROM evidence_graphs WHERE project_id = %s",
        (project_id,),
    ).fetchone()
    if graph_row and graph_row.get("graph_data"):
        try:
            import json as _json

            graph_data = graph_row["graph_data"]
            graph = _json.loads(graph_data) if isinstance(graph_data, str) else graph_data
            studies = [n for n in (graph.get("nodes") or []) if n.get("type") == "Study"]
            partes.append(f"=== EVIDENCE_GRAPH: estudos={len(studies)} ===")
            for s in studies[:20]:
                partes.append(
                    f"- {s.get('label') or s.get('id') or 'Study'} | year={s.get('year') or ''} | n={s.get('n') or ''}"
                )
        except Exception as e:
            logging.warning(f"[META_ANALYSIS] Falha ao interpretar evidence_graph: {e}")

    return "\n\n".join(partes).strip()


def escrever_secao_artigo(
    project_id: int,
    tema: str,
    secao: str,
    estilo_referencia: str = "Vancouver",
    idioma: str = "pt",
    instrucoes_adicionais: str = "",
) -> str:
    """
    Gera uma seção do artigo científico usando dados consolidados do projeto.
    """
    conn = get_connection()
    try:
        contexto = montar_contexto_projeto(project_id, conn)
    finally:
        conn.close()

    if not contexto:
        return "Erro: Nenhum dado encontrado para o projeto. Execute as etapas anteriores antes de gerar o artigo."

    secao_norm = (secao or "").strip().lower()
    prompt_template = PROMPTS_SECAO.get(secao_norm)
    if not prompt_template:
        return f"Erro: Seção '{secao}' não reconhecida."

    idioma_texto = "português científico brasileiro" if idioma == "pt" else "scientific English"
    prompt = prompt_template.format(contexto=contexto[:7000], idioma=idioma_texto)
    prompt += f"\n\nTema do projeto: {tema or 'não informado'}"
    prompt += f"\nEstilo de referência: {estilo_referencia}"
    if instrucoes_adicionais:
        prompt += f"\nInstruções adicionais: {instrucoes_adicionais}"

    try:
        return gerar_resposta(
            prompt,
            temperatura=0.5,
            max_output_tokens=2200,
            tipo="redacao",
        )
    except Exception as e:
        logging.error(f"[META_ANALYSIS] Erro ao escrever seção '{secao_norm}': {e}")
        return f"Erro ao gerar seção '{secao_norm}': {e}"
