"""
Generador de capturas PNG para los 4 árboles Branch & Bound.
Produce imágenes limpias aptas para incluir en el README.
"""

import json
import math
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyArrowPatch

COLORES = {
    "Expandido":               "#2563eb",
    "Podado por Cota":         "#dc2626",
    "Podado por Inviabilidad": "#ea580c",
    "Solución Completa":       "#16a34a",
}

TITULOS = {
    "arbol_lifo":         "Árbol B&B — Estrategia LIFO (DFS)\n34 nodos | Mejor costo: 30 | A→C→E→D→B→A",
    "arbol_best":         "Árbol B&B — Estrategia Best-First (Least-Cost)\n23 nodos | Mejor costo: 30 | A→C→E→D→B→A",
    "arbol_cota_ingenua": "Árbol B&B — Cota Ingenua (Best-First)\n18 nodos | Cota débil: menos poda real",
    "arbol_ce99":         "Árbol B&B — C→E = 99 (Best-First)\n23 nodos | Nodo A→C→E podado con LB=119",
}


def calcular_posiciones(nodos, edges):
    """Posiciona nodos por nivel con distribución horizontal uniforme."""
    by_level = {}
    for n in nodos:
        lv = n["nivel"]
        by_level.setdefault(lv, []).append(n["id"])

    # Orden horizontal respetando árbol: padre centra sobre hijos
    # Construir mapa padre→hijos
    children = {n["id"]: [] for n in nodos}
    for e in edges:
        children[e["from"]].append(e["to"])

    node_map = {n["id"]: n for n in nodos}
    pos = {}

    def subtree_width(nid):
        ch = children[nid]
        if not ch:
            return 1
        return sum(subtree_width(c) for c in ch)

    def assign_x(nid, left_offset):
        w = subtree_width(nid)
        pos[nid] = left_offset + w / 2
        cursor = left_offset
        for c in children[nid]:
            cw = subtree_width(c)
            assign_x(c, cursor)
            cursor += cw

    # Raíz
    root = nodos[0]["id"]
    total_w = subtree_width(root)
    assign_x(root, 0)

    # Y por nivel
    max_level = max(n["nivel"] for n in nodos)
    y_pos = {}
    for n in nodos:
        y_pos[n["id"]] = max_level - n["nivel"]

    return {nid: (pos[nid], y_pos[nid]) for nid in pos}, total_w, max_level


def dibujar_arbol(json_path, output_path, titulo):
    with open(json_path) as f:
        data = json.load(f)

    nodos = data["nodes"]
    edges = data["edges"]
    node_map = {n["id"]: n for n in nodos}

    positions, total_w, max_level = calcular_posiciones(nodos, edges)

    fig_w = max(12, total_w * 1.1)
    fig_h = max(7, (max_level + 1) * 1.6)

    fig, ax = plt.subplots(figsize=(fig_w, fig_h))
    ax.set_facecolor("#f8f9fa")
    fig.patch.set_facecolor("#ffffff")

    # Dibujar aristas
    for e in edges:
        p1 = positions[e["from"]]
        p2 = positions[e["to"]]
        ax.annotate("",
            xy=(p2[0], p2[1] + 0.22),
            xytext=(p1[0], p1[1] - 0.22),
            arrowprops=dict(
                arrowstyle="-|>",
                color="#9ca3af",
                lw=0.8,
                mutation_scale=10,
            )
        )

    # Dibujar nodos
    R = 0.20
    for n in nodos:
        nid = n["id"]
        x, y = positions[nid]
        color = COLORES.get(n["estado"], "#888888")

        circle = plt.Circle((x, y), R, color=color, zorder=3, alpha=0.9)
        ax.add_patch(circle)

        # ID del nodo
        ax.text(x, y + 0.02, str(nid),
                ha="center", va="center",
                fontsize=7.5, fontweight="bold",
                color="white", zorder=4)

        # LB debajo del nodo
        lb_str = str(n["lb"]) if n["lb"] != "INF" else "∞"
        ax.text(x, y - R - 0.09, f"LB={lb_str}",
                ha="center", va="top",
                fontsize=5.5, color="#374151", zorder=4)

        # Camino (solo última ciudad para no saturar)
        partes = n["camino"].split(" → ")
        label = "→".join(partes)
        ax.text(x, y - R - 0.22, label,
                ha="center", va="top",
                fontsize=4.8, color="#6b7280", zorder=4,
                style="italic")

    ax.set_xlim(-0.5, total_w + 0.5)
    ax.set_ylim(-0.8, max_level + 0.8)
    ax.axis("off")

    ax.set_title(titulo, fontsize=11, fontweight="bold",
                 color="#111827", pad=14, loc="center")

    # Leyenda
    legend_handles = [
        mpatches.Patch(color=c, label=estado)
        for estado, c in COLORES.items()
    ]
    ax.legend(handles=legend_handles, loc="upper right",
              fontsize=7, framealpha=0.9,
              edgecolor="#e5e7eb", fancybox=True)

    # Nivel labels al costado
    for lv in range(max_level + 1):
        y_lv = max_level - lv
        ax.text(-0.3, y_lv, f"Nv.{lv}",
                ha="right", va="center",
                fontsize=7, color="#9ca3af")

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight",
                facecolor="white")
    plt.close()
    print(f"  → PNG generado: {output_path}")


if __name__ == "__main__":
    casos = [
        ("arbol_lifo.json",         "captura_lifo.png",         TITULOS["arbol_lifo"]),
        ("arbol_best.json",         "captura_best.png",         TITULOS["arbol_best"]),
        ("arbol_cota_ingenua.json", "captura_cota_ingenua.png", TITULOS["arbol_cota_ingenua"]),
        ("arbol_ce99.json",         "captura_ce99.png",         TITULOS["arbol_ce99"]),
    ]

    for json_f, png_f, titulo in casos:
        dibujar_arbol(json_f, png_f, titulo)

    print("\nListo. 4 capturas generadas.")
