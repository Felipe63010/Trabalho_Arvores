"""Árvore binária de busca sem balanceamento, usada como referência.

Esta implementação serve de linha de base para a comparação exigida no
trabalho: a ausência de qualquer mecanismo de reequilíbrio faz com que a
altura da árvore dependa diretamente da ordem de inserção, variando de
``O(log n)`` para chaves aleatórias a ``O(n)`` para chaves ordenadas.
Todas as operações são iterativas, de modo que a degeneração em lista
encadeada não provoque estouro de pilha.
"""

from .instrumentation import Counters


class BSTNode:
    """Nó de uma árvore binária de busca."""

    __slots__ = ("key", "value", "left", "right")

    def __init__(self, key, value=None):
        self.key = key
        self.value = value
        self.left = None
        self.right = None


class BinarySearchTree:
    """Árvore binária de busca com inserção, busca, remoção e percurso em ordem."""

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
        """Insere ``key`` como folha, mantendo a ordem simétrica."""
        if self.root is None:
            self.root = BSTNode(key, value)
            self.counters.nodes_created += 1
            self._size = 1
            return True
        node = self.root
        while True:
            self.counters.node_visits += 1
            self.counters.comparisons += 1
            if key == node.key:
                node.value = value
                return False
            self.counters.comparisons += 1
            if key < node.key:
                if node.left is None:
                    node.left = BSTNode(key, value)
                    break
                node = node.left
            else:
                if node.right is None:
                    node.right = BSTNode(key, value)
                    break
                node = node.right
        self.counters.nodes_created += 1
        self._size += 1
        return True

    def search(self, key, default=None):
        """Retorna o valor associado a ``key`` ou ``default`` se ausente."""
        node = self._locate(key)[0]
        return default if node is None else node.value

    def contains(self, key):
        """Informa se ``key`` pertence à árvore."""
        return self._locate(key)[0] is not None

    def remove(self, key):
        """Remove ``key`` pelo algoritmo de Hibbard; retorna ``True`` se existia."""
        node, parent = self._locate(key)
        if node is None:
            return False
        if node.left is not None and node.right is not None:
            successor_parent, successor = node, node.right
            while successor.left is not None:
                self.counters.node_visits += 1
                successor_parent, successor = successor, successor.left
            node.key, node.value = successor.key, successor.value
            node, parent = successor, successor_parent
        child = node.left if node.left is not None else node.right
        if parent is None:
            self.root = child
        elif parent.left is node:
            parent.left = child
        else:
            parent.right = child
        self._size -= 1
        self.counters.nodes_removed += 1
        return True

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

    def _locate(self, key):
        node = self.root
        parent = None
        while node is not None:
            self.counters.node_visits += 1
            self.counters.comparisons += 1
            if key == node.key:
                return node, parent
            self.counters.comparisons += 1
            parent = node
            node = node.left if key < node.key else node.right
        return None, None
