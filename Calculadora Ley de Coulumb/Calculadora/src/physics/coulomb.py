from __future__ import annotations

import math
from typing import Iterable

from models.charge import PointCharge

K_COULOMB = 9e9
MIN_DISTANCE = 1e-12


def _vector(initial: PointCharge, final: PointCharge) -> tuple[float, float]:
    return final.x - initial.x, final.y - initial.y


def _length(x: float, y: float) -> float:
    return math.sqrt(x * x + y * y)


def force_detail_on_target_from_source(
    target: PointCharge, source: PointCharge, label: str
) -> dict[str, float | str | tuple[float, float]]:
    vx, vy = _vector(source, target)  # r = punto final - punto inicial
    r2 = vx * vx + vy * vy
    if r2 < MIN_DISTANCE:
        raise ValueError("Dos cargas no pueden estar en la misma posicion.")

    distance = _length(vx, vy)
    same_sign = source.q * target.q >= 0

    # a representa la direccion fisica de la fuerza.
    ax, ay = (vx, vy) if same_sign else (-vx, -vy)
    ux, uy = ax / distance, ay / distance  # u = a / |a|

    # |F| = k * |q1*q2| / r^2
    force_magnitude = K_COULOMB * abs(source.q * target.q) / r2

    fx = force_magnitude * ux
    fy = force_magnitude * uy  # F = |F| * u

    return {
        "label": label,
        "source_q": source.q,
        "target_q": target.q,
        "source_pos": (source.x, source.y),
        "target_pos": (target.x, target.y),
        "distance": distance,
        "distance_squared": r2,
        "v_vector": (vx, vy),
        "a_vector": (ax, ay),
        "u_vector": (ux, uy),
        "force_magnitude": force_magnitude,
        "force_vector": (fx, fy),
        "interaction": "repulsion" if same_sign else "atraccion",
    }


def force_on_target_from_source(target: PointCharge, source: PointCharge) -> tuple[float, float]:
    detail = force_detail_on_target_from_source(target, source, label="q")
    fx, fy = detail["force_vector"]  # type: ignore[assignment]
    return float(fx), float(fy)


def net_force(target: PointCharge, sources: Iterable[PointCharge]) -> tuple[float, float]:
    fx_total = 0.0
    fy_total = 0.0

    for source in sources:
        fx, fy = force_on_target_from_source(target, source)
        fx_total += fx
        fy_total += fy

    return fx_total, fy_total


def vector_magnitude(x: float, y: float) -> float:
    return math.sqrt(x * x + y * y)


def vector_angle_degrees(x: float, y: float) -> float:
    return math.degrees(math.atan2(y, x))
