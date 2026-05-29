"""
Pregunta 4.2 — Comparación Cota Robusta vs Cota Ingenua
DAA - Diseño y Análisis de Algoritmos

Variante del motor principal que reemplaza la función de acotación
por una cota ingenua: suma de mínimos salientes de ciudades no visitadas,
sin reducción de columnas ni penalización de conectividad hamiltoniana.

Ejecutar directamente para ver la comparación y generar:
  - arbol_cota_ingenua.json / .dot
"""

# Código para comparar la cantidad de nodos instanciados con cota robusta vs cota ingenua
from bnb_tsp import (
    branch_and_bound,
    exportar_json,
    exportar_dot,
    MATRIZ_ORIGINAL,
    CIUDADES,
)

if __name__ == "__main__":
    print("·" * 55)
    print("  Pregunta 4.2 — Cota Robusta vs Cota Ingenua")
    print("·" * 55)

    # Cota robusta (reducción completa de matriz)
    _, _, nodos_robusta = branch_and_bound(MATRIZ_ORIGINAL, estrategia="best", usar_cota_ingenua=False)

    # Cota ingenua (suma de mínimos salientes)
    _, _, nodos_ingenua = branch_and_bound(MATRIZ_ORIGINAL, estrategia="best", usar_cota_ingenua=True)

    exportar_json(nodos_ingenua, "arbol_cota_ingenua.json")
    exportar_dot(nodos_ingenua, "arbol_cota_ingenua.dot")

    print()
    print(f"  Nodos instanciados — cota robusta : {len(nodos_robusta)}")
    print(f"  Nodos instanciados — cota ingenua : {len(nodos_ingenua)}")
    print()

    # Mostrar nodo nivel 3 de cada árbol para comparación directa
    print("  Nodo de nivel 3 — A → C → B → E:")
    print()

    for nombre, nodos in [("Robusta", nodos_robusta), ("Ingenua", nodos_ingenua)]:
        for n in nodos:
            if "C" in n.camino_str() and "B" in n.camino_str() and "E" in n.camino_str() and len(n.camino) == 4:
                print(f"    [{nombre}] ID:{n.id} | Camino: {n.camino_str()} | LB: {n.lb} | Estado: {n.estado}")
                break

    print()
    print("  Conclusión:")
    print("  La cota ingenua subestima el LB real porque ignora que")
    print("  las columnas se bloquean al seleccionar aristas.")
    print("  Un LB artificialmente bajo = menos poda efectiva = más")
    print("  nodos explorados innecesariamente en instancias grandes.")
    print("·" * 55)
