from gpt_engine import gerar_resposta
from pdf_processor import extrair_texto_pdf
from explain_concept import explicar_conceito
from critical_analysis import aplicar_leitura_critica
from Fact_checker import verificar_fatos as verificar_fatos_artigo
from Perspective_research import buscar_perspectivas_pubmed
from structure_visualizer import gerar_mapa_visual

print("=== MEDQUESTRESEARCH ===")
print("1 - Explicar conceito ou trecho")
print("2 - Aplicar leitura crítica (9 métodos)")
print("3 - Verificar fatos e possíveis erros")
print("4 - Buscar múltiplas perspectivas (PubMed)")
print("5 - Gerar mapa mental da estrutura do artigo")
print("6 - Gerar mapa visual da estrutura do artigo")

opcao = input("Escolha uma opção: ")

if opcao in ["1", "2", "3", "4", "5", "6"]:
    caminho = input("Caminho do PDF: ").strip()
    texto = extrair_texto_pdf(caminho)

    if opcao == "1":
        conceito = input("Qual conceito ou trecho deseja que seja explicado? ")
        nivel = input("Nível de explicação (ex: leigo, graduação, pós): ").strip() or "graduação"
        print("\n🧠 Explicação:")
        print(explicar_conceito(texto, conceito, nivel))

    elif opcao == "2":
        print("\n📚 Leitura crítica:")
        print(aplicar_leitura_critica(texto))

    elif opcao == "3":
        print("\n🔍 Verificação de fatos:")
        print(verificar_fatos_artigo(texto))

    elif opcao == "4":
        print("\n🔬 Perspectivas científicas:")
        print(buscar_perspectivas_pubmed(texto))

    elif opcao == "5":
        print("\n🗺️ Mapa mental da estrutura:")
        print(gerar_mapa_visual(texto))

    elif opcao == "6":
        print("\n🗺️ Mapa visual da estrutura:")
        print(gerar_mapa_visual(texto))
else:
    print("Opção inválida.")
