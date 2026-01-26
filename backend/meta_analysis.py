# Tentar importação relativa primeiro, depois absoluta
try:
    from .gpt_engine import gerar_resposta
    from .chunker import estimate_tokens
except ImportError:
    try:
        from gpt_engine import gerar_resposta
        from chunker import estimate_tokens
    except ImportError:
        import backend.gpt_engine as gpt_engine
        import backend.chunker as chunker
        gerar_resposta = gpt_engine.gerar_resposta
        estimate_tokens = chunker.estimate_tokens

def gerar_meta_analise(texto_artigo: str, etapa: str = "1", dados_extras: dict = None) -> str:
    """
    Gera análise e criação de artigos de Meta-Análises seguindo protocolo PRISMA.
    
    Args:
        texto_artigo: Texto do(s) artigo(s) científico(s) para análise
        etapa: Etapa do workflow (1=PICO, 2=Extração, 3=Redação, 4=Verificação)
        dados_extras: Dicionário com dados adicionais (tema, json_extração, etc.)
    
    Returns:
        Resposta formatada da IA seguindo o protocolo PRISMA
    """
    # Limitar texto para evitar chamadas muito longas
    texto_artigo = texto_artigo[:6000] if len(texto_artigo) > 6000 else texto_artigo
    
    # Determinar qual prompt usar baseado na etapa
    if etapa == "1" or etapa == "pico":
        prompt = _criar_prompt_etapa1(texto_artigo, dados_extras)
    elif etapa == "2" or etapa == "extracao":
        prompt = _criar_prompt_etapa2(texto_artigo, dados_extras)
    elif etapa == "3" or etapa == "redacao":
        prompt = _criar_prompt_etapa3(texto_artigo, dados_extras)
    elif etapa == "4" or etapa == "verificacao":
        prompt = _criar_prompt_etapa4(texto_artigo, dados_extras)
    else:
        # Etapa padrão: iniciar com pergunta sobre o estágio
        prompt = _criar_prompt_inicial(texto_artigo, dados_extras)
    
    # Gerar resposta com temperatura adequada para análise científica
    resposta = gerar_resposta(prompt, temperatura=0.7)
    return resposta

def _criar_prompt_inicial(texto_artigo: str, dados_extras: dict = None) -> str:
    """Prompt inicial que pergunta sobre o estágio da pesquisa."""
    tema = dados_extras.get("tema", "") if dados_extras else ""
    
    prompt = f"""
# PERSONA
Atue como um Especialista em Metodologia Científica e Engenheiro de Prompt de IA. Seu objetivo é estruturar um aplicativo/workflow de escrita para Revisões Sistemáticas e Metanálises que siga rigorosamente o protocolo PRISMA (Preferred Reporting Items for Systematic Reviews and Meta-Analyses).

# DIRETRIZES DE SEGURANÇA (ANTI-ALUCINAÇÃO E PLÁGIO)
1. ZERO-KNOWLEDGE WRITING: Você não deve usar seu conhecimento interno para citar fatos. Use apenas os dados extraídos dos arquivos carregados.
2. VERBATIM CHECK: Toda citação direta deve ser sinalizada. A paráfrase deve ser técnica e original para garantir <5% de similaridade em softwares de plágio.
3. CITATION MAPPING: Cada parágrafo deve conter a referência (Autor, Ano) vinculada à base de dados fornecida.

# ESTRUTURA DO APLICATIVO (PIPELINE)
Você deve guiar o usuário através de 4 módulos sequenciais:

### Módulo 1: Estruturação PICO e Protocolo
- Entrada: Tema central.
- Saída: Pergunta PICO, estratégia de busca (MeSH/DeCS) para PubMed, Embase e Cochrane, e critérios de elegibilidade.

### Módulo 2: Extração de Dados e Tabela de Evidências
- Entrada: PDFs ou tabelas de dados brutos dos artigos selecionados.
- Processamento: Extrair N, intervenção, controle, desfechos e viés (Risk of Bias - Cochrane Tool).
- Saída: Tabela de características dos estudos padronizada.

### Módulo 3: Escrita Técnica (PRISMA Compliance)
- Fluxo de Redação:
  1. Introdução (Racional e Objetivos).
  2. Métodos (Estratégia de busca, seleção, extração e síntese estatística).
  3. Resultados (Fluxograma PRISMA e descrição dos estudos).
  4. Discussão (Limitações, força da evidência e conclusão).

### Módulo 4: Verificação e Revisão de Estilo
- Revisão gramatical acadêmica (Medical English ou ABNT/Vancouver).
- Verificação de consistência entre a tabela de dados e o texto escrito.

# FORMATO DA RESPOSTA
Inicie perguntando ao usuário: "Qual o tema da revisão e qual o estágio atual da sua pesquisa (Ideia, Busca de Artigos ou Extração de Dados)?"

{f"Tema fornecido: {tema}" if tema else ""}

Texto do(s) artigo(s) fornecido(s):
{texto_artigo}

IMPORTANTE: Responda SEMPRE em português brasileiro, mesmo que o artigo esteja em inglês.
"""
    return prompt

