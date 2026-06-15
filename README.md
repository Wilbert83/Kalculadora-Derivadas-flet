# 🧮 Calculadora de Derivadas

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat-square&logo=python&logoColor=white)
![Flet](https://img.shields.io/badge/Flet-0.85-00D4AA?style=flat-square)
![SymPy](https://img.shields.io/badge/SymPy-1.12%2B-3B5526?style=flat-square)
![License](https://img.shields.io/badge/Licencia-MIT-green?style=flat-square)
![Estado](https://img.shields.io/badge/Estado-En%20desarrollo-orange?style=flat-square)

Aplicación de escritorio para calcular derivadas de funciones matemáticas, con derivación simbólica exacta (SymPy), método numérico por cociente de Fermat (NumPy) y visualización de fórmulas en LaTeX renderizado mediante matplotlib. Construida con Flet 0.85 sobre Python.

---

## ¿Qué hace?

- **Derivación simbólica** — obtiene la derivada exacta analítica usando SymPy, detecta la regla aplicada (potencia, producto, cadena, etc.) y muestra los pasos intermedios.
- **Cociente de Fermat numérico** — estima f′(x₀) por diferencia central y adelantada con h = 10⁻⁷, calcula el error absoluto contra el valor simbólico exacto.
- **Render LaTeX** — cada expresión matemática se convierte en imagen PNG con matplotlib `mathtext` (sin LaTeX instalado) y se embebe en la UI como data URI.
- **Referencia lateral** — panel fijo con la heurística de Fermat y tabla de derivadas inmediatas.
- **Ejemplos preestablecidos** — chips clicables para cargar funciones de muestra.

---

## Contexto matemático

La derivada se calcula por dos vías independientes:

**Simbólica (exacta)**
```
f'(x) = lim_{Δx→0} [f(x + Δx) − f(x)] / Δx
```
SymPy resuelve este límite de forma algebraica y simplifica el resultado.

**Numérica (Cociente de Fermat — diferencia central)**
```
f'(x₀) ≈ [f(x₀ + h) − f(x₀ − h)] / (2h),   h = 10⁻⁷
```
El error de truncamiento de la diferencia central es O(h²), frente a O(h) de la diferencia adelantada. Ambos valores se muestran para comparación.

---

## Instalación y uso

### Requisitos

- Python 3.10 o superior
- pip

### 1. Clonar el repositorio

```bash
git clone https://github.com/tu-usuario/calculadora-derivadas-flet.git
cd calculadora-derivadas-flet
```

### 2. Crear entorno virtual (recomendado)

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux / macOS
source .venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Ejecutar

```bash
python calculadora_derivadas.py
```

---

## Sintaxis de entrada

| Operación        | Sintaxis aceptada               | Ejemplo              |
|------------------|---------------------------------|----------------------|
| Potencia         | `x**n` o `x^n`                 | `x**3`, `x^3`        |
| Multiplicación   | `*` o implícita con coef.       | `2*x`, `2x`          |
| División         | `/`                             | `sin(x)/x`           |
| Raíz cuadrada    | `sqrt(x)`                       | `sqrt(x**2 + 1)`     |
| Logaritmo nat.   | `log(x)` o `ln(x)`             | `log(x**2 + 1)`      |
| Exponencial      | `exp(x)` o `e` (constante)     | `exp(-x**2)`         |
| Trigonométricas  | `sin`, `cos`, `tan`, `cot`, ... | `sin(x**2) * cos(x)` |
| Inversas trig.   | `asin`, `acos`, `atan`, `acot` | `atan(x) + asin(x)`  |
| Hiperbólicas     | `sinh`, `cosh`, `tanh`, ...    | `sinh(x) * cosh(2*x)`|
| Constantes       | `pi`, `e`                       | `e**x * sin(pi*x)`   |

---

## Ejemplo de ejecución

```
Entrada:   sin(x**2) * exp(-x)

f(x)  = sin(x²) · e^(−x)
f′(x) = 2x·cos(x²)·e^(−x) − sin(x²)·e^(−x)
      = e^(−x)·(2x·cos(x²) − sin(x²))

Fermat numérico en x₀ = 1.0:
  f′(1.0) ≈  0.05872567   (diferencia central)
  Exacto  =  0.05872567
  Error   =  3.47e-13
```

---

## Tecnologías

| Componente     | Versión mínima | Rol                                           |
|----------------|---------------|-----------------------------------------------|
| Python         | 3.10          | Lenguaje base                                 |
| Flet           | 0.85          | Framework UI de escritorio (Flutter/Python)   |
| SymPy          | 1.12          | Motor de derivación simbólica                 |
| NumPy          | 1.24          | Evaluación numérica (diferencia central)      |
| matplotlib     | 3.7           | Render de fórmulas LaTeX → PNG embebido       |

> **Nota:** El render LaTeX usa `matplotlib.mathtext` (`usetex=False`), por lo que **no se requiere** una instalación de LaTeX en el sistema.

---

## Estado del proyecto

> ⚠️ **En desarrollo activo.** La funcionalidad base está operativa. Se trabaja en:
> - Desglose pedagógico completo con identificación de `u` y `u′` por cada regla
> - Soporte de constantes simbólicas (`a`, `b`, `k`, `n`)
> - Derivadas de orden `n`
> - Tabla de referencia completa con 24 tipos
> - Correcciones de compatibilidad con Flet 0.85 en Windows

---

## Estructura del proyecto

```
calculadora-derivadas-flet/
├── calculadora_derivadas.py   # Aplicación principal (UI + motor)
├── requirements.txt           # Dependencias Python
├── .gitignore
└── README.md
```

> Estructura de módulos planificada para versiones futuras:
> ```
> src/
> ├── engine/
> │   ├── parser.py        # Parseo y normalización de expresiones
> │   ├── symbolic.py      # Derivación simbólica + detección de reglas
> │   └── numeric.py       # Cociente de Fermat numérico
> ├── ui/
> │   ├── components.py    # Widgets reutilizables
> │   ├── sidebar.py       # Panel lateral (Fermat + referencia)
> │   └── cards.py         # Tarjetas de resultado
> ├── render/
> │   └── latex.py         # Render matplotlib → data URI PNG
> └── main.py
> ```

---

## Autor

**Wilbert Miguel Nahuatlato**  
Ingeniero Mecatrónico  
GitHub: [@tu-usuario](https://github.com/tu-usuario)

---

## Licencia

MIT © 2025 Wilbert Miguel Nahuatlato
