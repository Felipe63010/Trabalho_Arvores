"""Construção dos gráficos a partir dos resultados experimentais gravados.

O módulo lê os arquivos CSV produzidos por ``benchmark.py`` e gera as
figuras utilizadas na seção de resultados do relatório.
"""

import csv
import math
import os
import sys

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ORIGEM = os.path.join(RAIZ, "results")
DESTINO = os.path.join(RAIZ, "figures")

ESTILOS = {
    "BST": {"cor": "#b23a3a", "marcador": "o", "traco": "-"},
    "AVL": {"cor": "#2b4a72", "marcador": "s", "traco": "--"},
    "Splay": {"cor": "#1b7f4d", "marcador": "^", "traco": "-."},
    "Treap": {"cor": "#b25f12", "marcador": "D", "traco": ":"},
    "Trie": {"cor": "#1b7f4d", "marcador": "o", "traco": "-"},
    "Patricia": {"cor": "#b25f12", "marcador": "s", "traco": "--"},
    "KD-Tree": {"cor": "#2b4a72", "marcador": "o", "traco": "-"},
    "Busca linear": {"cor": "#b23a3a", "marcador": "s", "traco": "--"},
}

TAMANHO_FONTE = 8.0


def ler(nome):
    """Lê um arquivo CSV de resultados como lista de dicionários."""
    with open(os.path.join(ORIGEM, nome), "r", encoding="utf-8") as arquivo:
        return list(csv.DictReader(arquivo))


def numero(texto):
    """Converte um campo textual em número, tratando valores ausentes."""
    try:
        valor = float(texto)
    except (TypeError, ValueError):
        return float("nan")
    return valor


def serie(linhas, filtros, eixo_x, eixo_y):
    """Extrai um par de séries numéricas ordenadas pelo eixo das abscissas."""
    selecionadas = [
        linha
        for linha in linhas
        if all(linha[campo] == valor for campo, valor in filtros.items())
    ]
    selecionadas.sort(key=lambda linha: numero(linha[eixo_x]))
    return (
        [numero(linha[eixo_x]) for linha in selecionadas],
        [numero(linha[eixo_y]) for linha in selecionadas],
    )


def configurar(eixo, titulo, rotulo_x, rotulo_y, log_x=False, log_y=False):
    """Aplica a formatação comum a todos os gráficos."""
    eixo.set_title(titulo, fontsize=TAMANHO_FONTE + 0.5, pad=6)
    eixo.set_xlabel(rotulo_x, fontsize=TAMANHO_FONTE)
    eixo.set_ylabel(rotulo_y, fontsize=TAMANHO_FONTE)
    if log_x:
        eixo.set_xscale("log", base=2)
    if log_y:
        eixo.set_yscale("log")
    eixo.tick_params(labelsize=TAMANHO_FONTE - 1)
    eixo.grid(True, which="major", linewidth=0.4, alpha=0.45)
    for borda in eixo.spines.values():
        borda.set_linewidth(0.6)


def tracar(eixo, nome, abscissas, ordenadas, rotulo=None):
    """Desenha uma série com o estilo associado ao nome da estrutura."""
    estilo = ESTILOS.get(nome, {"cor": "#444444", "marcador": "o", "traco": "-"})
    eixo.plot(
        abscissas,
        ordenadas,
        color=estilo["cor"],
        marker=estilo["marcador"],
        linestyle=estilo["traco"],
        markersize=3.4,
        linewidth=1.2,
        label=rotulo or nome,
    )


def grafico_comparacao():
    """Custo de inserção e altura das árvores de busca por comparação."""
    linhas = ler("e1_comparacao.csv")
    figura, eixos = plt.subplots(1, 3, figsize=(7.2, 2.15))

    for nome in ["BST", "AVL", "Splay", "Treap"]:
        abscissas, ordenadas = serie(
            linhas, {"cenario": "aleatoria", "estrutura": nome}, "n", "t_insercao_ms"
        )
        if abscissas:
            tracar(eixos[0], nome, abscissas, ordenadas)
    configurar(
        eixos[0],
        "(a) inserção com chaves aleatórias",
        "número de chaves (n)",
        "tempo total (ms)",
        log_x=True,
        log_y=True,
    )

    for nome in ["BST", "AVL", "Splay", "Treap"]:
        abscissas, ordenadas = serie(
            linhas, {"cenario": "ordenada", "estrutura": nome}, "n", "t_insercao_ms"
        )
        if abscissas:
            tracar(eixos[1], nome, abscissas, ordenadas)
    configurar(
        eixos[1],
        "(b) inserção com chaves ordenadas",
        "número de chaves (n)",
        "tempo total (ms)",
        log_x=True,
        log_y=True,
    )

    for nome in ["BST", "AVL", "Splay", "Treap"]:
        abscissas, ordenadas = serie(
            linhas, {"cenario": "aleatoria", "estrutura": nome}, "n", "altura"
        )
        if abscissas:
            tracar(eixos[2], nome, abscissas, ordenadas)
    referencia = sorted({numero(linha["n"]) for linha in linhas})
    eixos[2].plot(
        referencia,
        [math.log2(valor) for valor in referencia],
        color="#555555",
        linewidth=1.0,
        linestyle=(0, (1, 1)),
        label="log2(n)",
    )
    configurar(
        eixos[2],
        "(c) altura final (chaves aleatórias)",
        "número de chaves (n)",
        "altura (arestas)",
        log_x=True,
    )

    eixos[0].legend(fontsize=TAMANHO_FONTE - 1.5, loc="upper left", framealpha=0.92)
    eixos[2].legend(fontsize=TAMANHO_FONTE - 1.5, loc="upper left", framealpha=0.92)
    figura.tight_layout(w_pad=1.4)
    caminho = os.path.join(DESTINO, "fig_comparacao.png")
    figura.savefig(caminho, dpi=220, bbox_inches="tight", facecolor="white")
    plt.close(figura)
    return caminho


