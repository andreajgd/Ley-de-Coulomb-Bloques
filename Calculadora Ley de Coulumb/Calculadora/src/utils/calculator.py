from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from models.charge import PointCharge
from physics.coulomb import force_detail_on_target_from_source, vector_angle_degrees, vector_magnitude
from utils.formatting import format_scientific

K_TEXT = "9 x 10^9"
STEP_TITLES = [
    "1. Los puntos",
    "2. Calcular distancias entre los puntos",
    "3. Formula F para cada punto",
    "4. Calcular v",
    "5. Calcular u",
    "6. F = |F| u para cada combinacion",
    "7. Sumatoria de vectores fuerza",
]
DEFAULT_STEP_MESSAGE = "Completa los datos y presiona 'Calcular Fuerza Neta'."


@dataclass
class CalculationReport:
    target: PointCharge
    sources: list[PointCharge]
    details: list[dict[str, object]]
    fx: float
    fy: float
    magnitude: float
    angle: float
    steps: list[tuple[str, str]]


def validate_float(value: str, field_name: str) -> float:
    clean = value.strip()
    if not clean:
        raise ValueError(f"{field_name} es obligatorio.")

    try:
        return float(clean)
    except ValueError as exc:
        raise ValueError(f"{field_name} debe ser un numero valido.") from exc


def validate_positive_int(value: str, field_name: str) -> int:
    clean = value.strip()
    if not clean:
        raise ValueError(f"{field_name} es obligatorio.")

    try:
        number = int(clean)
    except ValueError as exc:
        raise ValueError(f"{field_name} debe ser un numero entero valido.") from exc

    if number < 1:
        raise ValueError(f"{field_name} debe ser mayor o igual a 1.")
    return number


def format_plain_value(value: float) -> str:
    if abs(value) >= 10000 or (0 < abs(value) < 0.001):
        return format_scientific(value, 4)

    text = f"{value:.4f}".rstrip("0").rstrip(".")
    return text if text not in {"", "-0"} else "0"


def format_result_value(value: float) -> str:
    return format_scientific(value, 4)


def initial_steps() -> list[tuple[str, str]]:
    return [(title, DEFAULT_STEP_MESSAGE) for title in STEP_TITLES]


def build_steps(
    target: PointCharge,
    details: list[dict[str, object]],
    fx: float,
    fy: float,
) -> list[tuple[str, str]]:
    lines: list[list[str]] = [
        [
            f"K = {K_TEXT} N m^2 / C^2",
            f"q0 (objetivo) = {format_plain_value(target.q)} C en ({format_plain_value(target.x)}, {format_plain_value(target.y)})",
        ],
        [],
        [],
        [],
        [],
        [],
        [],
    ]

    for index, detail in enumerate(details, start=1):
        source_x, source_y = detail["source_pos"]  # type: ignore[misc]
        target_x, target_y = detail["target_pos"]  # type: ignore[misc]
        vx, vy = detail["v_vector"]  # type: ignore[misc]
        ax, ay = detail["a_vector"]  # type: ignore[misc]
        ux, uy = detail["u_vector"]  # type: ignore[misc]
        fvx, fvy = detail["force_vector"]  # type: ignore[misc]
        source_q = float(detail["source_q"])
        distance = float(detail["distance"])
        force_magnitude = float(detail["force_magnitude"])

        lines[0].append(
            f"q{index} = {format_plain_value(source_q)} C en ({format_plain_value(float(source_x))}, {format_plain_value(float(source_y))})"
        )
        lines[0].append(f"Combinacion {index}: punto inicial = q{index}, punto final = q0.")
        lines[1].append(
            "q{0} -> q0: d{0} = sqrt(({1} - {2})^2 + ({3} - {4})^2) = {5} m".format(
                index,
                format_plain_value(float(target_x)),
                format_plain_value(float(source_x)),
                format_plain_value(float(target_y)),
                format_plain_value(float(source_y)),
                format_plain_value(distance),
            )
        )
        lines[2].append(
            f"|F{index}| = k |q{index} q0| / d{index}^2 = "
            f"{K_TEXT} |{format_plain_value(source_q)} x {format_plain_value(target.q)}| / "
            f"({format_plain_value(distance)})^2 = {format_result_value(force_magnitude)} N"
        )
        lines[3].append(
            "v{0} = punto final - punto inicial = ({1} - {2}, {3} - {4}) = ({5}, {6})".format(
                index,
                format_plain_value(float(target_x)),
                format_plain_value(float(source_x)),
                format_plain_value(float(target_y)),
                format_plain_value(float(source_y)),
                format_plain_value(float(vx)),
                format_plain_value(float(vy)),
            )
        )
        relation = "repulsion, por eso a = v" if detail["interaction"] == "repulsion" else "atraccion, por eso a = -v"
        lines[4].append(
            f"q{index} -> q0: {relation}\n"
            f"a{index} = ({format_plain_value(float(ax))}, {format_plain_value(float(ay))})\n"
            f"u{index} = a{index} / |a{index}| = ({format_result_value(float(ux))}, {format_result_value(float(uy))})"
        )
        lines[5].append(
            f"F{index} = |F{index}| u{index} = {format_result_value(force_magnitude)} "
            f"({format_result_value(float(ux))}, {format_result_value(float(uy))}) = "
            f"({format_result_value(float(fvx))}, {format_result_value(float(fvy))}) N"
        )
        lines[6].append(f"F{index} = ({format_result_value(float(fvx))}, {format_result_value(float(fvy))}) N")

    lines[6].append(f"F_neta = ({format_result_value(fx)}, {format_result_value(fy)}) N")
    lines[6].append(f"|F_neta| = {format_result_value(vector_magnitude(fx, fy))} N")
    lines[6].append(f"Angulo = {vector_angle_degrees(fx, fy):.2f} grados")

    return [
        (title, "\n".join(block) if index == 0 else "\n\n".join(block))
        for index, (title, block) in enumerate(zip(STEP_TITLES, lines))
    ]


def build_calculation_report(target: PointCharge, sources: Iterable[PointCharge]) -> CalculationReport:
    source_list = list(sources)
    details = [
        force_detail_on_target_from_source(target, source, label=f"q{index}")
        for index, source in enumerate(source_list, start=1)
    ]
    fx = sum(float(detail["force_vector"][0]) for detail in details)  # type: ignore[index]
    fy = sum(float(detail["force_vector"][1]) for detail in details)  # type: ignore[index]
    magnitude = vector_magnitude(fx, fy)
    angle = vector_angle_degrees(fx, fy)

    return CalculationReport(
        target=target,
        sources=source_list,
        details=details,
        fx=fx,
        fy=fy,
        magnitude=magnitude,
        angle=angle,
        steps=build_steps(target, details, fx, fy),
    )
