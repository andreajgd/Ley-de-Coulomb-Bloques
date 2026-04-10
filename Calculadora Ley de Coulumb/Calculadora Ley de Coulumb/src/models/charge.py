from dataclasses import dataclass

@dataclass
class CargaPuntual:
    """Representa una carga electrica puntual en el plano cartesiano."""

    q: float
    x: float
    y: float
