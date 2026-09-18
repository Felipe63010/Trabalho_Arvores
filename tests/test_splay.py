"""Testes de corretude da árvore splay."""

import random
import unittest

from src.splay import SplayTree


class SplayTest(unittest.TestCase):
    """Verifica a ordem simétrica, a promoção do nó acessado e a remoção."""

    def _invariante_ordem(self, arvore):
        chaves = arvore.keys()
        self.assertEqual(chaves, sorted(chaves))
        self.assertEqual(len(chaves), len(set(chaves)))
        self.assertEqual(len(chaves), len(arvore))

    def test_insercao_promove_raiz(self):
        arvore = SplayTree()
        for chave in [30, 10, 50, 20, 40]:
            self.assertTrue(arvore.insert(chave, chave * 2))
            self.assertEqual(arvore.root.key, chave)
        self.assertFalse(arvore.insert(30, 60))
        self.assertEqual(len(arvore), 5)
        self._invariante_ordem(arvore)

    def test_busca_promove_raiz(self):
        arvore = SplayTree()
        for chave in [50, 30, 70, 20, 40, 60, 80]:
            arvore.insert(chave, chave)
        self.assertEqual(arvore.search(20), 20)
        self.assertEqual(arvore.root.key, 20)
        self.assertEqual(arvore.search(80), 80)
        self.assertEqual(arvore.root.key, 80)
        self._invariante_ordem(arvore)

    def test_busca_ausente_promove_vizinho(self):
        arvore = SplayTree()
        for chave in [10, 20, 30, 40, 50]:
            arvore.insert(chave)
        self.assertIsNone(arvore.search(35))
        self.assertIn(arvore.root.key, (30, 40))
        self.assertFalse(arvore.contains(35))
        self._invariante_ordem(arvore)

    def test_remocao(self):
        arvore = SplayTree()
        for chave in [50, 30, 70, 20, 40, 60, 80]:
            arvore.insert(chave)
        self.assertTrue(arvore.remove(30))
        self.assertFalse(arvore.contains(30))
        self.assertEqual(len(arvore), 6)
        self.assertFalse(arvore.remove(30))
        for chave in [50, 70, 20, 40, 60, 80]:
            self.assertTrue(arvore.remove(chave))
        self.assertEqual(len(arvore), 0)
        self.assertIsNone(arvore.root)
        self.assertEqual(arvore.height(), -1)

    def test_extremos(self):
        arvore = SplayTree()
        self.assertIsNone(arvore.minimum())
        for chave in [5, 1, 9, 3, 7]:
            arvore.insert(chave)
        self.assertEqual(arvore.minimum(), 1)
        self.assertEqual(arvore.root.key, 1)
        self.assertEqual(arvore.maximum(), 9)
        self.assertEqual(arvore.root.key, 9)

    def test_insercao_ordenada_nao_estoura_pilha(self):
        arvore = SplayTree()
        total = 20000
        for chave in range(total):
            arvore.insert(chave)
        self.assertEqual(len(arvore), total)
        self.assertTrue(arvore.contains(0))
        self.assertEqual(arvore.root.key, 0)
        self.assertEqual(arvore.keys()[:3], [0, 1, 2])

    def test_estresse_aleatorio(self):
        gerador = random.Random(11)
        arvore = SplayTree()
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


if __name__ == "__main__":
    unittest.main()
