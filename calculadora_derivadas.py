# -*- coding: utf-8 -*-
# ## ########################################################################
#
# Authors: Miguel Nahuatlato
# License: MIT
#
# ========================================================
# CALCULADORA DE DERIVADAS  v4.0 — Flet 0.85 + SymPy
#
# Motor:   parser robusto + constantes simbólicas                
#  Métodos: Simbólico · Fermat simbólico · Fermat numérico        
#  Pasos:   regla detectada + forma general + derivación          
#  LaTeX:   render matplotlib sin dependencia externa 
#
# Dependencias:
#   pip install -r requirements.txt
#
# Uso:
#   py calculadora_derivadas.py
# ========================================================
# ## ########################################################################

import flet as ft
import sympy as sp
import numpy as np
import threading, io, base64, re
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sympy.parsing.sympy_parser import (
    parse_expr, standard_transformations,
    implicit_multiplication_application, convert_xor,
)

# ══════════════════════════════════════════════════════════════════
#  PALETA
# ══════════════════════════════════════════════════════════════════
BG       = "#0D1117"
SURFACE  = "#161B22"
CARD     = "#1C2128"
CARD2    = "#21262D"
BORDER   = "#30363D"
BORDER_LO= "#21262D"
ACCENT   = "#00D4AA"
BLUE     = "#58A6FF"
AMBER    = "#F0883E"
PURPLE   = "#BC8CFF"
GREEN    = "#3FB950"
RED      = "#F85149"
TEXT     = "#E6EDF3"
TEXT_MID = "#C9D1D9"
TEXT_DIM = "#8B949E"
TEXT_FAINT="#484F58"
_BLANK   = "data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7"

# ══════════════════════════════════════════════════════════════════
#  MOTOR SIMBÓLICO
# ══════════════════════════════════════════════════════════════════
_x,_a,_b,_c,_k,_n,_m = sp.symbols("x a b c k n m", real=True)
_LOCAL = {
    "x":_x,"a":_a,"b":_b,"c":_c,"k":_k,"n":_n,"m":_m,
    "e":sp.E,"pi":sp.pi,
    "ln":sp.log,"log":sp.log,"sqrt":sp.sqrt,"abs":sp.Abs,"sign":sp.sign,
    "sin":sp.sin,"cos":sp.cos,"tan":sp.tan,
    "sec":sp.sec,"csc":sp.csc,"cot":sp.cot,
    "asin":sp.asin,"acos":sp.acos,"atan":sp.atan,"acot":sp.acot,
    "arcsin":sp.asin,"arccos":sp.acos,"arctan":sp.atan,
    "sinh":sp.sinh,"cosh":sp.cosh,"tanh":sp.tanh,"coth":sp.coth,
    "sech":sp.sech,"csch":sp.csch,
    "asinh":sp.asinh,"acosh":sp.acosh,"atanh":sp.atanh,
    "exp":sp.exp,
}
_TRANS = standard_transformations + (convert_xor, implicit_multiplication_application)


def parsear(texto: str) -> sp.Expr:
    t = texto.strip()
    t = t.replace("π","pi").replace("∞","oo").replace("√","sqrt")
    t = t.replace("tg(","tan(").replace("arctg(","atan(")
    t = t.replace("arcsin(","asin(").replace("arccos(","acos(").replace("arctan(","atan(")
    t = re.sub(r"(\d)(x)", r"\1*\2", t)
    try:
        return parse_expr(t, transformations=_TRANS, local_dict=_LOCAL)
    except Exception:
        return sp.sympify(t, locals=_LOCAL)


# ── Detección de regla con forma general ─────────────────────────
_TRIG_RULES = [
    (sp.sin,  "Seno",         r"\frac{d}{dx}[\sin u] = \cos u \cdot u'"),
    (sp.cos,  "Coseno",       r"\frac{d}{dx}[\cos u] = -\sin u \cdot u'"),
    (sp.tan,  "Tangente",     r"\frac{d}{dx}[\tan u] = \sec^2 u \cdot u'"),
    (sp.sec,  "Secante",      r"\frac{d}{dx}[\sec u] = \sec u\tan u \cdot u'"),
    (sp.csc,  "Cosecante",    r"\frac{d}{dx}[\csc u] = -\csc u\cot u \cdot u'"),
    (sp.cot,  "Cotangente",   r"\frac{d}{dx}[\cot u] = -\csc^2 u \cdot u'"),
    (sp.asin, "Arcoseno",     r"\frac{d}{dx}[\arcsin u] = \frac{u'}{\sqrt{1-u^2}}"),
    (sp.acos, "Arcocoseno",   r"\frac{d}{dx}[\arccos u] = \frac{-u'}{\sqrt{1-u^2}}"),
    (sp.atan, "Arcotangente", r"\frac{d}{dx}[\arctan u] = \frac{u'}{1+u^2}"),
    (sp.acot, "Arcocotangente",r"\frac{d}{dx}[\text{arccot}\,u] = \frac{-u'}{1+u^2}"),
    (sp.exp,  "Exponencial",  r"\frac{d}{dx}[e^u] = e^u \cdot u'"),
    (sp.log,  "Logaritmo ln", r"\frac{d}{dx}[\ln u] = \frac{u'}{u}"),
    (sp.sinh, "Sinh",         r"\frac{d}{dx}[\sinh u] = \cosh u \cdot u'"),
    (sp.cosh, "Cosh",         r"\frac{d}{dx}[\cosh u] = \sinh u \cdot u'"),
    (sp.tanh, "Tanh",         r"\frac{d}{dx}[\tanh u] = \text{sech}^2 u \cdot u'"),
    (sp.coth, "Coth",         r"\frac{d}{dx}[\coth u] = -\text{csch}^2 u \cdot u'"),
    (sp.sech, "Sech",         r"\frac{d}{dx}[\text{sech}\,u] = -\text{sech}\,u\tanh u \cdot u'"),
    (sp.csch, "Csch",         r"\frac{d}{dx}[\text{csch}\,u] = -\text{csch}\,u\coth u \cdot u'"),
    (sp.asinh,"Arcsinh",      r"\frac{d}{dx}[\sinh^{-1}u] = \frac{u'}{\sqrt{u^2+1}}"),
    (sp.acosh,"Arccosh",      r"\frac{d}{dx}[\cosh^{-1}u] = \frac{u'}{\sqrt{u^2-1}}"),
    (sp.atanh,"Arctanh",      r"\frac{d}{dx}[\tanh^{-1}u] = \frac{u'}{1-u^2}"),
    (sp.Abs,  "Valor absoluto",r"\frac{d}{dx}[|u|] = \frac{u \cdot u'}{|u|}"),
]

