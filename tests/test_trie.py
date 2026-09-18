"""Testes de corretude da trie."""

import random
import unittest

from src.trie import Trie


class TrieTest(unittest.TestCase):
    """Verifica inserção, busca, remoção e consultas por prefixo."""

    def test_insercao_e_busca(self):
        trie = Trie()
        palavras = ["casa", "casal", "caso", "cara", "carro", "carta"]
        for posicao, palavra in enumerate(palavras):
            self.assertTrue(trie.insert(palavra, posicao))
        self.assertEqual(len(trie), len(palavras))
        for posicao, palavra in enumerate(palavras):
            self.assertTrue(palavra in trie)
            self.assertEqual(trie.search(palavra), posicao)
        self.assertFalse(trie.insert("casa", 99))
        self.assertEqual(trie.search("casa"), 99)
        self.assertEqual(len(trie), len(palavras))

    def test_chave_ausente_e_prefixo_nao_terminal(self):
        trie = Trie()
        trie.insert("casamento")
        self.assertFalse(trie.contains("casa"))
        self.assertIsNone(trie.search("casa"))
        self.assertTrue(trie.starts_with("casa"))
        self.assertFalse(trie.starts_with("cx"))

    def test_chave_vazia(self):
        trie = Trie()
        self.assertTrue(trie.insert("", "raiz"))
        self.assertTrue(trie.contains(""))
        self.assertEqual(trie.search(""), "raiz")
        self.assertTrue(trie.remove(""))
        self.assertFalse(trie.contains(""))

    def test_tipo_invalido(self):
        trie = Trie()
        with self.assertRaises(TypeError):
            trie.insert(10)

    def test_remocao_poda_nos(self):
        trie = Trie()
        trie.insert("casa")
        trie.insert("casal")
        nos_antes = trie.node_count
        self.assertTrue(trie.remove("casal"))
        self.assertEqual(trie.node_count, nos_antes - 1)
        self.assertTrue(trie.contains("casa"))
        self.assertFalse(trie.remove("casal"))

    def test_consultas_por_prefixo(self):
        trie = Trie()
        for palavra in ["casa", "casal", "caso", "cara", "carro", "carta"]:
            trie.insert(palavra)
        self.assertEqual(sorted(trie.keys_with_prefix("car")), ["cara", "carro", "carta"])
        self.assertEqual(trie.keys_with_prefix("cas"), ["casa", "casal", "caso"])
        self.assertEqual(trie.keys_with_prefix("z"), [])
        self.assertEqual(trie.keys_with_prefix(""), sorted(trie.keys()))

    def test_maior_prefixo(self):
        trie = Trie()
        for palavra in ["ca", "casa", "casamento"]:
            trie.insert(palavra)
        self.assertEqual(trie.longest_prefix_of("casarao"), "casa")
        self.assertIsNone(trie.longest_prefix_of("cb"))

    def test_ordem_lexicografica(self):
        trie = Trie()
        palavras = ["banana", "abacaxi", "caju", "abacate", "banjo"]
        for palavra in palavras:
            trie.insert(palavra)
        self.assertEqual(trie.keys(), sorted(palavras))

    def test_estresse_aleatorio(self):
        gerador = random.Random(2024)
        alfabeto = "abcd"
        trie = Trie()
        referencia = set()
        for _ in range(4000):
            palavra = "".join(gerador.choice(alfabeto) for _ in range(gerador.randint(1, 7)))
            if gerador.random() < 0.65:
                esperado = palavra not in referencia
                self.assertEqual(trie.insert(palavra), esperado)
                referencia.add(palavra)
            else:
                esperado = palavra in referencia
                self.assertEqual(trie.remove(palavra), esperado)
                referencia.discard(palavra)
            self.assertEqual(len(trie), len(referencia))
        self.assertEqual(trie.keys(), sorted(referencia))
        for palavra in sorted(referencia):
            prefixo = palavra[:2]
            esperado = sorted(chave for chave in referencia if chave.startswith(prefixo))
            self.assertEqual(trie.keys_with_prefix(prefixo), esperado)


if __name__ == "__main__":
    unittest.main()
