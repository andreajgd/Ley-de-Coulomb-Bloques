"""Version simplificada e independiente de la calculadora de fuerza electrica."""

import math


def pedir_numero(mensaje: str) -> float:
    """Solicita un numero real hasta recibir una entrada valida."""

    while True:
        try:
            return float(input(mensaje))
        except ValueError:
            print("Debe ingresar un numero valido.")


def pedir_entero_positivo(mensaje: str) -> int:
    """Solicita un entero positivo mayor o igual que 1."""

    while True:
        try:
            numero = int(input(mensaje))
            if numero >= 1:
                return numero
            print("Debe ser al menos 1.")
        except ValueError:
            print("Debe ingresar un numero entero.")


def calcular_fuerza_neta() -> None:
    """Calcula la fuerza electrica neta sobre una carga objetivo."""

    print("Calculadora de Fuerza Electrica")
    print("\n--- Carga objetivo q0 ---")
    q0 = pedir_numero("Magnitud de q0 (C): ")
    x0 = pedir_numero("Posicion X de q0 (m): ")
    y0 = pedir_numero("Posicion Y de q0 (m): ")

    cantidad_cargas = pedir_entero_positivo("\nCantidad de otras cargas: ")

    fx_total = 0.0
    fy_total = 0.0
    constante_coulomb = 9e9

    for indice in range(1, cantidad_cargas + 1):
        print(f"\n--- Carga {indice} ---")
        q = pedir_numero(f"Magnitud de q{indice} (C): ")
        x = pedir_numero(f"Posicion X de q{indice} (m): ")
        y = pedir_numero(f"Posicion Y de q{indice} (m): ")

        #el vector r apunta desde la carga fuente hacia la carga objetivo.
        rx = x0 - x
        ry = y0 - y
        distancia = math.sqrt(rx * rx + ry * ry)

        if distancia == 0:
            print("Error: dos cargas no pueden estar en el mismo punto.")
            return

        #ley de Coulomb: |F| = k |q1 q2| / r^2.
        fuerza_magnitud = constante_coulomb * abs(q * q0) / (distancia * distancia)

        #el vector unitario conserva la direccion del desplazamiento.
        ux = rx / distancia
        uy = ry / distancia

        #la repulsion sigue el sentido de r; la atraccion invierte ese sentido.
        if q * q0 > 0:
            fx = fuerza_magnitud * ux
            fy = fuerza_magnitud * uy
        else:
            fx = -fuerza_magnitud * ux
            fy = -fuerza_magnitud * uy

        #la fuerza neta se obtiene mediante la suma vectorial de todas las contribuciones.
        fx_total += fx
        fy_total += fy

    fuerza_neta = math.sqrt(fx_total * fx_total + fy_total * fy_total)
    angulo = math.degrees(math.atan2(fy_total, fx_total))

    print("\n--- RESULTADO ---")
    print(f"Fuerza neta = ({fx_total:.4e}, {fy_total:.4e}) N")
    print(f"Magnitud = {fuerza_neta:.4e} N")
    print(f"Angulo = {angulo:.2f} grados")


def principal() -> None:
    """Punto de entrada del script simplificado."""

    try:
        calcular_fuerza_neta()
    except KeyboardInterrupt:
        print("\nOperacion cancelada.")


if __name__ == "__main__":
    principal()
