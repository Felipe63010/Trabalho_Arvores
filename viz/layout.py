"""Layout e renderização das árvores em figuras vetoriais rasterizadas.

O módulo implementa um algoritmo de posicionamento independente da
estrutura desenhada. Uma árvore de exibição (:class:`DrawNode`) é mapeada
em coordenadas cartesianas por duas estratégias:

* árvores binárias recebem abscissas pelo percurso em ordem, o que
  preserva visualmente a ordem simétrica das chaves e distingue filhos a
  esquerda de filhos a direita mesmo quando o nó possui um único filho;
* árvores de grau arbitrário recebem abscissas pela regra das folhas
  consecutivas, com cada nó interno centralizado sobre seus descendentes.

A renderização é feita com Matplotlib e não depende de ferramentas
externas de desenho de grafos.
"""

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Circle, FancyBboxPatch

COR_PREENCHIMENTO = "#e8eef7"
COR_BORDA = "#2b4a72"
COR_DESTAQUE = "#fde3c0"
COR_BORDA_DESTAQUE = "#b25f12"
COR_ARESTA = "#5a6673"
COR_TEXTO = "#12202f"


class DrawNode:
    """No de exibição, independente da estrutura de dados de origem."""

    __slots__ = ("label", "sublabel", "edge_label", "children", "highlight", "terminal")

    def __init__(
        self,
        label="",
        sublabel="",
        edge_label="",
        children=None,
        highlight=False,
        terminal=False,
    ):
        self.label = label
        self.sublabel = sublabel
        self.edge_label = edge_label
        self.children = list(children) if children else []
        self.highlight = highlight
        self.terminal = terminal


def compute_positions(root, binary=False):
    """Mapeia cada nó de exibição em uma coordenada ``(x, y)``."""
    positions = {}
    cursor = [0.0]

    def place(node, depth):
        if node is None:
            return
        if binary:
            left = node.children[0] if len(node.children) > 0 else None
            right = node.children[1] if len(node.children) > 1 else None
            place(left, depth + 1)
            positions[id(node)] = (cursor[0], -float(depth))
            cursor[0] += 1.0
            place(right, depth + 1)
        else:
            filhos = [child for child in node.children if child is not None]
            if not filhos:
                positions[id(node)] = (cursor[0], -float(depth))
                cursor[0] += 1.0
                return
            for child in filhos:
                place(child, depth + 1)
            abscissas = [positions[id(child)][0] for child in filhos]
            positions[id(node)] = ((min(abscissas) + max(abscissas)) / 2.0, -float(depth))

    place(root, 0)
    return positions


def _iterate(root):
    pilha = [root]
    while pilha:
        node = pilha.pop()
        if node is None:
            continue
        yield node
        for child in node.children:
            pilha.append(child)


def draw_tree(axes, root, binary=False, node_style="box", y_gap=1.35, font_size=9.0, y_limits=None):
    """Desenha a árvore de exibição em um eixo do Matplotlib."""
    positions = compute_positions(root, binary=binary)
    if not positions:
        axes.axis("off")
        return 1.0, 1.0

    escalar = {chave: (x, y * y_gap) for chave, (x, y) in positions.items()}
    raio = 0.16 if node_style == "point" else 0.30
    largura, altura = 0.86, 0.62

    for node in _iterate(root):
        origem = escalar[id(node)]
        for child in node.children:
            if child is None:
                continue
            destino = escalar[id(child)]
            axes.add_line(
                Line2D(
                    [origem[0], destino[0]],
                    [origem[1], destino[1]],
                    color=COR_ARESTA,
                    linewidth=1.0,
                    zorder=1,
                )
            )
            if child.edge_label:
                meio_x = (origem[0] + destino[0]) / 2.0
                meio_y = (origem[1] + destino[1]) / 2.0
                axes.text(
                    meio_x,
                    meio_y,
                    child.edge_label,
                    fontsize=font_size - 0.5,
                    ha="center",
                    va="center",
                    color=COR_TEXTO,
                    zorder=3,
                    bbox=dict(boxstyle="round,pad=0.16", facecolor="white", edgecolor="none"),
                )

    for node in _iterate(root):
        x, y = escalar[id(node)]
        preenchimento = COR_DESTAQUE if node.highlight else COR_PREENCHIMENTO
        borda = COR_BORDA_DESTAQUE if node.highlight else COR_BORDA
        espessura = 1.8 if node.highlight else 1.0
        if node_style == "point":
            if node.terminal:
                axes.add_patch(
                    Circle(
                        (x, y),
                        raio * 1.5,
                        facecolor="none",
                        edgecolor=borda,
                        linewidth=espessura,
                        zorder=2,
                    )
                )
            axes.add_patch(
                Circle(
                    (x, y),
                    raio,
                    facecolor=borda if node.terminal else preenchimento,
                    edgecolor=borda,
                    linewidth=espessura,
                    zorder=3,
                )
            )
            if node.label and not node.children:
                axes.text(
                    x,
                    y - raio * 2.6,
                    node.label,
                    fontsize=font_size - 1.0,
                    ha="center",
                    va="top",
                    color=COR_TEXTO,
                    zorder=4,
                )
        else:
            axes.add_patch(
                FancyBboxPatch(
                    (x - largura / 2.0, y - altura / 2.0),
                    largura,
                    altura,
                    boxstyle="round,pad=0.04,rounding_size=0.12",
                    facecolor=preenchimento,
                    edgecolor=borda,
                    linewidth=espessura,
                    zorder=2,
                )
            )
            if node.sublabel:
                axes.text(
                    x,
                    y + 0.10,
                    node.label,
                    fontsize=font_size,
                    ha="center",
                    va="center",
                    color=COR_TEXTO,
                    zorder=4,
                )
                axes.text(
                    x,
                    y - 0.15,
                    node.sublabel,
                    fontsize=font_size * 0.82,
                    ha="center",
                    va="center",
                    color=COR_ARESTA,
                    zorder=4,
                )
            else:
                axes.text(
                    x,
                    y,
                    node.label,
                    fontsize=font_size,
                    ha="center",
                    va="center",
                    color=COR_TEXTO,
                    zorder=4,
                )

    abscissas = [ponto[0] for ponto in escalar.values()]
    ordenadas = [ponto[1] for ponto in escalar.values()]
    margem_x = 0.8
    margem_y = 0.7
    axes.set_xlim(min(abscissas) - margem_x, max(abscissas) + margem_x)
    if y_limits is None:
        axes.set_ylim(min(ordenadas) - margem_y, max(ordenadas) + margem_y)
    else:
        axes.set_ylim(y_limits[0], y_limits[1])
    axes.set_aspect("equal")
    axes.axis("off")
    return (max(abscissas) - min(abscissas)) + 2 * margem_x, (
        max(ordenadas) - min(ordenadas)
    ) + 2 * margem_y


