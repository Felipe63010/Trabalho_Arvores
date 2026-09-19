"""Demonstração do funcionamento das cinco estruturas implementadas.

O roteiro executa, para cada estrutura, um conjunto representativo de
operações e registra os resultados obtidos e os contadores de operações
elementares consumidas. A saída é exibida no terminal e gravada em
``results/demonstração.txt``.
"""

import io
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.bst import BinarySearchTree
from src.kdtree import KDTree
from src.patricia import PatriciaTree
from src.splay import SplayTree
from src.treap import Treap
from src.trie import Trie

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAIDA = os.path.join(RAIZ, "results", "demonstracao.txt")

PALAVRAS = [
    "busca",
    "buscador",
    "buscar",
    "compilador",
    "compilar",
    "complexidade",
    "computador",
    "computar",
    "estrutura",
    "estruturas",
]
CHAVES = [45, 12, 78, 33, 90, 5, 67, 23, 56, 81]
PONTOS = [
    (2, 3),
    (5, 4),
    (9, 6),
    (4, 7),
    (8, 1),
    (7, 2),
    (6, 9),
    (1, 8),
    (3, 5),
    (10, 10),
    (12, 4),
    (0, 0),
]


def titulo(texto, arquivo):
    print("", file=arquivo)
    print("=" * 74, file=arquivo)
    print(texto, file=arquivo)
    print("=" * 74, file=arquivo)


def subtitulo(texto, arquivo):
    print("", file=arquivo)
    print("-- %s" % texto, file=arquivo)


def contadores(estrutura, arquivo, campos):
    dados = estrutura.counters.snapshot()
    resumo = "; ".join("%s = %d" % (campo, dados[campo]) for campo in campos)
    print("   contadores acumulados: %s" % resumo, file=arquivo)


def demonstrar_trie(arquivo):
    titulo("TRIE (ÁRVORE DE PREFIXOS)", arquivo)
    trie = Trie()
    for palavra in PALAVRAS:
        trie.insert(palavra, len(palavra))
    subtitulo("estado após a inserção de %d chaves" % len(PALAVRAS), arquivo)
    print("   chaves armazenadas: %d" % len(trie), file=arquivo)
    print("   nós alocados: %d" % trie.node_count, file=arquivo)
    print("   altura: %d" % trie.height(), file=arquivo)
    print("   soma dos comprimentos das chaves: %d" % sum(len(p) for p in PALAVRAS), file=arquivo)

    subtitulo("busca exata", arquivo)
    for chave in ["compilar", "compila", "estruturas", "estruturado"]:
        print(
            "   busca('%s') -> %s (valor associado: %s)"
            % (chave, trie.contains(chave), trie.search(chave)),
            file=arquivo,
        )

    subtitulo("consultas por prefixo", arquivo)
    for prefixo in ["comp", "busca", "estrutura", "z"]:
        print(
            "   chaves com prefixo '%s': %s" % (prefixo, trie.keys_with_prefix(prefixo)),
            file=arquivo,
        )
    print(
        "   maior prefixo armazenado de 'computadorizado': %s"
        % trie.longest_prefix_of("computadorizado"),
        file=arquivo,
    )

    subtitulo("remoção com poda de nós", arquivo)
    for chave in ["buscar", "estruturas"]:
        antes = trie.node_count
        removida = trie.remove(chave)
        print(
            "   remove('%s') -> %s; nós: %d -> %d" % (chave, removida, antes, trie.node_count),
            file=arquivo,
        )
    print("   chaves restantes: %s" % trie.keys(), file=arquivo)
    contadores(trie, arquivo, ["comparisons", "node_visits", "nodes_created", "nodes_removed"])


