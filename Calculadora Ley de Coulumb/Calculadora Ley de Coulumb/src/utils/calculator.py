from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from models.charge import CargaPuntual
from physics.coulomb import (
    angulo_vector_grados,
    detalle_fuerza_sobre_objetivo_desde_fuente,
    magnitud_vector,
)
from utils.formatting import formatear_cientifico

TEXTO_CONSTANTE_K = "9 x 10^9"
TITULOS_PASOS = [
    "1. Los puntos",
    "2. Calcular distancias entre los puntos",
    "3. Formula F para cada punto",
    "4. Calcular v",
    "5. Calcular u",
    "6. F = |F| u para cada combinacion",
    "7. Sumatoria de vectores fuerza",
]
MENSAJE_PASO_PREDETERMINADO = "Completa los datos y presiona 'Calcular Fuerza Neta'."


@dataclass
class ReporteCalculo:
    """Agrupa el resultado numerico y el desarrollo textual del calculo."""

    objetivo: CargaPuntual
    fuentes: list[CargaPuntual]
    detalles: list[dict[str, object]]
    fx: float
    fy: float
    magnitud: float
    angulo: float
    pasos: list[tuple[str, str]]


def validar_flotante(valor: str, nombre_campo: str) -> float:
    texto = valor.strip()
    if not texto:
        raise ValueError(f"{nombre_campo} es obligatorio.")

    try:
        return float(texto)
    except ValueError as error:
        raise ValueError(f"{nombre_campo} debe ser un numero valido.") from error


def validar_entero_positivo(valor: str, nombre_campo: str) -> int:
    texto = valor.strip()
    if not texto:
        raise ValueError(f"{nombre_campo} es obligatorio.")

    try:
        numero = int(texto)
    except ValueError as error:
        raise ValueError(f"{nombre_campo} debe ser un numero entero valido.") from error

    if numero < 1:
        raise ValueError(f"{nombre_campo} debe ser mayor o igual a 1.")
    return numero


def formatear_valor_plano(valor: float) -> str:
    if abs(valor) >= 10000 or (0 < abs(valor) < 0.001):
        return formatear_cientifico(valor, 4)

    texto = f"{valor:.4f}".rstrip("0").rstrip(".")
    return texto if texto not in {"", "-0"} else "0"


def formatear_valor_resultado(valor: float) -> str:
    return formatear_cientifico(valor, 4)


def pasos_iniciales() -> list[tuple[str, str]]:
    return [(titulo, MENSAJE_PASO_PREDETERMINADO) for titulo in TITULOS_PASOS]


