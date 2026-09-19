"""Execução dos experimentos computacionais e gravação dos resultados.

O módulo organiza quatro experimentos independentes:

* E1 - árvores de busca por comparação (BST, AVL, splay e treap) sob
  inserção aleatória, inserção ordenada e acesso enviesado;
* E2 - estruturas indexadas por prefixo (trie e Patricia) contra uma AVL de
  cadeias, sobre três vocabulários com graus distintos de compartilhamento
  de prefixos;
* E3 - KD-Tree: custo de construção, consulta ao vizinho mais próximo
  comparada à busca linear, consultas por região e efeito da
  dimensionalidade;
* E4 - efeito da localidade temporal de referência sobre o custo médio de
  acesso.

Cada configuração é repetida ``REPETICOES`` vezes sobre instâncias
regeneradas, e as médias são gravadas em arquivos CSV no diretório
``results``.
"""

import csv
import gc
import math
import os
import sys
import time
import tracemalloc

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from experiments.datasets import (
    acessos_uniformes,
    acessos_zipf,
    chaves_aleatorias,
    chaves_ordenadas,
    palavras_aleatorias,
    palavras_lexico,
    palavras_prefixadas,
    pontos_agrupados,
    pontos_uniformes,
)
from src.avl import AVLTree
from src.bst import BinarySearchTree
from src.kdtree import KDTree
from src.patricia import PatriciaTree
from src.splay import SplayTree
from src.treap import Treap
from src.trie import Trie

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DESTINO = os.path.join(RAIZ, "results")

REPETICOES = 3
SEMENTE_BASE = 2024
LIMITE_SEGUNDOS = 3.0

TAMANHOS_COMPARACAO = [2000, 4000, 8000, 16000, 32000]
TAMANHOS_TEXTO = [2000, 4000, 8000, 16000, 32000]
TAMANHOS_ESPACIAL = [1000, 2000, 4000, 8000, 16000, 32000]
DIMENSOES = [2, 3, 4, 6, 8, 12, 16]
EXPOENTES_ZIPF = [0.0, 0.4, 0.8, 1.0, 1.2, 1.6, 2.0]


def cronometrar(acao):
    """Executa ``ação`` e devolve o tempo decorrido em segundos."""
    inicio = time.perf_counter()
    acao()
    return time.perf_counter() - inicio


def memoria_da_construcao(construtor, chaves):
    """Mede, em kibibytes, a memória alocada pela construção da estrutura."""
    gc.collect()
    tracemalloc.start()
    base = tracemalloc.get_traced_memory()[0]
    estrutura = construtor()
    for chave in chaves:
        estrutura.insert(chave)
    consumo = tracemalloc.get_traced_memory()[0] - base
    tracemalloc.stop()
    return consumo / 1024.0, estrutura


def media(valores):
    """Média aritmética de uma sequência não vazia."""
    return sum(valores) / len(valores)


def gravar(nome, colunas, linhas):
    """Grava um arquivo CSV no diretório de resultados."""
    os.makedirs(DESTINO, exist_ok=True)
    caminho = os.path.join(DESTINO, nome)
    with open(caminho, "w", newline="", encoding="utf-8") as arquivo:
        escritor = csv.DictWriter(arquivo, fieldnames=colunas)
        escritor.writeheader()
        for linha in linhas:
            escritor.writerow(linha)
    print("   gravado: %s (%d linhas)" % (caminho, len(linhas)))
    return caminho


def construtores_comparacao(semente):
    """Fabricas das quatro árvores de busca por comparação."""
    return {
        "BST": BinarySearchTree,
        "AVL": AVLTree,
        "Splay": SplayTree,
        "Treap": lambda: Treap(seed=semente),
    }