def demonstrar_patricia(arquivo):
    titulo("ÁRVORE PATRICIA (RADIX TREE COMPACTA)", arquivo)
    arvore = PatriciaTree()
    trie = Trie()
    for palavra in PALAVRAS:
        arvore.insert(palavra, len(palavra))
        trie.insert(palavra, len(palavra))
    subtitulo("estado após a inserção de %d chaves" % len(PALAVRAS), arquivo)
    print("   chaves armazenadas: %d" % len(arvore), file=arquivo)
    print(
        "   nós alocados: %d (trie equivalente: %d nós)" % (arvore.node_count, trie.node_count),
        file=arquivo,
    )
    print(
        "   redução de nós em relação à trie: %.1f%%"
        % (100.0 * (1.0 - arvore.node_count / trie.node_count)),
        file=arquivo,
    )
    print("   altura: %d (trie equivalente: %d)" % (arvore.height(), trie.height()), file=arquivo)
    print("   divisões de rótulo realizadas: %d" % arvore.counters.splits, file=arquivo)

    subtitulo("rótulos armazenados nas arestas", arquivo)
    pilha = [(arvore.root, 0)]
    linhas = []
    while pilha:
        no, profundidade = pilha.pop()
        if no.label:
            linhas.append(
                "   %s'%s'%s" % ("   " * profundidade, no.label, " (chave)" if no.is_terminal else "")
            )
        for simbolo in sorted(no.children, reverse=True):
            pilha.append((no.children[simbolo], profundidade + 1))
    for linha in linhas:
        print(linha, file=arquivo)

    subtitulo("busca exata e consultas por prefixo", arquivo)
    for chave in ["compilar", "compila", "computador"]:
        print("   busca('%s') -> %s" % (chave, arvore.contains(chave)), file=arquivo)
    for prefixo in ["comp", "busca"]:
        print(
            "   chaves com prefixo '%s': %s" % (prefixo, arvore.keys_with_prefix(prefixo)),
            file=arquivo,
        )

    subtitulo("remoção com fusão de nós", arquivo)
    for chave in ["computar", "computador"]:
        antes = arvore.node_count
        removida = arvore.remove(chave)
        print(
            "   remove('%s') -> %s; nós: %d -> %d; fusões acumuladas: %d"
            % (chave, removida, antes, arvore.node_count, arvore.counters.merges),
            file=arquivo,
        )
    print("   chaves restantes: %s" % arvore.keys(), file=arquivo)
    contadores(arvore, arquivo, ["comparisons", "node_visits", "splits", "merges"])


def demonstrar_splay(arquivo):
    titulo("ÁRVORE SPLAY", arquivo)
    arvore = SplayTree()
    for chave in CHAVES:
        arvore.insert(chave, chave)
    subtitulo("estado após a inserção de %d chaves" % len(CHAVES), arquivo)
    print("   ordem de inserção: %s" % CHAVES, file=arquivo)
    print("   raiz após as inserções: %d" % arvore.root.key, file=arquivo)
    print("   altura: %d; percurso em ordem: %s" % (arvore.height(), arvore.keys()), file=arquivo)

    subtitulo("promoção do nó acessado", arquivo)
    for chave in [5, 90, 5]:
        antes = arvore.counters.snapshot()
        arvore.search(chave)
        variacao = arvore.counters.delta(antes)
        print(
            "   busca(%d) -> raiz = %d; %d nós visitados; %d rotações"
            % (chave, arvore.root.key, variacao["node_visits"], variacao["rotations"]),
            file=arquivo,
        )
    print(
        "   a segunda busca por 5 visita menos nós: o acesso anterior já o aproximou da raiz",
        file=arquivo,
    )

    subtitulo("efeito da localidade de referência", arquivo)
    repeticoes = 200
    antes = arvore.counters.snapshot()
    for _ in range(repeticoes):
        arvore.search(5)
    concentrado = arvore.counters.delta(antes)["node_visits"]
    antes = arvore.counters.snapshot()
    for indice in range(repeticoes):
        arvore.search(CHAVES[indice % len(CHAVES)])
    disperso = arvore.counters.delta(antes)["node_visits"]
    print(
        "   %d acessos a uma única chave: %d nós visitados (%.2f por acesso)"
        % (repeticoes, concentrado, concentrado / repeticoes),
        file=arquivo,
    )
    print(
        "   %d acessos cíclicos às %d chaves: %d nós visitados (%.2f por acesso)"
        % (repeticoes, len(CHAVES), disperso, disperso / repeticoes),
        file=arquivo,
    )

    subtitulo("remoção", arquivo)
    for chave in [45, 45]:
        print(
            "   remove(%d) -> %s; chaves restantes: %d" % (chave, arvore.remove(chave), len(arvore)),
            file=arquivo,
        )
    print("   percurso em ordem: %s" % arvore.keys(), file=arquivo)
    contadores(arvore, arquivo, ["comparisons", "node_visits", "rotations"])


