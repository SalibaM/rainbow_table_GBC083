"""Gera os graficos do trabalho a partir dos CSVs de resultados/ (Passo 9)."""

import csv
import os

import matplotlib
matplotlib.use("Agg")                 # sem janela; so salva arquivo
import matplotlib.pyplot as plt

RAIZ = os.path.dirname(os.path.abspath(__file__))
RESULTADOS = os.path.join(RAIZ, "resultados")

AZUL = "#0072B2"
LARANJA = "#E69F00"
VERDE = "#009E73"
CINZA = "#8A8A8A"
TINTA = "#222222"

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Arial", "DejaVu Sans"],
    "font.size": 11,
    "axes.edgecolor": "#555555",
    "axes.labelcolor": TINTA,
    "text.color": TINTA,
    "xtick.color": TINTA,
    "ytick.color": TINTA,
    "figure.facecolor": "white",
    "axes.facecolor": "white",
})


def _ler_csv(nome):
    """Le um CSV de resultados/ como lista de dicts, convertendo numeros."""
    caminho = os.path.join(RESULTADOS, nome)
    linhas = []
    with open(caminho, "r", newline="", encoding="utf-8") as arquivo:
        for linha in csv.DictReader(arquivo):
            convertida = {}
            for chave, valor in linha.items():
                try:
                    convertida[chave] = float(valor)
                except (ValueError, TypeError):
                    convertida[chave] = valor
            linhas.append(convertida)
    return linhas


def grafico_memoria_tempo(nome_saida="fig_memoria_tempo.png"):
    """Memoria usada (disco, em KB) x tempo medio para quebrar, em log-log."""
    dados = _ler_csv("varredura_media.csv")
    mem_kb = [linha["disco_bytes"] / 1024 for linha in dados]
    tempo = [linha["tempo_medio_quebra_us"] for linha in dados]
    larguras = [int(linha["largura"]) for linha in dados]

    figura, eixo = plt.subplots(figsize=(6.2, 4.3))
    eixo.plot(mem_kb, tempo, "-o", color=AZUL, markersize=8,
              markerfacecolor=AZUL, markeredgecolor="white", linewidth=2)
    for mem, tmp, larg in zip(mem_kb, tempo, larguras):
        eixo.annotate(f"largura {larg}", (mem, tmp),
                      textcoords="offset points", xytext=(10, 10),
                      fontsize=9, color=TINTA)

    eixo.set_xscale("log")
    eixo.set_yscale("log")
    eixo.set_xlim(min(mem_kb) / 1.7, max(mem_kb) * 1.9)
    eixo.set_ylim(min(tempo) / 1.8, max(tempo) * 2.6)
    eixo.set_xticks(mem_kb)
    eixo.set_xticklabels([f"{m:.0f}" for m in mem_kb])
    eixo.set_yticks(tempo)
    eixo.set_yticklabels([f"{t:.0f}" for t in tempo])
    eixo.minorticks_off()
    eixo.set_xlabel("tabela em disco (KB)")
    eixo.set_ylabel("tempo por busca (microssegundos)")
    eixo.set_title("Memória usada e tempo por busca (mesma cobertura)")
    eixo.grid(True, which="major", color="0.9")
    figura.tight_layout()
    figura.savefig(os.path.join(RESULTADOS, nome_saida), dpi=150)
    plt.close(figura)


def grafico_custo_busca(nome_saida="fig_custo_busca.png"):
    """Operacoes por busca conforme a largura, com a referencia ~largura^2."""
    dados = _ler_csv("varredura_media.csv")
    larguras = [int(linha["largura"]) for linha in dados]
    operacoes = [linha["ops_media_miss"] for linha in dados]

    figura, eixo = plt.subplots(figsize=(6.2, 4.3))
    fator = operacoes[0] / (larguras[0] ** 2)
    referencia = [fator * (w ** 2) for w in larguras]
    eixo.plot(larguras, referencia, linestyle="--", color=CINZA, linewidth=2,
              label="proporcional à largura ao quadrado")
    eixo.plot(larguras, operacoes, linestyle="none", marker="o", markersize=9,
              markerfacecolor=AZUL, markeredgecolor="white", color=AZUL,
              label="medido")
    eixo.set_xlabel("largura da cadeia")
    eixo.set_ylabel("operações por busca")
    eixo.set_title("Custo da busca conforme a largura")
    eixo.legend(frameon=False)
    eixo.grid(True, color="0.9")
    figura.tight_layout()
    figura.savefig(os.path.join(RESULTADOS, nome_saida), dpi=150)
    plt.close(figura)


