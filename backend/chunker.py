# ============================================
# ✅ CHUNKER.PY - DIVISÃO INTELIGENTE DE TEXTOS
# ============================================

try:
    import tiktoken  # pyright: ignore[reportMissingImports]
    _HAS_TIKTOKEN = True
except ImportError:
    _HAS_TIKTOKEN = False

from typing import List, Callable, Any

# Inicializar tokenizer da OpenAI (se disponível)
if _HAS_TIKTOKEN:
    encoding = tiktoken.encoding_for_model("gpt-4o")
else:
    encoding = None

def estimate_tokens(texto: str, model="gpt-4o-mini"):
    if not _HAS_TIKTOKEN:
        # fallback simples: ~4 caracteres por token
        return max(1, len(texto) // 4)

    enc = tiktoken.encoding_for_model(model)
    return len(enc.encode(texto))


def chunk_text(text: str, chunk_size: int = 3000, overlap: int = 500) -> List[str]:
    """
    Divide texto em chunks com sobreposição.
    
    Args:
        text: Texto a dividir
        chunk_size: Tamanho máximo do chunk em tokens (padrão: 3000)
        overlap: Sobreposição entre chunks em tokens (padrão: 500)
    
    Returns:
        Lista de chunks
    """
    if not _HAS_TIKTOKEN:
        # Fallback: dividir por caracteres (~4 chars por token)
        char_size = chunk_size * 4
        char_overlap = overlap * 4
        chunks = []
        start = 0
        while start < len(text):
            end = min(start + char_size, len(text))
            chunks.append(text[start:end])
            start = end - char_overlap
            if start >= len(text):
                break
        return chunks
    
    tokens = encoding.encode(text)
    chunks = []
    
    start = 0
    while start < len(tokens):
        end = min(start + chunk_size, len(tokens))
        chunk_tokens = tokens[start:end]
        chunk_text = encoding.decode(chunk_tokens)
        chunks.append(chunk_text)
        
        # Avançar com sobreposição
        start = end - overlap
        if start >= len(tokens):
            break
    
    return chunks


def process_chunks(
    text: str,
    process_func: Callable[[str], str],
    chunk_size: int = 3000,
    overlap: int = 500
) -> List[str]:
    """
    Processa texto em chunks usando uma função.
    
    Args:
        text: Texto a processar
        process_func: Função que processa cada chunk
        chunk_size: Tamanho do chunk em tokens
        overlap: Sobreposição em tokens
    
    Returns:
        Lista de respostas processadas
    """
    chunks = chunk_text(text, chunk_size, overlap)
    results = []
    
    for chunk in chunks:
        result = process_func(chunk)
        results.append(result)
    
    return results


def combine_responses(responses: List[str], separator: str = "\n\n---\n\n") -> str:
    """
    Combina múltiplas respostas em uma única.
    
    Args:
        responses: Lista de respostas
        separator: Separador entre respostas
    
    Returns:
        Texto combinado
    """
    return separator.join(responses)

