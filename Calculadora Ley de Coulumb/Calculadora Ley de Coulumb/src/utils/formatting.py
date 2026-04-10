def formatear_cientifico(valor: float, decimales: int = 4) -> str:
    if valor == 0:
        return "0"
    mantisa, exponente = f"{valor:.{decimales}e}".split("e")
    mantisa = mantisa.rstrip("0").rstrip(".")
    signo = exponente[0]
    potencia = exponente[1:].lstrip("0") or "0"
    return f"{mantisa}e{signo}{potencia}"
