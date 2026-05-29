# Branch & Bound — TSP
### Diseño y Análisis de Algoritmos
### Integrante: Sara Roman Leiva

Implementación del algoritmo de Ramificación y Poda (Branch & Bound) para el Problema del Viajante de Comercio (TSP), con reducción de matrices, múltiples estrategias de exploración y exportación completa del árbol de búsqueda.

---

## Cómo ejecutar

```bash
# Instalar dependencia para capturas
pip install matplotlib

# Ejecutar el motor principal (genera todos los JSON y DOT)
python3 bnb_tsp.py

# Ejecutar pregunta 4.2 individualmente
python3 pregunta_4_2_cota_ingenua.py

# Ejecutar pregunta 4.3 individualmente
python3 pregunta_4_3_espejismo.py

# Generar los PNG de los árboles
python3 generar_capturas.py
```

---

## Escenario experimental

Instancia asimétrica de 5 ciudades (A, B, C, D, E):

|       | A   | B   | C   | D   | E   |
|-------|-----|-----|-----|-----|-----|
| **A** | ∞   | 14  | 4   | 10  | 20  |
| **B** | 14  | ∞   | 7   | 8   | 12  |
| **C** | 4   | 5   | ∞   | 16  | 3   |
| **D** | 11  | 7   | 16  | ∞   | 2   |
| **E** | 18  | 10  | 4   | 2   | ∞   |

**Solución óptima:** A → C → E → D → B → A, costo = **30**

---

## Reducción del nodo raíz (cálculo completo)

### Paso 1 — Reducción de filas

| Fila | Mínimo | Aporte al LB |
|------|--------|-------------|
| A    | 4      | 4           |
| B    | 7      | 7           |
| C    | 3      | 3           |
| D    | 2      | 2           |
| E    | 2      | 2           |

Subtotal filas: 4+7+3+2+2 = **18**

### Paso 2 — Reducción de columnas (sobre matriz ya reducida)

| Col | Mínimo | Aporte al LB|
|-----|--------|-------------|
| A   | 1      | 1           |
| B   | 2      | 2           |
| C   | 0      | 0           |
| D   | 0      | 0           |
| E   | 0      | 0           |

Subtotal columnas: 1+2 = **3**

### LB raíz = 18 + 3 = **21**

Matriz reducida resultante:

|   | A  | B  | C  | D  | E  |
|---|----|----|----|----|----|
| A | ∞  | 8  | 0  | 6  | 16 |
| B | 6  | ∞  | 0  | 1  | 5  |
| C | 0  | 0  | ∞  | 13 | 0  |
| D | 8  | 3  | 14 | ∞  | 0  |
| E | 15 | 6  | 2  | 0  | ∞  |

---

## Pregunta 4.1 — Anatomía de la Poda y la Incumbente Temprana

### Árbol LIFO (DFS) — 34 nodos
<img width="1364" height="551" alt="imagen" src="https://github.com/user-attachments/assets/b7c01c2c-d985-468d-9ee3-ba74c5220648" />


**Primera incumbente:** Nodo ID **10**, camino `[A→E→D→C→B]`, costo = **57**.

Bajo LIFO el algoritmo desciende por la rama A→E (apilada al último), llega hasta hoja rápido pero por un camino costoso. La primera solución encontrada (57) está lejos del óptimo porque DFS no distingue qué rama es más prometedora.

### Árbol Best-First (Least-Cost) — 23 nodos
<img width="1130" height="576" alt="imagen" src="https://github.com/user-attachments/assets/daba2cd2-b4ce-4497-9ad0-c6e184a4fdec" />


**Nodo creado pero jamás expandido:** Nodo ID **4**, camino `[A→E]`, LB = **40**.

Justificación matemática de la poda:

```
LB(nodo 4) = 40
Incumbente óptima encontrada = 30

Condición de poda: LB >= incumbente  →  40 >= 30  ✓  PODADO
```

El nodo fue instanciado en nivel 1, pero para cuando llegó al frente de la cola de prioridad ya existía una solución de costo 30. Explorar una rama cuyo mejor caso sería 40 no tiene sentido.

**Comparación directa:**

| Métrica              | LIFO | Best-First |
|----------------------|------|-----------|
| Nodos instanciados   | 34   | 23        |
| Primera incumbente   | ID 10, costo 57 | — |
| Costo final óptimo   | 30   | 30        |
| Solución encontrada en | Nodo 26 | Nodo 22 |

---

## Pregunta 4.2 — Sensibilidad Estructural ante la Función de Acotación