def demonstrar_treap(arquivo):
    titulo("ÁRVORE TREAP", arquivo)
    arvore = Treap(seed=93)
    for chave in CHAVES:
        arvore.insert(chave, chave)
    subtitulo("estado após a inserção de %d chaves" % len(CHAVES), arquivo)
    print("   raiz: chave %d com prioridade %.4f" % (arvore.root.key, arvore.root.priority), file=arquivo)
    print("   altura: %d; percurso em ordem: %s" % (arvore.height(), arvore.keys()), file=arquivo)

    subtitulo("insensibilidade à ordem de inserção", arquivo)
    ordenada_treap = Treap(seed=93)
    ordenada_bst = BinarySearchTree()
    for chave in range(1, 1001):
        ordenada_treap.insert(chave)
        ordenada_bst.insert(chave)
    print(
        "   1000 chaves inseridas em ordem crescente: altura da treap = %d; altura da BST = %d"
        % (ordenada_treap.height(), ordenada_bst.height()),
        file=arquivo,
    )
    print(
        "   limite teórico de referência: 3 * log2(1000) = %.1f"
        % (3 * math.log2(1000)),
        file=arquivo,
    )

    subtitulo("estatísticas de ordem", arquivo)
    for indice in [0, 4, 9]:
        print("   kth(%d) = %d" % (indice, arvore.kth(indice)), file=arquivo)
    for chave in [5, 56, 91]:
        print("   rank(%d) = %d" % (chave, arvore.rank(chave)), file=arquivo)

    subtitulo("divisão e união", arquivo)
    menores, maiores = arvore.split(50)
    print("   split(50) -> chaves < 50: %s" % menores.keys(), file=arquivo)
    print("   split(50) -> chaves >= 50: %s" % maiores.keys(), file=arquivo)
    menores.join(maiores)
    print("   join -> %s" % menores.keys(), file=arquivo)

    subtitulo("remoção por rotações de descida", arquivo)
    rotacoes_antes = menores.counters.rotations
    print("   remove(45) -> %s" % menores.remove(45), file=arquivo)
    print(
        "   rotações consumidas na remoção: %d" % (menores.counters.rotations - rotacoes_antes),
        file=arquivo,
    )
    print("   percurso em ordem: %s" % menores.keys(), file=arquivo)
    contadores(menores, arquivo, ["comparisons", "node_visits", "rotations"])