def detectar_regla(expr) -> tuple[str, str]:
    """Devuelve (nombre_regla, latex_forma_general)."""
    if isinstance(expr, (sp.Integer, sp.Float, sp.Rational)):
        return "Constante", r"\frac{d}{dx}[k] = 0"
    if expr == _x:
        return "Identidad", r"\frac{d}{dx}[x] = 1"
    if isinstance(expr, sp.Symbol) and expr != _x:
        return "Constante simbólica", r"\frac{d}{dx}[c] = 0"
    if isinstance(expr, sp.Add):
        return "Linealidad (suma/resta)", \
               r"[u \pm v]' = u' \pm v'"
    if isinstance(expr, sp.Pow):
        base, exp_ = expr.as_base_exp()
        if base == _x and not exp_.has(_x):
            return "Potencia", r"\frac{d}{dx}[x^n] = n\,x^{n-1}"
        if not base.has(_x) and exp_.has(_x):
            return "Exponencial base constante", r"\frac{d}{dx}[a^x] = a^x \ln a"
        if base.has(_x) and exp_.has(_x):
            return "Exponencial generalizada u^v", \
                   r"\frac{d}{dx}[u^v] = u^v\!\left(v'\ln u + \frac{v\,u'}{u}\right)"
        # (u(x))^n
        return "Potencia compuesta", \
               r"\frac{d}{dx}[u^n] = n\,u^{n-1}\cdot u'"
    if isinstance(expr, sp.Mul):
        args  = expr.args
        has_x = [f.has(_x) for f in args]
        if sum(has_x) == 1:
            return "Múltiplo constante", r"\frac{d}{dx}[c\,u] = c\,u'"
        if sum(has_x) == 2:
            return "Producto de dos funciones", r"[u\cdot v]' = u'v + u\,v'"
        return "Producto generalizado", \
               r"[u_1\cdots u_n]' = \sum_{i=1}^{n} u_i' \prod_{j\neq i} u_j"
    for cls, nombre, forma in _TRIG_RULES:
        if isinstance(expr, cls):
            return nombre + " (regla de la cadena)", forma
    return "Regla de la cadena", r"[f(g(x))]' = f'(g(x))\cdot g'(x)"


# ── Generador de pasos completos ──────────────────────────────────
def pasos_simbolico(texto: str, orden: int) -> dict:
    f_expr = parsear(texto)
    acum   = f_expr
    pasos  = []
    for i in range(1, orden + 1):
        regla, forma_gen = detectar_regla(acum)
        df_raw  = sp.diff(acum, _x)
        df_simp = sp.simplify(df_raw)
        pasos.append({
            "orden":      i,
            "f_lat":      sp.latex(acum),
            "regla":      regla,
            "forma_lat":  forma_gen,
            "df_raw_lat": sp.latex(df_raw),
            "df_lat":     sp.latex(df_simp),
        })
        acum = df_simp

    return {
        "f_expr":  f_expr,
        "df_expr": acum,
        "lat_f":   sp.latex(f_expr),
        "lat_df":  sp.latex(acum),
        "pasos":   pasos,
    }


def pasos_fermat(texto: str, orden: int) -> dict:
    h      = sp.Symbol("h", positive=True)
    f_expr = parsear(texto)
    acum   = f_expr
    pasos  = []
    for i in range(1, orden + 1):
        coc    = (acum.subs(_x, _x + h) - acum) / h
        coc_ex = sp.expand(coc)
        res    = sp.simplify(sp.limit(coc, h, 0))
        pasos.append({
            "orden":    i,
            "f_lat":    sp.latex(acum),
            "coc_lat":  sp.latex(coc_ex),
            "res_lat":  sp.latex(res),
        })
        acum = res
    return {
        "f_expr":  f_expr,
        "df_expr": acum,
        "lat_f":   sp.latex(f_expr),
        "lat_df":  sp.latex(acum),
        "pasos":   pasos,
    }


def calculo_numerico(texto: str, x_val: float, h: float = 1e-7) -> dict:
    f_expr = parsear(texto)
    f_lam  = sp.lambdify(_x, f_expr, modules=["numpy"])
    d_cen  = (f_lam(x_val + h) - f_lam(x_val - h)) / (2.0 * h)
    d_fwd  = (f_lam(x_val + h) - f_lam(x_val))     / h
    f_x    = float(f_lam(x_val))
    exacto = None
    error  = None
    try:
        exacto = float(sp.diff(f_expr, _x).subs(_x, x_val))
        error  = abs(float(d_cen) - exacto)
    except Exception:
        pass
    return {
        "d_cen": float(d_cen), "d_fwd": float(d_fwd),
        "f_x": f_x, "x_val": x_val, "h": h,
        "exacto": exacto, "error": error,
    }


# ══════════════════════════════════════════════════════════════════
#  RENDER LaTeX → data-URI PNG
# ══════════════════════════════════════════════════════════════════
def _render(latex_str: str, color: str = TEXT, bg: str = CARD,
            fontsize: int = 22, dpi: int = 160) -> str:
    try:
        plt.rcParams.update({"mathtext.fontset": "dejavuserif", "text.color": color})
        fig  = plt.figure(figsize=(1, 0.5))
        fig.patch.set_facecolor(bg)
        txt  = fig.text(0.5, 0.5, f"${latex_str}$",
                        fontsize=fontsize, ha="center", va="center",
                        color=color, usetex=False)
        r    = fig.canvas.get_renderer()
        bbox = txt.get_window_extent(renderer=r)
        px, py = 30, 20
        w = (bbox.width  + px * 2) / dpi
        h = (bbox.height + py * 2) / dpi
        fig.set_size_inches(max(w, 3.0), max(h, 0.65))
        txt.set_position((0.5, 0.5))
        buf = io.BytesIO()
        fig.savefig(buf, format="png", dpi=dpi, facecolor=bg,
                    bbox_inches="tight", pad_inches=py / dpi)
        plt.close(fig)
        buf.seek(0)
        return "data:image/png;base64," + base64.b64encode(buf.read()).decode()
    except Exception:
        plt.close("all")
        return _BLANK


def _render_multi(lineas: list, bg: str = CARD) -> str:
    try:
        plt.rcParams.update({"mathtext.fontset": "dejavuserif"})
        n   = len(lineas)
        fig = plt.figure(figsize=(9.5, max(0.75, 0.82 * n)))
        ax  = fig.add_axes([0, 0, 1, 1])
        ax.set_axis_off()
        fig.patch.set_facecolor(bg)
        ax.set_facecolor(bg)
        ys = [1 - (i + 0.5) / n for i in range(n)]
        for (lat, col), y in zip(lineas, ys):
            ax.text(0.5, y, f"${lat}$", fontsize=17, ha="center",
                    va="center", color=col, transform=ax.transAxes)
        buf = io.BytesIO()
        fig.savefig(buf, format="png", dpi=150, facecolor=bg,
                    bbox_inches="tight", pad_inches=0.12)
        plt.close(fig)
        buf.seek(0)
        return "data:image/png;base64," + base64.b64encode(buf.read()).decode()
    except Exception:
        plt.close("all")
        return _BLANK


