"""Conversão das estruturas implementadas em árvores de exibição."""

from .layout import DrawNode


def trie_to_draw(node, edge_label="", accumulated="", highlights=frozenset()):
    """Converte uma trie em árvore de exibição com um caractere por aresta."""
    children = [
        trie_to_draw(node.children[symbol], symbol, accumulated + symbol, highlights)
        for symbol in sorted(node.children)
    ]
    return DrawNode(
        label=accumulated if node.is_terminal else "",
        edge_label=edge_label,
        children=children,
        terminal=node.is_terminal,
        highlight=accumulated in highlights,
    )


def patricia_to_draw(node, accumulated="", highlights=frozenset()):
    """Converte uma árvore Patricia em árvore de exibição com rótulos nas arestas."""
    children = [
        patricia_to_draw(child, accumulated + child.label, highlights)
        for _symbol, child in sorted(node.children.items())
    ]
    return DrawNode(
        label=accumulated if node.is_terminal else "",
        edge_label=node.label,
        children=children,
        terminal=node.is_terminal,
        highlight=accumulated in highlights,
    )


def binary_to_draw(node, label, sublabel=None, highlight=None, depth=0):
    """Converte uma árvore binária em árvore de exibição preservando a ordem simétrica."""
    if node is None:
        return None
    return DrawNode(
        label=label(node, depth),
        sublabel="" if sublabel is None else sublabel(node, depth),
        children=[
            binary_to_draw(node.left, label, sublabel, highlight, depth + 1),
            binary_to_draw(node.right, label, sublabel, highlight, depth + 1),
        ],
        highlight=False if highlight is None else highlight(node, depth),
    )
