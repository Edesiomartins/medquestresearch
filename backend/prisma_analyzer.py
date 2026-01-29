"""
Módulo para análise PRISMA de artigos científicos.
Avalia qualidade metodológica e gera escore para cada artigo.
"""

try:
    from .gpt_engine import gerar_resposta
except ImportError:
    try:
        from gpt_engine import gerar_resposta
    except ImportError:
        import backend.gpt_engine as gpt_engine
        gerar_resposta = gpt_engine.gerar_resposta

import json

def _criar_analise_fallback(resposta: str) -> dict:
    """Cria estrutura de análise básica em caso de erro no parsing."""
    return {
        "tipo_estudo": "not_reported",
        "design_metodologico": "not_reported",
        "pico": {
            "population": "not_reported",
            "intervention": "not_reported",
            "comparison": "not_reported",
            "outcomes": []
        },
        "quantitative_outcomes": [],
        "checklist_prisma": {},
        "risco_vies": "Insufficient_information",
        "pontuacao_prisma": 0,
        "escore_qualidade": 0,
        "justificativa_escore": "Erro ao processar análise: " + resposta[:200],
        "pontos_fortes": [],
        "pontos_fracos": ["Erro ao processar análise"],
        "recomendacao": "Exclude",
        "observacoes": resposta[:500]
    }

def analisar_artigo_prisma(texto_artigo: str, titulo: str = "") -> dict:
    """
    Analisa um artigo científico usando critérios PRISMA e gera escore de qualidade.
    Prompt otimizado para NVIDIA Nemotron-Nano-12B-v2-VL.
    
    Args:
        texto_artigo: Texto completo do artigo extraído do PDF
        titulo: Título do artigo (opcional, ajuda na análise)
    
    Returns:
        Dicionário com análise PRISMA e escore
    """
    prompt = f"""Role: Você é um Agente de Extração de Dados Científicos de alta precisão, especializado em Revisões Sistemáticas e Metanálises na área da Saúde.

Instrução de Fluxo: Analise o texto do artigo científico fornecido. Sua tarefa é realizar a triagem e extração seguindo estas etapas:

1. Identifique se o estudo é um Ensaio Clínico Randomizado (RCT), Coorte, Caso-Controle, Revisão Sistemática/Metanálise ou Outro.

2. Extraia os componentes PICO:
   - P (Population): População/Pacientes
   - I (Intervention): Intervenção
   - C (Comparison): Comparação/Controle
   - O (Outcome): Desfechos

3. Localize os desfechos quantitativos (médias, desvios-padrão, n, ou OR/RR com IC 95%).

4. Avalie critérios PRISMA 2020 e risco de viés.

Artigo para Análise:
Título: {titulo if titulo else "not_reported"}

Texto do Artigo:
{texto_artigo[:8000]}

Restrições Rígidas:
- Responda EXCLUSIVAMENTE em formato JSON.
- Não escreva introduções como "Aqui está o resumo".
- Se um dado não estiver explícito, preencha com "not_reported".
- Mantenha os termos técnicos em inglês (padrão de publicação).

Formato JSON Obrigatório:
{{
  "study_type": "RCT|Cohort|Case_Control|Systematic_Review|Meta_Analysis|Other",
  "pico": {{
    "population": "string|not_reported",
    "intervention": "string|not_reported",
    "comparison": "string|not_reported",
    "outcomes": ["string", "string"]
  }},
  "quantitative_outcomes": [
    {{
      "outcome_name": "string",
      "measure_type": "mean_sd|n_percentage|or_ci|rr_ci|other",
      "intervention_group": {{
        "n": "integer|not_reported",
        "mean": "number|not_reported",
        "sd": "number|not_reported",
        "events": "integer|not_reported",
        "percentage": "number|not_reported"
      }},
      "control_group": {{
        "n": "integer|not_reported",
        "mean": "number|not_reported",
        "sd": "number|not_reported",
        "events": "integer|not_reported",
        "percentage": "number|not_reported"
      }},
      "effect_measure": {{
        "or": "number|not_reported",
        "rr": "number|not_reported",
        "ci_95_lower": "number|not_reported",
        "ci_95_upper": "number|not_reported",
        "p_value": "number|not_reported"
      }}
    }}
  ],
  "prisma_checklist": {{
    "title_abstract": true|false,
    "introduction": true|false,
    "methods_protocol": true|false,
    "methods_search": true|false,
    "methods_selection": true|false,
    "methods_extraction": true|false,
    "methods_bias": true|false,
    "methods_synthesis": true|false,
    "results_flowchart": true|false,
    "results_characteristics": true|false,
    "results_individual": true|false,
    "discussion_summary": true|false,
    "discussion_limitations": true|false,
    "discussion_conclusion": true|false
  }},
  "risk_of_bias": "Low|Some_concerns|High|Insufficient_information",
  "prisma_score": "integer (0-14)",
  "quality_score": "integer (0-10)",
  "strengths": ["string"],
  "weaknesses": ["string"],
  "recommendation": "Include|Include_with_reservations|Exclude"
}}"""

    try:
        resposta = gerar_resposta(prompt, temperatura=0.3)  # Temperatura baixa para análise mais precisa
        
        # Tentar extrair JSON da resposta (modelo deve retornar apenas JSON)
        resposta_limpa = resposta.strip()
        
        # Remover markdown code blocks se houver
        if resposta_limpa.startswith("```json"):
            resposta_limpa = resposta_limpa[7:]
        if resposta_limpa.startswith("```"):
            resposta_limpa = resposta_limpa[3:]
        if resposta_limpa.endswith("```"):
            resposta_limpa = resposta_limpa[:-3]
        
        resposta_limpa = resposta_limpa.strip()
        
        # Parsear JSON
        try:
            analise_raw = json.loads(resposta_limpa)
            
            # Converter formato novo (inglês) para formato compatível (português)
            analise = {
                "tipo_estudo": analise_raw.get("study_type", "not_reported"),
                "design_metodologico": f"{analise_raw.get('study_type', 'Unknown')} study",
                "pico": analise_raw.get("pico", {}),
                "quantitative_outcomes": analise_raw.get("quantitative_outcomes", []),
                "checklist_prisma": analise_raw.get("prisma_checklist", {}),
                "risco_vies": analise_raw.get("risk_of_bias", "Insufficient_information"),
                "pontuacao_prisma": analise_raw.get("prisma_score", 0),
                "escore_qualidade": analise_raw.get("quality_score", 0),
                "justificativa_escore": f"PRISMA Score: {analise_raw.get('prisma_score', 0)}/14, Risk of Bias: {analise_raw.get('risk_of_bias', 'Unknown')}",
                "pontos_fortes": analise_raw.get("strengths", []),
                "pontos_fracos": analise_raw.get("weaknesses", []),
                "recomendacao": analise_raw.get("recommendation", "Exclude"),
                "observacoes": f"Study Type: {analise_raw.get('study_type', 'Unknown')}"
            }
            
        except json.JSONDecodeError:
            # Se falhar, tentar extrair JSON do texto
            import re
            json_match = re.search(r'\{.*\}', resposta_limpa, re.DOTALL)
            if json_match:
                try:
                    analise_raw = json.loads(json_match.group())
                    # Converter formato
                    analise = {
                        "tipo_estudo": analise_raw.get("study_type", "not_reported"),
                        "design_metodologico": f"{analise_raw.get('study_type', 'Unknown')} study",
                        "pico": analise_raw.get("pico", {}),
                        "quantitative_outcomes": analise_raw.get("quantitative_outcomes", []),
                        "checklist_prisma": analise_raw.get("prisma_checklist", {}),
                        "risco_vies": analise_raw.get("risk_of_bias", "Insufficient_information"),
                        "pontuacao_prisma": analise_raw.get("prisma_score", 0),
                        "escore_qualidade": analise_raw.get("quality_score", 0),
                        "justificativa_escore": f"PRISMA Score: {analise_raw.get('prisma_score', 0)}/14",
                        "pontos_fortes": analise_raw.get("strengths", []),
                        "pontos_fracos": analise_raw.get("weaknesses", []),
                        "recomendacao": analise_raw.get("recommendation", "Exclude"),
                        "observacoes": resposta[:500]
                    }
                except:
                    analise = _criar_analise_fallback(resposta)
            else:
                analise = _criar_analise_fallback(resposta)
        
        return analise
        
    except Exception as e:
        import traceback
        return _criar_analise_fallback(f"Erro técnico: {str(e)}\n{traceback.format_exc()[:300]}")

