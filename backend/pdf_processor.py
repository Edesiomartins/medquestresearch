import os
import fitz  # PyMuPDF
import re
import unicodedata

# Tentar importação relativa primeiro, depois absoluta
try:
    from .gpt_engine import gerar_resposta
except ImportError:
    try:
        from gpt_engine import gerar_resposta
    except ImportError:
        import backend.gpt_engine as gpt_engine
        gerar_resposta = gpt_engine.gerar_resposta


def _traduzir_chunk_qwen(chunk, max_tokens=2000):
    """Traduz um chunk para português usando Groq + Qwen quando GROQ_API_KEY está definida."""
    groq_key = os.getenv("GROQ_API_KEY")
    if groq_key:
        try:
            from groq import Groq
            client = Groq(api_key=groq_key)
            model = os.getenv("GROQ_MODEL_TRADUCAO", "qwen2.5-7b-instruct")
            prompt = f"""Traduza o seguinte texto científico para português brasileiro. Mantenha termos técnicos e nomes próprios. Seja preciso e mantenha a formatação. Responda apenas com a tradução.

Texto:
{chunk}

Tradução em português brasileiro:"""
            r = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=max_tokens,
            )
            if r.choices and r.choices[0].message.content:
                return r.choices[0].message.content.strip()
        except Exception as e:
            print(f"[PDF] Groq/Qwen tradução falhou: {e}, usando fallback")
    return gerar_resposta(
        f"Traduza para português brasileiro (mantenha termos técnicos e formatação). Responda só com a tradução:\n\n{chunk}",
        temperatura=0.3,
    )

def extrair_texto_pdf(caminho_pdf, max_chars_por_chunk=5000):
    doc = fitz.open(caminho_pdf)
    texto_completo = ""
    
    # Tentar diferentes métodos de extração para melhor qualidade
    for pagina in doc:
        # Método 1: Tentar extração com dict (preserva melhor formatação)
        try:
            blocks = pagina.get_text("dict")
            pagina_texto = ""
            for block in blocks["blocks"]:
                if "lines" in block:
                    for line in block["lines"]:
                        for span in line["spans"]:
                            # Extrair texto preservando espaços
                            texto_span = span.get("text", "")
                            # Tentar preservar acentos usando a fonte se disponível
                            pagina_texto += texto_span + " "
                        pagina_texto += "\n"
        except:
            # Fallback: Método padrão
            pagina_texto = pagina.get_text()
        
        # Se ainda estiver vazio, usar método padrão
        if not pagina_texto or len(pagina_texto.strip()) == 0:
            pagina_texto = pagina.get_text()
        
        texto_completo += pagina_texto + "\n"
    
    doc.close()
    
    # Normalizar encoding primeiro
    try:
        # Garantir que o texto está em UTF-8
        if isinstance(texto_completo, bytes):
            texto_completo = texto_completo.decode('utf-8', errors='ignore')
        else:
            texto_completo = texto_completo.encode('utf-8', errors='ignore').decode('utf-8')
    except:
        pass
    
    # Corrigir acentos separados antes de formatar (múltiplas passadas)
    texto_completo = _corrigir_acentos_separados(texto_completo)
    texto_completo = _corrigir_acentos_separados(texto_completo)  # Segunda passada para casos aninhados
    
    # Normalizar e limpar formatação
    texto_completo = _formatar_texto(texto_completo)
    
    # Manter texto original na extração; versão em português é gerada na API
    # texto_completo = _traduzir_para_portugues(texto_completo)  # desativado: retornamos original + pt na rota
    
    # Dividir em chunks para PDFs longos
    chunks = []
    while texto_completo:
        chunk = texto_completo[:max_chars_por_chunk]
        chunks.append(chunk)
        texto_completo = texto_completo[max_chars_por_chunk:]
    
    if len(chunks) > 1:
        chunks[-1] += "\n[Chunk final resumido]"
    
    return chunks

