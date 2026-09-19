# Estruturas em Árvores Avançadas

Trabalho Prático Individual I — modelagem, implementação e análise comparativa de cinco estruturas de dados hierárquicas não convencionais: **trie**, **árvore Patricia** (radix tree compacta), **árvore splay**, **treap** e **KD-Tree**. As implementações são comparadas entre si e com duas estruturas de referência, a **árvore binária de busca (BST)** e a **árvore AVL**[cite: 1].

---

## Sumário

- [Requisitos](#requisitos)
- [Reprodução completa](#reprodução-completa)
- [Estrutura do repositório](#estrutura-do-repositório)
- [As estruturas implementadas](#as-estruturas-implementadas)
- [Interface pública](#interface-pública)
- [Instrumentação](#instrumentação)
- [Testes](#testes)
- [Experimentos](#experimentos)
- [Figuras](#figuras)
- [Conjuntos de dados](#conjuntos-de-dados)
- [Principais resultados](#principais-resultados)

---

## Requisitos

- Python 3.10 ou superior (desenvolvido e medido em CPython 3.12.3)
- `matplotlib` e `pillow`, usados na geração das figuras e dos gráficos experimentais — **o núcleo das estruturas, em `src/`, não depende de bibliotecas externas**.

```bash
python3 -m pip install -r requirements.txt
```

---

## Reprodução completa

```bash
python3 run_all.py
```

O roteiro executa, nesta ordem: testes automatizados, demonstração textual, figuras de rastreamento visual, bateria de experimentos e gráficos de resultados. A execução leva cerca de quatro minutos, quase todos consumidos pelos experimentos.

Cada etapa também pode ser executada isoladamente:

```bash
python3 -m unittest discover -s tests -t .   # 43 testes de corretude
python3 demo/demonstracao.py                 # demonstração das operações
python3 viz/gerar_figuras.py                 # figuras das estruturas
python3 experiments/benchmark.py             # experimentos (grava CSV em results/)
python3 experiments/gerar_graficos.py        # gráficos a partir dos CSV
```

---

## Estrutura do repositório

```text
.
├── src/                    Implementações (sem dependências externas)
│   ├── trie.py             Trie: um caractere por aresta
│   ├── patricia.py         Radix tree compacta, com divisão e fusão de rótulos
│   ├── splay.py            Árvore splay com reestruturação top-down
│   ├── treap.py            Treap com prioridades aleatórias e estatísticas de ordem
│   ├── kdtree.py           KD-Tree com construção por medianas e poda geométrica
│   ├── bst.py              Árvore binária de busca (referência)
│   ├── avl.py              Árvore AVL (referência)
│   └── instrumentation.py  Contadores de operações elementares
├── tests/                  43 testes de unidade e de esforço com oráculo
├── demo/                   Demonstração textual das operações
├── viz/                    Layout e renderização das árvores
├── experiments/            Geradores de dados e bateria de medições
├── data/lexico.txt         Léxico natural usado nos experimentos de texto
├── figures/                Figuras geradas (PNG)
├── results/                Resultados dos experimentos (CSV) e saída da demonstração
└── run_all.py              Reprodução completa
```

---

## As estruturas implementadas

| Estrutura | Módulo | Critério de organização | Garantia |
|---|---|---|---|
| Trie | `src/trie.py` | um caractere por aresta | `O(m)` por operação[cite: 1, 3] |
| Patricia | `src/patricia.py` | subcadeia por aresta, sem nós de passagem | `O(m)`, no máximo `2n-1` nós[cite: 1, 3] |
| Splay | `src/splay.py` | comparação, com promoção do nó acessado | `O(log n)` amortizado[cite: 1, 3] |
| Treap | `src/treap.py` | comparação + heap de prioridades aleatórias | `O(log n)` esperado[cite: 1, 3] |
| KD-Tree | `src/kdtree.py` | comparação por eixo alternado | `O(log n)` esperado para `k` fixo[cite: 1, 3] |

---

## Interface pública

As sete estruturas expõem a mesma interface básica, o que permite submetê-las ao mesmo procedimento de medição[cite: 1]:

```python
from src.patricia import PatriciaTree

arvore = PatriciaTree()
arvore.insert("computador", 1)     # True se a chave era inédita
arvore.search("computador")        # valor associado, ou None
"computador" in arvore             # True
arvore.remove("computador")        # True se a chave existia
arvore.keys()                      # chaves em ordem lexicográfica
arvore.height(), arvore.node_count, len(arvore)
```

Operações específicas de cada estrutura[cite: 1]:

```python
trie.keys_with_prefix("comp")          # chaves que começam por um prefixo
trie.longest_prefix_of("computadores") # maior chave que é prefixo do texto
splay.minimum(); splay.maximum()       # extremos, promovidos à raiz
menores, maiores = treap.split(50)     # partição por chave
menores.join(maiores)                  # concatenação
treap.kth(3); treap.rank(50)           # estatísticas de ordem
kd.build(pontos)                       # construção balanceada por medianas
kd.nearest((5, 4))                     # vizinho mais próximo
kd.k_nearest((5, 4), 3)                # m vizinhos mais próximos
kd.range_search((0, 0), (10, 10))      # consulta por hiper-retângulo
kd.radius_search((5, 4), 3.0)          # consulta por raio
kd.nearest_with_trace((5, 4))          # consulta com rastro para as figuras
```

---

## Instrumentação

Cada estrutura mantém um objeto `Counters` com contadores de comparações, visitas a nós, rotações, divisões e fusões de rótulos, nós criados e removidos, avaliações de distância e subárvores descartadas por poda[cite: 1]. Essa métrica é determinista e independe do relógio e da carga da máquina[cite: 1]:

```python
marca = arvore.counters.snapshot()
arvore.search(chave)
print(arvore.counters.delta(marca))
```

---

## Testes

```bash
python3 -m unittest discover -s tests -t . -v
```

Além dos testes de unidade sobre casos de borda — chave vazia, chave ausente, remoção de chave inexistente, reinserção, estrutura vazia, tipo inválido e ponto com dimensão incompatível —, cada estrutura é submetida a um teste de esforço que executa milhares de operações aleatórias e compara o estado resultante com um oráculo: um conjunto da biblioteca padrão para as estruturas associativas e a busca exaustiva para as consultas espaciais[cite: 1, 2]. As invariantes estruturais são verificadas após cada sequência[cite: 1].

---

## Experimentos

`experiments/benchmark.py` executa quatro experimentos e grava os resultados em `results/`[cite: 2]:

| Arquivo | Conteúdo |
|---|---|
| `e1_comparacao.csv` | BST, AVL, splay e treap sob inserção aleatória, inserção ordenada e acesso enviesado[cite: 1, 2] |
| `e2_texto.csv` | trie, Patricia e AVL de cadeias sobre três vocabulários[cite: 1, 2] |
| `e3_espacial.csv` | KD-Tree contra busca linear, distribuições uniforme e agrupada[cite: 1, 2] |
| `e3b_dimensionalidade.csv` | efeito da dimensão do espaço sobre a poda geométrica[cite: 1, 2] |
| `e4_localidade.csv` | custo de acesso em função da concentração da carga (Zipf)[cite: 1, 2] |

Cada configuração é repetida três vezes sobre instâncias regeneradas por semente; os valores gravados são médias aritméticas[cite: 1]. O consumo de memória é medido com `tracemalloc`, considerando apenas o que a estrutura aloca além dos objetos das próprias chaves[cite: 1].

---

## Figuras

`viz/gerar_figuras.py` produz, para cada estrutura, três estados sucessivos — após as inserções, após a operação característica e após uma remoção — desenhados a partir do estado real das estruturas em memória[cite: 1, 2]. O posicionamento usa percurso em ordem nas árvores binárias e a regra das folhas consecutivas nas árvores de grau arbitrário; não há dependência de ferramentas externas de desenho de grafos[cite: 1].

---

## Conjuntos de dados

`data/lexico.txt` contém 63.737 palavras minúsculas com três ou mais letras, extraídas da lista `american-english` distribuída com o pacote `wamerican` (SCOWL, de livre distribuição)[cite: 1]. O arquivo é versionado para que os experimentos de texto sejam reproduzíveis em qualquer máquina[cite: 1]. Os demais conjuntos — cadeias aleatórias, identificadores com prefixos compartilhados, chaves inteiras e nuvens de pontos — são gerados por `experiments/datasets.py` a partir de sementes fixas[cite: 1, 2].

---

## Principais resultados

- A compactação da Patricia reduz a memória da trie em **55,9 %** sobre léxico natural e em **83,7 %** sobre cadeias aleatórias, mantendo a mesma capacidade de consulta por prefixo[cite: 3].
- Sob chaves ordenadas, a BST degenera e consome **4.069,8 ms** para inserir 8.000 chaves, contra **49,1 ms** da AVL; a splay é a mais rápida do cenário, com **23,2 ms** para 32.000 chaves[cite: 3].
- Sob acesso enviesado, a splay precisa de **12,8** comparações por busca contra **28,2** da AVL, invertendo-se a vantagem quando o acesso é uniforme[cite: 3].
- A KD-Tree supera a busca linear em **341×** com 32.000 pontos em duas dimensões, inspecionando apenas **0,07 %** da base; a partir de **doze dimensões** o ganho cai abaixo de um e a varredura exaustiva volta a ser mais rápida[cite: 3].

Os valores acima correspondem à execução registrada em `results/`; tempos absolutos variam com a máquina, mas as relações entre as estruturas e os contadores de operações elementares são estáveis[cite: 1, 3].
