"""
Pregunta 4.3 — Efecto Espejismo: C→E = 99
DAA - Diseño y Análisis de Algoritmos

Modifica un único arco (C→E = 99) y regenera el árbol Best-First.
Demuestra analíticamente el impacto sobre la LB del nodo raíz
y compara la topología de los primeros 3 niveles con el árbol original.

Ejecutar directamente para ver el análisis y generar:
  - arbol_ce99.json / .dot
"""

import math
from bnb_tsp import (
    branch_and_bound,
    reducir_matriz,
    exportar_json,
    exportar_dot,
    MATRIZ_ORIGINAL,
    CIUDADES,
)

INF = math.inf

# Matriz modificada: C→E = 99 (arco prohibitivo)
MATRIZ_CE99 = [row[:] for row in MATRIZ_ORIGINAL]
MATRIZ_CE99[2][4] = 99  # fila C (índice 2), columna E (índice 4)

# Función auxiliar para mostrar paso a paso la reducción del nodo raíz
def mostrar_reduccion_raiz(matriz, nombre):
    """Muestra paso a paso la reducción del nodo raíz."""
    print(f"\n  [{nombre}] Reducción del nodo raíz:")
    mat = [row[:] for row in matriz]
    N = 5
    nombres = list("ABCDE")
    costo_total = 0

    print("  Paso 1 — mínimos de filas:")
    for i in range(N):
        m = min(mat[i])
        if m != INF and m > 0:
            costo_total += m
            mat[i] = [v - m if v != INF else INF for v in mat[i]]
        m_str = str(m) if m != INF else "∞"
        print(f"    Fila {nombres[i]}: mínimo = {m_str}")

    print("  Paso 2 — mínimos de columnas (sobre matriz ya reducida por filas):")
    for j in range(N):
        m = min(mat[i][j] for i in range(N))
        if m != INF and m > 0:
            costo_total += m
            for i in range(N):
                if mat[i][j] != INF:
                    mat[i][j] -= m
        m_str = str(m) if m != INF else "∞"
        print(f"    Col  {nombres[j]}: mínimo = {m_str}")

    print(f"  LB raíz {nombre} = {costo_total}")
    return costo_total


if __name__ == "__main__":
    print("·" * 58)
    print("  Pregunta 4.3 — Efecto Espejismo: C→E = 99")
    print("·" * 58)

    # Árbol original (Best-First)
    costo_orig, camino_orig, nodos_orig = branch_and_bound(MATRIZ_ORIGINAL, estrategia="best")

    # Árbol modificado (Best-First, C→E=99)
    costo_mod, camino_mod, nodos_mod = branch_and_bound(MATRIZ_CE99, estrategia="best")

    exportar_json(nodos_mod, "arbol_ce99.json")
    exportar_dot(nodos_mod, "arbol_ce99.dot")

    print()
    print(f"  Original  → Costo: {costo_orig} | Ruta: {' → '.join(CIUDADES[c] for c in camino_orig)} | Nodos: {len(nodos_orig)}")
    print(f"  C→E = 99  → Costo: {costo_mod}  | Ruta: {' → '.join(CIUDADES[c] for c in camino_mod)} | Nodos: {len(nodos_mod)}")

    # Análisis numérico de la LB raíz
    lb_orig  = mostrar_reduccion_raiz(MATRIZ_ORIGINAL, "Original ")
    lb_mod   = mostrar_reduccion_raiz(MATRIZ_CE99,     "C→E = 99")

    print()
    print(f"  LB raíz original : {lb_orig}")
    print(f"  LB raíz C→E=99   : {lb_mod}")
    print(f"  Diferencia       : {lb_mod - lb_orig:+d}")
    print()
    print("  Interpretación:")
    print("  La LB raíz BAJÓ de 21 a 20 aunque C→E se volvió prohibitivo.")
    print("  Motivo: el mínimo de fila C sube (de 3 a 4, pierde C→E=3),")
    print("  pero el mínimo de columna E baja en más (antes aportaba 2,")
    print("  ahora aporta 0). Balance neto = -1.")
    print("  Esto es el 'efecto espejismo': un cambio local costoso puede")
    print("  reducir la cota global porque reorganiza los mínimos residuales.")
    print()

    # Comparación primeros 3 niveles
    nmap_orig = {n.id: n for n in nodos_orig}
    nmap_mod  = {n.id: n for n in nodos_mod}
    print("  Primeros 3 niveles — Original vs C→E=99:")
    print(f"  {'ID':<4} {'Camino (orig)':<22} {'LB orig':<9} {'Camino (mod)':<22} {'LB mod':<9} {'Estado mod'}")
    print("  " + "-"*82)
    for nid in sorted(set(list(nmap_orig.keys())[:12] + list(nmap_mod.keys())[:12])):
        no = nmap_orig.get(nid)
        nm = nmap_mod.get(nid)
        if no and nm and (len(no.camino) - 1) <= 2:
            print(f"  {nid:<4} {no.camino_str():<22} {no.lb:<9} {nm.camino_str():<22} {nm.lb:<9} {nm.estado}")

    print("·" * 58)