def _corrigir_acentos_separados(texto):
    """
    Corrige acentos que foram separados dos caracteres durante a extração do PDF.
    Exemplos: "Ede ´sio" → "Edésio", "Sau ´ de" → "Saúde", "Cie ˆ ncias" → "Ciências"
    Também corrige ligaduras tipográficas: "ﬁ" → "fi", "ﬂ" → "fl", "Doenc ¸ as" → "Doenças"
    
    Usa múltiplas estratégias para garantir máxima cobertura.
    """
    # PRIMEIRO: Corrigir ligaduras tipográficas comuns (ﬁ, ﬂ, ﬀ, ﬃ, ﬄ, etc.)
    ligaduras = {
        'ﬁ': 'fi',   # fi ligature (U+FB01)
        'ﬂ': 'fl',   # fl ligature (U+FB02)
        'ﬀ': 'ff',   # ff ligature (U+FB00)
        'ﬃ': 'ffi',  # ffi ligature (U+FB03)
        'ﬄ': 'ffl',  # ffl ligature (U+FB04)
        'ﬅ': 'ft',   # ft ligature (U+FB05)
        'ﬆ': 'st',   # st ligature (U+FB06)
    }
    for ligadura, substituicao in ligaduras.items():
        texto = texto.replace(ligadura, substituicao)
    
    # SEGUNDO: Corrigir cedilhas separadas (ex: "Doenc ¸ as" → "Doenças", "Cl ı ´ nica" → "Clínica")
    # Cedilha (¸) - U+00B8
    # Padrão: c/C + espaço(s) + ¸ + espaço(s) + letra
    def corrigir_cedilha(match):
        c_letra = match.group(1)
        proxima_letra = match.group(2)
        # Se a próxima letra é vogal, adiciona cedilha ao c
        if proxima_letra.lower() in 'aeiou':
            return ('ç' if c_letra == 'c' else 'Ç') + proxima_letra
        return c_letra + proxima_letra
    
    texto = re.sub(r'([cC])\s*¸\s*([a-zA-Z])', corrigir_cedilha, texto)
    # Padrão: c/C + ¸ + espaço(s) + letra
    texto = re.sub(r'([cC])¸\s+([a-zA-Z])', corrigir_cedilha, texto)
    # Padrão: c/C + espaço(s) + ¸ (final de palavra ou antes de espaço/pontuação)
    texto = re.sub(r'([cC])\s*¸\s*([^a-zA-Z]|$)', lambda m: ('ç' if m.group(1) == 'c' else 'Ç') + (m.group(2) if m.group(2) else ''), texto)
    
    # Correções específicas para cedilhas comuns em português
    correcoes_cedilha = {
        r'Doenc\s*¸\s*as': 'Doenças',
        r'doenc\s*¸\s*as': 'doenças',
        r'([cC])onc\s*¸\s*o': r'\1onço',
        r'([cC])alc\s*¸\s*o': r'\1alço',
        r'([cC])orc\s*¸\s*o': r'\1orço',
        r'([cC])ruc\s*¸\s*o': r'\1ruço',
        r'([cC])orc\s*¸\s*ao': r'\1orção',
        r'([cC])alc\s*¸\s*ao': r'\1alção',
    }
    for padrao, correcao in correcoes_cedilha.items():
        texto = re.sub(padrao, correcao, texto, flags=re.IGNORECASE)
    # Mapeamento completo de letras para versões acentuadas
    acento_agudo = {'a': 'á', 'e': 'é', 'i': 'í', 'o': 'ó', 'u': 'ú',
                    'A': 'Á', 'E': 'É', 'I': 'Í', 'O': 'Ó', 'U': 'Ú'}
    acento_circunflexo = {'a': 'â', 'e': 'ê', 'o': 'ô',
                          'A': 'Â', 'E': 'Ê', 'O': 'Ô'}
    til = {'a': 'ã', 'o': 'õ', 'A': 'Ã', 'O': 'Õ'}
    
    # Dicionário de mapeamento de acentos Unicode para caracteres
    # Inclui diferentes representações do mesmo acento
    acentos_unicode = {
        # Acento agudo - diferentes representações
        '\u00B4': '´',  # ACUTE ACCENT
        '\u02CA': '´',  # MODIFIER LETTER ACUTE ACCENT
        '\u0301': '´',  # COMBINING ACUTE ACCENT
        # Acento circunflexo
        '\u02C6': 'ˆ',  # MODIFIER LETTER CIRCUMFLEX ACCENT
        '\u0302': 'ˆ',  # COMBINING CIRCUMFLEX ACCENT
        # Til
        '\u0303': '̃',  # COMBINING TILDE
        '\u02DC': '̃',  # SMALL TILDE
    }
    
    # Normalizar todos os tipos de acentos para uma representação única
    for unicode_char, normalizado in acentos_unicode.items():
        texto = texto.replace(unicode_char, normalizado)
    
    # ESTRATÉGIA 1: Padrão letra + espaço(s) + acento + espaço(s) + letra
    # Ex: "Ede ´sio" → "Edésio", "Sau ´ de" → "Saúde"
    def corrigir_padrao_acento_entre_letras(match):
        letra_antes = match.group(1)
        acento = match.group(2)
        letra_depois = match.group(3)
        
        # Tenta primeiro com a letra anterior (caso mais comum em português)
        if acento == '´' and letra_antes.lower() in acento_agudo:
            return acento_agudo.get(letra_antes, letra_antes) + letra_depois
        elif acento == 'ˆ' and letra_antes.lower() in acento_circunflexo:
            return acento_circunflexo.get(letra_antes, letra_antes) + letra_depois
        elif acento == '̃' and letra_antes.lower() in til:
            return til.get(letra_antes, letra_antes) + letra_depois
        
        # Se não funcionou, tenta com a letra posterior
        if acento == '´' and letra_depois.lower() in acento_agudo:
            return letra_antes + acento_agudo.get(letra_depois, letra_depois)
        elif acento == 'ˆ' and letra_depois.lower() in acento_circunflexo:
            return letra_antes + acento_circunflexo.get(letra_depois, letra_depois)
        elif acento == '̃' and letra_depois.lower() in til:
            return letra_antes + til.get(letra_depois, letra_depois)
        
        return match.group(0)
    
    # Aplicar correção para padrão entre letras (com espaços opcionais)
    texto = re.sub(r"([a-zA-Z])\s*([´ˆ̃])\s*([a-zA-Z])", corrigir_padrao_acento_entre_letras, texto)
    
    # ESTRATÉGIA 2: Padrão letra + acento + espaço(s) + letra (sem espaço antes do acento)
    texto = re.sub(r"([a-zA-Z])([´ˆ̃])\s+([a-zA-Z])", corrigir_padrao_acento_entre_letras, texto)
    
    # ESTRATÉGIA 3: Padrão letra + espaço(s) + acento (final de palavra ou antes de espaço/pontuação)
    def corrigir_acento_final(match):
        letra = match.group(1)
        acento = match.group(2)
        if acento == '´' and letra.lower() in acento_agudo:
            return acento_agudo.get(letra, letra)
        elif acento == 'ˆ' and letra.lower() in acento_circunflexo:
            return acento_circunflexo.get(letra, letra)
        elif acento == '̃' and letra.lower() in til:
            return til.get(letra, letra)
        return match.group(0)
    
    texto = re.sub(r"([a-zA-Z])\s*([´ˆ̃])\s*([^a-zA-Z]|$)", corrigir_acento_final, texto)
    
    # ESTRATÉGIA 4: Correções específicas para padrões comuns (mais agressiva)
    correcoes_especificas = {
        # Padrões com acento agudo
        r"Ede\s*´\s*sio": "Edésio",
        r"Ede\s*´": "Edé",
        r"Sau\s*´\s*de": "Saúde",
        r"Sau\s*´": "Saú",
        r"Goia\s*´\s*s": "Goiás",
        r"Goia\s*´": "Goiá",
        r"Laborato\s*´\s*rio": "Laboratório",
        r"Laborato\s*´": "Laborató",
        r"Pu\s*´\s*blica": "Pública",
        r"Pu\s*´": "Pú",
        r"Biolo\s*´\s*gicas": "Biológicas",
        r"Biolo\s*´": "Bioló",
        r"Tropical\s*´": "Tropical",
        r"Pu\s*´\s*blica": "Pública",
        # Padrões com acento circunflexo
        r"Cie\s*ˆ\s*ncias": "Ciências",
        r"Cie\s*ˆ": "Ciê",
        r"Goia\s*ˆ\s*nia": "Goiânia",
        r"Goia\s*ˆ": "Goiâ",
        # Padrões com til
        r"na\s*̃\s*o": "não",
        r"na\s*̃": "nã",
        r"ca\s*̃\s*o": "cão",
        r"pa\s*̃\s*o": "pão",
        r"co\s*̃\s*o": "côo",
    }
    
    # Aplicar correções específicas (case-insensitive)
    for padrao, correcao in correcoes_especificas.items():
        texto = re.sub(padrao, correcao, texto, flags=re.IGNORECASE)
    
    # ESTRATÉGIA 5: Corrigir acentos separados em padrões específicos do texto fornecido
    # Ex: "Cl ı ´ nica" → "Clínica" (i + espaço + ´)
    # Corrigir padrões onde o acento está separado do i
    texto = re.sub(r'([iI])\s+´\s*([a-zA-Z])', lambda m: ('í' if m.group(1) == 'i' else 'Í') + m.group(2), texto)
    texto = re.sub(r'([iI])\s*´\s+([a-zA-Z])', lambda m: ('í' if m.group(1) == 'i' else 'Í') + m.group(2), texto)
    # Corrigir padrão específico: "ı ´" → "í" (i sem ponto + acento agudo)
    texto = re.sub(r'ı\s*´', 'í', texto)
    texto = re.sub(r'I\s*´', 'Í', texto)
    # Corrigir outros padrões comuns de acentos separados
    texto = re.sub(r'([aA])\s+´\s*([a-zA-Z])', lambda m: ('á' if m.group(1) == 'a' else 'Á') + m.group(2), texto)
    texto = re.sub(r'([eE])\s+´\s*([a-zA-Z])', lambda m: ('é' if m.group(1) == 'e' else 'É') + m.group(2), texto)
    texto = re.sub(r'([oO])\s+´\s*([a-zA-Z])', lambda m: ('ó' if m.group(1) == 'o' else 'Ó') + m.group(2), texto)
    texto = re.sub(r'([uU])\s+´\s*([a-zA-Z])', lambda m: ('ú' if m.group(1) == 'u' else 'Ú') + m.group(2), texto)
    
    # ESTRATÉGIA 6: Normalizar Unicode (NFD → NFC)
    # Isso garante que acentos combinados estejam corretos
    texto = unicodedata.normalize('NFC', texto)
    
    # ESTRATÉGIA 7: Limpar espaços duplos que possam ter sido criados
    texto = re.sub(r'\s+', ' ', texto)
    
    return texto

