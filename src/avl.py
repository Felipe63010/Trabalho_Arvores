"""Árvore AVL, usada como referência de balanceamento estrito.

A AVL mantém, em todo nó, a diferença entre as alturas das subárvores
limitada a uma unidade. A invariante é restaurada após cada inserção ou
remoção por meio de rotações simples e duplas, o que garante altura
``O(log n)`` no pior caso, ao custo de armazenar e atualizar o fator de
balanceamento e de executar rotações mesmo em cargas de trabalho em que
elas não trazem benefício.
"""

from .instrumentation import Counters


class AVLNode:
    """Nó de uma árvore AVL, com a altura da subárvore armazenada."""

    __slots__ = ("key", "value", "left", "right", "height")

    def __init__(self, key, value=None):
        self.key = key
        self.value = value
        self.left = None
        self.right = None
        self.height = 1


class AVLTree:
    """Árvore AVL com inserção, busca, remoção e percurso em ordem."""

    def __init__(self):
        self.root = None
        self.counters = Counters()
        self._size = 0

    def __len__(self):
        return self._size

    def __contains__(self, key):
        return self.contains(key)

    @property
    def node_count(self):
        """Número de nós alocados."""
        return self._size

    def insert(self, key, value=None):
        """Insere ``key`` e restaura a invariante de balanceamento."""
        self.root, inserted = self._insert(self.root, key, value)
        if inserted:
            self._size += 1
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
        """Remove ``key`` e restaura a invariante de balanceamento."""
        self.root, removed = self._remove(self.root, key)
        if removed:
            self._size -= 1
            self.counters.nodes_removed += 1
        return removed

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
        return self._height(self.root) - 1

    def _insert(self, node, key, value):
        if node is None:
            self.counters.nodes_created += 1
            return AVLNode(key, value), True
        self.counters.node_visits += 1
        self.counters.comparisons += 1
        if key == node.key:
            node.value = value
            return node, False
        self.counters.comparisons += 1
        if key < node.key:
            node.left, inserted = self._insert(node.left, key, value)
        else:
            node.right, inserted = self._insert(node.right, key, value)
        return self._rebalance(node), inserted

    def _remove(self, node, key):
        if node is None:
            return None, False
        self.counters.node_visits += 1
        self.counters.comparisons += 1
        if key == node.key:
            if node.left is None:
                return node.right, True
            if node.right is None:
                return node.left, True
            successor = node.right
            while successor.left is not None:
                self.counters.node_visits += 1
                successor = successor.left
            node.key, node.value = successor.key, successor.value
            node.right, _ = self._remove(node.right, successor.key)
            return self._rebalance(node), True
        self.counters.comparisons += 1
        if key < node.key:
            node.left, removed = self._remove(node.left, key)
        else:
            node.right, removed = self._remove(node.right, key)
        return self._rebalance(node), removed

    def _rebalance(self, node):
        self._update(node)
        balance = self._balance_factor(node)
        if balance > 1:
            if self._balance_factor(node.left) < 0:
                node.left = self._rotate_left(node.left)
            return self._rotate_right(node)
        if balance < -1:
            if self._balance_factor(node.right) > 0:
                node.right = self._rotate_right(node.right)
            return self._rotate_left(node)
        return node

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
        node.height = 1 + max(self._height(node.left), self._height(node.right))

    def _balance_factor(self, node):
        return self._height(node.left) - self._height(node.right)

    @staticmethod
    def _height(node):
        return 0 if node is None else node.height
