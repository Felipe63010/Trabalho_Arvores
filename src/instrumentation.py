"""Instrumentação de operações elementares das estruturas de dados.

Cada estrutura implementada neste trabalho mantém uma instância de
:class:`Counters`, que registra o número de operações elementares
executadas. Esses contadores são independentes do relógio do sistema e
permitem comparar as estruturas por uma métrica determinista, imune a
variações de carga da máquina e ao custo do interpretador.
"""

from dataclasses import dataclass, asdict, fields


@dataclass
class Counters:
    """Contadores de operações elementares."""

    comparisons: int = 0
    node_visits: int = 0
    rotations: int = 0
    splits: int = 0
    merges: int = 0
    nodes_created: int = 0
    nodes_removed: int = 0
    distance_evals: int = 0
    pruned_subtrees: int = 0

    def reset(self):
        """Zera todos os contadores."""
        for field in fields(self):
            setattr(self, field.name, 0)

    def snapshot(self):
        """Retorna uma cópia dos contadores no formato de dicionário."""
        return asdict(self)

    def delta(self, previous):
        """Retorna a diferença entre o estado atual e um estado anterior."""
        current = self.snapshot()
        return {name: current[name] - previous[name] for name in current}
