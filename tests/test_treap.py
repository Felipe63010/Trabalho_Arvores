"""Testes de corretude da treap."""

import random
import unittest

from src.treap import Treap


class TreapTest(unittest.TestCase):
    """Verifica as duas invariantes, as estatísticas de ordem e a divisão/união."""

    def _invariantes(self, arvore):
        pilha = [(arvore.root, None, None)]
        total = 0
        while pilha:
            no, limite_inferior, limite_superior = pilha.pop()
            if no is None:
                continue
            total += 1
            if limite_inferior is not None:
                self.assertGreater(no.key, limite_inferior)
            if limite_superior is not None:
                self.assertLess(no.key, limite_superior)
            esquerda = 0 if no.left is None else no.left.size
            direita = 0 if no.right is None else no.right.size
            self.assertEqual(no.size, 1 + esquerda + direita)
            if no.left is not None:
                self.assertLessEqual(no.left.priority, no.priority)
            if no.right is not None:
                self.assertLessEqual(no.right.priority, no.priority)
            pilha.append((no.left, limite_inferior, no.key))
            pilha.append((no.right, no.key, limite_superior))
        self.assertEqual(total, len(arvore))

    def test_insercao_e_busca(self):
        arvore = Treap(seed=1)
        for chave in [50, 30, 70, 20, 40, 60, 80]:
            self.assertTrue(arvore.insert(chave, chave * 10))
        self.assertFalse(arvore.insert(50, 999))
        self.assertEqual(arvore.search(50), 999)
        self.assertIsNone(arvore.search(1000))
        self.assertEqual(len(arvore), 7)
        self._invariantes(arvore)

    def test_prioridade_explicita_sobe_a_raiz(self):
        arvore = Treap(seed=2)
        for chave in range(10):
            arvore.insert(chave, priority=chave / 100.0)
        arvore.insert(42, priority=1.0)
        self.assertEqual(arvore.root.key, 42)
        self.assertGreater(arvore.counters.rotations, 0)
        self._invariantes(arvore)

    def test_remocao(self):
        arvore = Treap(seed=3)
        chaves = [15, 7, 23, 3, 11, 19, 27]
        for chave in chaves:
            arvore.insert(chave)
        self.assertTrue(arvore.remove(15))
        self.assertFalse(arvore.contains(15))
        self.assertFalse(arvore.remove(15))
        self.assertEqual(len(arvore), 6)
        self._invariantes(arvore)
        for chave in chaves:
            arvore.remove(chave)
        self.assertEqual(len(arvore), 0)
        self.assertIsNone(arvore.root)
        self.assertEqual(arvore.height(), -1)

    def test_estatisticas_de_ordem(self):
        arvore = Treap(seed=4)
        chaves = [8, 3, 17, 1, 12, 25, 9]
        for chave in chaves:
            arvore.insert(chave)
        ordenadas = sorted(chaves)
        for posicao, chave in enumerate(ordenadas):
            self.assertEqual(arvore.kth(posicao), chave)
            self.assertEqual(arvore.rank(chave), posicao)
        self.assertEqual(arvore.rank(0), 0)
        self.assertEqual(arvore.rank(100), len(chaves))
        with self.assertRaises(IndexError):
            arvore.kth(len(chaves))

    def test_divisao_e_uniao(self):
        arvore = Treap(seed=5)
        for chave in range(20):
            arvore.insert(chave)
        menores, maiores = arvore.split(10)
        self.assertEqual(menores.keys(), list(range(10)))
        self.assertEqual(maiores.keys(), list(range(10, 20)))
        self._invariantes(menores)
        self._invariantes(maiores)
        menores.join(maiores)
        self.assertEqual(menores.keys(), list(range(20)))
        self.assertEqual(len(maiores), 0)
        self._invariantes(menores)

    def test_altura_esperada_logaritmica(self):
        arvore = Treap(seed=6)
        total = 20000
        for chave in range(total):
            arvore.insert(chave)
        self.assertEqual(len(arvore), total)
        self.assertEqual(arvore.keys(), list(range(total)))
        self.assertLess(arvore.height(), 60)

    def test_estresse_aleatorio(self):
        gerador = random.Random(13)
        arvore = Treap(seed=7)
        referencia = set()
        for _ in range(6000):
            chave = gerador.randint(0, 400)
            escolha = gerador.random()
            if escolha < 0.5:
                self.assertEqual(arvore.insert(chave, chave), chave not in referencia)
                referencia.add(chave)
            elif escolha < 0.8:
                self.assertEqual(arvore.contains(chave), chave in referencia)
            else:
                self.assertEqual(arvore.remove(chave), chave in referencia)
                referencia.discard(chave)
            self.assertEqual(len(arvore), len(referencia))
        self.assertEqual(arvore.keys(), sorted(referencia))
        self._invariantes(arvore)


if __name__ == "__main__":
    unittest.main()