def _formatar_texto(texto):
    """
    Formata o texto extraído do PDF para melhor legibilidade.
    """
    # Remover múltiplas quebras de linha consecutivas (mais de 2)
    texto = re.sub(r'\n{3,}', '\n\n', texto)
    
    # Remover espaços em branco no início e fim de cada linha
    linhas = [linha.strip() for linha in texto.split('\n')]
    
    # Remover linhas vazias consecutivas
    linhas_formatadas = []
    linha_anterior_vazia = False
    for linha in linhas:
        if linha:
            linhas_formatadas.append(linha)
            linha_anterior_vazia = False
        elif not linha_anterior_vazia:
            # Permite uma linha vazia entre parágrafos
            linhas_formatadas.append('')
            linha_anterior_vazia = True
    
    # Juntar linhas
    texto_formatado = '\n'.join(linhas_formatadas)
    
    # Normalizar espaços múltiplos dentro das linhas
    texto_formatado = re.sub(r' +', ' ', texto_formatado)
    
    # Juntar linhas que foram quebradas incorretamente no PDF
    # Linhas que não terminam com pontuação provavelmente foram quebradas
    linhas = texto_formatado.split('\n')
    linhas_finais = []
    i = 0
    while i < len(linhas):
        linha_atual = linhas[i]
        
        if not linha_atual:
            # Linha vazia - mantém para separar parágrafos
            linhas_finais.append('')
            i += 1
            continue
        
        # Se a linha não termina com pontuação e não está vazia
        if linha_atual and linha_atual[-1] not in '.!?:;':
            # Tenta juntar com a próxima linha se ela existir e não estiver vazia
            if i + 1 < len(linhas) and linhas[i + 1]:
                proxima_linha = linhas[i + 1]
                primeira_letra_proxima = proxima_linha[0] if proxima_linha else ''
                
                # Condições para juntar linhas:
                # 1. Linha atual termina com hífen (palavra quebrada)
                # 2. Linha atual é curta e próxima não começa com maiúscula
                # 3. Ambas são curtas e próxima não começa com número ou maiúscula isolada
                deve_juntar = False
                
                if linha_atual.endswith('-'):
                    # Palavra quebrada - sempre junta
                    deve_juntar = True
                    linha_atual = linha_atual.rstrip('-')  # Remove o hífen
                elif len(linha_atual) < 70:
                    # Linha curta - verifica contexto
                    if not primeira_letra_proxima.isupper():
                        # Próxima não começa com maiúscula - provavelmente continuação
                        deve_juntar = True
                    elif len(proxima_linha) < 70 and not proxima_linha[0].isdigit():
                        # Ambas curtas e próxima não é número - pode ser continuação
                        # Mas verifica se não é início de nova frase
                        if i + 2 < len(linhas) and not linhas[i + 2]:
                            # Há uma linha vazia depois - provavelmente é título quebrado
                            deve_juntar = True
                
                if deve_juntar:
                    # Junta as linhas com espaço
                    linha_atual = linha_atual + ' ' + proxima_linha
                    i += 1  # Pula a próxima linha já que foi juntada
        
        linhas_finais.append(linha_atual)
        i += 1
    
    texto_formatado = '\n'.join(linhas_finais)
    
    # Limpar novamente múltiplas quebras de linha
    texto_formatado = re.sub(r'\n{3,}', '\n\n', texto_formatado)
    
    return texto_formatado.strip()

