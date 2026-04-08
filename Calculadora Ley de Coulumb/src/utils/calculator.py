# utils/calculator.py
def validate_float(value: str, field_name: str) -> float:
    """Convierte a float o lanza ValueError con mensaje claro."""
    try:
        return float(value)
    except ValueError:
        raise ValueError(f"{field_name} debe ser un número válido.")