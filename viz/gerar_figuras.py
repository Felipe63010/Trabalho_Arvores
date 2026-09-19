"""Geração das figuras de demonstração e rastreamento visual das estruturas.

Para cada estrutura são produzidos três estados: o estado inicial após um
conjunto de inserções, um estado intermediário que evidencia o mecanismo
característico da estrutura e o estado resultante de uma remoção ou
reorganização. As figuras são gravadas no diretório ``figures``.
"""

import os
import sys

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.kdtree import KDTree
from src.patricia import PatriciaTree
from src.splay import SplayTree
from src.treap import Treap
from src.trie import Trie
from viz.adapters import binary_to_draw, patricia_to_draw, trie_to_draw
from viz.layout import COR_ARESTA, COR_BORDA, COR_BORDA_DESTAQUE, COR_TEXTO, render_panels

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DESTINO = os.path.join(RAIZ, "figures")

PALAVRAS_INICIAIS = ["casa", "casal", "caso", "cara"]
PALAVRAS_ADICIONAIS = ["carro"]
PALAVRAS_REMOVIDAS = ["casal", "carro"]

CHAVES_SPLAY = [30, 70, 10, 50, 90, 20]
CHAVES_TREAP = [50, 20, 70, 10, 60, 30]
SEMENTE_TREAP = 93
PRIORIDADE_DESTAQUE = 0.99
CHAVE_DESTAQUE = 55
CHAVE_REMOVIDA_TREAP = 20
PONTOS_KD = [
    (30, 40),
    (5, 25),
    (10, 12),
    (70, 70),
    (50, 30),
    (35, 45),
    (25, 60),
]
CONSULTA_KD = (52, 58)
DESLOCAMENTOS_ROTULO = {(30, 40): (-6, -16), (25, 60): (-10, 8)}


def gerar_trie():
    """Três estados da trie: prefixos compartilhados, bifurcação e poda."""
    trie = Trie()
    for palavra in PALAVRAS_INICIAIS:
        trie.insert(palavra)
    painel_a = trie_to_draw(trie.root)

    for palavra in PALAVRAS_ADICIONAIS:
        trie.insert(palavra)
    destaques_b = set()
    for palavra in PALAVRAS_ADICIONAIS:
        for tamanho in range(4, len(palavra) + 1):
            destaques_b.add(palavra[:tamanho])
    painel_b = trie_to_draw(trie.root, highlights=destaques_b)


    for palavra in PALAVRAS_REMOVIDAS:
        trie.remove(palavra)
    painel_c = trie_to_draw(trie.root, highlights={"cara"})

    caminho = os.path.join(DESTINO, "trie_estados.png")
    render_panels(
        [
            ("(a) inserções iniciais", painel_a),
            ("(b) inserção de carro", painel_b),
            ("(c) após as remoções", painel_c),
        ],
        caminho,
        binary=False,
        node_style="point",
        unit=0.50,
        font_scale=0.30,
        orientation="horizontal",
        y_gap=1.0,
    )
    return caminho


def gerar_patricia():
    """Três estados da Patricia: compactação, divisão de rótulo e reunificação."""
    arvore = PatriciaTree()
    for palavra in PALAVRAS_INICIAIS:
        arvore.insert(palavra)
    painel_a = patricia_to_draw(arvore.root)

    for palavra in PALAVRAS_ADICIONAIS:
        arvore.insert(palavra)
    painel_b = patricia_to_draw(arvore.root, highlights={"car", "cara", "carro"})

    for palavra in PALAVRAS_REMOVIDAS:
        arvore.remove(palavra)
    painel_c = patricia_to_draw(arvore.root, highlights={"cara"})

    caminho = os.path.join(DESTINO, "patricia_estados.png")
    render_panels(
        [
            ("(a) inserções iniciais", painel_a),
            ("(b) divisão do rótulo ra", painel_b),
            ("(c) fusão de r com a", painel_c),
        ],
        caminho,
        binary=False,
        node_style="point",
        unit=0.50,
        font_scale=0.30,
        orientation="horizontal",
        y_gap=1.0,
    )
    return caminho


def gerar_splay():
    """Três estados da splay: inserções, promoção pela busca e remoção."""
    arvore = SplayTree()
    for chave in CHAVES_SPLAY:
        arvore.insert(chave)
    rotulo = lambda no, _profundidade: str(no.key)
    painel_a = binary_to_draw(arvore.root, rotulo)

    arvore.search(90)
    painel_b = binary_to_draw(
        arvore.root, rotulo, highlight=lambda no, _p: no.key == 90
    )

    arvore.remove(30)
    painel_c = binary_to_draw(
        arvore.root, rotulo, highlight=lambda no, _p: no is arvore.root
    )

    caminho = os.path.join(DESTINO, "splay_estados.png")
    render_panels(
        [
            ("(a) após as inserções", painel_a),
            ("(b) após buscar 90", painel_b),
            ("(c) após remover 30", painel_c),
        ],
        caminho,
        binary=True,
        node_style="box",
        unit=0.50,
        font_scale=0.42,
        orientation="horizontal",
    )
    return caminho


