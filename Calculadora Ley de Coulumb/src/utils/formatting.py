def format_scientific(value: float, decimals: int = 4) -> str:
    if value == 0:
        return "0"
    mantissa, exponent = f"{value:.{decimals}e}".split("e")
    mantissa = mantissa.rstrip("0").rstrip(".")
    sign = exponent[0]
    power = exponent[1:].lstrip("0") or "0"
    return f"{mantissa}e{sign}{power}"
