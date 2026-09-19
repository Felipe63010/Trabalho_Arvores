"""Geradores dos conjuntos de dados utilizados nos experimentos.

Todos os geradores são parametrizados por uma semente, de modo que cada
medição possa ser reproduzida integralmente. Os conjuntos foram escolhidos
para expor tanto os casos favoráveis quanto os desfavoráveis de cada
estrutura: chaves aleatórias e chaves ordenadas para as árvores de busca,
vocabulários com pouco e com muito compartilhamento de prefixos para as
estruturas de string, e nuvens de pontos uniformes e agrupadas para a
KD-Tree.
"""

import os
import random
import string

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LEXICO = os.path.join(RAIZ, "data", "lexico.txt")


def chaves_aleatorias(quantidade, semente):
    """Permutação aleatória de chaves inteiras distintas."""
    chaves = list(range(quantidade))
    random.Random(semente).shuffle(chaves)
    return chaves


def chaves_ordenadas(quantidade):
    """Chaves inteiras distintas em ordem crescente: pior caso da BST."""
    return list(range(quantidade))


def acessos_uniformes(chaves, quantidade, semente):
    """Sequência de acessos sorteados uniformemente entre as chaves."""
    gerador = random.Random(semente)
    return [gerador.choice(chaves) for _ in range(quantidade)]


def acessos_zipf(chaves, quantidade, expoente, semente):
    """Sequência de acessos com distribuição de Zipf de expoente dado.

    Com expoente igual a zero a distribuição é uniforme; à medida que o
    expoente cresce, a massa de probabilidade concentra-se nas primeiras
    chaves, reproduzindo a localidade temporal de referência observada em
    cargas reais.
    """
    gerador = random.Random(semente)
    pesos = []
    acumulado = 0.0
    for posicao in range(1, len(chaves) + 1):
        acumulado += 1.0 / (posicao ** expoente)
        pesos.append(acumulado)
    return gerador.choices(chaves, cum_weights=pesos, k=quantidade)


def palavras_lexico(quantidade, semente):
    """Amostra de palavras de um léxico natural, com prefixos compartilhados."""
    with open(LEXICO, "r", encoding="utf-8") as arquivo:
        vocabulario = [linha.strip() for linha in arquivo if linha.strip()]
    gerador = random.Random(semente)
    if quantidade >= len(vocabulario):
        return list(vocabulario)
    return gerador.sample(vocabulario, quantidade)


def palavras_aleatorias(quantidade, semente, comprimento=10):
    """Cadeias aleatórias sobre o alfabeto latino: pouco compartilhamento de prefixos."""
    gerador = random.Random(semente)
    alfabeto = string.ascii_lowercase
    conjunto = set()
    while len(conjunto) < quantidade:
        conjunto.add("".join(gerador.choice(alfabeto) for _ in range(comprimento)))
    return list(conjunto)


def palavras_prefixadas(quantidade, semente, ramos=40, comprimento=8):
    """Identificadores hierárquicos com forte compartilhamento de prefixos.

    O padrão reproduz chaves de sistemas reais, como caminhos de diretórios,
    endereços de rede e identificadores de recursos, em que um número
    reduzido de prefixos é compartilhado por muitas chaves.
    """
    gerador = random.Random(semente)
    alfabeto = string.ascii_lowercase
    prefixos = ["".join(gerador.choice(alfabeto) for _ in range(6)) for _ in range(ramos)]
    conjunto = set()
    while len(conjunto) < quantidade:
        prefixo = gerador.choice(prefixos)
        sufixo = "".join(gerador.choice(alfabeto) for _ in range(comprimento))
        conjunto.add(prefixo + sufixo)
    return list(conjunto)


def pontos_uniformes(quantidade, dimensoes, semente, extensao=1000.0):
    """Nuvem de pontos independentes e uniformemente distribuídos."""
    gerador = random.Random(semente)
    return [
        tuple(gerador.uniform(0.0, extensao) for _ in range(dimensoes))
        for _ in range(quantidade)
    ]


def pontos_agrupados(quantidade, dimensoes, semente, grupos=12, dispersao=25.0, extensao=1000.0):
    """Nuvem de pontos concentrada em grupos, com densidade fortemente desigual."""
    gerador = random.Random(semente)
    centros = [
        tuple(gerador.uniform(0.0, extensao) for _ in range(dimensoes)) for _ in range(grupos)
    ]
    pontos = []
    for _ in range(quantidade):
        centro = gerador.choice(centros)
        pontos.append(tuple(gerador.gauss(coordenada, dispersao) for coordenada in centro))
    return pontos
