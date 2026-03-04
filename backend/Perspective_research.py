# Tentar importação relativa primeiro, depois absoluta
try:
    from .gpt_engine import gerar_resposta
    from .pubmed_client import buscar_artigos_pubmed
except ImportError:
    try:
        from gpt_engine import gerar_resposta
        from pubmed_client import buscar_artigos_pubmed
    except ImportError:
        import backend.gpt_engine as gpt_engine
        from backend.pubmed_client import buscar_artigos_pubmed  # type: ignore[reportMissingImports]
        gerar_resposta = gpt_engine.gerar_resposta


def buscar_perspectivas_pubmed(texto_artigo: str, tema_foco: str = "") -> str:
    """
    Gera uma perspectiva baseada na literatura real do PubMed.

    Passos:
    1. Extrai/usa um tema curto.
    2. Busca artigos relacionados no PubMed (via pubmed_client).
    3. Pede à IA para comparar o artigo-alvo com esses estudos.
    """
    # Limitar texto para evitar chamadas muito longas
    texto_artigo = (texto_artigo or "")[:4000]

    # 1) Determinar tema/foco
    tema = (tema_foco or "").strip()
    if not tema:
        try:
            tema_prompt = f"Em UMA frase curta, em português, resuma o tema principal do artigo abaixo:\n\n{texto_artigo[:1500]}"
            tema = gerar_resposta(tema_prompt, temperatura=0.2, max_output_tokens=60).strip()
        except Exception:
            tema = ""

    # 2) Buscar artigos no PubMed
    query = tema or texto_artigo[:200]
    artigos = buscar_artigos_pubmed(query, max_results=5)

    if not artigos:
        # Fallback: comportamento antigo (sem contexto PubMed explícito)
        prompt = f"""
Você é um pesquisador em medicina baseada em evidências.
Seu objetivo é contextualizar criticamente o ARTIGO-ALVO em relação à literatura
recente disponível na base PubMed/MEDLINE.

Responda EM PORTUGUÊS BRASILEIRO, em no máximo 5 blocos numerados:
1) Estado atual da evidência sobre o tema.
2) Como o artigo-alvo se posiciona em relação a essa evidência.
3) Convergências e divergências com estudos semelhantes.
4) Lacunas na literatura e perguntas ainda em aberto.
5) Implicações práticas e linhas de pesquisa futuras.

Texto do artigo (trecho relevante):
{texto_artigo}
"""
        return gerar_resposta(prompt, temperatura=0.6)

    # 3) Montar contexto dos estudos encontrados
    contexto_estudos = []
    for i, art in enumerate(artigos, start=1):
        contexto_estudos.append(
            f"Estudo {i}: {art.get('titulo','(sem título)')} "
            f"({art.get('ano','s/d')}, {art.get('journal','journal não informado')})."
        )
    contexto_str = "\n".join(contexto_estudos)

    # 4) Prompt final combinando artigo-alvo + estudos PubMed
    prompt_final = f"""
Você é um pesquisador em medicina baseada em evidências.
Seu objetivo é contextualizar criticamente o ARTIGO-ALVO em relação à literatura
recente disponível na base PubMed/MEDLINE (artigos de acesso livre).

TEMA/Foco principal: {tema or '(não claramente definido, deduza a partir do texto)'}

ESTUDOS RELEVANTES ENCONTRADOS NO PUBMED (títulos e journals):
{contexto_str}

TAREFA (responda EM PORTUGUÊS BRASILEIRO, de forma estruturada e concisa):
1) Estado atual da evidência no PubMed sobre esse tema (o que já se sabe em linhas gerais).
2) Como o artigo-alvo se posiciona em relação a essa evidência (confirma, diverge, acrescenta, é preliminar?).
3) Principais convergências e divergências com esses estudos.
4) Lacunas na literatura e perguntas ainda em aberto.
5) Implicações práticas e linhas de pesquisa futuras sugeridas.

LIMITAÇÕES:
- Não invente dados específicos (número de pacientes, p‑values) se não puder inferir com segurança.
- Quando algo não puder ser inferido com segurança, diga explicitamente que a evidência é limitada ou indireta.

ARTIGO-ALVO (trecho relevante):
{texto_artigo}
"""
    return gerar_resposta(prompt_final, temperatura=0.6)