### Árbol con cota ingenua — 18 nodos
<img width="878" height="581" alt="imagen" src="https://github.com/user-attachments/assets/d70a5aa1-74b3-4835-9344-632c2f3292ff" />


### Tabla comparativa (Best-First)

| Esquema de acotación | Nodos instanciados |
|----------------------|-------------------|
| Cota robusta (reducción de matriz) | 23 |
| Cota ingenua (suma de mínimos salientes) | 18 |

> La cota ingenua genera *menos* nodos en esta instancia pequeña, pero eso no significa que sea mejor: entrega valores subvalorados que en instancias grandes retrasan la poda y producen más iteraciones inútiles.

### Comparación a nivel 3 — nodo `A → C → B → E`

| Método | LB calculado | Cómo se obtiene |
|--------|-------------|-----------------|
| Cota robusta | **34** | LB padre (27) + costo arco B→E en matriz reducida (7) + reducción residual (0) |
| Cota ingenua | **23** | Costo real acumulado A→C→B→E (21) + mínimo saliente de D (2) |

La diferencia de **11 puntos** ocurre porque la cota ingenua ignora que las columnas ya bloqueadas por aristas previas elevan el costo mínimo necesario para completar el ciclo hamiltoniano.

### Fenómeno de retraso en la poda

Con cota ingenua, el camino `A → C → B → D → E` llega hasta nivel hoja (nodo 14) con LB=19. La cota robusta lo habría podado en nivel 3 porque la reducción residual de la matriz ya refleja que no quedan columnas baratas disponibles. Este comportamiento no puede predecirse sin instanciar la matriz reducida: el costo adicional depende de cuáles columnas quedaron bloqueadas, lo cual es combinatoriamente dependiente del camino exacto recorrido.

---

## Pregunta 4.3 — El "Efecto Espejismo" y Resiliencia Topológica

### Modificación: C→E = 99 (arco prohibitivo)

### Árbol Best-First con C→E=99 — 23 nodos
<img width="1133" height="562" alt="imagen" src="https://github.com/user-attachments/assets/1adaf6d9-d65c-45ab-b3bc-007774b39f74" />


### Comparación primeros 3 niveles

| ID | Camino | LB original | LB C→E=99 | Estado C→E=99 |
|----|--------|-------------|-----------|---------------|
| 0  | A      | 21          | 20        | Expandido     |
| 1  | A→B    | 29          | 29        | Expandido     |
| 2  | A→C    | 27          | 27        | Expandido     |
| 3  | A→D    | 29          | 28        | Expandido     |
| 4  | A→E    | 40          | 40        | Podado        |
| 7  | A→C→E  | **30**      | **126**   | Podado        |

Los IDs se mantienen estables en los primeros niveles porque el orden de generación es determinístico (el algoritmo siempre genera los hijos de A en el mismo orden). El cambio en C→E no afecta qué nodos se crean primero, solo cuándo se podan.

### Análisis numérico del nodo raíz con C→E=99

**Paso 1 — Reducción de filas:**

| Fila | Original | C→E=99 | Diferencia |
|------|----------|--------|-----------|
| A    | 4        | 4      | —         |
| B    | 7        | 7      | —         |
| C    | **3**    | **4**  | +1 (pierde C→E=3, nuevo mín es C→A=4) |
| D    | 2        | 2      | —         |
| E    | 2        | 2      | —         |

Subtotal filas C→E=99: **19** (+1)

**Paso 2 — Reducción de columnas (sobre matriz ya reducida):**

| Col | Original | C→E=99 | Diferencia |
|-----|----------|--------|-----------|
| A   | 1        | **0**  | −1 (el 0 de C→A ahora queda en col A) |
| B   | 2        | **1**  | −1 |
| C   | 0        | 0      | —  |
| D   | 0        | 0      | —  |
| E   | 0        | 0      | — (el mínimo de col E ahora viene de D→E=2→0) |

Subtotal columnas C→E=99: **1** (−2)

**LB raíz C→E=99 = 19 + 1 = 20** (bajó de 21)

**Interpretación del efecto espejismo:** aunque C→E=99 hace ese arco inviable en la práctica, el nodo raíz reporta una cota *menor* que el original. Esto ocurre porque la reorganización de mínimos residuales produce un balance neto negativo: la fila C sube en 1 pero las columnas bajan en 2. La cota global "parece" más prometedora a pesar de que internamente hay una ruta bloqueada. Este es el efecto espejismo: una alteración costosa puede hacer que el espacio de búsqueda aparente ser más barato en su cota global.
