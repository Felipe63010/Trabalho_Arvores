"""Testes de corretude das estruturas de referência BST e AVL."""

import random
import unittest

from src.avl import AVLTree
from src.bst import BinarySearchTree


class EstruturasDeReferenciaTest(unittest.TestCase):
    """Verifica a ordem simétrica da BST e o balanceamento estrito da AVL."""

    def _altura(self, no):
        if no is None:
            return 0
        return 1 + max(self._altura(no.left), self._altura(no.right))

    def _invariante_avl(self, arvore):
        pilha = [arvore.root]
        while pilha:
            no = pilha.pop()
            if no is None:
                continue
            esquerda = self._altura(no.left)
            direita = self._altura(no.right)
            self.assertLessEqual(abs(esquerda - direita), 1)
            self.assertEqual(no.height, 1 + max(esquerda, direita))
            pilha.append(no.left)
            pilha.append(no.right)

    def test_bst_degenera_com_chaves_ordenadas(self):
        arvore = BinarySearchTree()
        for chave in range(200):
            arvore.insert(chave)
        self.assertEqual(arvore.height(), 199)
        self.assertEqual(arvore.keys(), list(range(200)))

    def test_avl_mantem_altura_logaritmica(self):
        arvore = AVLTree()
        for chave in range(2000):
            arvore.insert(chave)
        self.assertLessEqual(arvore.height(), 15)
        self.assertEqual(arvore.keys(), list(range(2000)))
        self._invariante_avl(arvore)

    def test_estresse_aleatorio(self):
        gerador = random.Random(31)
        bst = BinarySearchTree()
        avl = AVLTree()
        referencia = set()
        for _ in range(4000):
            chave = gerador.randint(0, 300)
            escolha = gerador.random()
            if escolha < 0.55:
                esperado = chave not in referencia
                self.assertEqual(bst.insert(chave, chave), esperado)
                self.assertEqual(avl.insert(chave, chave), esperado)
                referencia.add(chave)
            else:
                esperado = chave in referencia
                self.assertEqual(bst.remove(chave), esperado)
                self.assertEqual(avl.remove(chave), esperado)
                referencia.discard(chave)
            self.assertEqual(len(bst), len(referencia))
            self.assertEqual(len(avl), len(referencia))
        self.assertEqual(bst.keys(), sorted(referencia))
        self.assertEqual(avl.keys(), sorted(referencia))
        self._invariante_avl(avl)


if __name__ == "__main__":
    unittest.main()
