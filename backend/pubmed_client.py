"""
Cliente simples para buscar artigos no PubMed via E-utilities (API oficial do NCBI).

Usado pela rota de Perspectiva para contextualizar o artigo-alvo na literatura real.
"""

import os
from typing import List, Dict

import requests


EUTILS_BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"


def _build_common_params() -> Dict[str, str]:
    """Parâmetros comuns (email e api_key) recomendados pelo NCBI."""
    params: Dict[str, str] = {}
    email = os.getenv("PUBMED_EMAIL")
    api_key = os.getenv("PUBMED_API_KEY")
    if email:
        params["email"] = email
    if api_key:
        params["api_key"] = api_key
    return params


def buscar_artigos_pubmed(query: str, max_results: int = 5) -> List[Dict[str, str]]:
    """
    Busca artigos no PubMed pelo termo informado e retorna lista com título, ano, journal e (quando possível) resumo curto.

    Não traz o texto completo, apenas metadados suficientes para a IA gerar uma perspectiva.
    """
    query = (query or "").strip()
    if not query:
        return []

    params = {
        "db": "pubmed",
        "term": query,
        "retmode": "json",
        "retmax": str(max_results),
        "sort": "bestmatch",
    }
    params.update(_build_common_params())

    try:
        r = requests.get(f"{EUTILS_BASE}/esearch.fcgi", params=params, timeout=10)
        r.raise_for_status()
        data = r.json()
        id_list = data.get("esearchresult", {}).get("idlist", [])
        if not id_list:
            return []
    except Exception as e:
        print(f"[PUBMED] Erro na esearch: {e}")
        return []

    # Buscar resumos/títulos via esummary (mais leve que efetch + XML)
    summary_params = {
        "db": "pubmed",
        "id": ",".join(id_list),
        "retmode": "json",
    }
    summary_params.update(_build_common_params())

    try:
        r = requests.get(f"{EUTILS_BASE}/esummary.fcgi", params=summary_params, timeout=10)
        r.raise_for_status()
        data = r.json()
        result = data.get("result", {})
    except Exception as e:
        print(f"[PUBMED] Erro na esummary: {e}")
        return []

    artigos: List[Dict[str, str]] = []
    for pid in id_list:
        item = result.get(pid)
        if not item:
            continue
        titulo = item.get("title", "").strip()
        journal = item.get("fulljournalname") or item.get("source") or ""
        pubdate = (item.get("pubdate") or "").split(" ")[0]  # ano ou ano-mês
        ano = ""
        if pubdate:
            ano = pubdate.split("-")[0]

        # Alguns registros têm "elocationid" com DOI, etc. Não forçamos resumo aqui.
        artigos.append(
            {
                "titulo": titulo,
                "journal": journal,
                "ano": ano,
            }
        )

    return artigos

