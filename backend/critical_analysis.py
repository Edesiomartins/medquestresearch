# Tentar importação relativa primeiro, depois absoluta
try:
    from .gpt_engine import gerar_resposta
except ImportError:
    try:
        from gpt_engine import gerar_resposta
    except ImportError:
        import backend.gpt_engine as gpt_engine
        gerar_resposta = gpt_engine.gerar_resposta

# Mapeamento de focos de análise para prompts específicos (simplificados para velocidade)
PROMPTS_POR_FOCO = {
    "metodologia": """
Analise CRITICAMENTE a METODOLOGIA do artigo científico abaixo.
Responda em português brasileiro, em formato estruturado e conciso:

1. Desenho do estudo (2–4 frases)
2. Amostragem e tamanho amostral (2–4 frases)
3. Procedimentos / intervenção / controles (2–4 frases)
4. Análise estatística (2–4 frases)
5. Principais vieses e limitações (2–4 frases)

Não repita o texto original, não faça resumo narrativo geral: foque na avaliação crítica.

Texto do artigo:
{texto_artigo}
""",
    "validade": """
Avalie CRITICAMENTE a validade interna e externa do estudo. Foque em: controle de variáveis, vieses, causalidade, generalização, representatividade da amostra.

IMPORTANTE: Responda SEMPRE em português brasileiro, mesmo que o artigo esteja em inglês.

Texto: {texto_artigo}
""",
    "confiabilidade": """
Avalie CRITICAMENTE a confiabilidade e reprodutibilidade. Foque em: consistência dos resultados, confiabilidade das medidas, concordância entre avaliadores, precisão dos instrumentos.

IMPORTANTE: Responda SEMPRE em português brasileiro, mesmo que o artigo esteja em inglês.

Texto: {texto_artigo}
""",
    "vieses": """
Identifique e analise CRITICAMENTE vieses e limitações: seleção, informação, confusão, publicação. Como afetam os resultados?

IMPORTANTE: Responda SEMPRE em português brasileiro, mesmo que o artigo esteja em inglês.

Texto: {texto_artigo}
""",
    "amostra": """
Avalie CRITICAMENTE amostragem e tamanho amostral: adequação do tamanho, método (probabilística/não-probabilística), representatividade, critérios de inclusão/exclusão, perdas.

IMPORTANTE: Responda SEMPRE em português brasileiro, mesmo que o artigo esteja em inglês.

Texto: {texto_artigo}
""",
    "estatistica": """
Avalie CRITICAMENTE a análise estatística: métodos utilizados, testes escolhidos, pressupostos, significância, interpretação, possíveis erros.

IMPORTANTE: Responda SEMPRE em português brasileiro, mesmo que o artigo esteja em inglês.

Texto: {texto_artigo}
""",
    "etico": """
Avalie CRITICAMENTE aspectos éticos: aprovação de comitê, consentimento informado, confidencialidade, riscos/benefícios, conflitos de interesse.

IMPORTANTE: Responda SEMPRE em português brasileiro, mesmo que o artigo esteja em inglês.

Texto: {texto_artigo}
""",
    "relevancia": """
Avalie CRITICAMENTE a relevância científica e clínica: impacto prático, contribuição ao conhecimento, significância clínica vs estatística, aplicabilidade.

IMPORTANTE: Responda SEMPRE em português brasileiro, mesmo que o artigo esteja em inglês.

Texto: {texto_artigo}
""",
    "geral": """
Realize uma ANÁLISE CRÍTICA ABRANGENTE do artigo científico abaixo.
Responda em português brasileiro em, no máximo, 7 blocos numerados:

1. Desenho do estudo (2–3 frases)
2. Amostragem e participantes (2–3 frases)
3. Métodos / intervenção / instrumentos (2–3 frases)
4. Análise estatística (2–3 frases)
5. Vieses e limitações (2–3 frases)
6. Aspectos éticos relevantes (1–3 frases, se houver)
7. Relevância clínica/científica e implicações (2–3 frases)

Se alguma informação não estiver clara no texto, declare explicitamente que não foi possível avaliar.
Não reescreva o artigo; foque em julgamento crítico.

Texto do artigo:
{texto_artigo}
"""
}

def aplicar_leitura_critica(texto_artigo: str, foco_analise: str = "geral") -> str:
    """
    Realiza uma análise crítica de um texto de artigo científico com foco específico.
    NOTA: Esta função é chamada diretamente, SEM chunking, para análise focada e rápida.
    """
    # Limitar texto para evitar chamadas muito longas (já limitado no processar_job_critica)
    texto_artigo = texto_artigo[:3000]
    
    # Obter prompt específico para o foco escolhido, ou usar o geral
    prompt_template = PROMPTS_POR_FOCO.get(foco_analise, PROMPTS_POR_FOCO["geral"])
    prompt = prompt_template.format(texto_artigo=texto_artigo)
    
    # Temperatura reduzida (0.7) para respostas mais rápidas e focadas
    resposta = gerar_resposta(prompt, temperatura=0.7)
    return resposta
