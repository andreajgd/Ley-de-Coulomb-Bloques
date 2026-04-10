"""Utilidades compartidas de validacion y orquestacion del calculo."""

from .calculator import (
    ReporteCalculo,
    construir_pasos,
    construir_reporte_calculo,
    formatear_valor_plano,
    formatear_valor_resultado,
    pasos_iniciales,
    validar_entero_positivo,
    validar_flotante,
)

__all__ = [
    "ReporteCalculo",
    "construir_pasos",
    "construir_reporte_calculo",
    "formatear_valor_plano",
    "formatear_valor_resultado",
    "pasos_iniciales",
    "validar_entero_positivo",
    "validar_flotante",
]
