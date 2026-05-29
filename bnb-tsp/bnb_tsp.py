"""
Branch & Bound - TSP (Traveling Salesman Problem)
DAA - Diseño y Análisis de Algoritmos

Técnica: Reducción de matriz de costos para calcular Lower Bound.
Estrategias de exploración: LIFO (DFS), Best-First (Least-Cost).
Exporta el árbol completo a JSON y formato Graphviz DOT.

Ciudades: A=0, B=1, C=2, D=3, E=4
"""

import json
import heapq
import copy
import math

INF = math.inf

# Matriz de costos original 
#       A    B    C    D    E
MATRIZ_ORIGINAL = [
    [INF, 14,  4,  10,  20],   # A
    [14,  INF,  7,   8,  12],   # B
    [ 4,   5, INF,  16,   3],   # C
    [11,   7,  16, INF,   2],   # D
    [18,  10,   4,   2, INF],   # E
]

CIUDADES = ['A', 'B', 'C', 'D', 'E']
N = 5


# Funciones para reducción de matriz 

def reducir_matriz(mat):
    """
    Reduce filas y columnas restando el mínimo de cada una.
    Retorna (matriz reducida, costo de reducción acumulado).
    """
    mat = [row[:] for row in mat]  # copia
    costo = 0

    # Reducción de filas
    for i in range(N):
        min_fila = min(mat[i])
        if min_fila == INF:
            continue
        if min_fila > 0:
            costo += min_fila
            mat[i] = [v - min_fila if v != INF else INF for v in mat[i]]

    # Reducción de columnas
    for j in range(N):
        min_col = min(mat[i][j] for i in range(N))
        if min_col == INF:
            continue
        if min_col > 0:
            costo += min_col
            for i in range(N):
                if mat[i][j] != INF:
                    mat[i][j] -= min_col

    return mat, costo


# Función para calcular LB del hijo al añadir una arista (desde → hacia)
def calcular_lb_hijo(mat_padre, lb_padre, desde, hacia):
    """
    Calcula la LB del hijo al añadir la arista (desde → hacia).
    Proceso:
      1. Costo del arco en la matriz padre
      2. Poner fila 'desde' y columna 'hacia' en INF
      3. Poner arco inverso (hacia → desde) en INF para evitar subciclos
      4. Reducir la nueva matriz y sumar costos
    """
    mat = [row[:] for row in mat_padre]
    costo_arco = mat[desde][hacia]

    # Bloquea fila de origen y columna de destino
    for k in range(N):
        mat[desde][k] = INF
        mat[k][hacia] = INF

    # Bloquea arco inverso
    mat[hacia][desde] = INF

    mat_reducida, costo_reduccion = reducir_matriz(mat)

    lb = lb_padre + costo_arco + costo_reduccion
    return mat_reducida, lb


# Función para cota ingenua (Pregunta 4.2) - sin reducción ni penalización de conectividad

def cota_ingenua(camino, mat_original):
    """
    Suma los mínimos salientes de cada ciudad NO visitada aún,
    más el costo del último arco añadido.
    Sin reducción de columnas ni penalización de conectividad.
    """
    visitadas = set(camino)
    costo = 0

    # Costo acumulado real del camino actual
    for k in range(len(camino) - 1):
        costo += mat_original[camino[k]][camino[k+1]]

    # Mínimo saliente de cada ciudad no visitada
    for i in range(N):
        if i not in visitadas:
            mins = [mat_original[i][j] for j in range(N) if j != i]
            m = min(mins)
            if m != INF:
                costo += m

    return costo


# Nodo del árbol

class Nodo:
    _contador = 0

    def __init__(self, camino, lb, mat_reducida, padre_id=None):
        self.id = Nodo._contador
        Nodo._contador += 1
        self.camino = camino          # Lista de índices de ciudades
        self.lb = lb
        self.mat = mat_reducida
        self.padre_id = padre_id
        self.estado = "Expandido"     # Se actualiza durante la búsqueda

    def __lt__(self, other):
        return self.lb < other.lb

    def camino_str(self):
        return " → ".join(CIUDADES[c] for c in self.camino)


# Funcion principla con la implementación de motor de Branch & Bound

