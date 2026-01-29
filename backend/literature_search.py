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
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

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
    Busca artigos no PubMed usando a API E-utilities do NCBI.
    Foca em ensaios clínicos e estudos randomizados.
    
    Args:
        tema: Tema da busca
        max_results: Número máximo de resultados (padrão: 50)
    
    Returns:
        Dicionário com resultados da busca
    """
    try:
        # Obter credenciais da API do PubMed
        api_key = os.getenv("PUBMED_API_KEY", "")
        email = os.getenv("PUBMED_EMAIL", "edesio.martins@unirv.edu.br")
        tool_name = "MedquestResearch"
        
        # Construir query focada em ensaios clínicos
        # Adicionar filtros para ensaios clínicos e estudos randomizados
        query = f"{tema} AND (Clinical Trial[ptyp] OR Randomized Controlled Trial[ptyp] OR Controlled Clinical Trial[ptyp] OR Meta-Analysis[ptyp] OR Systematic Review[ptyp])"
        
        # Primeiro, buscar IDs dos artigos
        search_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
        params = {
            'db': 'pubmed',
            'term': query,
            'retmax': max_results,
            'retmode': 'json',
            'sort': 'relevance',
            'tool': tool_name,
            'email': email
        }
        
        # Adicionar API key se disponível
        if api_key:
            params['api_key'] = api_key
        
        response = requests.get(search_url, params=params, timeout=15)
        if response.status_code != 200:
            return {
                'erro': f'Erro ao buscar no PubMed: {response.status_code}',
                'artigos': [],
                'mensagem': f'Erro HTTP {response.status_code}'
            }
        
        data = response.json()
        ids = data.get('esearchresult', {}).get('idlist', [])
        total_found = int(data.get('esearchresult', {}).get('count', 0))
        
        if not ids:
            return {
                'total': 0,
                'artigos': [],
                'mensagem': 'Nenhum ensaio clínico encontrado no PubMed para este tema',
                'query_usada': query
            }
        
        # Buscar detalhes dos artigos (limitar a 20 para não sobrecarregar)
        fetch_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
        fetch_params = {
            'db': 'pubmed',
            'id': ','.join(ids[:20]),
            'retmode': 'xml',
            'rettype': 'abstract',
            'tool': tool_name,
            'email': email
        }
        
        if api_key:
            fetch_params['api_key'] = api_key
        
        fetch_response = requests.get(fetch_url, params=fetch_params, timeout=20)
        
        artigos_detalhados = []
        if fetch_response.status_code == 200:
            # Processar XML básico (extrair título, autores, ano, abstract)
            import xml.etree.ElementTree as ET
            try:
                root = ET.fromstring(fetch_response.content)
                for article in root.findall('.//PubmedArticle'):
                    try:
                        # Extrair título
                        title_elem = article.find('.//ArticleTitle')
                        title = title_elem.text if title_elem is not None else "Sem título"
                        
                        # Extrair autores
                        authors = []
                        for author in article.findall('.//Author'):
                            last_name = author.find('LastName')
                            first_name = author.find('ForeName')
                            if last_name is not None:
                                author_name = last_name.text
                                if first_name is not None:
                                    author_name += f" {first_name.text}"
                                authors.append(author_name)
                        
                        # Extrair ano de publicação
                        pub_date = article.find('.//PubDate/Year')
                        year = pub_date.text if pub_date is not None else "N/A"
                        
                        # Extrair abstract
                        abstract_parts = []
                        for abstract_text in article.findall('.//AbstractText'):
                            if abstract_text.text:
                                abstract_parts.append(abstract_text.text)
                        abstract = " ".join(abstract_parts) if abstract_parts else "Sem resumo disponível"
                        
                        # Extrair DOI
                        doi_elem = article.find('.//ELocationID[@EIdType="doi"]')
                        doi = doi_elem.text if doi_elem is not None else None
                        
                        # Extrair PMID
                        pmid_elem = article.find('.//PMID')
                        pmid = pmid_elem.text if pmid_elem is not None else None
                        
                        artigos_detalhados.append({
                            'pmid': pmid,
                            'title': title,
                            'authors': authors[:5],  # Limitar a 5 primeiros autores
                            'year': year,
                            'abstract': abstract[:500] if len(abstract) > 500 else abstract,  # Limitar abstract
                            'doi': doi
                        })
                    except Exception as e:
                        # Continuar mesmo se um artigo falhar
                        continue
            except ET.ParseError:
                # Se não conseguir parsear XML, retornar apenas IDs
                pass
        
        # Rate limiting - aguardar antes de próxima requisição
        time.sleep(0.34)  # NCBI recomenda não mais que 3 requisições/segundo
        
        return {
            'total': total_found,
            'ids_encontrados': ids[:20],
            'artigos': artigos_detalhados if artigos_detalhados else ids[:20],
            'mensagem': f'Encontrados {total_found} ensaios clínicos no PubMed (detalhes de {len(artigos_detalhados)} artigos)',
            'query_usada': query,
            'api_key_utilizada': 'Sim' if api_key else 'Não'
        }
        
    except requests.exceptions.Timeout:
        return {
            'erro': 'Timeout ao buscar no PubMed',
            'artigos': [],
            'mensagem': 'A requisição demorou muito. Tente novamente.'
        }
    except Exception as e:
        import traceback
        return {
            'erro': f'Erro ao buscar no PubMed: {str(e)}',
            'artigos': [],
            'mensagem': f'Erro: {str(e)}',
            'traceback': traceback.format_exc() if __debug__ else None
        }

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