def construir_pasos(
    objetivo: CargaPuntual,
    detalles: list[dict[str, object]],
    fx: float,
    fy: float,
) -> list[tuple[str, str]]:
    lineas: list[list[str]] = [
        [
            f"K = {TEXTO_CONSTANTE_K} N m^2 / C^2",
            "q0 (objetivo) = "
            f"{formatear_valor_plano(objetivo.q)} C en "
            f"({formatear_valor_plano(objetivo.x)}, {formatear_valor_plano(objetivo.y)})",
        ],
        [],
        [],
        [],
        [],
        [],
        [],
    ]

    for indice, detalle in enumerate(detalles, start=1):
        x_fuente, y_fuente = detalle["posicion_fuente"]  # type: ignore[misc]
        x_objetivo, y_objetivo = detalle["posicion_objetivo"]  # type: ignore[misc]
        vx, vy = detalle["vector_v"]  # type: ignore[misc]
        ax, ay = detalle["vector_a"]  # type: ignore[misc]
        ux, uy = detalle["vector_u"]  # type: ignore[misc]
        fx_vector, fy_vector = detalle["vector_fuerza"]  # type: ignore[misc]
        carga_fuente = float(detalle["carga_fuente"])
        distancia = float(detalle["distancia"])
        magnitud_fuerza = float(detalle["magnitud_fuerza"])

        lineas[0].append(
            f"q{indice} = {formatear_valor_plano(carga_fuente)} C en "
            f"({formatear_valor_plano(float(x_fuente))}, {formatear_valor_plano(float(y_fuente))})"
        )
        lineas[0].append(f"Combinacion {indice}: punto inicial = q{indice}, punto final = q0.")
        lineas[1].append(
            "q{0} -> q0: d{0} = sqrt(({1} - {2})^2 + ({3} - {4})^2) = {5} m".format(
                indice,
                formatear_valor_plano(float(x_objetivo)),
                formatear_valor_plano(float(x_fuente)),
                formatear_valor_plano(float(y_objetivo)),
                formatear_valor_plano(float(y_fuente)),
                formatear_valor_plano(distancia),
            )
        )
        lineas[2].append(
            f"|F{indice}| = k |q{indice} q0| / d{indice}^2 = "
            f"{TEXTO_CONSTANTE_K} |{formatear_valor_plano(carga_fuente)} x {formatear_valor_plano(objetivo.q)}| / "
            f"({formatear_valor_plano(distancia)})^2 = {formatear_valor_resultado(magnitud_fuerza)} N"
        )
        lineas[3].append(
            "v{0} = punto final - punto inicial = ({1} - {2}, {3} - {4}) = ({5}, {6})".format(
                indice,
                formatear_valor_plano(float(x_objetivo)),
                formatear_valor_plano(float(x_fuente)),
                formatear_valor_plano(float(y_objetivo)),
                formatear_valor_plano(float(y_fuente)),
                formatear_valor_plano(float(vx)),
                formatear_valor_plano(float(vy)),
            )
        )
        relacion = (
            "repulsion, por eso a = v"
            if detalle["interaccion"] == "repulsion"
            else "atraccion, por eso a = -v"
        )
        lineas[4].append(
            f"q{indice} -> q0: {relacion}\n"
            f"a{indice} = ({formatear_valor_plano(float(ax))}, {formatear_valor_plano(float(ay))})\n"
            f"u{indice} = a{indice} / |a{indice}| = "
            f"({formatear_valor_resultado(float(ux))}, {formatear_valor_resultado(float(uy))})"
        )
        lineas[5].append(
            f"F{indice} = |F{indice}| u{indice} = {formatear_valor_resultado(magnitud_fuerza)} "
            f"({formatear_valor_resultado(float(ux))}, {formatear_valor_resultado(float(uy))}) = "
            f"({formatear_valor_resultado(float(fx_vector))}, {formatear_valor_resultado(float(fy_vector))}) N"
        )
        lineas[6].append(
            f"F{indice} = ({formatear_valor_resultado(float(fx_vector))}, "
            f"{formatear_valor_resultado(float(fy_vector))}) N"
        )

    lineas[6].append(f"F_neta = ({formatear_valor_resultado(fx)}, {formatear_valor_resultado(fy)}) N")
    lineas[6].append(f"|F_neta| = {formatear_valor_resultado(magnitud_vector(fx, fy))} N")
    lineas[6].append(f"Angulo = {angulo_vector_grados(fx, fy):.2f} grados")

    return [
        (titulo, "\n".join(bloque) if indice == 0 else "\n\n".join(bloque))
        for indice, (titulo, bloque) in enumerate(zip(TITULOS_PASOS, lineas))
    ]


def construir_reporte_calculo(
    objetivo: CargaPuntual,
    fuentes: Iterable[CargaPuntual],
) -> ReporteCalculo:
    """Construye un reporte completo para reutilizar el mismo calculo en terminal y GUI."""

    lista_fuentes = list(fuentes)

    # Cada detalle conserva la informacion intermedia necesaria para reconstruir el algoritmo paso a paso.
    detalles = [
        detalle_fuerza_sobre_objetivo_desde_fuente(objetivo, fuente, etiqueta=f"q{indice}")
        for indice, fuente in enumerate(lista_fuentes, start=1)
    ]
    fx = sum(float(detalle["vector_fuerza"][0]) for detalle in detalles)  # type: ignore[index]
    fy = sum(float(detalle["vector_fuerza"][1]) for detalle in detalles)  # type: ignore[index]
    magnitud = magnitud_vector(fx, fy)
    angulo = angulo_vector_grados(fx, fy)

    return ReporteCalculo(
        objetivo=objetivo,
        fuentes=lista_fuentes,
        detalles=detalles,
        fx=fx,
        fy=fy,
        magnitud=magnitud,
        angulo=angulo,
        pasos=construir_pasos(objetivo, detalles, fx, fy),
    )
