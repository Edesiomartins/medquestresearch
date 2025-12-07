from gpt_engine import gerar_resposta

def analisar_artigo_por_metodo(texto_artigo, metodo):
    metodos = {
        "1": "Resuma o artigo abaixo e formule três perguntas provocativas baseadas no conteúdo.",
        "2": "Com base no artigo abaixo, desenvolva três perguntas que desafiem a compreensão crítica do texto.",
        "3": "Compare perspectivas diferentes apresentadas no artigo abaixo. Crie uma tabela estruturada com os pontos de contraste.",
        "4": "Identifique e explique os principais conceitos apresentados no artigo abaixo.",
        "5": "Crie um mapa mental ou descreva a estrutura lógica do artigo abaixo.",
        "6": "Analise o artigo abaixo buscando e comparando pontos de vista alternativos ou complementares.",
        "7": "Escolha trechos notáveis do artigo abaixo e comente criticamente sobre eles.",
        "8": "Liste possíveis imprecisões factuais encontradas no artigo abaixo, se houver.",
        "9": "Enumere as suposições feitas pelo autor no artigo abaixo, mesmo que não estejam explicitamente declaradas."
    }

    if metodo not in metodos:
        return "Método inválido. Por favor, escolha um número de 1 a 9."

    prompt = f"""
    Aplique o seguinte método de análise crítica a este artigo:
    {metodos[metodo]}

    Artigo:
    {texto_artigo}
    """

    return gerar_resposta(prompt)

def aplicar_leitura_critica(texto_artigo):
    """
    Aplica todos os 9 métodos de leitura crítica ao artigo.
    """
    resultado_completo = []
    
    for i in range(1, 10):
        metodo_num = str(i)
        resultado = analisar_artigo_por_metodo(texto_artigo, metodo_num)
        resultado_completo.append(f"\n{'='*60}\nMÉTODO {i}\n{'='*60}\n{resultado}\n")
    
    return "\n".join(resultado_completo)