# ══════════════════════════════════════════════════════════════════
#  DATOS ESTÁTICOS
# ══════════════════════════════════════════════════════════════════
EJEMPLOS = [
    ("Polinomio",      "x^3 - 2*x^2 + 5*x - 7"),
    ("Constantes",     "a*x^2 + b*x + c"),
    ("Potencia xᵏ",   "x^k"),
    ("Potencia u^k",  "sin(x)^k"),
    ("Trig. comp.",   "sin(k*x^2)"),
    ("Exponencial",   "e^(a*x) * cos(b*x)"),
    ("Logaritmo",     "ln(x^2 + 1)"),
    ("Raíz irrac.",   "sqrt(x^3 - x)"),
    ("Producto",      "x^2 * sin(x)"),
    ("Potenc. gral.", "a * x^n"),
    ("Cociente",      "sin(x) / (1 + cos(x))"),
    ("Hiperbólica",   "sinh(a*x) * cosh(b*x)"),
    ("xˣ",           "x**x"),
    ("Triple cadena", "ln(sin(exp(x)))"),
    ("Inv. trig.",    "atan(x) + asin(sqrt(x))"),
    ("Racional",      "(x^2 + 1) / (x^2 - 1)"),
    ("Prod. triple",  "x * sin(x) * exp(x)"),
    ("Frac. compuesta","(x / (x+1))^n"),
]
CONSTANTES = ["a", "b", "c", "k", "n", "m", "π", "e"]

SIDEBAR_FERMAT = [
    r"1.\; f(x + \Delta x)",
    r"2.\; \Delta y = f(x+\Delta x)-f(x)",
    r"3.\; \frac{\Delta y}{\Delta x}",
    r"4.\; \lim_{\Delta x\to 0} \Rightarrow f'(x)",
]
SIDEBAR_REF = [
    (r"x^n \to n x^{n-1}",          r"\sin x \to \cos x"),
    (r"\cos x \to -\sin x",          r"e^x \to e^x"),
    (r"\ln x \to \tfrac{1}{x}",      r"\sqrt{x} \to \tfrac{1}{2\sqrt{x}}"),
    (r"\tan x \to \sec^2 x",         r"\sinh x \to \cosh x"),
    (r"\arctan x \to \tfrac{1}{1+x^2}",r"a^x \to a^x\ln a"),
]

TABLA_TIPOS = [
    ("Constante",          r"k",                r"0"),
    ("Identidad",          r"x",                r"1"),
    ("Potencia",           r"x^n",              r"n\,x^{n-1}"),
    ("Raíz n-ésima",      r"\sqrt[n]{x}",      r"\frac{1}{n\sqrt[n]{x^{n-1}}}"),
    ("Exponencial e",      r"e^x",              r"e^x"),
    ("Exponencial base a", r"a^x",              r"a^x \ln a"),
    ("u^v (gral.)",        r"u^v",              r"u^v\!\!\left(v'\ln u+\frac{vu'}{u}\right)"),
    ("Logaritmo ln",       r"\ln x",            r"\frac{1}{x}"),
    ("Logaritmo base a",   r"\log_a x",         r"\frac{1}{x \ln a}"),
    ("Seno",               r"\sin x",           r"\cos x"),
    ("Coseno",             r"\cos x",           r"-\sin x"),
    ("Tangente",           r"\tan x",           r"\sec^2 x"),
    ("Secante",            r"\sec x",           r"\sec x \tan x"),
    ("Cosecante",          r"\csc x",           r"-\csc x \cot x"),
    ("Cotangente",         r"\cot x",           r"-\csc^2 x"),
    ("Arcoseno",           r"\arcsin x",        r"\frac{1}{\sqrt{1-x^2}}"),
    ("Arcocoseno",         r"\arccos x",        r"\frac{-1}{\sqrt{1-x^2}}"),
    ("Arcotangente",       r"\arctan x",        r"\frac{1}{1+x^2}"),
    ("Sinh",               r"\sinh x",          r"\cosh x"),
    ("Cosh",               r"\cosh x",          r"\sinh x"),
    ("Tanh",               r"\tanh x",          r"\text{sech}^2 x"),
    ("Arcsinh",            r"\sinh^{-1}x",      r"\frac{1}{\sqrt{x^2+1}}"),
    ("Arccosh",            r"\cosh^{-1}x",      r"\frac{1}{\sqrt{x^2-1}}"),
    ("Arctanh",            r"\tanh^{-1}x",      r"\frac{1}{1-x^2}"),
]
REGLAS = [
    ("Suma / Resta",   r"[u \pm v]' = u' \pm v'"),
    ("Múltiplo cte.",  r"[c\,u]' = c\,u'"),
    ("Producto",       r"[u\cdot v]' = u'v + u\,v'"),
    ("Cociente",       r"\left[\tfrac{u}{v}\right]' = \tfrac{u'v - u v'}{v^2}"),
    ("Cadena",         r"[f(g)]' = f'(g)\cdot g'"),
    ("Pot. gral.",     r"[u^v]' = u^v\!\left(v'\ln u + \tfrac{vu'}{u}\right)"),
    ("Inversa",        r"[f^{-1}]'(x) = \tfrac{1}{f'(f^{-1}(x))}"),
]


# ══════════════════════════════════════════════════════════════════
#  HELPERS UI
# ══════════════════════════════════════════════════════════════════
def _img(src=_BLANK, h=None):
    kw = {"src": src, "fit": ft.BoxFit.SCALE_DOWN}
    if h: kw["height"] = h
    return ft.Image(**kw)