def gerar_treap():
    """Três estados da treap: heap de prioridades, promoção e remoção por rotações."""
    arvore = Treap(seed=SEMENTE_TREAP)
    for chave in CHAVES_TREAP:
        arvore.insert(chave)
    rotulo = lambda no, _profundidade: str(no.key)
    subrotulo = lambda no, _profundidade: ("%.2f" % no.priority).replace(".", ",")
    painel_a = binary_to_draw(arvore.root, rotulo, subrotulo)

    arvore.insert(CHAVE_DESTAQUE, priority=PRIORIDADE_DESTAQUE)
    painel_b = binary_to_draw(
        arvore.root, rotulo, subrotulo, highlight=lambda no, _p: no.key == CHAVE_DESTAQUE
    )

    alvo = CHAVE_REMOVIDA_TREAP
    filhos = set()
    pilha = [arvore.root]
    while pilha:
        no = pilha.pop()
        if no is None:
            continue
        if no.key == alvo:
            if no.left is not None:
                filhos.add(no.left.key)
            if no.right is not None:
                filhos.add(no.right.key)
        pilha.append(no.left)
        pilha.append(no.right)
    arvore.remove(alvo)
    painel_c = binary_to_draw(
        arvore.root, rotulo, subrotulo, highlight=lambda no, _p: no.key in filhos
    )

    caminho = os.path.join(DESTINO, "treap_estados.png")
    render_panels(
        [
            ("(a) após as inserções", painel_a),
            ("(b) inserção de 55, p = 0,99", painel_b),
            ("(c) após remover 20", painel_c),
        ],
        caminho,
        binary=True,
        node_style="box",
        unit=0.54,
        font_scale=0.40,
        orientation="horizontal",
    )
    return caminho


def gerar_kdtree():
    """Três estados da KD-Tree: construção, rastro da consulta e remoção."""
    arvore = KDTree(2).build(PONTOS_KD)
    rotulo = lambda no, _profundidade: "%d,%d" % no.point
    subrotulo = lambda _no, profundidade: "x" if profundidade % 2 == 0 else "y"
    painel_a = binary_to_draw(arvore.root, rotulo, subrotulo)

    _resultado, visitados, podados = arvore.nearest_with_trace(CONSULTA_KD)
    visitados_conjunto = set(visitados)
    painel_b = binary_to_draw(
        arvore.root,
        rotulo,
        subrotulo,
        highlight=lambda no, _p: no.point in visitados_conjunto,
    )

    removido = arvore.root.point
    arvore.remove(removido)
    nova_raiz = arvore.root.point
    painel_c = binary_to_draw(
        arvore.root, rotulo, subrotulo, highlight=lambda no, _p: no.point == nova_raiz
    )

    caminho = os.path.join(DESTINO, "kdtree_estados.png")
    render_panels(
        [
            ("(a) construção balanceada", painel_a),
            ("(b) rastro da busca", painel_b),
            ("(c) após remover a raiz", painel_c),
        ],
        caminho,
        binary=True,
        node_style="box",
        unit=0.56,
        font_scale=0.34,
        orientation="horizontal",
    )
    return caminho, removido, visitados, podados


