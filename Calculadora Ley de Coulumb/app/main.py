from __future__ import annotations

from pathlib import Path
import sys


def _bootstrap_src_path() -> None:
    root_dir = Path(__file__).resolve().parents[1]
    src_dir = root_dir / "src"
    src_path = str(src_dir)
    if src_path not in sys.path:
        sys.path.insert(0, src_path)


_bootstrap_src_path()

from models.charge import PointCharge
from utils.calculator import (
    build_calculation_report,
    format_plain_value,
    format_result_value,
    validate_float,
    validate_positive_int,
)


def _prompt_float(prompt: str, field_name: str) -> float:
    while True:
        raw = input(prompt)
        try:
            return validate_float(raw, field_name)
        except ValueError as exc:
            print(f"Error: {exc}")


def _prompt_positive_int(prompt: str, field_name: str) -> int:
    while True:
        raw = input(prompt)
        try:
            return validate_positive_int(raw, field_name)
        except ValueError as exc:
            print(f"Error: {exc}")


def _prompt_charge(title: str) -> PointCharge:
    print(f"\n{title}")
    q = _prompt_float("  Magnitud q (C): ", f"Magnitud de {title}")
    x = _prompt_float("  Posicion X (m): ", f"Posicion X de {title}")
    y = _prompt_float("  Posicion Y (m): ", f"Posicion Y de {title}")
    return PointCharge(q=q, x=x, y=y)


def _print_summary(target: PointCharge, sources: list[PointCharge]) -> None:
    print("\nDatos capturados")
    print(f"  q0 = {format_plain_value(target.q)} C en ({format_plain_value(target.x)}, {format_plain_value(target.y)})")
    for index, source in enumerate(sources, start=1):
        print(
            f"  q{index} = {format_plain_value(source.q)} C "
            f"en ({format_plain_value(source.x)}, {format_plain_value(source.y)})"
        )


def _print_report() -> None:
    print("Calculadora de Fuerza Electrica - Terminal")
    target = _prompt_charge("Carga objetivo q0")
    total_sources = _prompt_positive_int("\nCantidad de cargas puntuales: ", "Cantidad de cargas puntuales")
    sources = [_prompt_charge(f"Carga {index}") for index in range(1, total_sources + 1)]

    report = build_calculation_report(target, sources)

    _print_summary(target, sources)
    print("\nResultado")
    print(f"  Fuerza neta = < {format_result_value(report.fx)}, {format_result_value(report.fy)} > N")
    print(f"  Fx = {format_result_value(report.fx)} N")
    print(f"  Fy = {format_result_value(report.fy)} N")
    print(f"  |F| = {format_result_value(report.magnitude)} N")
    print(f"  Angulo = {report.angle:.2f} grados")

    show_steps = input("\nMostrar pasos detallados? [s/N]: ").strip().lower()
    if show_steps in {"s", "si", "y", "yes"}:
        print()
        for title, content in report.steps:
            print(title)
            print(content)
            print()


def main() -> None:
    try:
        _print_report()
    except KeyboardInterrupt:
        print("\nOperacion cancelada.")
    except ValueError as exc:
        print(f"\nError: {exc}")


if __name__ == "__main__":
    main()
