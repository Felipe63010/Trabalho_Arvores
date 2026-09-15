"""Árvore Treap: árvore binária de busca com balanceamento probabilístico.

Cada nó armazena uma chave e uma prioridade sorteada de forma independente
e uniforme. A estrutura respeita simultaneamente duas invariantes:

* ordem simétrica das chaves, como em uma árvore binária de busca;
* ordem de heap máximo das prioridades, isto é, a prioridade de um nó é
  maior ou igual à de seus filhos.

Como as prioridades são aleatórias, a forma da árvore corresponde à de uma
árvore binária de busca construída a partir de uma permutação aleatória das
chaves, cuja altura esperada é ``O(log n)`` independentemente da ordem em
que as chaves são inseridas.
"""

import random

from .instrumentation import Counters


class TreapNode:
    """Nó da treap, com prioridade e tamanho da subárvore."""

    __slots__ = ("key", "value", "priority", "left", "right", "size")

    def __init__(self, key, value=None, priority=0.0):
        self.key = key
        self.value = value
        self.priority = priority
        self.left = None
        self.right = None
        self.size = 1


class Treap:
    """Treap com inserção, busca, remoção, divisão, união e estatísticas de ordem."""

    def __init__(self, seed=None):
        self.root = None
        self.counters = Counters()
        self._random = random.Random(seed)

    def __len__(self):
        return self._subtree_size(self.root)

    def __contains__(self, key):
        return self.contains(key)

    @property
    def node_count(self):
        """Número de nós alocados."""
        return self._subtree_size(self.root)

    def insert(self, key, value=None, priority=None):
        """Insere ``key`` e restabelece a ordem de heap por rotações.

        Retorna ``True`` se a chave era inédita e ``False`` se apenas o
        valor associado foi atualizado.
        """
        if priority is None:
            priority = self._random.random()
        self.root, inserted = self._insert(self.root, key, value, priority)
        return inserted

    def search(self, key, default=None):
        """Retorna o valor associado a ``key`` ou ``default`` se ausente."""
        node = self.root
        while node is not None:
            self.counters.node_visits += 1
            self.counters.comparisons += 1
            if key == node.key:
                return node.value
            self.counters.comparisons += 1
            node = node.left if key < node.key else node.right
        return default

    def contains(self, key):
        """Informa se ``key`` pertence à árvore."""
        node = self.root
        while node is not None:
            self.counters.node_visits += 1
            self.counters.comparisons += 1
            if key == node.key:
                return True
            self.counters.comparisons += 1
            node = node.left if key < node.key else node.right
        return False

    def remove(self, key):
        """Remove ``key`` rotacionando o nó até que se torne uma folha.

        Retorna ``True`` se a chave existia.
        """
        self.root, removed = self._remove(self.root, key)
        if removed:
            self.counters.nodes_removed += 1
        return removed

    def split(self, key):
        """Divide a treap em duas: chaves ``< key`` e chaves ``>= key``.

        A árvore original torna-se vazia e as duas partes são devolvidas
        como treaps independentes que compartilham os contadores da árvore
        de origem, preservando a continuidade da instrumentação.
        """
        left, right = self._split(self.root, key)
        self.root = None
        first, second = Treap(), Treap()
        first.root, second.root = left, right
        first.counters = second.counters = self.counters
        return first, second

    def join(self, other):
        """Une ``other`` a esta treap, assumindo chaves maiores em ``other``.

        A treap ``other`` torna-se vazia.
        """
        self.root = self._join(self.root, other.root)
        other.root = None
        return self

    def kth(self, index):
        """Retorna a ``index``-ésima menor chave, com ``index`` iniciando em zero."""
        total = self._subtree_size(self.root)
        if index < 0 or index >= total:
            raise IndexError("índice fora dos limites da treap")
        node = self.root
        while True:
            self.counters.node_visits += 1
            left_size = self._subtree_size(node.left)
            if index < left_size:
                node = node.left
            elif index == left_size:
                return node.key
            else:
                index -= left_size + 1
                node = node.right

    def rank(self, key):
        """Número de chaves estritamente menores que ``key``."""
        node = self.root
        smaller = 0
        while node is not None:
            self.counters.node_visits += 1
            self.counters.comparisons += 1
            if key <= node.key:
                node = node.left
            else:
                smaller += self._subtree_size(node.left) + 1
                node = node.right
        return smaller

    def minimum(self):
        """Retorna a menor chave armazenada."""
        node = self.root
        if node is None:
            return None
        while node.left is not None:
            self.counters.node_visits += 1
            node = node.left
        return node.key

    def maximum(self):
        """Retorna a maior chave armazenada."""
        node = self.root
        if node is None:
            return None
        while node.right is not None:
            self.counters.node_visits += 1
            node = node.right
        return node.key

    def keys(self):
        """Percurso em ordem, sem recursão, devolvendo as chaves ordenadas."""
        result = []
        stack = []
        node = self.root
        while stack or node is not None:
            while node is not None:
                stack.append(node)
                node = node.left
            node = stack.pop()
            result.append(node.key)
            node = node.right
        return result

    def height(self):
        """Altura da árvore medida em número de arestas."""
        if self.root is None:
            return -1
        best = 0
        stack = [(self.root, 0)]
        while stack:
            node, depth = stack.pop()
            if depth > best:
                best = depth
            if node.left is not None:
                stack.append((node.left, depth + 1))
            if node.right is not None:
                stack.append((node.right, depth + 1))
        return best

    def _insert(self, node, key, value, priority):
        if node is None:
            self.counters.nodes_created += 1
            return TreapNode(key, value, priority), True
        self.counters.node_visits += 1
        self.counters.comparisons += 1
        if key == node.key:
            node.value = value
            return node, False
        self.counters.comparisons += 1
        if key < node.key:
            node.left, inserted = self._insert(node.left, key, value, priority)
            self.counters.comparisons += 1
            if node.left.priority > node.priority:
                node = self._rotate_right(node)
        else:
            node.right, inserted = self._insert(node.right, key, value, priority)
            self.counters.comparisons += 1
            if node.right.priority > node.priority:
                node = self._rotate_left(node)
        self._update(node)
        return node, inserted

    def _remove(self, node, key):
        if node is None:
            return None, False
        self.counters.node_visits += 1
        self.counters.comparisons += 1
        if key == node.key:
            return self._remove_root(node), True
        self.counters.comparisons += 1
        if key < node.key:
            node.left, removed = self._remove(node.left, key)
        else:
            node.right, removed = self._remove(node.right, key)
        self._update(node)
        return node, removed

    def _remove_root(self, node):
        if node.left is None:
            return node.right
        if node.right is None:
            return node.left
        self.counters.comparisons += 1
        if node.left.priority > node.right.priority:
            node = self._rotate_right(node)
            node.right = self._remove_root(node.right)
        else:
            node = self._rotate_left(node)
            node.left = self._remove_root(node.left)
        self._update(node)
        return node

    def _split(self, node, key):
        if node is None:
            return None, None
        self.counters.node_visits += 1
        self.counters.comparisons += 1
        if node.key < key:
            left, right = self._split(node.right, key)
            node.right = left
            self._update(node)
            return node, right
        left, right = self._split(node.left, key)
        node.left = right
        self._update(node)
        return left, node

    def _join(self, left, right):
        if left is None:
            return right
        if right is None:
            return left
        self.counters.node_visits += 1
        self.counters.comparisons += 1
        if left.priority > right.priority:
            left.right = self._join(left.right, right)
            self._update(left)
            return left
        right.left = self._join(left, right.left)
        self._update(right)
        return right

    def _rotate_right(self, node):
        self.counters.rotations += 1
        pivot = node.left
        node.left = pivot.right
        pivot.right = node
        self._update(node)
        self._update(pivot)
        return pivot

    def _rotate_left(self, node):
        self.counters.rotations += 1
        pivot = node.right
        node.right = pivot.left
        pivot.left = node
        self._update(node)
        self._update(pivot)
        return pivot

    def _update(self, node):
        node.size = 1 + self._subtree_size(node.left) + self._subtree_size(node.right)

    @staticmethod
    def _subtree_size(node):
        return 0 if node is None else node.size