def branch_and_bound(matriz, estrategia="best", usar_cota_ingenua=False):
    """
    estrategia: "best" (Best-First/Least-Cost) | "lifo" (DFS)
    usar_cota_ingenua: True para la variante de Pregunta 4.2
    Retorna (mejor_costo, mejor_camino, lista_de_nodos)
    """
    Nodo._contador = 0

    mat_inicial, lb_inicial = reducir_matriz([row[:] for row in matriz])

    raiz = Nodo([0], lb_inicial, mat_inicial)  # Empieza en ciudad A (índice 0)
    todos_los_nodos = [raiz]

    mejor_costo = INF
    mejor_camino = None

    # Estructura de cola según estrategia
    if estrategia == "best":
        cola = []
        heapq.heappush(cola, (raiz.lb, raiz))
    else:  # lifo
        cola = [raiz]

    while cola:
        if estrategia == "best":
            _, nodo = heapq.heappop(cola)
        else:
            nodo = cola.pop()

        # Poda por cota
        if nodo.lb >= mejor_costo:
            nodo.estado = "Podado por Cota"
            continue

        # Solución completa
        if len(nodo.camino) == N:
            # Cierra el ciclo volviendo al origen
            costo_retorno = nodo.mat[nodo.camino[-1]][0]
            if costo_retorno == INF:
                nodo.estado = "Podado por Inviabilidad"
                continue
            costo_total = nodo.lb + costo_retorno
            if costo_total < mejor_costo:
                mejor_costo = costo_total
                mejor_camino = nodo.camino + [0]
                nodo.estado = "Solución Completa"
                nodo.lb = costo_total  # Actualiza para visualización
            continue

        # Expandir: generar hijos
        nodo.estado = "Expandido"
        for siguiente in range(N):
            if siguiente in nodo.camino:
                continue

            if usar_cota_ingenua:
                nuevo_camino = nodo.camino + [siguiente]
                lb_hijo = cota_ingenua(nuevo_camino, matriz)
                mat_hijo = nodo.mat  # No se actualiza en cota ingenua
            else:
                mat_hijo, lb_hijo = calcular_lb_hijo(
                    nodo.mat, nodo.lb, nodo.camino[-1], siguiente
                )

            # Poda por inviabilidad: si lb_hijo es INF
            hijo = Nodo(nodo.camino + [siguiente], lb_hijo, mat_hijo, nodo.id)
            todos_los_nodos.append(hijo)

            if lb_hijo == INF:
                hijo.estado = "Podado por Inviabilidad"
                continue

            if lb_hijo >= mejor_costo:
                hijo.estado = "Podado por Cota"
                continue

            if estrategia == "best":
                heapq.heappush(cola, (lb_hijo, hijo))
            else:
                cola.append(hijo)

    # Marcar nodos que quedaron en cola sin expandirse (creados pero nunca expandidos)
    ids_expandidos = {n.id for n in todos_los_nodos if n.estado == "Expandido"}
    # Los que tienen estado default y no llegaron a expandirse
    for n in todos_los_nodos:
        if n.estado == "Expandido" and len(n.camino) < N:
            # Puede que sí se expandieron — se deja el estado como está
            pass

    return mejor_costo, mejor_camino, todos_los_nodos


# Exportación a JSON 

COLORES_ESTADO = {
    "Expandido":              "blue",
    "Podado por Cota":        "red",
    "Podado por Inviabilidad":"orange",
    "Solución Completa":      "green",
}

# Funciones para exportar el árbol a JSON 
def exportar_json(nodos, nombre_archivo):
    """Exporta el árbol a JSON procesable por D3.js."""
    data = {
        "nodes": [],
        "edges": []
    }

    for n in nodos:
        data["nodes"].append({
            "id": n.id,
            "camino": n.camino_str(),
            "lb": round(n.lb, 2) if n.lb != INF else "INF",
            "estado": n.estado,
            "color": COLORES_ESTADO.get(n.estado, "gray"),
            "nivel": len(n.camino) - 1
        })
        if n.padre_id is not None:
            data["edges"].append({"from": n.padre_id, "to": n.id})

    with open(nombre_archivo, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"  → JSON exportado: {nombre_archivo}")
    return data