def grafico_texto():
    """Ocupação e desempenho das estruturas indexadas por prefixo."""
    linhas = ler("e2_texto.csv")
    figura, eixos = plt.subplots(1, 3, figsize=(7.2, 2.15))

    for nome in ["Trie", "Patricia"]:
        abscissas, ordenadas = serie(
            linhas, {"cenario": "lexico", "estrutura": nome}, "n", "nos_por_chave"
        )
        tracar(eixos[0], nome, abscissas, ordenadas, rotulo="%s (léxico)" % nome)
        abscissas, ordenadas = serie(
            linhas, {"cenario": "aleatorio", "estrutura": nome}, "n", "nos_por_chave"
        )
        estilo = ESTILOS[nome]
        eixos[0].plot(
            abscissas,
            ordenadas,
            color=estilo["cor"],
            marker=estilo["marcador"],
            linestyle=(0, (1, 1)),
            markersize=3.4,
            linewidth=1.0,
            markerfacecolor="white",
            label="%s (aleatório)" % nome,
        )
    configurar(
        eixos[0],
        "(a) nós alocados por chave",
        "número de chaves (n)",
        "nós / chave",
        log_x=True,
    )

    for nome in ["Trie", "Patricia", "AVL"]:
        abscissas, ordenadas = serie(
            linhas, {"cenario": "lexico", "estrutura": nome}, "n", "bytes_por_chave"
        )
        tracar(eixos[1], nome, abscissas, ordenadas)
    configurar(
        eixos[1],
        "(b) memória por chave (léxico)",
        "número de chaves (n)",
        "bytes / chave",
        log_x=True,
    )

    for nome in ["Trie", "Patricia", "AVL"]:
        abscissas, ordenadas = serie(
            linhas, {"cenario": "lexico", "estrutura": nome}, "n", "t_busca_acerto_ms"
        )
        ordenadas = [valor * 1000.0 / abscissa for valor, abscissa in zip(ordenadas, abscissas)]
        tracar(eixos[2], nome, abscissas, ordenadas)
    configurar(
        eixos[2],
        "(c) tempo médio de busca (léxico)",
        "número de chaves (n)",
        "microssegundos / busca",
        log_x=True,
    )

    eixos[0].legend(fontsize=TAMANHO_FONTE - 2.0, loc="best", framealpha=0.92)
    eixos[1].legend(fontsize=TAMANHO_FONTE - 1.5, loc="best", framealpha=0.92)
    figura.tight_layout(w_pad=1.4)
    caminho = os.path.join(DESTINO, "fig_texto.png")
    figura.savefig(caminho, dpi=220, bbox_inches="tight", facecolor="white")
    plt.close(figura)
    return caminho


