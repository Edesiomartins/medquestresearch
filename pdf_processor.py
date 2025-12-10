import fitz  # PyMuPDF

def extrair_texto_pdf(caminho_pdf, max_chars_por_chunk=5000):
    doc = fitz.open(caminho_pdf)
    texto_completo = ""
    
    for pagina in doc:
        pagina_texto = pagina.get_text()
        texto_completo += pagina_texto + "\n"  # Preserva quebras
    
    doc.close()
    
    # Dividir em chunks para PDFs longos
    chunks = []
    while texto_completo:
        chunk = texto_completo[:max_chars_por_chunk]
        chunks.append(chunk)
        texto_completo = texto_completo[max_chars_por_chunk:]
    
    if len(chunks) > 1:
        chunks[-1] += "\n[Chunk final resumido]"  # Marca último
    
    return chunks  # Lista de chunks em vez de string única