# Función para exportar a formato Graphviz DOT (para visualización con Graphviz o herramientas online)
def exportar_dot(nodos, nombre_archivo):
    """Exporta el árbol a formato Graphviz DOT."""
    lines = ['digraph TSP_Tree {', '  node [shape=box, fontname="Arial"];']

    for n in nodos:
        color = COLORES_ESTADO.get(n.estado, "gray")
        lb_str = str(round(n.lb, 2)) if n.lb != INF else "INF"
        label = f"ID: {n.id}\\nCamino: [{n.camino_str()}]\\nCota: {lb_str}\\nEstado: {n.estado}"
        lines.append(f'  Node{n.id} [label="{label}", color={color}];')

    for n in nodos:
        if n.padre_id is not None:
            lines.append(f'  Node{n.padre_id} -> Node{n.id};')

    lines.append("}")

    with open(nombre_archivo, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"  → DOT exportado: {nombre_archivo}")

if __name__ == "__main__":
    print("·" * 60)
    print("  BRANCH & BOUND — TSP — 5 ciudades (A,B,C,D,E)")
    print("·" * 60)

    # Escenario 1: LIFO 
    print("\n[1] Estrategia LIFO (DFS)")
    costo, camino, nodos = branch_and_bound(MATRIZ_ORIGINAL, estrategia="lifo")
    print(f"    Mejor costo    : {costo}")
    print(f"    Mejor camino   : {' → '.join(CIUDADES[c] for c in camino)}")
    print(f"    Nodos creados  : {len(nodos)}")
    exportar_json(nodos, "arbol_lifo.json")
    exportar_dot(nodos, "arbol_lifo.dot")

    # Identificar incumbente (primera solución completa encontrada)
    for n in nodos:
        if n.estado == "Solución Completa":
            print(f"    Primera incumbente → Nodo ID: {n.id}, Costo: {n.lb}")
            break

    # Escenario 2: Best-First 
    print("\n[2] Estrategia Best-First (Least-Cost)")
    costo2, camino2, nodos2 = branch_and_bound(MATRIZ_ORIGINAL, estrategia="best")
    print(f"    Mejor costo    : {costo2}")
    print(f"    Mejor camino   : {' → '.join(CIUDADES[c] for c in camino2)}")
    print(f"    Nodos creados  : {len(nodos2)}")
    exportar_json(nodos2, "arbol_best.json")
    exportar_dot(nodos2, "arbol_best.dot")

    # Nodo podado por cota en Best-First
    for n in nodos2:
        if n.estado == "Podado por Cota":
            print(f"    Ejemplo nodo podado por cota → ID: {n.id}, LB: {n.lb} >= {costo2}")
            break

    # Escenario 3: Cota ingenua vs robusta 
    print("\n[3] Cota Ingenua vs Cota Robusta (Best-First)")
    _, _, nodos_ingenua = branch_and_bound(MATRIZ_ORIGINAL, estrategia="best", usar_cota_ingenua=True)
    print(f"    Nodos con cota robusta : {len(nodos2)}")
    print(f"    Nodos con cota ingenua : {len(nodos_ingenua)}")
    exportar_json(nodos_ingenua, "arbol_cota_ingenua.json")
    exportar_dot(nodos_ingenua, "arbol_cota_ingenua.dot")

    # Escenario 4: Modificar C→E = 99 
    print("\n[4] C→E = 99 (Efecto Espejismo)")
    matriz_mod = [row[:] for row in MATRIZ_ORIGINAL]
    matriz_mod[2][4] = 99  # C→E

    _, _, nodos_mod = branch_and_bound(matriz_mod, estrategia="best")
    print(f"    Nodos original : {len(nodos2)}")
    print(f"    Nodos modificado: {len(nodos_mod)}")
    exportar_json(nodos_mod, "arbol_ce99.json")
    exportar_dot(nodos_mod, "arbol_ce99.dot")

    # Analisis del nodo raíz modificado
    print("\n  Reducción del nodo raíz con C→E=99:")
    mat_mod_copy = [row[:] for row in matriz_mod]
    mat_red, lb_raiz = reducir_matriz(mat_mod_copy)
    print(f"    LB raíz original : 21")
    print(f"    LB raíz modificado: {lb_raiz}")
    print(f"    Diferencia       : {lb_raiz - 21}")

    print("\n" + "·" * 60)
    print("  Archivos generados:")
    print("    arbol_lifo.json / .dot")
    print("    arbol_best.json / .dot")
    print("    arbol_cota_ingenua.json / .dot")
    print("    arbol_ce99.json / .dot")
    print("·" * 60)