def _criar_prompt_etapa1(texto_artigo: str, dados_extras: dict = None) -> str:
    """Prompt para Etapa 1: Estruturação PICO e Protocolo."""
    tema = dados_extras.get("tema", "") if dados_extras else ""
    
    prompt = f"""
# PERSONA
Atue como um Especialista em Metodologia Científica especializado em Revisões Sistemáticas e Metanálises seguindo protocolo PRISMA.

# ETAPA 1: MAPEAMENTO PICO E CRITÉRIOS

Tema da revisão: {tema if tema else "Não especificado"}

Texto do(s) artigo(s):
{texto_artigo}

# TAREFA
1. Gere a pergunta estruturada PICO (Paciente, Intervenção, Comparação, Outcome).
2. Defina critérios de inclusão/exclusão baseados no protocolo fornecido.
3. Crie estratégia de busca com termos MeSH/DeCS para PubMed, Embase e Cochrane.
4. Estabeleça critérios de elegibilidade claros e objetivos.

# DIRETRIZES
- Use apenas informações presentes no texto fornecido.
- Se algum dado não estiver disponível, indique claramente.
- Formate a saída de forma estruturada e clara.

IMPORTANTE: Responda SEMPRE em português brasileiro, mesmo que o artigo esteja em inglês.
"""
    return prompt

def _criar_prompt_etapa2(texto_artigo: str, dados_extras: dict = None) -> str:
    """Prompt para Etapa 2: Extração de Dados e Tabela de Evidências."""
    prompt = f"""
# PERSONA
Atue como um Especialista em Extração de Dados para Revisões Sistemáticas e Metanálises.

# ETAPA 2: EXTRAÇÃO DE DADOS (DATA EXTRACTION)

Texto do(s) artigo(s):
{texto_artigo}

# TAREFA
Extraia os dados do(s) artigo(s) seguindo estritamente o esquema JSON fornecido abaixo. Se um valor numérico não for encontrado, use null. Não tente calcular valores ausentes. Extraia apenas o que está explicitamente escrito no texto para garantir 0% de alucinação nos dados brutos.

# ESQUEMA JSON DE EXTRAÇÃO (Standard de Ouro)
{{
  "study_metadata": {{
    "title": "string",
    "authors": "string",
    "year": "integer",
    "doi": "string",
    "study_design": "string (ex: RCT, Cohort, Case-Control)"
  }},
  "population": {{
    "total_sample_size": "integer",
    "intervention_group_n": "integer",
    "control_group_n": "integer",
    "age_mean": "number",
    "setting": "string (ex: Hospital, Community)"
  }},
  "outcomes": [
    {{
      "outcome_name": "string",
      "measure_type": "string (ex: Mean, Odds Ratio, Risk Ratio)",
      "intervention_results": {{
        "mean_or_event": "number",
        "sd_or_total": "number"
      }},
      "control_results": {{
        "mean_or_event": "number",
        "sd_or_total": "number"
      }},
      "p_value": "number",
      "confidence_interval": "string (ex: 95% CI 1.2-1.8)"
    }}
  ],
  "risk_of_bias": {{
    "tool_used": "string (ex: RoB 2, Newcastle-Ottawa)",
    "overall_score": "string (ex: Low, High, Some concerns)",
    "justification": "string"
  }}
}}

# INSTRUÇÕES
1. Crie uma tabela estruturada contendo: Autor/Ano, N total, Média/Evento em cada braço, Desfechos Primários e Avaliação de Viés.
2. Se houver múltiplos estudos, extraia cada um separadamente.
3. Valide se intervention_group_n + control_group_n == total_sample_size.
4. Se p_value < 0.05 mas confidence_interval cruza a linha de nulidade, sinalize inconsistência estatística.

IMPORTANTE: Responda SEMPRE em português brasileiro, mesmo que o artigo esteja em inglês. Retorne o JSON estruturado seguido de uma tabela formatada para visualização.
"""
    return prompt