def gerar_resumo_analises(analises: list) -> dict:
    """
    Gera resumo consolidado das análises PRISMA de múltiplos artigos.
    
    Args:
        analises: Lista de dicionários com análises PRISMA de cada artigo
    
    Returns:
        Dicionário com resumo consolidado
    """
    total_artigos = len(analises)
    
    if total_artigos == 0:
        return {
            "total_artigos": 0,
            "resumo": "Nenhum artigo analisado"
        }
    
    # Calcular estatísticas
    escores = [a.get("escore_qualidade", 0) for a in analises if isinstance(a.get("escore_qualidade"), (int, float))]
    pontuacoes_prisma = [a.get("pontuacao_prisma", 0) for a in analises if isinstance(a.get("pontuacao_prisma"), int)]
    
    recomendacoes = {}
    for analise in analises:
        rec = analise.get("recomendacao", "Não definida")
        recomendacoes[rec] = recomendacoes.get(rec, 0) + 1
    
    tipos_estudo = {}
    for analise in analises:
        tipo = analise.get("tipo_estudo", "Não identificado")
        tipos_estudo[tipo] = tipos_estudo.get(tipo, 0) + 1
    
    return {
        "total_artigos": total_artigos,
        "escore_medio": sum(escores) / len(escores) if escores else 0,
        "escore_minimo": min(escores) if escores else 0,
        "escore_maximo": max(escores) if escores else 0,
        "pontuacao_prisma_media": sum(pontuacoes_prisma) / len(pontuacoes_prisma) if pontuacoes_prisma else 0,
        "recomendacoes": recomendacoes,
        "tipos_estudo": tipos_estudo,
        "artigos_por_qualidade": {
            "excelente": len([e for e in escores if e >= 9]),
            "boa": len([e for e in escores if 7 <= e < 9]),
            "regular": len([e for e in escores if 5 <= e < 7]),
            "baixa": len([e for e in escores if e < 5])
        }
    }