def experimento_comparacao():
    """E1: árvores de busca por comparação sob três cenários de carga."""
    print("E1: árvores de busca por comparação")
    linhas = []
    bloqueados = set()
    for cenario in ["aleatoria", "ordenada", "enviesada"]:
        for tamanho in TAMANHOS_COMPARACAO:
            for nome in ["BST", "AVL", "Splay", "Treap"]:
                if (cenario, nome) in bloqueados:
                    continue
                amostras = []
                for repeticao in range(REPETICOES):
                    semente = SEMENTE_BASE + repeticao
                    if cenario == "ordenada":
                        insercoes = chaves_ordenadas(tamanho)
                    else:
                        insercoes = chaves_aleatorias(tamanho, semente)
                    if cenario == "enviesada":
                        ranqueamento = chaves_aleatorias(tamanho, semente + 97)
                        buscas = acessos_zipf(ranqueamento, tamanho, 1.2, semente + 13)
                    else:
                        buscas = acessos_uniformes(insercoes, tamanho, semente + 13)
                    remocoes = chaves_aleatorias(tamanho, semente + 31)[: tamanho // 2]

                    estrutura = construtores_comparacao(semente)[nome]()
                    marca = estrutura.counters.snapshot()
                    tempo_insercao = cronometrar(
                        lambda: [estrutura.insert(chave, chave) for chave in insercoes]
                    )
                    insercao = estrutura.counters.delta(marca)
                    altura = estrutura.height()

                    marca = estrutura.counters.snapshot()
                    tempo_busca = cronometrar(
                        lambda: [estrutura.contains(chave) for chave in buscas]
                    )
                    busca = estrutura.counters.delta(marca)

                    marca = estrutura.counters.snapshot()
                    tempo_remocao = cronometrar(
                        lambda: [estrutura.remove(chave) for chave in remocoes]
                    )
                    remocao = estrutura.counters.delta(marca)

                    amostras.append(
                        {
                            "t_insercao": tempo_insercao,
                            "t_busca": tempo_busca,
                            "t_remocao": tempo_remocao,
                            "comp_insercao": insercao["comparisons"],
                            "comp_busca": busca["comparisons"],
                            "visitas_busca": busca["node_visits"],
                            "rotacoes": insercao["rotations"] + busca["rotations"] + remocao["rotations"],
                            "altura": altura,
                        }
                    )

                memoria, _estrutura = memoria_da_construcao(
                    construtores_comparacao(SEMENTE_BASE)[nome],
                    chaves_ordenadas(tamanho)
                    if cenario == "ordenada"
                    else chaves_aleatorias(tamanho, SEMENTE_BASE),
                )
                linhas.append(
                    {
                        "cenario": cenario,
                        "estrutura": nome,
                        "n": tamanho,
                        "repeticoes": REPETICOES,
                        "t_insercao_ms": round(media([a["t_insercao"] for a in amostras]) * 1000.0, 4),
                        "t_busca_ms": round(media([a["t_busca"] for a in amostras]) * 1000.0, 4),
                        "t_remocao_ms": round(media([a["t_remocao"] for a in amostras]) * 1000.0, 4),
                        "comp_por_insercao": round(
                            media([a["comp_insercao"] for a in amostras]) / tamanho, 3
                        ),
                        "comp_por_busca": round(media([a["comp_busca"] for a in amostras]) / tamanho, 3),
                        "visitas_por_busca": round(
                            media([a["visitas_busca"] for a in amostras]) / tamanho, 3
                        ),
                        "rotacoes": int(media([a["rotacoes"] for a in amostras])),
                        "altura": int(media([a["altura"] for a in amostras])),
                        "memoria_kb": round(memoria, 1),
                        "bytes_por_chave": round(memoria * 1024.0 / tamanho, 1),
                    }
                )
                custo = media([a["t_insercao"] + a["t_busca"] + a["t_remocao"] for a in amostras])
                print(
                    "   %-10s %-6s n=%6d  inserção %7.1f ms  busca %7.1f ms  altura %5d"
                    % (
                        cenario,
                        nome,
                        tamanho,
                        linhas[-1]["t_insercao_ms"],
                        linhas[-1]["t_busca_ms"],
                        linhas[-1]["altura"],
                    )
                )
                if custo > LIMITE_SEGUNDOS:
                    bloqueados.add((cenario, nome))
                    print(
                        "      configuração interrompida: custo por repetição acima de %.0f s"
                        % LIMITE_SEGUNDOS
                    )
    colunas = [
        "cenario",
        "estrutura",
        "n",
        "repeticoes",
        "t_insercao_ms",
        "t_busca_ms",
        "t_remocao_ms",
        "comp_por_insercao",
        "comp_por_busca",
        "visitas_por_busca",
        "rotacoes",
        "altura",
        "memoria_kb",
        "bytes_por_chave",
    ]
    return gravar("e1_comparacao.csv", colunas, linhas)


def experimento_texto():
    """E2: trie e Patricia contra uma AVL de cadeias em três vocabulários."""
    print("E2: estruturas indexadas por prefixo")
    geradores = {
        "lexico": palavras_lexico,
        "aleatorio": palavras_aleatorias,
        "prefixado": palavras_prefixadas,
    }
    construtores = {"Trie": Trie, "Patricia": PatriciaTree, "AVL": AVLTree}
    linhas = []
    for cenario, gerador in geradores.items():
        for tamanho in TAMANHOS_TEXTO:
            for nome, construtor in construtores.items():
                amostras = []
                for repeticao in range(REPETICOES):
                    semente = SEMENTE_BASE + repeticao
                    palavras = gerador(tamanho, semente)
                    ausentes = [palavra + "zqx" for palavra in palavras]
                    prefixos = sorted({palavra[:3] for palavra in palavras})[:200]
                    remocoes = palavras[: tamanho // 2]

                    estrutura = construtor()
                    marca = estrutura.counters.snapshot()
                    tempo_insercao = cronometrar(
                        lambda: [estrutura.insert(palavra, 1) for palavra in palavras]
                    )
                    insercao = estrutura.counters.delta(marca)
                    altura = estrutura.height()
                    nos = estrutura.node_count

                    marca = estrutura.counters.snapshot()
                    tempo_acerto = cronometrar(
                        lambda: [estrutura.contains(palavra) for palavra in palavras]
                    )
                    acerto = estrutura.counters.delta(marca)
                    tempo_falha = cronometrar(
                        lambda: [estrutura.contains(palavra) for palavra in ausentes]
                    )

                    if nome == "AVL":
                        tempo_prefixo = float("nan")
                        encontrados = 0
                    else:
                        inicio = time.perf_counter()
                        encontrados = sum(
                            len(estrutura.keys_with_prefix(prefixo)) for prefixo in prefixos
                        )
                        tempo_prefixo = time.perf_counter() - inicio

                    tempo_remocao = cronometrar(
                        lambda: [estrutura.remove(palavra) for palavra in remocoes]
                    )

                    amostras.append(
                        {
                            "t_insercao": tempo_insercao,
                            "t_acerto": tempo_acerto,
                            "t_falha": tempo_falha,
                            "t_prefixo": tempo_prefixo,
                            "t_remocao": tempo_remocao,
                            "comp_insercao": insercao["comparisons"],
                            "comp_acerto": acerto["comparisons"],
                            "altura": altura,
                            "nos": nos,
                            "encontrados": encontrados,
                            "consultas_prefixo": len(prefixos),
                        }
                    )

                palavras = gerador(tamanho, SEMENTE_BASE)
                memoria, _estrutura = memoria_da_construcao(construtor, palavras)
                comprimento = media([len(palavra) for palavra in palavras])
                linhas.append(
                    {
                        "cenario": cenario,
                        "estrutura": nome,
                        "n": tamanho,
                        "repeticoes": REPETICOES,
                        "comprimento_medio": round(comprimento, 2),
                        "t_insercao_ms": round(media([a["t_insercao"] for a in amostras]) * 1000.0, 4),
                        "t_busca_acerto_ms": round(media([a["t_acerto"] for a in amostras]) * 1000.0, 4),
                        "t_busca_falha_ms": round(media([a["t_falha"] for a in amostras]) * 1000.0, 4),
                        "t_prefixo_ms": round(media([a["t_prefixo"] for a in amostras]) * 1000.0, 4),
                        "t_remocao_ms": round(media([a["t_remocao"] for a in amostras]) * 1000.0, 4),
                        "comp_por_busca": round(media([a["comp_acerto"] for a in amostras]) / tamanho, 3),
                        "altura": int(media([a["altura"] for a in amostras])),
                        "nos": int(media([a["nos"] for a in amostras])),
                        "nos_por_chave": round(media([a["nos"] for a in amostras]) / tamanho, 3),
                        "memoria_kb": round(memoria, 1),
                        "bytes_por_chave": round(memoria * 1024.0 / tamanho, 1),
                        "chaves_por_prefixo": round(
                            media([a["encontrados"] for a in amostras])
                            / max(1, amostras[0]["consultas_prefixo"]),
                            2,
                        ),
                    }
                )
                print(
                    "   %-10s %-9s n=%6d  inserção %7.1f ms  busca %7.1f ms  nós %8d"
                    % (
                        cenario,
                        nome,
                        tamanho,
                        linhas[-1]["t_insercao_ms"],
                        linhas[-1]["t_busca_acerto_ms"],
                        linhas[-1]["nos"],
                    )
                )
    colunas = [
        "cenario",
        "estrutura",
        "n",
        "repeticoes",
        "comprimento_medio",
        "t_insercao_ms",
        "t_busca_acerto_ms",
        "t_busca_falha_ms",
        "t_prefixo_ms",
        "t_remocao_ms",
        "comp_por_busca",
        "altura",
        "nos",
        "nos_por_chave",
        "memoria_kb",
        "bytes_por_chave",
        "chaves_por_prefixo",
    ]
    return gravar("e2_texto.csv", colunas, linhas)


def vizinho_por_forca_bruta(pontos, consulta):
    """Vizinho mais próximo obtido por varredura linear, usado como referência."""
    melhor = None
    menor = math.inf
    for ponto in pontos:
        distancia = 0.0
        for indice, coordenada in enumerate(ponto):
            diferenca = coordenada - consulta[indice]
            distancia += diferenca * diferenca
        if distancia < menor:
            menor, melhor = distancia, ponto
    return melhor, menor


def experimento_espacial():
    """E3: construção, consulta e poda geométrica na KD-Tree."""
    print("E3: KD-Tree - escala e distribuição")
    consultas_por_configuracao = 100
    linhas = []
    for cenario, gerador in [("uniforme", pontos_uniformes), ("agrupado", pontos_agrupados)]:
        for tamanho in TAMANHOS_ESPACIAL:
            amostras = []
            for repeticao in range(REPETICOES):
                semente = SEMENTE_BASE + repeticao
                pontos = gerador(tamanho, 2, semente)
                consultas = pontos_uniformes(consultas_por_configuracao, 2, semente + 5)

                arvore = KDTree(2)
                tempo_construcao = cronometrar(lambda: arvore.build(pontos))
                altura = arvore.height()

                marca = arvore.counters.snapshot()
                tempo_consulta = cronometrar(
                    lambda: [arvore.nearest(consulta) for consulta in consultas]
                )
                consulta_contadores = arvore.counters.delta(marca)

                tempo_linear = cronometrar(
                    lambda: [vizinho_por_forca_bruta(pontos, consulta) for consulta in consultas]
                )

                lado = 50.0
                regioes = [
                    (
                        tuple(coordenada - lado for coordenada in consulta),
                        tuple(coordenada + lado for coordenada in consulta),
                    )
                    for consulta in consultas
                ]
                marca = arvore.counters.snapshot()
                tempo_regiao = cronometrar(
                    lambda: [arvore.range_search(inferior, superior) for inferior, superior in regioes]
                )
                regiao_contadores = arvore.counters.delta(marca)

                divergencias = 0
                for consulta in consultas[:20]:
                    ponto, _valor, distancia = arvore.nearest(consulta)
                    referencia, quadrado = vizinho_por_forca_bruta(pontos, consulta)
                    if abs(distancia - math.sqrt(quadrado)) > 1e-9:
                        divergencias += 1

                amostras.append(
                    {
                        "t_construcao": tempo_construcao,
                        "t_consulta": tempo_consulta,
                        "t_linear": tempo_linear,
                        "t_regiao": tempo_regiao,
                        "visitas_consulta": consulta_contadores["node_visits"],
                        "podas_consulta": consulta_contadores["pruned_subtrees"],
                        "visitas_regiao": regiao_contadores["node_visits"],
                        "altura": altura,
                        "divergencias": divergencias,
                    }
                )

            memoria, _arvore = memoria_da_construcao(
                lambda: KDTree(2), gerador(tamanho, 2, SEMENTE_BASE)
            )
            linhas.append(
                {
                    "cenario": cenario,
                    "n": tamanho,
                    "repeticoes": REPETICOES,
                    "consultas": consultas_por_configuracao,
                    "t_construcao_ms": round(media([a["t_construcao"] for a in amostras]) * 1000.0, 4),
                    "t_consulta_kd_us": round(
                        media([a["t_consulta"] for a in amostras])
                        * 1e6
                        / consultas_por_configuracao,
                        3,
                    ),
                    "t_consulta_linear_us": round(
                        media([a["t_linear"] for a in amostras]) * 1e6 / consultas_por_configuracao,
                        3,
                    ),
                    "aceleracao": round(
                        media([a["t_linear"] for a in amostras])
                        / media([a["t_consulta"] for a in amostras]),
                        2,
                    ),
                    "t_regiao_us": round(
                        media([a["t_regiao"] for a in amostras]) * 1e6 / consultas_por_configuracao,
                        3,
                    ),
                    "visitas_por_consulta": round(
                        media([a["visitas_consulta"] for a in amostras]) / consultas_por_configuracao,
                        2,
                    ),
                    "fracao_visitada": round(
                        media([a["visitas_consulta"] for a in amostras])
                        / consultas_por_configuracao
                        / tamanho,
                        5,
                    ),
                    "podas_por_consulta": round(
                        media([a["podas_consulta"] for a in amostras]) / consultas_por_configuracao,
                        2,
                    ),
                    "altura": int(media([a["altura"] for a in amostras])),
                    "memoria_kb": round(memoria, 1),
                    "divergencias": int(sum(a["divergencias"] for a in amostras)),
                }
            )
            print(
                "   %-9s n=%6d  construção %8.1f ms  kd %8.2f us  linear %9.2f us  aceleração %6.1fx"
                % (
                    cenario,
                    tamanho,
                    linhas[-1]["t_construcao_ms"],
                    linhas[-1]["t_consulta_kd_us"],
                    linhas[-1]["t_consulta_linear_us"],
                    linhas[-1]["aceleracao"],
                )
            )
    colunas = [
        "cenario",
        "n",
        "repeticoes",
        "consultas",
        "t_construcao_ms",
        "t_consulta_kd_us",
        "t_consulta_linear_us",
        "aceleracao",
        "t_regiao_us",
        "visitas_por_consulta",
        "fracao_visitada",
        "podas_por_consulta",
        "altura",
        "memoria_kb",
        "divergencias",
    ]
    return gravar("e3_espacial.csv", colunas, linhas)


def experimento_dimensionalidade():
    """E3b: degradação da poda geométrica com o aumento da dimensão."""
    print("E3b: KD-Tree - efeito da dimensionalidade")
    tamanho = 8000
    consultas_por_configuracao = 100
    linhas = []
    for dimensoes in DIMENSOES:
        amostras = []
        for repeticao in range(REPETICOES):
            semente = SEMENTE_BASE + repeticao
            pontos = pontos_uniformes(tamanho, dimensoes, semente)
            consultas = pontos_uniformes(consultas_por_configuracao, dimensoes, semente + 5)
            arvore = KDTree(dimensoes).build(pontos)
            marca = arvore.counters.snapshot()
            tempo = cronometrar(lambda: [arvore.nearest(consulta) for consulta in consultas])
            contadores = arvore.counters.delta(marca)
            tempo_linear = cronometrar(
                lambda: [vizinho_por_forca_bruta(pontos, consulta) for consulta in consultas]
            )
            amostras.append(
                {
                    "t_consulta": tempo,
                    "t_linear": tempo_linear,
                    "visitas": contadores["node_visits"],
                    "podas": contadores["pruned_subtrees"],
                    "altura": arvore.height(),
                }
            )
        linhas.append(
            {
                "dimensoes": dimensoes,
                "n": tamanho,
                "repeticoes": REPETICOES,
                "consultas": consultas_por_configuracao,
                "t_consulta_kd_us": round(
                    media([a["t_consulta"] for a in amostras]) * 1e6 / consultas_por_configuracao, 3
                ),
                "t_consulta_linear_us": round(
                    media([a["t_linear"] for a in amostras]) * 1e6 / consultas_por_configuracao, 3
                ),
                "aceleracao": round(
                    media([a["t_linear"] for a in amostras]) / media([a["t_consulta"] for a in amostras]),
                    2,
                ),
                "visitas_por_consulta": round(
                    media([a["visitas"] for a in amostras]) / consultas_por_configuracao, 2
                ),
                "fracao_visitada": round(
                    media([a["visitas"] for a in amostras]) / consultas_por_configuracao / tamanho, 5
                ),
                "podas_por_consulta": round(
                    media([a["podas"] for a in amostras]) / consultas_por_configuracao, 2
                ),
                "altura": int(media([a["altura"] for a in amostras])),
            }
        )
        print(
            "   d=%2d  visitas/consulta %8.1f  fração da base %6.2f%%  aceleração %6.2fx"
            % (
                dimensoes,
                linhas[-1]["visitas_por_consulta"],
                100.0 * linhas[-1]["fracao_visitada"],
                linhas[-1]["aceleracao"],
            )
        )
    colunas = [
        "dimensoes",
        "n",
        "repeticoes",
        "consultas",
        "t_consulta_kd_us",
        "t_consulta_linear_us",
        "aceleracao",
        "visitas_por_consulta",
        "fracao_visitada",
        "podas_por_consulta",
        "altura",
    ]
    return gravar("e3b_dimensionalidade.csv", colunas, linhas)


def experimento_localidade():
    """E4: custo médio de acesso em função da concentracao da carga."""
    print("E4: localidade temporal de referência")
    tamanho = 20000
    acessos = 40000
    linhas = []
    for expoente in EXPOENTES_ZIPF:
        for nome in ["BST", "AVL", "Splay", "Treap"]:
            amostras = []
            for repeticao in range(REPETICOES):
                semente = SEMENTE_BASE + repeticao
                insercoes = chaves_aleatorias(tamanho, semente)
                ranqueamento = chaves_aleatorias(tamanho, semente + 97)
                consultas = acessos_zipf(ranqueamento, acessos, expoente, semente + 13)
                estrutura = construtores_comparacao(semente)[nome]()
                for chave in insercoes:
                    estrutura.insert(chave, chave)
                marca = estrutura.counters.snapshot()
                tempo = cronometrar(lambda: [estrutura.contains(chave) for chave in consultas])
                contadores = estrutura.counters.delta(marca)
                amostras.append(
                    {
                        "t": tempo,
                        "visitas": contadores["node_visits"],
                        "comparacoes": contadores["comparisons"],
                        "rotacoes": contadores["rotations"],
                    }
                )
            linhas.append(
                {
                    "expoente_zipf": expoente,
                    "estrutura": nome,
                    "n": tamanho,
                    "acessos": acessos,
                    "repeticoes": REPETICOES,
                    "t_por_acesso_us": round(media([a["t"] for a in amostras]) * 1e6 / acessos, 4),
                    "visitas_por_acesso": round(media([a["visitas"] for a in amostras]) / acessos, 3),
                    "comparacoes_por_acesso": round(
                        media([a["comparacoes"] for a in amostras]) / acessos, 3
                    ),
                    "rotacoes_por_acesso": round(media([a["rotacoes"] for a in amostras]) / acessos, 3),
                }
            )
            print(
                "   s=%.1f %-6s visitas/acesso %8.3f  tempo/acesso %7.3f us"
                % (
                    expoente,
                    nome,
                    linhas[-1]["visitas_por_acesso"],
                    linhas[-1]["t_por_acesso_us"],
                )
            )
    colunas = [
        "expoente_zipf",
        "estrutura",
        "n",
        "acessos",
        "repeticoes",
        "t_por_acesso_us",
        "visitas_por_acesso",
        "comparacoes_por_acesso",
        "rotacoes_por_acesso",
    ]
    return gravar("e4_localidade.csv", colunas, linhas)


def main():
    """Executa a bateria completa de experimentos."""
    inicio = time.perf_counter()
    experimento_comparacao()
    experimento_texto()
    experimento_espacial()
    experimento_dimensionalidade()
    experimento_localidade()
    print("\nTempo total dos experimentos: %.1f s" % (time.perf_counter() - inicio))


if __name__ == "__main__":
    main()
