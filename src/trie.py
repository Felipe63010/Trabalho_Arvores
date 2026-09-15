"""Trie (árvore de prefixos) sobre alfabeto arbitrário.

A trie armazena um conjunto de chaves do tipo string distribuindo cada
caractere da chave em um nível distinto da árvore. Chaves com prefixo
comum compartilham o mesmo caminho a partir da raiz, de modo que o custo
de busca depende apenas do comprimento da chave e não da quantidade de
chaves armazenadas.
"""

from .instrumentation import Counters


class TrieNode:
    """No da trie: um caractere por aresta, um filho por caractere."""

    __slots__ = ("children", "is_terminal", "value") #Economiza ram pq trava a classe nesses 3 
                                                     #atributos exatos children, terminal e value   
    def __init__(self):
        self.children = {} #dicionário dinâmico {}. Se o nó só tem filho 'a', o dicionário tem tamanho 1, sem desperdiçar memória para as outras 25 letras
        self.is_terminal = False
        self.value = None


class Trie:
    """Árvore de prefixos com inserção, busca, remoção e consultas por prefixo."""

    def __init__(self):
        self.root = TrieNode()
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

    def insert(self, key, value=None):
        """Insere ``key`` associada a ``value``.

        Retorna ``True`` se a chave era inédita e ``False`` se apenas o
        valor associado foi atualizado.
        """
        self._validate(key)
        node = self.root
        for symbol in key:
            self.counters.node_visits += 1
            self.counters.comparisons += 1
            child = node.children.get(symbol)
            if child is None:
                child = TrieNode()
                node.children[symbol] = child
                self._nodes += 1
                self.counters.nodes_created += 1
            node = child
        self.counters.node_visits += 1
        node.value = value
        if node.is_terminal:
            return False
        node.is_terminal = True
        self._size += 1
        return True

    def search(self, key, default=None):
        """Retorna o valor associado a ``key`` ou ``default`` se ausente."""
        node = self._descend(key)
        if node is None or not node.is_terminal:
            return default
        return node.value

    def contains(self, key):
        """Informa se ``key`` pertence ao conjunto armazenado."""
        node = self._descend(key)
        return node is not None and node.is_terminal

    def remove(self, key):
        """Remove ``key``, podando os nós que deixam de ser necessários.

        Retorna ``True`` se a chave existia.
        """
        self._validate(key)
        path = []
        node = self.root
        for symbol in key:
            self.counters.node_visits += 1
            self.counters.comparisons += 1
            child = node.children.get(symbol)
            if child is None:
                return False
            path.append((node, symbol))
            node = child
        if not node.is_terminal:
            return False
        node.is_terminal = False
        node.value = None
        self._size -= 1
        while path and not node.is_terminal and not node.children:
            parent, symbol = path.pop()
            del parent.children[symbol]
            self._nodes -= 1
            self.counters.nodes_removed += 1
            node = parent
        return True

    def starts_with(self, prefix):
        """Informa se existe alguma chave armazenada com o prefixo dado."""
        return self._descend(prefix) is not None

    def keys_with_prefix(self, prefix):
        """Lista, em ordem lexicográfica, as chaves que iniciam por ``prefix``."""
        self._validate(prefix)
        node = self._descend(prefix)
        if node is None:
            return []
        return list(self._collect(node, prefix))

    def longest_prefix_of(self, text):
        """Retorna a maior chave armazenada que é prefixo de ``text``."""
        self._validate(text)
        node = self.root
        best = None
        consumed = 0
        if node.is_terminal:
            best = ""
        for symbol in text:
            self.counters.node_visits += 1
            self.counters.comparisons += 1
            node = node.children.get(symbol)
            if node is None:
                break
            consumed += 1
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

    def _descend(self, key):
        self._validate(key)
        node = self.root
        for symbol in key:
            self.counters.node_visits += 1
            self.counters.comparisons += 1
            node = node.children.get(symbol)
            if node is None:
                return None
        return node

    def _collect(self, node, prefix):
        stack = [(node, prefix)]
        while stack:
            current, accumulated = stack.pop()
            if current.is_terminal:
                yield accumulated
            for symbol in sorted(current.children, reverse=True):
                stack.append((current.children[symbol], accumulated + symbol))

    @staticmethod
    def _validate(key):
        if not isinstance(key, str):
            raise TypeError("a trie aceita apenas chaves do tipo str")