def grafico_eficacia(nome_saida="fig_eficacia.png"):
    """Eficacia real x cobertura teorica, com a reta de referencia y = x."""
    dados = _ler_csv("curva_eficacia_grande.csv")
    cobertura = [linha["cota_teorica"] for linha in dados]
    eficacia = [linha["taxa_acerto"] for linha in dados]

    figura, eixo = plt.subplots(figsize=(6.2, 4.3))
    eixo.plot([0, 1], [0, 1], linestyle="--", color=CINZA, linewidth=2,
              label="se nenhuma senha se repetisse")
    eixo.fill_between(cobertura, eficacia, color=AZUL, alpha=0.08)
    eixo.plot(cobertura, eficacia, marker="o", color=AZUL, markersize=8,
              markerfacecolor=AZUL, markeredgecolor="white", linewidth=2,
              label="eficácia medida")
    eixo.set_xlabel("cobertura teórica (altura × largura / N)")
    eixo.set_ylabel("fração das senhas encontradas")
    eixo.set_title("Eficácia conforme a cobertura cresce")
    eixo.set_xlim(0, 1)
    eixo.set_ylim(0, 1)
    eixo.legend(frameon=False)
    eixo.grid(True, color="0.9")
    figura.tight_layout()
    figura.savefig(os.path.join(RESULTADOS, nome_saida), dpi=150)
    plt.close(figura)


def grafico_rainbow_vs_1cor(nome_saida="fig_rainbow_vs_1cor.png"):
    """Barras do aproveitamento de senhas, rainbow e cor unica, por largura."""
    dados = _ler_csv("rainbow_vs_1cor.csv")
    larguras = sorted({int(linha["largura"]) for linha in dados})
    rainbow = [next(l["aproveitamento"] for l in dados
                    if l["rotulo"] == "rainbow" and int(l["largura"]) == w)
               for w in larguras]
    uma_cor = [next(l["aproveitamento"] for l in dados
                    if l["rotulo"] == "1cor" and int(l["largura"]) == w)
               for w in larguras]

    posicoes = range(len(larguras))
    largura_barra = 0.38
    figura, eixo = plt.subplots(figsize=(6.2, 4.3))
    barras_r = eixo.bar([p - largura_barra / 2 for p in posicoes], rainbow,
                        largura_barra, color=AZUL, label="rainbow (cor por coluna)")
    barras_c = eixo.bar([p + largura_barra / 2 for p in posicoes], uma_cor,
                        largura_barra, color=LARANJA, label="cor única")
    for grupo in (barras_r, barras_c):
        for barra in grupo:
            altura = barra.get_height()
            eixo.annotate(f"{altura:.2f}", (barra.get_x() + barra.get_width() / 2, altura),
                          textcoords="offset points", xytext=(0, 3),
                          ha="center", fontsize=9, color=TINTA)
    eixo.set_xticks(list(posicoes))
    eixo.set_xticklabels([f"largura {w}" for w in larguras])
    eixo.set_ylabel("fração das senhas aproveitada")
    eixo.set_title("Aproveitamento das senhas: rainbow e cor única")
    eixo.set_ylim(0, 1.30)
    eixo.legend(loc="upper center", ncol=2, frameon=False)
    eixo.grid(True, axis="y", color="0.9")
    figura.tight_layout()
    figura.savefig(os.path.join(RESULTADOS, nome_saida), dpi=150)
    plt.close(figura)


if __name__ == "__main__":
    grafico_memoria_tempo()
    grafico_custo_busca()
    grafico_eficacia()
    grafico_rainbow_vs_1cor()
    print("Graficos gerados em:", RESULTADOS)
    for nome in ("fig_memoria_tempo.png", "fig_custo_busca.png",
                 "fig_eficacia.png", "fig_rainbow_vs_1cor.png"):
        print("  ", nome)
