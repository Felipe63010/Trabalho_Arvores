"""Árvore Splay com reestruturação top-down (SLEATOR; TARJAN, 1985).

A árvore splay é uma árvore binária de busca autoajustável: não armazena
qualquer informação de balanceamento e, a cada acesso, aplica a operação
``splay``, que leva o nó acessado até a raiz por meio das transformações
``zig``, ``zig-zig`` e ``zig-zag``. O custo individual de uma operação pode
ser ``O(n)``, mas o custo amortizado de qualquer sequência de ``m``
operações sobre ``n`` chaves é ``O(log n)`` por operação.

A variante implementada é a ``top-down``, que executa a reestruturação em
uma única descida, dispensa ponteiros para o pai e não utiliza recursão,
evitando estouro de pilha em árvores degeneradas.
"""

from .instrumentation import Counters


class SplayNode:
    """Nó de uma árvore binária de busca autoajustável."""

    __slots__ = ("key", "value", "left", "right")

    def __init__(self, key, value=None):
        self.key = key
        self.value = value
        self.left = None
        self.right = None


class SplayTree:
    """Árvore splay com inserção, busca, remoção e percurso em ordem."""

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
        """Insere ``key`` e a promove à raiz.

        Retorna ``True`` se a chave era inédita e ``False`` se apenas o
        valor associado foi atualizado.
        """
        if self.root is None:
            self.root = SplayNode(key, value)
            self.counters.nodes_created += 1
            self._size = 1
            return True
        self.root = self._splay(self.root, key)
        self.counters.comparisons += 1
        if self.root.key == key:
            self.root.value = value
            return False
        node = SplayNode(key, value)
        self.counters.nodes_created += 1
        self.counters.comparisons += 1
        if key < self.root.key:
            node.left = self.root.left
            node.right = self.root
            self.root.left = None
        else:
            node.right = self.root.right
            node.left = self.root
            self.root.right = None
        self.root = node
        self._size += 1
        return True

    def search(self, key, default=None):
        """Busca ``key`` e a promove à raiz; retorna o valor ou ``default``."""
        if self.root is None:
            return default
        self.root = self._splay(self.root, key)
        self.counters.comparisons += 1
        if self.root.key == key:
            return self.root.value
        return default

    def contains(self, key):
        """Informa se ``key`` pertence à árvore, promovendo-a à raiz."""
        if self.root is None:
            return False
        self.root = self._splay(self.root, key)
        self.counters.comparisons += 1
        return self.root.key == key

    def remove(self, key):
        """Remove ``key`` unindo as duas subárvores resultantes.

        Retorna ``True`` se a chave existia.
        """
        if self.root is None:
            return False
        self.root = self._splay(self.root, key)
        self.counters.comparisons += 1
        if self.root.key != key:
            return False
        left, right = self.root.left, self.root.right
        if left is None:
            self.root = right
        else:
            left = self._splay(left, key)
            left.right = right
            self.root = left
        self._size -= 1
        self.counters.nodes_removed += 1
        return True

    def minimum(self):
        """Retorna a menor chave e a promove à raiz."""
        if self.root is None:
            return None
        node = self.root
        while node.left is not None:
            self.counters.node_visits += 1
            node = node.left
        self.root = self._splay(self.root, node.key)
        return self.root.key

    def maximum(self):
        """Retorna a maior chave e a promove à raiz."""
        if self.root is None:
            return None
        node = self.root
        while node.right is not None:
            self.counters.node_visits += 1
            node = node.right
        self.root = self._splay(self.root, node.key)
        return self.root.key

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

    def _splay(self, root, key):
        """Reestrutura a árvore trazendo ``key`` (ou seu vizinho) à raiz."""
        if root is None:
            return None
        header = SplayNode(None)
        left_tree, right_tree = header, header
        node = root
        while True:
            self.counters.node_visits += 1
            self.counters.comparisons += 1
            if key < node.key:
                if node.left is None:
                    break
                self.counters.comparisons += 1
                if key < node.left.key:
                    node = self._rotate_right(node)
                    if node.left is None:
                        break
                right_tree.left = node
                right_tree = node
                node = node.left
            elif key > node.key:
                if node.right is None:
                    break
                self.counters.comparisons += 1
                if key > node.right.key:
                    node = self._rotate_left(node)
                    if node.right is None:
                        break
                left_tree.right = node
                left_tree = node
                node = node.right
            else:
                break
        left_tree.right = node.left
        right_tree.left = node.right
        node.left = header.right
        node.right = header.left
        return node

    def _rotate_right(self, node):
        self.counters.rotations += 1
        pivot = node.left
        node.left = pivot.right
        pivot.right = node
        return pivot

    def _rotate_left(self, node):
        self.counters.rotations += 1
        pivot = node.right
        node.right = pivot.left
        pivot.left = node
        return pivot