def grafico_espacial():
    """Desempenho da KD-Tree frente à busca linear e efeito da dimensionalidade."""
    escala = ler("e3_espacial.csv")
    dimensao = ler("e3b_dimensionalidade.csv")
    figura, eixos = plt.subplots(1, 3, figsize=(7.2, 2.15))

    abscissas, ordenadas = serie(escala, {"cenario": "uniforme"}, "n", "t_consulta_kd_us")
    tracar(eixos[0], "KD-Tree", abscissas, ordenadas, rotulo="KD-Tree (uniforme)")
    abscissas_agrupado, ordenadas_agrupado = serie(
        escala, {"cenario": "agrupado"}, "n", "t_consulta_kd_us"
    )
    eixos[0].plot(
        abscissas_agrupado,
        ordenadas_agrupado,
        color="#1b7f4d",
        marker="^",
        linestyle="-.",
        markersize=3.4,
        linewidth=1.2,
        label="KD-Tree (agrupado)",
    )
    abscissas_linear, ordenadas_linear = serie(
        escala, {"cenario": "uniforme"}, "n", "t_consulta_linear_us"
    )
    tracar(eixos[0], "Busca linear", abscissas_linear, ordenadas_linear)
    configurar(
        eixos[0],
        "(a) consulta ao vizinho mais próximo",
        "número de pontos (n)",
        "microssegundos / consulta",
        log_x=True,
        log_y=True,
    )

    abscissas, ordenadas = serie(escala, {"cenario": "uniforme"}, "n", "t_construcao_ms")
    tracar(eixos[1], "KD-Tree", abscissas, ordenadas, rotulo="construção balanceada")
    configurar(
        eixos[1],
        "(b) custo de construção",
        "número de pontos (n)",
        "tempo total (ms)",
        log_x=True,
        log_y=True,
    )

    abscissas = [numero(linha["dimensoes"]) for linha in dimensao]
    ordenadas = [100.0 * numero(linha["fracao_visitada"]) for linha in dimensao]
    eixos[2].plot(
        abscissas,
        ordenadas,
        color="#2b4a72",
        marker="o",
        linestyle="-",
        markersize=3.4,
        linewidth=1.2,
        label="nós visitados",
    )
    aceleracoes = [numero(linha["aceleracao"]) for linha in dimensao]
    gemeo = eixos[2].twinx()
    gemeo.plot(
        abscissas,
        aceleracoes,
        color="#b23a3a",
        marker="s",
        linestyle="--",
        markersize=3.4,
        linewidth=1.2,
        label="aceleração relativa",
    )
    gemeo.set_ylabel("aceleração sobre a busca linear", fontsize=TAMANHO_FONTE - 0.5)
    gemeo.tick_params(labelsize=TAMANHO_FONTE - 1)
    gemeo.set_yscale("log")
    configurar(
        eixos[2],
        "(c) efeito da dimensionalidade (n = 8000)",
        "dimensão do espaço (k)",
        "% da base visitada",
        log_y=True,
    )

    eixos[0].legend(fontsize=TAMANHO_FONTE - 2.0, loc="upper left", framealpha=0.92)
    linhas_esquerda, rotulos_esquerda = eixos[2].get_legend_handles_labels()
    linhas_direita, rotulos_direita = gemeo.get_legend_handles_labels()
    eixos[2].legend(
        linhas_esquerda + linhas_direita,
        rotulos_esquerda + rotulos_direita,
        fontsize=TAMANHO_FONTE - 2.0,
        loc="center left",
        framealpha=0.92,
    )
    figura.tight_layout(w_pad=1.6)
    caminho = os.path.join(DESTINO, "fig_kdtree.png")
    figura.savefig(caminho, dpi=220, bbox_inches="tight", facecolor="white")
    plt.close(figura)
    return caminho


def grafico_localidade():
    """Custo médio de acesso em função da concentracao da carga de consultas."""
    linhas = ler("e4_localidade.csv")
    figura, eixos = plt.subplots(1, 2, figsize=(7.2, 2.35))

    for nome in ["BST", "AVL", "Splay", "Treap"]:
        abscissas, ordenadas = serie(
            linhas, {"estrutura": nome}, "expoente_zipf", "visitas_por_acesso"
        )
        tracar(eixos[0], nome, abscissas, ordenadas)
    configurar(
        eixos[0],
        "(a) nós visitados por acesso",
        "expoente da distribuição de Zipf (s)",
        "nós visitados / acesso",
    )

    for nome in ["BST", "AVL", "Splay", "Treap"]:
        abscissas, ordenadas = serie(
            linhas, {"estrutura": nome}, "expoente_zipf", "t_por_acesso_us"
        )
        tracar(eixos[1], nome, abscissas, ordenadas)
    configurar(
        eixos[1],
        "(b) tempo médio por acesso",
        "expoente da distribuição de Zipf (s)",
        "microssegundos / acesso",
    )

    eixos[0].legend(fontsize=TAMANHO_FONTE - 1.5, loc="best", framealpha=0.92)
    figura.tight_layout(w_pad=1.4)
    caminho = os.path.join(DESTINO, "fig_localidade.png")
    figura.savefig(caminho, dpi=220, bbox_inches="tight", facecolor="white")
    plt.close(figura)
    return caminho


def main():
    """Gera todas as figuras derivadas dos resultados experimentais."""
    os.makedirs(DESTINO, exist_ok=True)
    print(grafico_comparacao())
    print(grafico_texto())
    print(grafico_espacial())
    print(grafico_localidade())


if __name__ == "__main__":
    main()
