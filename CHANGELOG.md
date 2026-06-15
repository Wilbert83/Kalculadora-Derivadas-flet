# Changelog

Todas las versiones notables de este proyecto se documentan aquí.
Formato basado en [Keep a Changelog](https://keepachangelog.com/es/1.0.0/).

---

## [Unreleased]

### En progreso
- Desglose pedagógico completo: identificación explícita de `u`, `u'` por cada regla de derivación
- Soporte de constantes simbólicas arbitrarias (`a`, `b`, `k`, `n`, `m`)
- Derivadas de orden `n` (1 a 6) con pasos intermedios
- Tabla de referencia con 24 tipos de derivadas + 7 reglas
- Módulo de Fermat simbólico exacto (límite simbólico vía SymPy, no solo numérico)

### Bugs conocidos
- `u` y `v` interpretados como constantes si se escriben literalmente en el campo
- Layout puede mostrar área gris en algunas resoluciones (fix en progreso)

---

## [0.1.0] — 2025

### Agregado
- Derivación simbólica con SymPy + detección básica de regla aplicada
- Cociente de Fermat numérico (diferencia central y adelantada, h = 10⁻⁷)
- Cálculo de error absoluto contra valor exacto simbólico
- Render LaTeX → PNG vía `matplotlib.mathtext` embebido como data URI
- Panel lateral con heurística de Fermat y tabla de referencia rápida
- 10 ejemplos preestablecidos con chips clicables
- Soporte de: polinomios, trig, inv. trig, hiperbólicas, exponencial, logaritmo, raíz, xˣ
- UI oscura con Flet 0.85 compatible con Windows