def _criar_prompt_etapa3(texto_artigo: str, dados_extras: dict = None) -> str:
    """Prompt para Etapa 3: Síntese Qualitativa e Redação (PRISMA Compliance)."""
    json_extracao = dados_extras.get("json_extracao", "") if dados_extras else ""
    
    prompt = f"""
# PERSONA
Atue como um Redator Científico Sênior especializado em Revisões Sistemáticas. Sua tarefa é redigir a seção de "Resultados" e "Discussão" baseando-se EXCLUSIVAMENTE no objeto JSON de extração de dados fornecido.

# INPUT DATA
JSON de Extração:
{json_extracao if json_extracao else "Não fornecido - use os dados do texto abaixo"}

Texto do(s) artigo(s):
{texto_artigo}

# REGRAS DE OURO (RIGOR CIENTÍFICO)
1. ANCORAGEM NUMÉRICA: Toda vez que mencionar um resultado, você deve citar os valores exatos do JSON (n, p-valor, IC 95%).
2. SÍNTESE, NÃO REPETIÇÃO: Não faça apenas uma lista. Compare os estudos. Agrupe estudos com resultados similares e contraste os que apresentaram discrepâncias.
3. ANTI-PLÁGIO: Utilize paráfrases técnicas. Em vez de "o estudo X disse Y", use "Observou-se uma tendência de [Desfecho] no grupo [Intervenção] em comparação ao [Controle] (Estudo X, Ano)".
4. VERIFICAÇÃO DE VIÉS: Integre os dados de 'risk_of_bias' na narrativa. Discuta como a qualidade metodológica de cada estudo pode ter influenciado os resultados encontrados.

# ESTRUTURA DA REDAÇÃO
1. CARACTERÍSTICAS DOS ESTUDOS: Descreva o perfil populacional médio e os desenhos de estudo encontrados.
2. SÍNTESE DOS DESFECHOS: Organize por subtemas (ex: Eficácia, Segurança, Marcadores Bioquímicos).
3. ANÁLISE DE HETEROGENEIDADE: Comente sobre as variações entre os estudos (diferenças de doses, idade, tempo de seguimento).
4. CONCLUSÃO PRELIMINAR: Resuma a força da evidência atual.

# RESTRIÇÕES DE OUTPUT
- Proibido usar adjetivos subjetivos (ex: "estudo maravilhoso", "resultado incrível"). Use termos neutros (ex: "estatisticamente significativo", "robusto", "limitado").
- Limite de alucinação: Se o JSON marcar um campo como `null`, você deve escrever que "não foram reportados dados sobre [X] neste conjunto de evidências".
- Estilo: Linguagem acadêmica formal (Medical English ou Português Acadêmico), tom impessoal.

# ETAPA 3: SÍNTESE ESTATÍSTICA E RESULTADOS
- Descreva os resultados para o Forest Plot (Heterogeneidade I², Valor de p, e Effect Size). 
- *Nota: Se o usuário não fornecer os cálculos, descreva qualitativamente os resultados seguindo o rigor estatístico.*

# ETAPA 4: REDAÇÃO CONFORME PRISMA
- Redija as seções: Métodos, Resultados e Discussão.

IMPORTANTE: Responda SEMPRE em português brasileiro, mesmo que o artigo esteja em inglês.
"""
    return prompt

def _criar_prompt_etapa4(texto_artigo: str, dados_extras: dict = None) -> str:
    """Prompt para Etapa 4: Verificação Final, Rigor PRISMA e Formatação."""
    json_extracao = dados_extras.get("json_extracao", "") if dados_extras else ""
    estilo = dados_extras.get("estilo", "Vancouver") if dados_extras else "Vancouver"
    manuscrito = dados_extras.get("manuscrito", texto_artigo) if dados_extras else texto_artigo
    
    prompt = f"""
# PERSONA
Atue como Editor-Chefe de um periódico médico de alto fator de impacto e Especialista em Normatização Científica. Sua missão é realizar a revisão final do manuscrito para garantir ZERO erros de formatação e integridade total dos dados.

# INPUT
1. Manuscrito gerado no Módulo 3:
{manuscrito}

2. JSON de extração original (para conferência):
{json_extracao if json_extracao else "Não fornecido"}

# TAREFA 1: CROSS-CHECK DE DADOS (ANTI-ALUCINAÇÃO FINAL)
- Compare cada número, porcentagem e p-valor presente no texto com o JSON original.
- Liste em uma tabela de "Divergências Encontradas" qualquer dado que não seja idêntico ao JSON. Se não houver divergências, escreva: "Dados 100% íntegros".

# TAREFA 2: CHECKLIST PRISMA 2020
- Analise o texto e verifique se os seguintes itens estão presentes e claros:
    - Elegibilidade (Critérios PICO).
    - Fontes de informação e estratégia de busca.
    - Processo de seleção e extração.
    - Avaliação do risco de viés (RoB).
    - Síntese dos resultados.

# TAREFA 3: FORMATAÇÃO DE REFERÊNCIAS E ESTILO
- Aplique o estilo {estilo} (VANCOUVER OU ABNT).
- Garanta que todas as citações no corpo do texto tenham uma correspondência na lista de referências final.
- Verifique o tom: O texto deve ser estritamente impessoal, em voz passiva (ex: "Observou-se" em vez de "Nós observamos").

# TAREFA 4: REVISÃO DE PLÁGIO (PARÁFRASE CIENTÍFICA)
- Identifique frases que possuam estrutura sintática muito comum ou repetitiva.
- Sugira melhorias para aumentar a sofisticação do "Medical English" ou do "Português Acadêmico", mantendo a precisão dos termos MeSH/DeCS.

# OUTPUT FINAL
1. Relatório de Erros/Inconsistências (se houver).
2. Versão Final do Manuscrito formatada e polida.
3. Declaração de conformidade com as normas PRISMA.

IMPORTANTE: Responda SEMPRE em português brasileiro, mesmo que o artigo esteja em inglês.
"""
    return prompt