def _traduzir_para_portugues(texto):
    """
    Traduz o texto extraído do PDF para português brasileiro se estiver em inglês.
    Usa detecção simples baseada em palavras comuns em inglês.
    """
    # Detectar se o texto está principalmente em inglês
    # Contar palavras comuns em inglês vs português
    palavras_ingles = ['the', 'and', 'of', 'to', 'in', 'for', 'is', 'are', 'was', 'were', 'this', 'that', 'with', 'from', 'by', 'as', 'an', 'be', 'been', 'have', 'has', 'had', 'will', 'would', 'could', 'should']
    palavras_portugues = ['o', 'a', 'os', 'as', 'de', 'do', 'da', 'dos', 'das', 'em', 'no', 'na', 'nos', 'nas', 'para', 'por', 'com', 'sem', 'que', 'qual', 'quais', 'é', 'são', 'foi', 'foram', 'ser', 'estar', 'ter', 'tem', 'teve']
    
    # Contar ocorrências (case-insensitive)
    texto_lower = texto.lower()
    count_ingles = sum(1 for palavra in palavras_ingles if palavra in texto_lower)
    count_portugues = sum(1 for palavra in palavras_portugues if palavra in texto_lower)
    
    # Se há mais palavras em inglês que em português, provavelmente está em inglês
    # Mas só traduz se houver uma diferença significativa para evitar traduzir textos já em português
    if count_ingles > count_portugues * 2 and count_ingles > 10:
        try:
            # Traduzir em chunks para não sobrecarregar
            chunks = []
            chunk_size = 2000  # Chunks menores para tradução rápida
            for i in range(0, len(texto), chunk_size):
                chunk = texto[i:i+chunk_size]
                if chunk.strip():
                    prompt_traducao = f"""Traduza o seguinte texto científico para português brasileiro. Mantenha termos técnicos e nomes próprios quando apropriado. Seja preciso e mantenha a formatação.

Texto a traduzir:
{chunk}

Tradução em português brasileiro:"""
                    chunk_traduzido = gerar_resposta(prompt_traducao, temperatura=0.3)
                    chunks.append(chunk_traduzido)
            
            # Juntar chunks traduzidos
            texto_traduzido = '\n\n'.join(chunks)
            return texto_traduzido
        except Exception as e:
            # Se houver erro na tradução, retornar texto original
            print(f"Erro ao traduzir texto: {e}")
            return texto
    
    # Se já está em português ou não precisa traduzir, retornar original
    return texto


