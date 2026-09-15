"""Implementações de estruturas em árvore avançadas.

O pacote reúne as cinco estruturas exigidas pelo trabalho - trie, árvore
Patricia, árvore splay, treap e KD-Tree - e duas estruturas de referência
- árvore binária de busca e árvore AVL - utilizadas nas comparações
teóricas e experimentais.
"""

from .avl import AVLTree
from .bst import BinarySearchTree
from .instrumentation import Counters
from .kdtree import KDTree
from .patricia import PatriciaTree
from .splay import SplayTree
from .treap import Treap
from .trie import Trie

__all__ = [
    "AVLTree",
    "BinarySearchTree",
    "Counters",
    "KDTree",
    "PatriciaTree",
    "SplayTree",
    "Treap",
    "Trie",
]
