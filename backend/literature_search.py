# Tentar importação relativa primeiro, depois absoluta
try:
    from .gpt_engine import gerar_resposta
except ImportError:
    try:
        from gpt_engine import gerar_resposta
    except ImportError:
        import backend.gpt_engine as gpt_engine
        gerar_resposta = gpt_engine.gerar_resposta

import requests
import json
import time

def buscar_literatura(tema: str, bases_dados: list = None) -> dict:
    """
    Busca artigos científicos nas bases de dados PubMed, LILACS e Cochrane.
    
    Args:
        tema: Tema da revisão sistemática
        bases_dados: Lista de bases para buscar (padrão: ['pubmed', 'lilacs', 'cochrane'])
    
    Returns:
        Dicionário com resultados da busca por base de dados
    """
    if bases_dados is None:
        bases_dados = ['pubmed', 'lilacs', 'cochrane']
    
    resultados = {}
    
    # Buscar no PubMed
    if 'pubmed' in bases_dados:
        resultados['pubmed'] = _buscar_pubmed(tema)
        time.sleep(1)  # Rate limiting
    
    # Buscar no LILACS
    if 'lilacs' in bases_dados:
        resultados['lilacs'] = _buscar_lilacs(tema)
        time.sleep(1)
    
    # Buscar no Cochrane
    if 'cochrane' in bases_dados:
        resultados['cochrane'] = _buscar_cochrane(tema)
        time.sleep(1)
    
    return resultados

def _buscar_pubmed(tema: str, max_results: int = 50) -> dict:
    """
    Busca artigos no PubMed usando a API E-utilities.
    """
    try:
        # Primeiro, buscar IDs dos artigos
        search_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
        params = {
            'db': 'pubmed',
            'term': tema,
            'retmax': max_results,
            'retmode': 'json',
            'sort': 'relevance'
        }
        
        response = requests.get(search_url, params=params, timeout=10)
        if response.status_code != 200:
            return {'erro': f'Erro ao buscar no PubMed: {response.status_code}', 'artigos': []}
        
        data = response.json()
        ids = data.get('esearchresult', {}).get('idlist', [])
        
        if not ids:
            return {'total': 0, 'artigos': [], 'mensagem': 'Nenhum artigo encontrado no PubMed'}
        
        # Buscar detalhes dos artigos
        fetch_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
        fetch_params = {
            'db': 'pubmed',
            'id': ','.join(ids[:20]),  # Limitar a 20 para não sobrecarregar
            'retmode': 'xml',
            'rettype': 'abstract'
        }
        
        fetch_response = requests.get(fetch_url, params=fetch_params, timeout=15)
        if fetch_response.status_code != 200:
            return {
                'total': len(ids),
                'artigos': [],
                'ids_encontrados': ids,
                'mensagem': 'IDs encontrados, mas erro ao buscar detalhes'
            }
        
        # Processar XML (simplificado - retornar IDs e usar IA para resumir)
        return {
            'total': len(ids),
            'ids_encontrados': ids[:20],
            'artigos': ids[:20],  # Retornar IDs para processamento posterior
            'mensagem': f'Encontrados {len(ids)} artigos no PubMed'
        }
        
    except Exception as e:
        return {'erro': f'Erro ao buscar no PubMed: {str(e)}', 'artigos': []}

def _buscar_lilacs(tema: str, max_results: int = 50) -> dict:
    """
    Busca artigos no LILACS usando a API.
    Nota: LILACS usa BVS (Biblioteca Virtual em Saúde) API.
    """
    try:
        # API do LILACS via BVS
        search_url = "https://lilacs.bvsalud.org/api/search"
        params = {
            'q': tema,
            'limit': max_results,
            'format': 'json'
        }
        
        response = requests.get(search_url, params=params, timeout=10)
        if response.status_code != 200:
            return {'erro': f'Erro ao buscar no LILACS: {response.status_code}', 'artigos': []}
        
        data = response.json()
        artigos = data.get('data', [])
        
        return {
            'total': len(artigos),
            'artigos': artigos[:20],
            'mensagem': f'Encontrados {len(artigos)} artigos no LILACS'
        }
        
    except Exception as e:
        # Se a API não funcionar, retornar estrutura vazia
        return {
            'total': 0,
            'artigos': [],
            'mensagem': f'LILACS temporariamente indisponível: {str(e)}',
            'nota': 'A busca será simulada pela IA baseada no tema'
        }

def _buscar_cochrane(tema: str, max_results: int = 50) -> dict:
    """
    Busca revisões sistemáticas no Cochrane Library.
    Nota: Cochrane não tem API pública gratuita, então simulamos com IA.
    """
    try:
        # Como Cochrane não tem API pública, vamos usar IA para gerar estratégia de busca
        prompt = f"""
Como especialista em busca bibliográfica, gere uma estratégia de busca otimizada para o tema:
"{tema}"

Base de dados: Cochrane Library

Forneça:
1. Termos MeSH relevantes
2. Termos de texto livre
3. Estratégia de busca combinada
4. Filtros recomendados (tipo de estudo, data, etc.)

IMPORTANTE: Responda em português brasileiro.
"""
        
        estrategia = gerar_resposta(prompt, temperatura=0.7)
        
        return {
            'total': 0,  # Não temos acesso real à API
            'estrategia_busca': estrategia,
            'mensagem': 'Estratégia de busca gerada para Cochrane Library',
            'nota': 'Cochrane Library requer acesso institucional. Estratégia de busca fornecida.'
        }
        
    except Exception as e:
        return {
            'total': 0,
            'artigos': [],
            'mensagem': f'Erro ao gerar estratégia Cochrane: {str(e)}'
        }

def gerar_resumo_busca(resultados: dict, tema: str) -> str:
    """
    Gera um resumo da busca bibliográfica usando IA.
    """
    prompt = f"""
Como especialista em revisões sistemáticas, analise os resultados da busca bibliográfica e gere um resumo estruturado.

Tema da revisão: {tema}

Resultados da busca:
{json.dumps(resultados, indent=2, ensure_ascii=False)}

Gere um resumo que inclua:
1. Total de artigos encontrados por base de dados
2. Estratégia de busca utilizada
3. Principais achados
4. Recomendações para seleção de artigos

IMPORTANTE: Responda em português brasileiro.
"""
    
    return gerar_resposta(prompt, temperatura=0.7)