def _caja(hijo, bg=CARD2, bcolor=BORDER):
    return ft.Container(
        ft.Column([hijo], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
        bgcolor=bg, border_radius=10,
        padding=ft.Padding(left=14, right=14, top=10, bottom=10),
        border=ft.Border.all(1, bcolor),
    )

def _etiqueta(texto, color=TEXT_FAINT, size=11):
    return ft.Text(texto, size=size, color=color, weight=ft.FontWeight.W_600,
                   style=ft.TextStyle(letter_spacing=0.5))

def _chip(texto, on_click, color=TEXT_DIM, size=12):
    return ft.Container(
        ft.Text(texto, size=size, color=color),
        bgcolor=CARD, border_radius=20,
        padding=ft.Padding(left=12, right=12, top=5, bottom=5),
        border=ft.Border.all(1, BORDER),
        on_click=on_click, ink=True,
    )

def _chip_const(letra, on_click):
    return ft.Container(
        ft.Text(letra, size=13, color=BLUE,
                style=ft.TextStyle(font_family="monospace", weight=ft.FontWeight.W_700)),
        bgcolor="#0D1E3A", border_radius=7,
        padding=ft.Padding(left=10, right=10, top=4, bottom=4),
        border=ft.Border.all(1, "#1A3060"),
        on_click=on_click, ink=True, tooltip=f"Insertar {letra}",
    )

def _badge_regla(texto, color=AMBER):
    return ft.Container(
        ft.Text(texto, size=10, color=color, weight=ft.FontWeight.W_600,
                style=ft.TextStyle(letter_spacing=0.3)),
        bgcolor=color + "18", border_radius=6,
        padding=ft.Padding(left=8, right=8, top=3, bottom=3),
        border=ft.Border.all(1, color + "40"),
    )


# ══════════════════════════════════════════════════════════════════
#  CONSTRUCTOR DE TARJETA DE PASOS (simbólico)
# ══════════════════════════════════════════════════════════════════
def _construir_pasos_simb(pasos: list) -> list[ft.Control]:
    """Devuelve controles Flet mostrando cada paso de derivación."""
    items = []
    for p in pasos:
        orden  = p["orden"]
        regla  = p["regla"]
        forma  = p["forma_lat"]
        f_lat  = p["f_lat"]
        df_lat = p["df_lat"]
        df_raw = p["df_raw_lat"]

        # Imagen de forma general
        img_forma = _img(h=46, src=_render(forma, color=AMBER, bg=SURFACE, fontsize=16))
        # Imagen derivada sin simplificar (si difiere de la simplificada)
        mostrar_raw = df_raw != df_lat
        img_df_raw = _img(src=_render(
            r"\frac{d}{dx}\left[" + f_lat + r"\right] = " + df_raw,
            color=TEXT_DIM, bg=SURFACE, fontsize=15))
        # Imagen resultado simplificado
        img_df = _img(h=58, src=_render(df_lat, color=ACCENT, bg="#0C1F18", fontsize=22))

        bloque = ft.Container(
            ft.Column([
                # Encabezado del paso
                ft.Row([
                    ft.Container(
                        ft.Text(f"∂{orden}" if orden > 1 else "∂",
                                size=13, color=BG, weight=ft.FontWeight.BOLD),
                        bgcolor=ACCENT, border_radius=6,
                        padding=ft.Padding(left=8, right=8, top=2, bottom=2),
                    ),
                    _badge_regla(regla, AMBER),
                ], spacing=8),
                # Forma general de la regla
                ft.Container(
                    ft.Column([
                        _etiqueta("Forma general:", TEXT_FAINT),
                        _caja(img_forma, bg=SURFACE, bcolor=BORDER_LO),
                    ], spacing=4),
                ),
                # Aplicación
                ft.Container(
                    ft.Column([
                        _etiqueta("Aplicando la regla:", TEXT_FAINT),
                        _caja(img_df_raw, bg=SURFACE, bcolor=BORDER_LO),
                    ], spacing=4),
                    visible=mostrar_raw,
                ),
                # Resultado del paso
                ft.Container(
                    ft.Column([
                        _etiqueta(f"f{'′'*orden}(x) =", ACCENT, size=12),
                        _caja(img_df, bg="#0C1F18", bcolor=ACCENT + "40"),
                    ], spacing=4),
                ),
            ], spacing=8),
            bgcolor=CARD2, border_radius=10,
            padding=ft.Padding(left=14, right=14, top=12, bottom=12),
            border=ft.Border.all(1, BORDER),
        )
        items.append(bloque)
    return items


# ══════════════════════════════════════════════════════════════════
#  MAIN
# ══════════════════════════════════════════════════════════════════
def main(page: ft.Page):
    page.title         = "∂ Calculadora de Derivadas"
    page.window.width  = 1120
    page.window.height = 840
    page.window.min_width  = 900
    page.window.min_height = 680
    page.bgcolor = BG
    page.padding = 0

    snack = ft.SnackBar(content=ft.Text("", size=14), duration=3000, bgcolor=CARD2)
    page.overlay.append(snack)
    def toast(msg, col=TEXT):
        snack.content = ft.Text(msg, color=col, size=14)
        snack.open = True; page.update()

    # ══════════════════════════════════════════════════════════════
    #  CONTROLES DE ENTRADA
    # ══════════════════════════════════════════════════════════════
    campo_fx = ft.TextField(
        hint_text="Ej:  x^k    sin(x)^k    a*x^2 + b*x + c    e^(a*x)*cos(b*x)",
        bgcolor=CARD, border_color=BORDER, focused_border_color=ACCENT,
        color=TEXT, cursor_color=ACCENT,
        text_size=18,
        text_style=ft.TextStyle(font_family="monospace", letter_spacing=0.3),
        hint_style=ft.TextStyle(color=TEXT_FAINT, size=13),
        border_radius=12, height=58, expand=True,
        on_submit=lambda e: _iniciar(),
    )
    campo_x0 = ft.TextField(
        label="x₀", value="1.0",
        label_style=ft.TextStyle(color=BLUE, size=13, weight=ft.FontWeight.W_600),
        bgcolor=CARD, border_color=BORDER, focused_border_color=BLUE,
        color=TEXT, text_size=15, border_radius=12,
        height=58, width=100,
        tooltip="Punto x₀ para Fermat numérico",
    )
    dd_orden = ft.Dropdown(
        value="1",
        options=[ft.DropdownOption(key=str(i), text=f"n = {i}") for i in range(1, 7)],
        bgcolor=CARD, border_color=BORDER, focused_border_color=ACCENT,
        color=TEXT, border_radius=10, height=52, width=110,
    )

    # ── Selector de método ────────────────────────────────────────
    metodo = ["simbolico"]
    METODOS = [
        ("simbolico", "⚡ Simbólico",       ACCENT,  "#0D2218"),
        ("fermat_s",  "∂ Fermat exacto",    AMBER,   "#271A0A"),
        ("fermat_n",  "≈ Fermat numérico",  BLUE,    "#0D1B2E"),
        ("ambos",     "↔ Simb + Fermat",    PURPLE,  "#1A0E2E"),
    ]
    met_btns: list[ft.Button] = []

    def _estilo_met(act, col):
        return ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=9),
            side={ft.ControlState.DEFAULT: ft.BorderSide(2 if act else 1,
                                                          col if act else BORDER)},
        )

    def _set_met(mk):
        metodo[0] = mk
        for btn, (k, _, col, bg) in zip(met_btns, METODOS):
            act = k == mk
            btn.bgcolor = bg if act else CARD
            btn.color   = col if act else TEXT_DIM
            btn.style   = _estilo_met(act, col)
        page.update()

    for mk, lbl, col, bg in METODOS:
        act = mk == "simbolico"
        b = ft.Button(
            content=ft.Text(lbl, size=13, weight=ft.FontWeight.W_600),
            bgcolor=bg if act else CARD,
            color=col if act else TEXT_DIM,
            height=46,
            style=_estilo_met(act, col),
            on_click=lambda e, k=mk: _set_met(k),
        )
        met_btns.append(b)

    # ── Chips constantes ──────────────────────────────────────────
    def _ins(s):
        sym = "pi" if s == "π" else s
        campo_fx.value = (campo_fx.value or "") + sym
        page.update()

    fila_consts = ft.Row(
        [_etiqueta("Consts:", TEXT_FAINT, 12)] +
        [_chip_const(c, lambda e, s=c: _ins(s)) for c in CONSTANTES],
        spacing=7,
    )

    # ── Chips ejemplos ────────────────────────────────────────────
    chips_ej = ft.Row(
        [_chip(n, lambda e, ex=ex: setattr(campo_fx, "value", ex) or page.update(), size=11)
         for n, ex in EJEMPLOS],
        scroll=ft.ScrollMode.AUTO, spacing=6,
    )

    # ── Botones ───────────────────────────────────────────────────
    prog = ft.ProgressBar(value=None, bar_height=3, border_radius=2,
                          color=ACCENT, bgcolor=SURFACE, visible=False)

    btn_calc = ft.Button(
        content=ft.Row([
            ft.Icon(ft.Icons.CALCULATE_ROUNDED, size=20, color=BG),
            ft.Text("  Calcular ∂", size=14, color=BG, weight=ft.FontWeight.BOLD),
        ], tight=True),
        bgcolor={ft.ControlState.DEFAULT: ACCENT, ft.ControlState.DISABLED: TEXT_FAINT},
        height=50,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=12),
            padding=ft.Padding(left=20, right=20, top=0, bottom=0),
        ),
        on_click=lambda e: _iniciar(),
    )
    btn_clear = ft.Button(
        content=ft.Row([
            ft.Icon(ft.Icons.CLEAR_ROUNDED, size=18, color=TEXT_DIM),
            ft.Text("  Limpiar", size=13, color=TEXT_DIM),
        ], tight=True),
        bgcolor=CARD, height=50,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=12),
            side={ft.ControlState.DEFAULT: ft.BorderSide(1, BORDER)},
            padding=ft.Padding(left=16, right=16, top=0, bottom=0),
        ),
        on_click=lambda e: _limpiar(),
    )

    # ══════════════════════════════════════════════════════════════
    #  PANEL INFERIOR — expresión activa + instructivo
    # ══════════════════════════════════════════════════════════════
    img_expr   = _img(h=50)
    img_expr.visible = False
    lbl_expr_txt   = ft.Text("", size=12, color=TEXT_DIM,
                              font_family="monospace", selectable=True)
    lbl_expr_regla = ft.Text("", size=11, color=AMBER)

    panel_expr = ft.Container(
        ft.Row([
            ft.Container(
                ft.Column([
                    _etiqueta("Expresión actual:", TEXT_FAINT),
                    img_expr,
                    lbl_expr_txt,
                    lbl_expr_regla,
                ], spacing=5),
                expand=2,
            ),
            ft.VerticalDivider(width=1, color=BORDER),
            ft.Container(
                ft.Column([
                    _etiqueta("  Sintaxis de entrada", ACCENT, 12),
                    ft.Divider(height=1, color=BORDER_LO),
                    ft.Row([
                        ft.Column([
                            ft.Text("Potencia:    x^2  ó  x**2", size=12, color=TEXT_DIM, font_family="monospace"),
                            ft.Text("Multiplicar: 2*x  ó  2x",   size=12, color=TEXT_DIM, font_family="monospace"),
                            ft.Text("Raíz:        sqrt(x)",       size=12, color=TEXT_DIM, font_family="monospace"),
                            ft.Text("Log natural: ln(x)",          size=12, color=TEXT_DIM, font_family="monospace"),
                            ft.Text("Constantes:  a b c k n m pi e", size=12, color=TEXT_DIM, font_family="monospace"),
                        ], spacing=4, expand=True),
                        ft.Column([
                            ft.Text("Trig:   sin  cos  tan  sec  csc  cot", size=12, color=TEXT_DIM, font_family="monospace"),
                            ft.Text("Inv:    asin  acos  atan",  size=12, color=TEXT_DIM, font_family="monospace"),
                            ft.Text("Hiperb: sinh  cosh  tanh", size=12, color=TEXT_DIM, font_family="monospace"),
                            ft.Text("Exp:    exp(x)  ó  e^x",   size=12, color=TEXT_DIM, font_family="monospace"),
                            ft.Text("π: escribe 'pi' ó chip π",  size=12, color=TEXT_DIM, font_family="monospace"),
                        ], spacing=4, expand=True),
                    ], spacing=20),
                ], spacing=7),
                expand=3,
                padding=ft.Padding(left=16, right=0, top=0, bottom=0),
            ),
        ], spacing=16, vertical_alignment=ft.CrossAxisAlignment.START),
        bgcolor=SURFACE, border_radius=12,
        padding=ft.Padding(left=16, right=16, top=12, bottom=12),
        border=ft.Border.all(1, BORDER),
    )

    # ══════════════════════════════════════════════════════════════
    #  TARJETAS DE RESULTADO
    # ══════════════════════════════════════════════════════════════

    # ── Simbólico ─────────────────────────────────────────────────
    img_f_simb  = _img(h=52)
    img_df_simb = _img(h=68)
    col_pasos_s = ft.Column([], spacing=10)
    lbl_ord_s   = ft.Text("", size=11, color=TEXT_DIM)
    txt_lat_s   = ft.Text("", size=11, color=TEXT_FAINT, font_family="monospace", selectable=True)

    card_simb = ft.Container(
        ft.Column([
            ft.Row([
                ft.Container(ft.Text("⚡", size=14),
                             width=32, height=32, border_radius=8,
                             bgcolor=ACCENT+"20",
                             alignment=ft.alignment.Alignment(0, 0)),
                ft.Text("Derivada simbólica", size=16, color=ACCENT, weight=ft.FontWeight.W_700),
                ft.Container(expand=True),
                lbl_ord_s,
            ], spacing=10),
            ft.Divider(height=1, color=BORDER),
            _etiqueta("f (x)", TEXT_FAINT),
            _caja(img_f_simb, bg="#12201A", bcolor=BORDER),
            ft.Container(height=4),
            _etiqueta("Resultado final f ′(x)", ACCENT, 12),
            _caja(img_df_simb, bg="#0C1F18", bcolor=ACCENT+"50"),
            ft.Container(height=4),
            _etiqueta("Desglose por pasos:", TEXT_DIM, 12),
            col_pasos_s,
            ft.ExpansionTile(
                title=ft.Text("Ver código LaTeX", size=11, color=TEXT_FAINT),
                controls=[ft.Container(txt_lat_s, bgcolor=BG, border_radius=6,
                           padding=ft.Padding(left=10,right=10,top=8,bottom=8))],
                tile_padding=ft.Padding(left=0,right=0,top=0,bottom=0),
            ),
        ], spacing=8),
        bgcolor=CARD, border_radius=14,
        padding=ft.Padding(left=20, right=20, top=16, bottom=16),
        border=ft.Border.all(1, BORDER),
        visible=False,
    )

    # ── Fermat simbólico ──────────────────────────────────────────
    img_f_ferm_s  = _img(h=52)
    img_df_ferm_s = _img(h=66)
    col_pasos_fs  = ft.Column([], spacing=8)
    lbl_ord_fs    = ft.Text("", size=11, color=TEXT_DIM)

    card_ferm_s = ft.Container(
        ft.Column([
            ft.Row([
                ft.Container(ft.Text("∂", size=14),
                             width=32, height=32, border_radius=8,
                             bgcolor=AMBER+"20",
                             alignment=ft.alignment.Alignment(0, 0)),
                ft.Text("Fermat exacto  (límite simbólico)", size=16,
                        color=AMBER, weight=ft.FontWeight.W_700),
                ft.Container(expand=True),
                lbl_ord_fs,
            ], spacing=10),
            ft.Divider(height=1, color=BORDER),
            _caja(_img(h=48, src=_render(
                r"f'(x)=\lim_{h\to 0}\frac{f(x+h)-f(x)}{h}",
                color=TEXT_MID, bg=SURFACE, fontsize=17)),
                bg=SURFACE, bcolor=BORDER_LO),
            _etiqueta("f (x)", TEXT_FAINT),
            _caja(img_f_ferm_s, bg="#221808", bcolor=BORDER),
            _etiqueta("Pasos del límite:", TEXT_DIM, 12),
            col_pasos_fs,
            _etiqueta("Resultado f ′(x) =", AMBER, 12),
            _caja(img_df_ferm_s, bg="#1C1206", bcolor=AMBER+"50"),
        ], spacing=8),
        bgcolor=CARD, border_radius=14,
        padding=ft.Padding(left=20, right=20, top=16, bottom=16),
        border=ft.Border.all(1, BORDER),
        visible=False,
    )

    # ── Fermat numérico ───────────────────────────────────────────
    lbl_val_n  = ft.Text("", size=34, color=BLUE, weight=ft.FontWeight.BOLD)
    lbl_exact_n= ft.Text("", size=13, color=GREEN)
    lbl_err_n  = ft.Text("", size=12, color=TEXT_DIM)
    col_pasos_fn= ft.Column([], spacing=5)

    card_ferm_n = ft.Container(
        ft.Column([
            ft.Row([
                ft.Container(ft.Text("≈", size=16),
                             width=32, height=32, border_radius=8,
                             bgcolor=BLUE+"20",
                             alignment=ft.alignment.Alignment(0, 0)),
                ft.Text("Fermat numérico  (diferencia central)", size=16,
                        color=BLUE, weight=ft.FontWeight.W_700),
            ], spacing=10),
            ft.Divider(height=1, color=BORDER),
            _caja(_img(h=48, src=_render(
                r"\frac{f(x_0+h)-f(x_0-h)}{2h},\quad h=10^{-7}",
                color=TEXT_MID, bg=SURFACE, fontsize=16)),
                bg=SURFACE, bcolor=BORDER_LO),
            ft.Container(
                ft.Column([
                    ft.Text("f ′(x₀) ≈", size=14, color=TEXT_DIM),
                    lbl_val_n, lbl_exact_n, lbl_err_n,
                ], spacing=3, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                bgcolor="#0D1B2E", border_radius=10,
                padding=ft.Padding(left=16, right=16, top=12, bottom=12),
                border=ft.Border.all(1, "#1A3060"),
            ),
            col_pasos_fn,
        ], spacing=10),
        bgcolor=CARD, border_radius=14,
        padding=ft.Padding(left=20, right=20, top=16, bottom=16),
        border=ft.Border.all(1, BORDER),
        visible=False,
    )

    # ── Error ──────────────────────────────────────────────────────
    txt_err = ft.Text("", color=RED, size=13, font_family="monospace", selectable=True)
    card_err = ft.Container(
        ft.Row([ft.Text("⚠", size=20, color=RED), txt_err], spacing=10),
        bgcolor="#1E0A0A", border_radius=10,
        padding=ft.Padding(left=16, right=16, top=12, bottom=12),
        border=ft.Border.all(1, "#4A1010"),
        visible=False,
    )

    # ══════════════════════════════════════════════════════════════
    #  TAB CALCULAR  (un solo Column scroll — sin anidado expand)
    # ══════════════════════════════════════════════════════════════
    tab_calc = ft.Column([
        ft.Container(
            ft.Column([
                ft.Row([
                    ft.Text("f (x) =", size=17, color=TEXT_DIM,
                            style=ft.TextStyle(font_family="monospace",
                                               weight=ft.FontWeight.W_600)),
                    campo_fx, campo_x0,
                ], spacing=10, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                fila_consts,
                ft.Row([ft.Text("Método:", size=13, color=TEXT_DIM), *met_btns],
                       spacing=8, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                ft.Row([dd_orden, ft.Container(expand=True), btn_clear, btn_calc],
                       spacing=8, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                ft.ExpansionTile(
                    title=ft.Text("Ejemplos de funciones  (clic para cargar)", size=12, color=TEXT_FAINT),
                    controls=[ft.Container(chips_ej,
                               padding=ft.Padding(left=0,right=0,top=6,bottom=2))],
                    tile_padding=ft.Padding(left=0,right=0,top=2,bottom=2),
                ),
            ], spacing=10),
            bgcolor=SURFACE, border_radius=12,
            padding=ft.Padding(left=18, right=18, top=16, bottom=14),
            border=ft.Border.all(1, BORDER),
        ),
        panel_expr,
        prog,
        ft.Divider(height=1, color=BORDER_LO),
        card_simb,
        card_ferm_s,
        card_ferm_n,
        card_err,
    ], spacing=12, scroll=ft.ScrollMode.AUTO, expand=True)

    # ══════════════════════════════════════════════════════════════
    #  TAB HISTORIAL
    # ══════════════════════════════════════════════════════════════
    historial: list = []
    col_hist = ft.Column([], spacing=6)
    lbl_hist_vacio = ft.Text("Sin cálculos todavía…", color=TEXT_FAINT, size=13, italic=True)

    def _add_hist(fx, dfx, met, orden):
        col_c = {"simbolico":ACCENT,"fermat_s":AMBER,"fermat_n":BLUE,"ambos":PURPLE}.get(met, TEXT_DIM)
        item = ft.Container(
            ft.Column([
                ft.Row([
                    ft.Container(ft.Text(met[0].upper(), size=9, color=col_c),
                                 bgcolor=col_c+"25", border_radius=4, width=20, height=20,
                                 alignment=ft.alignment.Alignment(0, 0)),
                    ft.Text(f"n={orden}", size=10, color=TEXT_FAINT),
                    ft.Container(expand=True),
                    ft.Text(met, size=10, color=col_c),
                ], spacing=6),
                ft.Text(f"f : {fx}",  size=12, font_family="monospace",
                        color=TEXT_MID, overflow=ft.TextOverflow.ELLIPSIS),
                ft.Text(f"f': {dfx}", size=12, font_family="monospace",
                        color=col_c, overflow=ft.TextOverflow.ELLIPSIS,
                        weight=ft.FontWeight.W_500),
            ], spacing=3),
            bgcolor=SURFACE, border_radius=8,
            padding=ft.Padding(left=10, right=10, top=8, bottom=8),
            border=ft.Border.all(1, BORDER_LO),
        )
        historial.insert(0, item)
        col_hist.controls = historial[:40]
        lbl_hist_vacio.visible = False
        page.update()

    def _borrar_hist():
        historial.clear(); col_hist.controls = []
        lbl_hist_vacio.visible = True; page.update()

    tab_hist = ft.Column([
        ft.Row([
            ft.Text("Historial", size=16, color=TEXT, weight=ft.FontWeight.W_700),
            ft.Container(expand=True),
            ft.Button(content=ft.Text("Borrar todo", size=12, color=RED),
                      bgcolor=CARD, height=36,
                      style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8),
                                           side={ft.ControlState.DEFAULT:ft.BorderSide(1,BORDER)}),
                      on_click=lambda e: _borrar_hist()),
        ]),
        lbl_hist_vacio, col_hist,
    ], spacing=12, scroll=ft.ScrollMode.AUTO, expand=True)

    # ══════════════════════════════════════════════════════════════
    #  TAB TABLA
    # ══════════════════════════════════════════════════════════════
    col_tabla = ft.Column(
        [ft.Text("Cargando tabla de referencia…", color=TEXT_FAINT, italic=True)],
        spacing=4,
    )
    _tabla_ok = [False]

    def _build_tabla():
        items = [
            ft.Text("Tabla de Derivadas", size=17, color=TEXT, weight=ft.FontWeight.W_700),
            ft.Container(height=4),
        ]
        for tipo, fx, dfx in TABLA_TIPOS:
            img = _img(src=_render_multi([(fx, TEXT_MID),(dfx, GREEN)], bg=CARD))
            items.append(ft.Container(
                ft.Row([
                    ft.Container(ft.Text(tipo, size=11, color=TEXT_DIM), width=165,
                                 padding=ft.Padding(left=0,right=8,top=0,bottom=0)),
                    ft.Container(img, expand=True),
                ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
                bgcolor=CARD, border_radius=8,
                padding=ft.Padding(left=14,right=14,top=5,bottom=5),
                border=ft.Border.all(1, BORDER_LO),
            ))
        items += [ft.Container(height=10),
                  ft.Text("Reglas de Derivación", size=16, color=TEXT, weight=ft.FontWeight.W_600)]
        for nombre, formula in REGLAS:
            img = _img(src=_render(formula, color=PURPLE, bg=CARD, fontsize=17), h=46)
            items.append(ft.Container(
                ft.Row([
                    ft.Container(ft.Text(nombre, size=11, color=TEXT_DIM), width=165),
                    ft.Container(img, expand=True),
                ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
                bgcolor=CARD, border_radius=8,
                padding=ft.Padding(left=14,right=14,top=4,bottom=4),
                border=ft.Border.all(1, BORDER_LO),
            ))
        col_tabla.controls = items
        page.update()

    tab_tabla = ft.Column([col_tabla], spacing=0, scroll=ft.ScrollMode.AUTO, expand=True)

    # ══════════════════════════════════════════════════════════════
    #  NAV TABS
    # ══════════════════════════════════════════════════════════════
    TABS = [
        ("⚗  Calcular",  tab_calc),
        ("📋  Historial", tab_hist),
        ("📐  Tabla",     tab_tabla),
    ]
    tab_idx = [0]
    ctn_tab = ft.Container(content=TABS[0][1], expand=True)
    nav_btns: list[ft.Button] = []

    def _ir_tab(i):
        tab_idx[0] = i; ctn_tab.content = TABS[i][1]
        for j, nb in enumerate(nav_btns):
            act = j == i
            nb.bgcolor = ACCENT if act else CARD
            nb.color   = BG     if act else TEXT_DIM
            nb.style   = ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=9),
                side={ft.ControlState.DEFAULT: ft.BorderSide(0 if act else 1, BORDER)},
            )
        if i == 2 and not _tabla_ok[0]:
            _tabla_ok[0] = True
            threading.Thread(target=_build_tabla, daemon=True).start()
        page.update()

    for i, (lbl, _) in enumerate(TABS):
        b = ft.Button(
            content=ft.Text(lbl, size=13),
            bgcolor=ACCENT if i == 0 else CARD,
            color=BG if i == 0 else TEXT_DIM, height=40,
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=9),
                                  side={ft.ControlState.DEFAULT:ft.BorderSide(0 if i==0 else 1,BORDER)}),
            on_click=lambda e, idx=i: _ir_tab(idx),
        )
        nav_btns.append(b)

    # ══════════════════════════════════════════════════════════════
    #  SIDEBAR
    # ══════════════════════════════════════════════════════════════
    sidebar_fermat = ft.Column([
        ft.Container(
            _img(h=42, src=_render(lat, color=TEXT_MID, bg=CARD, fontsize=14)),
            bgcolor=CARD, border_radius=8,
            padding=ft.Padding(left=8,right=8,top=4,bottom=4),
            border=ft.Border.only(left=ft.BorderSide(3, BLUE)),
        ) for lat in SIDEBAR_FERMAT
    ], spacing=7)

    sidebar_ref = ft.Column([
        ft.Container(
            _img(h=36, src=_render(f"{a}\\quad\\quad {b}",
                                   color=TEXT_DIM, bg=CARD, fontsize=12)),
            bgcolor=CARD, border_radius=7,
            padding=ft.Padding(left=6,right=6,top=3,bottom=3),
            border=ft.Border.all(1, BORDER),
        )
        for a, b in SIDEBAR_REF
    ], spacing=6)

    sidebar = ft.Container(
        ft.Column([
            ft.Text("Heurística de Fermat", color=BLUE, size=14, weight=ft.FontWeight.BOLD),
            ft.Divider(height=1, color=BORDER),
            sidebar_fermat,
            ft.Container(height=8),
            ft.Text("Referencia rápida", color=TEXT_FAINT, size=12,
                    style=ft.TextStyle(weight=ft.FontWeight.W_600, letter_spacing=0.8)),
            ft.Divider(height=1, color=BORDER),
            sidebar_ref,
        ], spacing=10, scroll=ft.ScrollMode.AUTO),
        width=290,
        padding=ft.Padding(left=14, right=14, top=20, bottom=14),
    )

    # ══════════════════════════════════════════════════════════════
    #  LÓGICA PRINCIPAL
    # ══════════════════════════════════════════════════════════════
    def _ocultar():
        card_simb.visible = card_ferm_s.visible = card_ferm_n.visible = card_err.visible = False

    def _error(msg):
        txt_err.value = msg; card_err.visible = True
        prog.visible = False; btn_calc.disabled = False
        page.update()

    def _iniciar():
        fx = (campo_fx.value or "").strip()
        if not fx:
            toast("Ingresa una función primero", AMBER); return
        _ocultar()
        prog.visible = True; btn_calc.disabled = True
        page.update()
        threading.Thread(target=_calcular, args=(fx,), daemon=True).start()

    def _calcular(fx: str):
        met   = metodo[0]
        orden = int(dd_orden.value)
        try:
            x0 = float(campo_x0.value.strip())
        except ValueError:
            x0 = 1.0; campo_x0.value = "1.0"

        try:
            # Pre-render expresión actual
            f_prev = parsear(fx)
            regla_prev, _ = detectar_regla(f_prev)
            img_expr.src     = _render(sp.latex(f_prev), color=TEXT_MID,
                                       bg=SURFACE, fontsize=19)
            img_expr.visible = True
            lbl_expr_txt.value   = fx
            lbl_expr_regla.value = f"Regla principal detectada: {regla_prev}"
            page.update()

            # ── Simbólico ────────────────────────────────────────
            if met in ("simbolico", "ambos"):
                res = pasos_simbolico(fx, orden)
                img_f_simb.src  = _render(res["lat_f"],  color=TEXT_MID,
                                          bg="#12201A", fontsize=20)
                img_df_simb.src = _render(res["lat_df"], color=ACCENT,
                                          bg="#0C1F18", fontsize=26)
                lbl_ord_s.value  = f"Orden {orden}"
                txt_lat_s.value  = (f"f(x)  = {res['lat_f']}\n"
                                    f"f'(x) = {res['lat_df']}")
                # Pasos detallados
                col_pasos_s.controls = _construir_pasos_simb(res["pasos"])
                card_simb.visible = True
                _add_hist(str(res["f_expr"])[:60], str(res["df_expr"])[:60], met, orden)

            # ── Fermat simbólico ──────────────────────────────────
            if met in ("fermat_s", "ambos"):
                res2 = pasos_fermat(fx, orden)
                img_f_ferm_s.src  = _render(res2["lat_f"],  color=TEXT_MID,
                                            bg="#221808", fontsize=20)
                img_df_ferm_s.src = _render(res2["lat_df"], color=AMBER,
                                            bg="#1C1206", fontsize=26)
                lbl_ord_fs.value = f"Orden {orden}"
                col_pasos_fs.controls = []
                for p in res2["pasos"]:
                    coc_lat = p["coc_lat"][:200]  # limitar para evitar render muy ancho
                    col_pasos_fs.controls.append(ft.Container(
                        ft.Column([
                            ft.Text(f"Orden {p['orden']}", size=10, color=TEXT_FAINT),
                            _caja(_img(src=_render(
                                r"\frac{f(x+h)-f(x)}{h} = " + coc_lat,
                                color=TEXT_DIM, bg=BG, fontsize=13)),
                                bg=BG, bcolor=BORDER_LO),
                            _caja(_img(h=48, src=_render(
                                r"\lim_{h\to 0} = " + p["res_lat"],
                                color=AMBER, bg=BG, fontsize=17)),
                                bg=BG, bcolor=AMBER+"30"),
                        ], spacing=5),
                        bgcolor=BG, border_radius=8,
                        padding=ft.Padding(left=10,right=10,top=8,bottom=8),
                        border=ft.Border.all(1, BORDER_LO),
                    ))
                card_ferm_s.visible = True
                if met == "fermat_s":
                    _add_hist(str(res2["f_expr"])[:60], str(res2["df_expr"])[:60], met, orden)

            # ── Fermat numérico ───────────────────────────────────
            if met == "fermat_n":
                rn = calculo_numerico(fx, x0)
                lbl_val_n.value   = f"{rn['d_cen']:.10f}"
                lbl_exact_n.value = (f"Valor exacto: {rn['exacto']:.10f}"
                                     if rn["exacto"] is not None else "Exacto: no disponible")
                lbl_err_n.value   = (f"Error absoluto: {rn['error']:.2e}"
                                     if rn["error"]  is not None else "")
                col_pasos_fn.controls = [
                    _fila_num("Fórmula",       "[f(x+h) − f(x−h)] / 2h"),
                    _fila_num("h",             f"{rn['h']:.0e}"),
                    _fila_num("x₀",            str(rn["x_val"])),
                    _fila_num("f(x₀)",         f"{rn['f_x']:.8f}"),
                    _fila_num("Dif. central",  f"{rn['d_cen']:.10f}"),
                    _fila_num("Dif. adelante", f"{rn['d_fwd']:.10f}"),
                ]
                card_ferm_n.visible = True
                _add_hist(fx[:60], f"{rn['d_cen']:.6f}", met, orden)

        except Exception as ex:
            _error(
                f"{ex}\n\n"
                "Revisa la sintaxis:\n"
                "  Potencia: x^2 ó x**2    Multiplicar: 2*x ó 2x\n"
                "  Funciones: sin cos tan ln sqrt exp\n"
                "  Constantes: a b c k n m pi e"
            )
            return
        prog.visible = False; btn_calc.disabled = False
        page.update()

    def _fila_num(etiqueta, valor):
        return ft.Row([
            ft.Container(ft.Text(etiqueta, size=12, color=TEXT_DIM,
                                  weight=ft.FontWeight.W_500), width=145),
            ft.Text("→", color=TEXT_FAINT, size=12),
            ft.Container(
                ft.Text(valor, size=13, color=TEXT, font_family="monospace", selectable=True),
                bgcolor=CARD2, border_radius=6, expand=True,
                padding=ft.Padding(left=8,right=8,top=5,bottom=5),
            ),
        ], vertical_alignment=ft.CrossAxisAlignment.CENTER, spacing=8)

    def _limpiar():
        campo_fx.value = ""
        img_expr.visible = False
        lbl_expr_txt.value = ""; lbl_expr_regla.value = ""
        _ocultar(); page.update()

    # ══════════════════════════════════════════════════════════════
    #  HEADER
    # ══════════════════════════════════════════════════════════════
    header = ft.Container(
        ft.Row([
            ft.Container(ft.Text("∂", size=30, color=ACCENT, weight=ft.FontWeight.BOLD),
                         bgcolor=CARD, border_radius=12,
                         padding=ft.Padding(left=14,right=14,top=8,bottom=8),
                         border=ft.Border.all(1, BORDER)),
            ft.Column([
                ft.Text("Calculadora de Derivadas", size=21, color=TEXT,
                        weight=ft.FontWeight.W_800),
                ft.Text("SymPy · NumPy · LaTeX · Fermat · Pasos detallados · Orden n",
                        size=11, color=TEXT_FAINT),
            ], spacing=2, expand=True),
            ft.Container(ft.Text("v4.0", size=9, color=ACCENT,
                                  style=ft.TextStyle(weight=ft.FontWeight.BOLD,letter_spacing=1.2)),
                         bgcolor=ACCENT+"18", border_radius=5,
                         padding=ft.Padding(left=8,right=8,top=4,bottom=4)),
        ], spacing=14, vertical_alignment=ft.CrossAxisAlignment.CENTER),
        bgcolor=SURFACE,
        padding=ft.Padding(left=24, right=24, top=14, bottom=14),
        border=ft.Border.only(bottom=ft.BorderSide(1, BORDER)),
    )

    # ══════════════════════════════════════════════════════════════
    #  LAYOUT RAÍZ
    # ══════════════════════════════════════════════════════════════
    page.add(ft.Column([
        header,
        ft.Row([
            ft.Container(
                ft.Column([ft.Row(nav_btns, spacing=8), ctn_tab], spacing=14, expand=True),
                padding=ft.Padding(left=22, right=14, top=18, bottom=18),
                expand=True,
            ),
            ft.VerticalDivider(width=1, color=BORDER),
            sidebar,
        ], spacing=0, expand=True, vertical_alignment=ft.CrossAxisAlignment.START),
    ], spacing=0, expand=True))


if __name__ == "__main__":
    ft.run(main)
