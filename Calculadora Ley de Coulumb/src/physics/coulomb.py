from __future__ import annotations

"""Rutinas fisicas para resolver interacciones electricas mediante la ley de Coulomb."""

import math
from typing import Iterable

from models.charge import CargaPuntual

CONSTANTE_COULOMB = 9e9
DISTANCIA_MINIMA = 1e-12


def _vector_entre_puntos(inicial: CargaPuntual, final: CargaPuntual) -> tuple[float, float]:
    """Devuelve el desplazamiento desde el punto inicial hasta el punto final."""

    return final.x - inicial.x, final.y - inicial.y


def _longitud_vector(x: float, y: float) -> float:
    return math.sqrt(x * x + y * y)


def detalle_fuerza_sobre_objetivo_desde_fuente(
    objetivo: CargaPuntual,
    fuente: CargaPuntual,
    etiqueta: str,
) -> dict[str, float | str | tuple[float, float]]:
    """Calcula el detalle vectorial de la fuerza ejercida por una fuente sobre la carga objetivo."""

    #el vector v conecta la carga fuente con la carga objetivo y define la linea de accion.
    vx, vy = _vector_entre_puntos(fuente, objetivo)
    distancia_cuadrada = vx * vx + vy * vy
    if distancia_cuadrada < DISTANCIA_MINIMA:
        raise ValueError("Dos cargas no pueden estar en la misma posicion.")

    distancia = _longitud_vector(vx, vy)
    mismo_signo = fuente.q * objetivo.q >= 0

    #en repulsion la fuerza sigue a v; en atraccion debe invertirse para apuntar hacia la fuente.
    ax, ay = (vx, vy) if mismo_signo else (-vx, -vy)

    #el vector unitario u conserva solo la direccion fisica de la interaccion.
    ux, uy = ax / distancia, ay / distancia
    magnitud_fuerza = CONSTANTE_COULOMB * abs(fuente.q * objetivo.q) / distancia_cuadrada

    fx = magnitud_fuerza * ux
    fy = magnitud_fuerza * uy

    return {
        "etiqueta": etiqueta,
        "carga_fuente": fuente.q,
        "carga_objetivo": objetivo.q,
        "posicion_fuente": (fuente.x, fuente.y),
        "posicion_objetivo": (objetivo.x, objetivo.y),
        "distancia": distancia,
        "distancia_cuadrada": distancia_cuadrada,
        "vector_v": (vx, vy),
        "vector_a": (ax, ay),
        "vector_u": (ux, uy),
        "magnitud_fuerza": magnitud_fuerza,
        "vector_fuerza": (fx, fy),
        "interaccion": "repulsion" if mismo_signo else "atraccion",
    }


def fuerza_sobre_objetivo_desde_fuente(
    objetivo: CargaPuntual,
    fuente: CargaPuntual,
) -> tuple[float, float]:
    detalle = detalle_fuerza_sobre_objetivo_desde_fuente(objetivo, fuente, etiqueta="q")
    fx, fy = detalle["vector_fuerza"]  # type: ignore[assignment]
    return float(fx), float(fy)


def fuerza_neta(objetivo: CargaPuntual, fuentes: Iterable[CargaPuntual]) -> tuple[float, float]:
    fx_total = 0.0
    fy_total = 0.0

    for fuente in fuentes:
        #la fuerza neta resulta de la superposicion de todas las contribuciones parciales.
        fx, fy = fuerza_sobre_objetivo_desde_fuente(objetivo, fuente)
        fx_total += fx
        fy_total += fy

    return fx_total, fy_total


def magnitud_vector(x: float, y: float) -> float:
    return math.sqrt(x * x + y * y)


def angulo_vector_grados(x: float, y: float) -> float:
    return math.degrees(math.atan2(y, x))
