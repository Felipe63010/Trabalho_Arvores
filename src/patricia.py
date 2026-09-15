"""Árvore Patricia na formulação de radix tree compacta.

Enquanto a trie dedica um nó a cada caractere da chave, a árvore Patricia
rotula cada aresta com uma subcadeia e elimina todo nó interno que possua
um único filho e não represente o fim de uma chave. A estrutura preserva o
tempo de busca proporcional ao comprimento da chave, mas reduz o número de
nós de ``O(n * m)`` para ``O(n)``, em que ``n`` é a quantidade de chaves e
``m`` o comprimento médio das chaves.

Duas operações estruturais mantêm a invariante de compactação:

* ``split`` - divide o rótulo de uma aresta quando uma nova chave diverge
  no meio dela;
* ``merge`` - concatena um nó não terminal de filho único ao seu filho após
  uma remoção.
"""

from .instrumentation import Counters


class PatriciaNode:
    """Nó da árvore Patricia; ``label`` é o rótulo da aresta que chega nele."""

    __slots__ = ("label", "children", "is_terminal", "value")

    def __init__(self, label="", is_terminal=False, value=None):
        self.label = label
        self.children = {}
        self.is_terminal = is_terminal
        self.value = value


class PatriciaTree:
    """Radix tree compacta com inserção, busca, remoção e consultas por prefixo."""

    def __init__(self):
        self.root = PatriciaNode()
        self.counters = Counters()
        self._size = 0
        self._nodes = 1
        self.counters.nodes_created += 1

    def __len__(self):
        return self._size

    def __contains__(self, key):
        return self.contains(key)

    @property
    def node_count(self):
        """Número de nós alocados, incluindo a raiz."""
        return self._nodes

    def label_chars(self):
        """Soma dos comprimentos de todos os rótulos armazenados."""
        total = 0
        stack = [self.root]
        while stack:
            node = stack.pop()
            total += len(node.label)
            stack.extend(node.children.values())
        return total

    def insert(self, key, value=None):
        """Insere ``key``, dividindo rótulos sempre que houver divergência parcial."""
        self._validate(key)
        node = self.root
        rest = key
        while True:
            if not rest:
                self.counters.node_visits += 1
                node.value = value
                if node.is_terminal:
                    return False
                node.is_terminal = True
                self._size += 1
                return True
            symbol = rest[0]
            child = node.children.get(symbol)
            self.counters.node_visits += 1
            self.counters.comparisons += 1
            if child is None:
                node.children[symbol] = PatriciaNode(rest, True, value)
                self._nodes += 1
                self._size += 1
                self.counters.nodes_created += 1
                return True
            shared = self._common_prefix_length(child.label, rest)
            self.counters.comparisons += shared
            if shared == len(child.label):
                node = child
                rest = rest[shared:]
                continue
            bridge = PatriciaNode(child.label[:shared])
            child.label = child.label[shared:]
            bridge.children[child.label[0]] = child
            node.children[symbol] = bridge
            self._nodes += 1
            self.counters.nodes_created += 1
            self.counters.splits += 1
            rest = rest[shared:]
            if not rest:
                bridge.is_terminal = True
                bridge.value = value
            else:
                bridge.children[rest[0]] = PatriciaNode(rest, True, value)
                self._nodes += 1
                self.counters.nodes_created += 1
            self._size += 1
            return True

    def search(self, key, default=None):
        """Retorna o valor associado a ``key`` ou ``default`` se ausente."""
        node = self._descend_exact(key)
        if node is None or not node.is_terminal:
            return default
        return node.value

    def contains(self, key):
        """Informa se ``key`` pertence ao conjunto armazenado."""
        node = self._descend_exact(key)
        return node is not None and node.is_terminal

    def remove(self, key):
        """Remove ``key`` e restaura a compactação da árvore.

        Retorna ``True`` se a chave existia.
        """
        self._validate(key)
        path = []
        node = self.root
        rest = key
        while rest:
            symbol = rest[0]
            child = node.children.get(symbol)
            self.counters.node_visits += 1
            self.counters.comparisons += 1
            if child is None or not rest.startswith(child.label):
                return False
            path.append((node, child))
            node = child
            rest = rest[len(child.label):]
        if not node.is_terminal:
            return False
        node.is_terminal = False
        node.value = None
        self._size -= 1
        while path:
            parent, current = path[-1]
            if not current.is_terminal and not current.children:
                del parent.children[current.label[0]]
                self._nodes -= 1
                self.counters.nodes_removed += 1
                path.pop()
                continue
            if not current.is_terminal and len(current.children) == 1:
                only_child = next(iter(current.children.values()))
                del parent.children[current.label[0]]
                only_child.label = current.label + only_child.label
                parent.children[only_child.label[0]] = only_child
                self._nodes -= 1
                self.counters.nodes_removed += 1
                self.counters.merges += 1
            break
        return True

    def starts_with(self, prefix):
        """Informa se existe alguma chave armazenada com o prefixo dado."""
        return self._descend_prefix(prefix) is not None

    def keys_with_prefix(self, prefix):
        """Lista, em ordem lexicográfica, as chaves que iniciam por ``prefix``."""
        found = self._descend_prefix(prefix)
        if found is None:
            return []
        node, accumulated = found
        return list(self._collect(node, accumulated))

    def longest_prefix_of(self, text):
        """Retorna a maior chave armazenada que é prefixo de ``text``."""
        self._validate(text)
        node = self.root
        best = None
        consumed = 0
        if node.is_terminal:
            best = ""
        while consumed < len(text):
            symbol = text[consumed]
            child = node.children.get(symbol)
            self.counters.node_visits += 1
            self.counters.comparisons += 1
            if child is None or not text.startswith(child.label, consumed):
                break
            consumed += len(child.label)
            node = child
            if node.is_terminal:
                best = text[:consumed]
        return best

    def keys(self):
        """Lista todas as chaves em ordem lexicográfica."""
        return list(self._collect(self.root, ""))

    def height(self):
        """Altura da árvore medida em número de arestas."""
        best = 0
        stack = [(self.root, 0)]
        while stack:
            node, depth = stack.pop()
            if depth > best:
                best = depth
            for child in node.children.values():
                stack.append((child, depth + 1))
        return best

    def _descend_exact(self, key):
        self._validate(key)
        node = self.root
        rest = key
        while rest:
            symbol = rest[0]
            child = node.children.get(symbol)
            self.counters.node_visits += 1
            self.counters.comparisons += 1
            if child is None or not rest.startswith(child.label):
                return None
            node = child
            rest = rest[len(child.label):]
        return node

    def _descend_prefix(self, prefix):
        self._validate(prefix)
        node = self.root
        rest = prefix
        accumulated = ""
        while rest:
            symbol = rest[0]
            child = node.children.get(symbol)
            self.counters.node_visits += 1
            self.counters.comparisons += 1
            if child is None:
                return None
            if rest.startswith(child.label):
                accumulated += child.label
                rest = rest[len(child.label):]
                node = child
            elif child.label.startswith(rest):
                accumulated += child.label
                node = child
                rest = ""
            else:
                return None
        return node, accumulated

    def _collect(self, node, accumulated):
        stack = [(node, accumulated)]
        while stack:
            current, text = stack.pop()
            if current.is_terminal:
                yield text
            for symbol in sorted(current.children, reverse=True):
                child = current.children[symbol]
                stack.append((child, text + child.label))

    @staticmethod
    def _common_prefix_length(first, second):
        limit = min(len(first), len(second))
        index = 0
        while index < limit and first[index] == second[index]:
            index += 1
        return index

    @staticmethod
    def _validate(key):
        if not isinstance(key, str):
            raise TypeError("a árvore Patricia aceita apenas chaves do tipo str")
