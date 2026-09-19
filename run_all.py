"""Reproduz integralmente o trabalho: testes, demonstração, figuras, experimentos e relatório.

A execução completa leva alguns minutos, dominados pela bateria de
experimentos. Cada etapa pode ser executada isoladamente pelos módulos
correspondentes; este roteiro apenas garante a ordem correta, já que os
gráficos dependem dos resultados e o relatório depende de ambos.
"""

import os
import subprocess
import sys
import time

RAIZ = os.path.dirname(os.path.abspath(__file__))

ETAPAS = [
    ("Testes automatizados", [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-t", "."]),
    ("Demonstração das estruturas", [sys.executable, "demo/demonstracao.py"]),
    ("Figuras de rastreamento visual", [sys.executable, "viz/gerar_figuras.py"]),
    ("Experimentos computacionais", [sys.executable, "experiments/benchmark.py"]),
    ("Gráficos dos resultados", [sys.executable, "experiments/gerar_graficos.py"]),
]


def main():
    """Executa todas as etapas na ordem de dependência."""
    inicio = time.perf_counter()
    for indice, (titulo, comando) in enumerate(ETAPAS, start=1):
        print("\n[%d/%d] %s" % (indice, len(ETAPAS), titulo))
        print("-" * 70)
        resultado = subprocess.run(comando, cwd=RAIZ)
        if resultado.returncode != 0:
            print("\nEtapa '%s' falhou com código %d." % (titulo, resultado.returncode))
            return resultado.returncode
    print("\n" + "=" * 70)
    print("Execução completa em %.1f s." % (time.perf_counter() - inicio))
    return 0


if __name__ == "__main__":
    sys.exit(main())