def demonstrar_kdtree(arquivo):
    titulo("KD-TREE (K = 2)", arquivo)
    arvore = KDTree(2).build(PONTOS)
    subtitulo("estado após a construção balanceada com %d pontos" % len(PONTOS), arquivo)
    print("   pontos armazenados: %d" % len(arvore), file=arquivo)
    print(
        "   altura: %d (limite de uma árvore perfeitamente balanceada: %d)"
        % (arvore.height(), math.ceil(math.log2(len(PONTOS)))),
        file=arquivo,
    )
    print("   raiz: %s" % (arvore.root.point,), file=arquivo)

    subtitulo("vizinho mais próximo", arquivo)
    consulta = (6, 5)
    antes = arvore.counters.snapshot()
    ponto, _valor, distancia = arvore.nearest(consulta)
    variacao = arvore.counters.delta(antes)
    forca_bruta = min(PONTOS, key=lambda p: math.dist(p, consulta))
    print(
        "   nearest(%s) = %s a distância %.4f" % (consulta, ponto, distancia),
        file=arquivo,
    )
    print("   verificação por força bruta: %s a distância %.4f" % (forca_bruta, math.dist(forca_bruta, consulta)), file=arquivo)
    print(
        "   custo: %d nós visitados e %d distâncias avaliadas, contra %d distâncias na busca linear"
        % (variacao["node_visits"], variacao["distance_evals"], len(PONTOS)),
        file=arquivo,
    )
    print(
        "   subárvores descartadas por poda geométrica: %d" % variacao["pruned_subtrees"],
        file=arquivo,
    )

    subtitulo("k vizinhos mais próximos", arquivo)
    for ponto, distancia in arvore.k_nearest(consulta, 3):
        print("   %s a distância %.4f" % (ponto, distancia), file=arquivo)

    subtitulo("consultas por região", arquivo)
    inferior, superior = (2, 2), (8, 7)
    encontrados = sorted(arvore.range_search(inferior, superior))
    esperados = sorted(
        p for p in PONTOS if inferior[0] <= p[0] <= superior[0] and inferior[1] <= p[1] <= superior[1]
    )
    print("   range_search(%s, %s) = %s" % (inferior, superior, encontrados), file=arquivo)
    print("   verificação por força bruta: %s" % esperados, file=arquivo)
    print(
        "   radius_search((6, 5), 3.0) = %s" % sorted(arvore.radius_search((6, 5), 3.0)),
        file=arquivo,
    )

    subtitulo("ganho de escala frente à busca linear", arquivo)
    gerador = random.Random(2024)
    massa = [
        (gerador.uniform(0.0, 1000.0), gerador.uniform(0.0, 1000.0)) for _ in range(20000)
    ]
    grande = KDTree(2).build(massa)
    total_visitas = 0
    total_consultas = 40
    for _ in range(total_consultas):
        consulta_aleatoria = (gerador.uniform(0.0, 1000.0), gerador.uniform(0.0, 1000.0))
        antes = grande.counters.snapshot()
        grande.nearest(consulta_aleatoria)
        total_visitas += grande.counters.delta(antes)["node_visits"]
    print(
        "   árvore com %d pontos e altura %d" % (len(grande), grande.height()),
        file=arquivo,
    )
    print(
        "   média de %.1f nós visitados por consulta, contra %d avaliações da busca linear"
        % (total_visitas / total_consultas, len(massa)),
        file=arquivo,
    )
    print(
        "   fração da base efetivamente inspecionada: %.2f%%"
        % (100.0 * total_visitas / total_consultas / len(massa)),
        file=arquivo,
    )

    subtitulo("remoção de nó interno", arquivo)
    alvo = arvore.root.point
    print("   raiz antes da remoção: %s" % (alvo,), file=arquivo)
    arvore.remove(alvo)
    print("   remove(%s) -> nova raiz: %s" % (alvo, arvore.root.point), file=arquivo)
    print("   pontos armazenados: %d" % len(arvore), file=arquivo)
    print("   %s ainda presente? %s" % (alvo, alvo in arvore), file=arquivo)
    contadores(arvore, arquivo, ["comparisons", "node_visits", "distance_evals", "pruned_subtrees"])


def main():
    """Executa todas as demonstrações e grava o relatório textual."""
    random.seed(2024)
    buffer = io.StringIO()
    print("DEMONSTRAÇÃO DO FUNCIONAMENTO DAS ESTRUTURAS IMPLEMENTADAS", file=buffer)
    print("Trabalho Prático Individual I - Estruturas em Árvores Avançadas", file=buffer)
    demonstrar_trie(buffer)
    demonstrar_patricia(buffer)
    demonstrar_splay(buffer)
    demonstrar_treap(buffer)
    demonstrar_kdtree(buffer)
    conteudo = buffer.getvalue()
    os.makedirs(os.path.dirname(SAIDA), exist_ok=True)
    with open(SAIDA, "w", encoding="utf-8") as destino:
        destino.write(conteudo)
    print(conteudo)
    print("Saída gravada em %s" % SAIDA)


if __name__ == "__main__":
    main()
