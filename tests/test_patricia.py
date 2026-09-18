"""Testes de corretude da árvore Patricia."""

import random
import unittest

from src.patricia import PatriciaTree
from src.trie import Trie


class PatriciaTest(unittest.TestCase):
    """Verifica inserção com divisão de rótulos, busca, remoção com compactação e prefixos."""

    def _invariante_compactacao(self, arvore):
        pilha = [(arvore.root, True)]
        while pilha:
            no, e_raiz = pilha.pop()
            if not e_raiz:
                self.assertNotEqual(no.label, "", "nenhum nó interno pode ter rótulo vazio")
                if len(no.children) == 1:
                    self.assertTrue(
                        no.is_terminal,
                        "nó não terminal com filho único viola a compactação",
                    )
            for simbolo, filho in no.children.items():
                self.assertEqual(simbolo, filho.label[0])
                pilha.append((filho, False))

    def test_insercao_e_busca(self):
        arvore = PatriciaTree()
        palavras = ["casa", "casal", "caso", "cara", "carro", "carta"]
        for posicao, palavra in enumerate(palavras):
            self.assertTrue(arvore.insert(palavra, posicao))
        self.assertEqual(len(arvore), len(palavras))
        for posicao, palavra in enumerate(palavras):
            self.assertTrue(palavra in arvore)
            self.assertEqual(arvore.search(palavra), posicao)
        self.assertFalse(arvore.insert("casa", 99))
        self.assertEqual(arvore.search("casa"), 99)
        self._invariante_compactacao(arvore)

    def test_divisao_de_rotulo(self):
        arvore = PatriciaTree()
        arvore.insert("casa")
        self.assertEqual(arvore.node_count, 2)
        arvore.insert("caso")
        self.assertEqual(arvore.counters.splits, 1)
        self.assertEqual(arvore.node_count, 4)
        self.assertEqual(sorted(arvore.keys()), ["casa", "caso"])
        self._invariante_compactacao(arvore)

    def test_compactacao_apos_remocao(self):
        arvore = PatriciaTree()
        for palavra in ["cara", "carro", "carta"]:
            arvore.insert(palavra)
        self.assertTrue(arvore.remove("carro"))
        self.assertTrue(arvore.remove("carta"))
        self.assertGreaterEqual(arvore.counters.merges, 1)
        self.assertEqual(arvore.keys(), ["cara"])
        self._invariante_compactacao(arvore)

    def test_prefixo_nao_terminal(self):
        arvore = PatriciaTree()
        arvore.insert("casamento")
        self.assertFalse(arvore.contains("casa"))
        self.assertTrue(arvore.starts_with("casa"))
        self.assertEqual(arvore.keys_with_prefix("cas"), ["casamento"])
        self.assertEqual(arvore.keys_with_prefix("casb"), [])

    def test_chave_vazia(self):
        arvore = PatriciaTree()
        self.assertTrue(arvore.insert("", "raiz"))
        self.assertEqual(arvore.search(""), "raiz")
        self.assertTrue(arvore.remove(""))
        self.assertFalse(arvore.contains(""))

    def test_tipo_invalido(self):
        arvore = PatriciaTree()
        with self.assertRaises(TypeError):
            arvore.insert(3.14)

    def test_maior_prefixo(self):
        arvore = PatriciaTree()
        for palavra in ["ca", "casa", "casamento"]:
            arvore.insert(palavra)
        self.assertEqual(arvore.longest_prefix_of("casarao"), "casa")
        self.assertEqual(arvore.longest_prefix_of("cartao"), "ca")
        self.assertIsNone(arvore.longest_prefix_of("bola"))

    def test_equivalencia_com_a_trie(self):
        gerador = random.Random(7)
        alfabeto = "abc"
        arvore = PatriciaTree()
        trie = Trie()
        referencia = set()
        for _ in range(4000):
            palavra = "".join(gerador.choice(alfabeto) for _ in range(gerador.randint(1, 8)))
            if gerador.random() < 0.65:
                esperado = palavra not in referencia
                self.assertEqual(arvore.insert(palavra), esperado)
                trie.insert(palavra)
                referencia.add(palavra)
            else:
                esperado = palavra in referencia
                self.assertEqual(arvore.remove(palavra), esperado)
                trie.remove(palavra)
                referencia.discard(palavra)
            self.assertEqual(len(arvore), len(referencia))
        self.assertEqual(arvore.keys(), sorted(referencia))
        self.assertEqual(arvore.keys(), trie.keys())
        self.assertLessEqual(arvore.node_count, trie.node_count)
        self._invariante_compactacao(arvore)
        for palavra in sorted(referencia):
            prefixo = palavra[:3]
            self.assertEqual(arvore.keys_with_prefix(prefixo), trie.keys_with_prefix(prefixo))


if __name__ == "__main__":
    unittest.main()
