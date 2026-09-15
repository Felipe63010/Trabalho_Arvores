"""KD-Tree: árvore binária de busca para pontos em espaços k-dimensionais.

Proposta por Bentley (1975), a KD-Tree generaliza a árvore binária de busca
para ``k`` dimensões alternando ciclicamente o eixo de comparação conforme a
profundidade do nó. Cada nó define um hiperplano perpendicular ao eixo
corrente e divide o espaço em dois semiespaços, o que permite descartar
regiões inteiras durante consultas por proximidade ou por intervalo.

A construção balanceada seleciona, em cada nível, a mediana das coordenadas
no eixo corrente; a inserção avulsa segue a mesma regra de comparação da
árvore binária de busca, sem rebalanceamento.
"""

import heapq
import math

from .instrumentation import Counters


class KDNode:
    """Nó da KD-Tree; o eixo de corte é determinado pela profundidade."""

    __slots__ = ("point", "value", "left", "right")

    def __init__(self, point, value=None):
        self.point = point
        self.value = value
        self.left = None
        self.right = None


class KDTree:
    """KD-Tree com construção balanceada, inserção, busca, remoção e consultas espaciais."""

    def __init__(self, dimensions=2):
        if dimensions < 1:
            raise ValueError("a KD-Tree exige pelo menos uma dimensão")
        self.dimensions = dimensions
        self.root = None
        self.counters = Counters()
        self._size = 0

    def __len__(self):
        return self._size

    def __contains__(self, point):
        return self.contains(point)

    @property
    def node_count(self):
        """Número de nós alocados."""
        return self._size

    def build(self, points, values=None):
        """Constrói a árvore balanceada a partir de uma coleção de pontos.

        Em cada nível seleciona-se a mediana das coordenadas do eixo
        corrente, o que garante altura ``O(log n)``. Pontos repetidos são
        descartados, preservando a semântica de conjunto adotada pela
        inserção avulsa.
        """
        if values is None:
            pares = ((self._validate(point), None) for point in points)
        else:
            pares = ((self._validate(point), value) for point, value in zip(points, values))
        unicos = {}
        for point, value in pares:
            unicos[point] = value
        items = list(unicos.items())
        self.root = self._build(items, 0)
        self._size = len(items)
        self.counters.nodes_created += len(items)
        return self

    def insert(self, point, value=None):
        """Insere ``point`` como folha, sem rebalanceamento.

        Retorna ``True`` se o ponto era inédito e ``False`` se apenas o
        valor associado foi atualizado.
        """
        point = self._validate(point)
        if self.root is None:
            self.root = KDNode(point, value)
            self.counters.nodes_created += 1
            self._size = 1
            return True
        node = self.root
        depth = 0
        while True:
            self.counters.node_visits += 1
            self.counters.comparisons += 1
            if node.point == point:
                node.value = value
                return False
            axis = depth % self.dimensions
            self.counters.comparisons += 1
            if point[axis] < node.point[axis]:
                if node.left is None:
                    node.left = KDNode(point, value)
                    break
                node = node.left
            else:
                if node.right is None:
                    node.right = KDNode(point, value)
                    break
                node = node.right
            depth += 1
        self.counters.nodes_created += 1
        self._size += 1
        return True

    def search(self, point, default=None):
        """Retorna o valor associado a ``point`` ou ``default`` se ausente."""
        node = self._locate(point)
        return default if node is None else node.value

    def contains(self, point):
        """Informa se ``point`` pertence à árvore."""
        return self._locate(point) is not None

    def remove(self, point):
        """Remove ``point`` substituindo-o pelo mínimo do eixo de corte.

        Quando o nó removido possui apenas subárvore esquerda, esta é
        transferida para a direita antes da substituição, preservando a
        invariante de ordenação por eixo. Retorna ``True`` se o ponto
        existia.
        """
        point = self._validate(point)
        self.root, removed = self._remove(self.root, point, 0)
        if removed:
            self._size -= 1
            self.counters.nodes_removed += 1
        return removed

    def nearest(self, query):
        """Retorna ``(ponto, valor, distância)`` do vizinho mais próximo."""
        query = self._validate(query)
        if self.root is None:
            return None
        best = [None, math.inf]
        self._nearest(self.root, query, 0, best)
        return best[0].point, best[0].value, math.sqrt(best[1])

    def nearest_with_trace(self, query):
        """Retorna o vizinho mais próximo acompanhado do rastro da consulta.

        Além do resultado, devolve a lista dos pontos efetivamente
        visitados e a lista das raízes das subárvores descartadas pela poda
        geométrica, o que permite documentar visualmente o caminho da busca.
        """
        query = self._validate(query)
        if self.root is None:
            return None, [], []
        best = [None, math.inf]
        visited, pruned = [], []
        self._nearest_traced(self.root, query, 0, best, visited, pruned)
        return (best[0].point, best[0].value, math.sqrt(best[1])), visited, pruned

    def k_nearest(self, query, amount):
        """Retorna os ``amount`` vizinhos mais próximos, do mais próximo ao mais distante."""
        query = self._validate(query)
        if amount <= 0 or self.root is None:
            return []
        heap = []
        self._k_nearest(self.root, query, 0, amount, heap)
        ordered = sorted(((-item[0], item[2]) for item in heap), key=lambda pair: pair[0])
        return [(point, math.sqrt(distance)) for distance, point in ordered]

    def range_search(self, lower, upper):
        """Retorna os pontos contidos no hiper-retângulo ``[lower, upper]``."""
        lower = self._validate(lower)
        upper = self._validate(upper)
        found = []
        stack = [(self.root, 0)]
        while stack:
            node, depth = stack.pop()
            if node is None:
                continue
            self.counters.node_visits += 1
            self.counters.comparisons += self.dimensions
            if all(lower[i] <= node.point[i] <= upper[i] for i in range(self.dimensions)):
                found.append(node.point)
            axis = depth % self.dimensions
            if lower[axis] < node.point[axis]:
                stack.append((node.left, depth + 1))
            elif node.left is not None:
                self.counters.pruned_subtrees += 1
            if upper[axis] >= node.point[axis]:
                stack.append((node.right, depth + 1))
            elif node.right is not None:
                self.counters.pruned_subtrees += 1
        return found

    def radius_search(self, center, radius):
        """Retorna os pontos cuja distância euclidiana até ``center`` não excede ``radius``."""
        center = self._validate(center)
        lower = tuple(coordinate - radius for coordinate in center)
        upper = tuple(coordinate + radius for coordinate in center)
        limit = radius * radius
        found = []
        for point in self.range_search(lower, upper):
            self.counters.distance_evals += 1
            if self._squared_distance(point, center) <= limit:
                found.append(point)
        return found

    def points(self):
        """Lista todos os pontos armazenados."""
        found = []
        stack = [self.root]
        while stack:
            node = stack.pop()
            if node is None:
                continue
            found.append(node.point)
            stack.append(node.left)
            stack.append(node.right)
        return found

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

    def _build(self, items, depth):
        if not items:
            return None
        axis = depth % self.dimensions
        items.sort(key=lambda item: item[0][axis])
        middle = len(items) // 2
        pivot = items[middle][0][axis]
        while middle > 0 and items[middle - 1][0][axis] == pivot:
            middle -= 1
        node = KDNode(items[middle][0], items[middle][1])
        node.left = self._build(items[:middle], depth + 1)
        node.right = self._build(items[middle + 1:], depth + 1)
        return node

    def _locate(self, point):
        point = self._validate(point)
        node = self.root
        depth = 0
        while node is not None:
            self.counters.node_visits += 1
            self.counters.comparisons += 1
            if node.point == point:
                return node
            axis = depth % self.dimensions
            self.counters.comparisons += 1
            node = node.left if point[axis] < node.point[axis] else node.right
            depth += 1
        return None

    def _remove(self, node, point, depth):
        if node is None:
            return None, False
        self.counters.node_visits += 1
        axis = depth % self.dimensions
        self.counters.comparisons += 1
        if node.point == point:
            if node.right is not None:
                substitute = self._find_min(node.right, axis, depth + 1)
                node.point, node.value = substitute.point, substitute.value
                node.right, _ = self._remove(node.right, substitute.point, depth + 1)
            elif node.left is not None:
                substitute = self._find_min(node.left, axis, depth + 1)
                node.point, node.value = substitute.point, substitute.value
                node.right, _ = self._remove(node.left, substitute.point, depth + 1)
                node.left = None
            else:
                return None, True
            return node, True
        self.counters.comparisons += 1
        if point[axis] < node.point[axis]:
            node.left, removed = self._remove(node.left, point, depth + 1)
        else:
            node.right, removed = self._remove(node.right, point, depth + 1)
        return node, removed

    def _find_min(self, node, axis, depth):
        if node is None:
            return None
        self.counters.node_visits += 1
        current_axis = depth % self.dimensions
        if current_axis == axis:
            if node.left is None:
                return node
            return self._minimum_by_axis(axis, node, self._find_min(node.left, axis, depth + 1))
        return self._minimum_by_axis(
            axis,
            node,
            self._find_min(node.left, axis, depth + 1),
            self._find_min(node.right, axis, depth + 1),
        )

    def _minimum_by_axis(self, axis, *candidates):
        best = None
        for candidate in candidates:
            if candidate is None:
                continue
            self.counters.comparisons += 1
            if best is None or candidate.point[axis] < best.point[axis]:
                best = candidate
        return best

    def _nearest(self, node, query, depth, best):
        if node is None:
            return
        self.counters.node_visits += 1
        self.counters.distance_evals += 1
        distance = self._squared_distance(node.point, query)
        if distance < best[1]:
            best[0], best[1] = node, distance
        axis = depth % self.dimensions
        difference = query[axis] - node.point[axis]
        near, far = (node.left, node.right) if difference < 0 else (node.right, node.left)
        self._nearest(near, query, depth + 1, best)
        if difference * difference < best[1]:
            self._nearest(far, query, depth + 1, best)
        elif far is not None:
            self.counters.pruned_subtrees += 1

    def _nearest_traced(self, node, query, depth, best, visited, pruned):
        if node is None:
            return
        visited.append(node.point)
        self.counters.node_visits += 1
        self.counters.distance_evals += 1
        distance = self._squared_distance(node.point, query)
        if distance < best[1]:
            best[0], best[1] = node, distance
        axis = depth % self.dimensions
        difference = query[axis] - node.point[axis]
        near, far = (node.left, node.right) if difference < 0 else (node.right, node.left)
        self._nearest_traced(near, query, depth + 1, best, visited, pruned)
        if difference * difference < best[1]:
            self._nearest_traced(far, query, depth + 1, best, visited, pruned)
        elif far is not None:
            pruned.append(far.point)
            self.counters.pruned_subtrees += 1

    def _k_nearest(self, node, query, depth, amount, heap):
        if node is None:
            return
        self.counters.node_visits += 1
        self.counters.distance_evals += 1
        distance = self._squared_distance(node.point, query)
        if len(heap) < amount:
            heapq.heappush(heap, (-distance, id(node), node.point))
        elif distance < -heap[0][0]:
            heapq.heapreplace(heap, (-distance, id(node), node.point))
        axis = depth % self.dimensions
        difference = query[axis] - node.point[axis]
        near, far = (node.left, node.right) if difference < 0 else (node.right, node.left)
        self._k_nearest(near, query, depth + 1, amount, heap)
        if len(heap) < amount or difference * difference < -heap[0][0]:
            self._k_nearest(far, query, depth + 1, amount, heap)
        elif far is not None:
            self.counters.pruned_subtrees += 1

    def _squared_distance(self, first, second):
        total = 0.0
        for index in range(self.dimensions):
            difference = first[index] - second[index]
            total += difference * difference
        return total

    def _validate(self, point):
        point = tuple(point)
        if len(point) != self.dimensions:
            raise ValueError(
                "esperado um ponto com %d coordenadas, recebido %d" % (self.dimensions, len(point))
            )
        return point