def gerar_particao_kd(limites=(0, 90, 0, 90)):
    """Particionamento do plano induzido pela KD-Tree e rastro da consulta."""
    arvore = KDTree(2).build(PONTOS_KD)
    resultado, visitados, podados = arvore.nearest_with_trace(CONSULTA_KD)
    vizinho, _valor, distancia = resultado
    visitados_conjunto = set(visitados)
    podados_conjunto = set(podados)

    figura, eixo = plt.subplots(figsize=(4.4, 4.4))

    def recursao(no, profundidade, x0, x1, y0, y1):
        if no is None:
            return
        eixo_corte = profundidade % 2
        espessura = max(0.6, 2.0 - 0.4 * profundidade)
        if eixo_corte == 0:
            eixo.plot(
                [no.point[0], no.point[0]],
                [y0, y1],
                color=COR_BORDA,
                linewidth=espessura,
                zorder=1,
            )
            recursao(no.left, profundidade + 1, x0, no.point[0], y0, y1)
            recursao(no.right, profundidade + 1, no.point[0], x1, y0, y1)
        else:
            eixo.plot(
                [x0, x1],
                [no.point[1], no.point[1]],
                color=COR_BORDA_DESTAQUE,
                linewidth=espessura,
                linestyle="--",
                zorder=1,
            )
            recursao(no.left, profundidade + 1, x0, x1, y0, no.point[1])
            recursao(no.right, profundidade + 1, x0, x1, no.point[1], y1)

    recursao(arvore.root, 0, *limites)

    for ponto in PONTOS_KD:
        if ponto in visitados_conjunto:
            cor, tamanho, borda = COR_BORDA_DESTAQUE, 58, 1.4
        elif ponto in podados_conjunto:
            cor, tamanho, borda = "#9aa5b1", 44, 0.8
        else:
            cor, tamanho, borda = "#9aa5b1", 34, 0.8
        eixo.scatter([ponto[0]], [ponto[1]], s=tamanho, color=cor, edgecolor="white", linewidth=borda, zorder=4)
        eixo.annotate(
            "(%d, %d)" % ponto,
            ponto,
            textcoords="offset points",
            xytext=DESLOCAMENTOS_ROTULO.get(ponto, (6, 5)),
            fontsize=9,
            color=COR_TEXTO,
            zorder=5,
        )

    eixo.scatter(
        [CONSULTA_KD[0]],
        [CONSULTA_KD[1]],
        marker="*",
        s=190,
        color="#1b7f4d",
        edgecolor="white",
        linewidth=0.9,
        zorder=6,
    )
    eixo.annotate(
        "consulta (%d, %d)" % CONSULTA_KD,
        CONSULTA_KD,
        textcoords="offset points",
        xytext=(8, -12),
        fontsize=9.5,
        color="#1b7f4d",
        zorder=6,
    )
    circulo = plt.Circle(
        CONSULTA_KD,
        distancia,
        fill=False,
        color="#1b7f4d",
        linestyle=":",
        linewidth=1.3,
        zorder=5,
    )
    eixo.add_patch(circulo)

    eixo.set_xlim(limites[0], limites[1])
    eixo.set_ylim(limites[2], limites[3])
    eixo.set_xlabel("coordenada x", fontsize=10.5, color=COR_TEXTO)
    eixo.set_ylabel("coordenada y", fontsize=10.5, color=COR_TEXTO)
    eixo.tick_params(labelsize=9.5, colors=COR_ARESTA)
    eixo.set_title(
        "Particionamento do plano e raio de busca",
        fontsize=10.5,
        color=COR_TEXTO,
        pad=6,
    )
    for borda in eixo.spines.values():
        borda.set_color(COR_ARESTA)
        borda.set_linewidth(0.7)

    legenda = [
        plt.Line2D([0], [0], color=COR_BORDA, linewidth=1.6, label="corte no eixo x"),
        plt.Line2D(
            [0], [0], color=COR_BORDA_DESTAQUE, linewidth=1.6, linestyle="--", label="corte no eixo y"
        ),
        plt.Line2D(
            [0],
            [0],
            marker="o",
            color="none",
            markerfacecolor=COR_BORDA_DESTAQUE,
            markersize=7,
            label="ponto visitado",
        ),
        plt.Line2D(
            [0],
            [0],
            marker="o",
            color="none",
            markerfacecolor="#9aa5b1",
            markersize=7,
            label="ponto não visitado",
        ),
    ]
    eixo.legend(handles=legenda, fontsize=8.5, loc="lower right", framealpha=0.94)

    caminho = os.path.join(DESTINO, "kdtree_particao.png")
    figura.tight_layout()
    figura.savefig(caminho, dpi=220, bbox_inches="tight", facecolor="white")
    plt.close(figura)
    return caminho, vizinho, distancia, len(visitados), len(podados)


def main():
    """Gera todas as figuras de demonstração visual."""
    os.makedirs(DESTINO, exist_ok=True)
    print(gerar_trie())
    print(gerar_patricia())
    print(gerar_splay())
    print(gerar_treap())
    caminho_kd, removido, visitados, podados = gerar_kdtree()
    print(caminho_kd)
    caminho_particao, vizinho, distancia, total_visitados, total_podados = gerar_particao_kd()
    print(caminho_particao)
    print(
        "KD-Tree: raiz removida %s; vizinho de %s é %s a distância %.3f; "
        "%d nós visitados e %d subárvore(s) podada(s)"
        % (removido, CONSULTA_KD, vizinho, distancia, total_visitados, total_podados)
    )


if __name__ == "__main__":
    main()
