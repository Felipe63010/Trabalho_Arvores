"""Testes de corretude da KD-Tree."""

import math
import random
import unittest

from src.kdtree import KDTree


class KDTreeTest(unittest.TestCase):
    """Verifica construção, inserção, remoção e consultas espaciais."""

    def _invariante_particao(self, arvore):
        pilha = [(arvore.root, 0)]
        total = 0
        while pilha:
            no, profundidade = pilha.pop()
            if no is None:
                continue
            total += 1
            eixo = profundidade % arvore.dimensions
            if no.left is not None:
                for ponto in self._pontos(no.left):
                    self.assertLess(ponto[eixo], no.point[eixo])
                pilha.append((no.left, profundidade + 1))
            if no.right is not None:
                for ponto in self._pontos(no.right):
                    self.assertGreaterEqual(ponto[eixo], no.point[eixo])
                pilha.append((no.right, profundidade + 1))
        self.assertEqual(total, len(arvore))

    @staticmethod
    def _pontos(no):
        encontrados = []
        pilha = [no]
        while pilha:
            atual = pilha.pop()
            if atual is None:
                continue
            encontrados.append(atual.point)
            pilha.append(atual.left)
            pilha.append(atual.right)
        return encontrados

    def test_construcao_balanceada(self):
        gerador = random.Random(21)
        pontos = [(gerador.randint(0, 999), gerador.randint(0, 999)) for _ in range(1000)]
        pontos = list(dict.fromkeys(pontos))
        arvore = KDTree(2).build(pontos)
        self.assertEqual(len(arvore), len(pontos))
        self.assertLessEqual(arvore.height(), 2 * math.ceil(math.log2(len(pontos))))
        self.assertEqual(sorted(arvore.points()), sorted(pontos))
        self._invariante_particao(arvore)

    def test_insercao_e_busca(self):
        arvore = KDTree(2)
        pontos = [(5, 5), (2, 8), (8, 2), (1, 1), (9, 9)]
        for posicao, ponto in enumerate(pontos):
            self.assertTrue(arvore.insert(ponto, posicao))
        self.assertFalse(arvore.insert((5, 5), 99))
        self.assertEqual(arvore.search((5, 5)), 99)
        self.assertIsNone(arvore.search((3, 3)))
        self.assertFalse((3, 3) in arvore)
        self._invariante_particao(arvore)

    def test_dimensao_invalida(self):
        arvore = KDTree(3)
        with self.assertRaises(ValueError):
            arvore.insert((1, 2))
        with self.assertRaises(ValueError):
            KDTree(0)

    def test_vizinho_mais_proximo(self):
        gerador = random.Random(22)
        pontos = list({(gerador.randint(0, 500), gerador.randint(0, 500)) for _ in range(600)})
        arvore = KDTree(2).build(pontos)
        for _ in range(60):
            consulta = (gerador.randint(0, 500), gerador.randint(0, 500))
            ponto, _valor, distancia = arvore.nearest(consulta)
            melhor = min(pontos, key=lambda p: (p[0] - consulta[0]) ** 2 + (p[1] - consulta[1]) ** 2)
            esperado = math.dist(melhor, consulta)
            self.assertAlmostEqual(distancia, esperado, places=9)
            self.assertAlmostEqual(math.dist(ponto, consulta), esperado, places=9)

    def test_k_vizinhos_mais_proximos(self):
        gerador = random.Random(23)
        pontos = list({(gerador.randint(0, 200), gerador.randint(0, 200)) for _ in range(300)})
        arvore = KDTree(2).build(pontos)
        consulta = (100, 100)
        obtidos = arvore.k_nearest(consulta, 10)
        esperados = sorted(math.dist(p, consulta) for p in pontos)[:10]
        self.assertEqual(len(obtidos), 10)
        for (_ponto, distancia), esperada in zip(obtidos, esperados):
            self.assertAlmostEqual(distancia, esperada, places=9)

    def test_consulta_por_intervalo(self):
        gerador = random.Random(24)
        pontos = list({(gerador.randint(0, 300), gerador.randint(0, 300)) for _ in range(500)})
        arvore = KDTree(2).build(pontos)
        inferior, superior = (50, 60), (180, 200)
        obtidos = sorted(arvore.range_search(inferior, superior))
        esperados = sorted(
            ponto
            for ponto in pontos
            if inferior[0] <= ponto[0] <= superior[0] and inferior[1] <= ponto[1] <= superior[1]
        )
        self.assertEqual(obtidos, esperados)
        self.assertGreater(arvore.counters.pruned_subtrees, 0)

    def test_consulta_por_raio(self):
        gerador = random.Random(25)
        pontos = list({(gerador.randint(0, 100), gerador.randint(0, 100)) for _ in range(200)})
        arvore = KDTree(2).build(pontos)
        centro, raio = (50, 50), 15.0
        obtidos = sorted(arvore.radius_search(centro, raio))
        esperados = sorted(ponto for ponto in pontos if math.dist(ponto, centro) <= raio)
        self.assertEqual(obtidos, esperados)

    def test_remocao_preserva_invariante(self):
        gerador = random.Random(26)
        pontos = list({(gerador.randint(0, 120), gerador.randint(0, 120)) for _ in range(250)})
        arvore = KDTree(2).build(pontos)
        restantes = set(pontos)
        gerador.shuffle(pontos)
        for ponto in pontos[:120]:
            self.assertTrue(arvore.remove(ponto))
            restantes.discard(ponto)
            self.assertFalse(ponto in arvore)
        self.assertEqual(len(arvore), len(restantes))
        self.assertEqual(sorted(arvore.points()), sorted(restantes))
        self._invariante_particao(arvore)
        self.assertFalse(arvore.remove((1000, 1000)))

    def test_estresse_tres_dimensoes(self):
        gerador = random.Random(27)
        arvore = KDTree(3)
        referencia = set()
        for _ in range(1500):
            ponto = tuple(gerador.randint(0, 40) for _ in range(3))
            if gerador.random() < 0.7:
                self.assertEqual(arvore.insert(ponto), ponto not in referencia)
                referencia.add(ponto)
            else:
                self.assertEqual(arvore.remove(ponto), ponto in referencia)
                referencia.discard(ponto)
            self.assertEqual(len(arvore), len(referencia))
        self.assertEqual(sorted(arvore.points()), sorted(referencia))
        self._invariante_particao(arvore)
        if referencia:
            consulta = (20, 20, 20)
            ponto, _valor, distancia = arvore.nearest(consulta)
            esperado = min(math.dist(p, consulta) for p in referencia)
            self.assertAlmostEqual(distancia, esperado, places=9)


if __name__ == "__main__":
    unittest.main()