def _precisa_traduzir_para_pt(texto):
    """Retorna True se o texto parece estar em inglês e deve ser traduzido."""
    if not texto or len(texto.strip()) < 50:
        return False
    palavras_ingles = ['the', 'and', 'of', 'to', 'in', 'for', 'is', 'are', 'was', 'were', 'this', 'that', 'with', 'from', 'by', 'as', 'an', 'be', 'been', 'have', 'has', 'had', 'will', 'would', 'could', 'should']
    palavras_portugues = ['o', 'a', 'os', 'as', 'de', 'do', 'da', 'dos', 'das', 'em', 'no', 'na', 'nos', 'nas', 'para', 'por', 'com', 'sem', 'que', 'qual', 'quais', 'é', 'são', 'foi', 'foram', 'ser', 'estar', 'ter', 'tem', 'teve']
    texto_lower = texto.lower()
    count_ingles = sum(1 for p in palavras_ingles if p in texto_lower)
    count_portugues = sum(1 for p in palavras_portugues if p in texto_lower)
    return count_ingles > count_portugues * 2 and count_ingles > 10


def obter_versao_portugues(texto):
    """
    Retorna a versão em português do texto (usando Qwen/Groq quando disponível).
    Se o texto já estiver em português ou tradução falhar, retorna o próprio texto.
    """
    if not texto or not texto.strip():
        return texto
    try:
        chunk_size = 2000
        chunks = []
        for i in range(0, len(texto), chunk_size):
            chunk = texto[i:i + chunk_size]
            if chunk.strip():
                chunk_traduzido = _traduzir_chunk_qwen(chunk)
                chunks.append(chunk_traduzido)
        return '\n\n'.join(chunks) if chunks else texto
    except Exception as e:
        print(f"Erro ao obter versão em português: {e}")
        return texto