def render_panels(
    panels,
    output_path,
    binary=False,
    node_style="box",
    unit=0.5,
    font_scale=0.30,
    orientation="horizontal",
    y_gap=1.35,
):
    """Renderiza vários estados de uma mesma estrutura em uma única figura.

    ``panels`` é uma sequência de pares ``(título, raiz_de_exibição)``. Todos
    os painéis compartilham a mesma escala de desenho, de modo que os
    estados sucessivos possam ser comparados diretamente. O tamanho da
    fonte é derivado de ``unit`` para que a legibilidade seja preservada
    após o redimensionamento da figura no documento final.
    """
    caixas = []
    for _titulo, raiz in panels:
        posicoes = compute_positions(raiz, binary=binary)
        abscissas = [ponto[0] for ponto in posicoes.values()] or [0.0]
        ordenadas = [ponto[1] * y_gap for ponto in posicoes.values()] or [0.0]
        caixas.append((min(abscissas), max(abscissas), min(ordenadas), max(ordenadas)))

    margem_x, margem_y = 0.8, 0.7
    larguras = [caixa[1] - caixa[0] + 2 * margem_x for caixa in caixas]
    inferior = min(caixa[2] for caixa in caixas) - margem_y
    superior = max(caixa[3] for caixa in caixas) + margem_y
    altura_comum = superior - inferior
    font_size = font_scale * unit * 72.0
    espaco_titulo = 0.34

    if orientation == "horizontal":
        figura, eixos = plt.subplots(
            1,
            len(panels),
            figsize=(sum(larguras) * unit, altura_comum * unit + espaco_titulo),
            gridspec_kw={"width_ratios": larguras},
        )
        limites = [(inferior, superior)] * len(panels)
    else:
        alturas = [caixa[3] - caixa[2] + 2 * margem_y for caixa in caixas]
        largura_comum = max(larguras)
        figura, eixos = plt.subplots(
            len(panels),
            1,
            figsize=(largura_comum * unit, sum(alturas) * unit + espaco_titulo * len(panels)),
            gridspec_kw={"height_ratios": alturas},
        )
        limites = [None] * len(panels)

    if len(panels) == 1:
        eixos = [eixos]

    for eixo, (titulo, raiz), limite in zip(eixos, panels, limites):
        draw_tree(
            eixo,
            raiz,
            binary=binary,
            node_style=node_style,
            y_gap=y_gap,
            font_size=font_size,
            y_limits=limite,
        )
        eixo.set_title(titulo, fontsize=font_size, loc="left", color=COR_TEXTO, pad=4)

    figura.tight_layout(h_pad=0.7, w_pad=0.5)
    figura.savefig(output_path, dpi=220, bbox_inches="tight", facecolor="white")
    plt.close(figura)
    return output_path
