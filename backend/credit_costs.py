"""
Sistema de Cobrança de Créditos - MedQuestResearch

Este módulo centraliza os custos de créditos para cada tipo de requisição.
Os valores podem ser configurados via variáveis de ambiente.
"""

import os
from typing import Dict, Optional

# ============================================
# CUSTOS PADRÃO (valores iniciais)
# ============================================
# Estes valores podem ser ajustados posteriormente conforme necessário

DEFAULT_COSTS: Dict[str, int] = {
    # Análises críticas
    "critica": 7,                     # Análise crítica
    "critical_analysis": 7,           # Alias para critica
    
    # Pesquisa de perspectivas
    "perspectiva": 10,                 # Pesquisa de perspectivas (mais caro por usar API externa)
    "perspective_research": 10,        # Alias para perspectiva
    
    # Metanálise (mais complexo)
    "meta_analise": 12,               # Metanálise completa
    "meta_analysis": 12,              # Alias para meta_analise
    "escrever_artigo": 5,             # Escrita de seção de artigo
    "escrever_artigo_completo": 15,   # Escrita do artigo completo
    
    # Upload de PDF
    "pdf": 3,                         # Upload e processamento de PDF
}


def get_credit_cost(modulo: str) -> int:
    """
    Obtém o custo em créditos para um módulo específico.
    
    Args:
        modulo: Nome do módulo (ex: "explicar", "critica", "meta_analise")
    
    Returns:
        Custo em créditos (int)
    
    Raises:
        ValueError: Se o módulo não tiver custo configurado
    """
    # Normalizar nome do módulo (lowercase)
    modulo = modulo.lower()
    
    # Tentar obter via variável de ambiente primeiro
    env_key = f"CREDIT_COST_{modulo.upper()}"
    env_value = os.getenv(env_key)
    
    if env_value:
        try:
            return int(env_value)
        except ValueError:
            print(f"⚠️ AVISO: Valor inválido para {env_key}: {env_value}. Usando valor padrão.")
    
    # Se não encontrou na env, usar valor padrão
    if modulo in DEFAULT_COSTS:
        return DEFAULT_COSTS[modulo]
    
    # Se não encontrou, tentar encontrar por alias ou similaridade
    for key, value in DEFAULT_COSTS.items():
        if key.startswith(modulo) or modulo in key:
            return value
    
    # Se não encontrou nada, levantar erro
    raise ValueError(
        f"Módulo '{modulo}' não possui custo configurado. "
        f"Módulos disponíveis: {', '.join(DEFAULT_COSTS.keys())}"
    )


def get_all_costs() -> Dict[str, int]:
    """
    Retorna todos os custos configurados (incluindo variáveis de ambiente).
    
    Returns:
        Dicionário com todos os custos (módulo -> créditos)
    """
    costs = DEFAULT_COSTS.copy()
    
    # Sobrescrever com valores de variáveis de ambiente se existirem
    for modulo in costs.keys():
        env_key = f"CREDIT_COST_{modulo.upper()}"
        env_value = os.getenv(env_key)
        if env_value:
            try:
                costs[modulo] = int(env_value)
            except ValueError:
                print(f"⚠️ AVISO: Valor inválido para {env_key}: {env_value}")
    
    return costs


def set_credit_cost(modulo: str, custo: int) -> None:
    """
    Define o custo de um módulo (apenas em memória, não persiste).
    Útil para testes ou ajustes dinâmicos.
    
    Args:
        modulo: Nome do módulo
        custo: Custo em créditos
    """
    DEFAULT_COSTS[modulo.lower()] = custo


def validate_credit_cost(modulo: str, custo: Optional[int] = None) -> bool:
    """
    Valida se um custo é válido (deve ser > 0).
    
    Args:
        modulo: Nome do módulo
        custo: Custo a validar (opcional, se None, obtém o custo do módulo)
    
    Returns:
        True se válido, False caso contrário
    """
    if custo is None:
        try:
            custo = get_credit_cost(modulo)
        except ValueError:
            return False
    
    return custo > 0


# ============================================
# FUNÇÃO HELPER PARA USO NAS ROTAS
# ============================================

def get_cost_for_route(route_name: str) -> int:
    """
    Função helper para obter custo baseado no nome da rota.
    Normaliza o nome da rota para o formato do módulo.
    
    Args:
        route_name: Nome da rota (ex: "/critica", "critica")
    
    Returns:
        Custo em créditos
    """
    # Remover barras e prefixos comuns
    modulo = route_name.replace("/", "").replace("genapi/", "").replace("api/", "")
    
    return get_credit_cost(modulo)
