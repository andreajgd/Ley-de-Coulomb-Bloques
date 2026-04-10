from __future__ import annotations

from dataclasses import dataclass
import tkinter as tk
from tkinter import messagebox, ttk
from typing import Callable

from models.charge import CargaPuntual
from utils.calculator import (
    TEXTO_CONSTANTE_K,
    construir_reporte_calculo,
    formatear_valor_resultado,
    pasos_iniciales,
    validar_flotante,
)

FONDO = "#f4f6fb"
TARJETA = "#ffffff"
BORDE = "#e7ebf2"
CAMPO = "#f6f8fc"
BORDE_CAMPO = "#e2e8f0"
ACTIVO = "#ff5b87"
TEXTO = "#122033"
TEXTO_SUAVE = "#64748b"
ROSA = "#ff2d55"
ROSA_SUAVE = "#fff2f7"
AZUL = "#eef4ff"
ROJO_CARGA = "#ff4d5d"
AZUL_CARGA = "#3b82f6"
COLOR_RESULTADO = "#f59e0b"

FUENTE_TITULO_ENCABEZADO = ("Segoe UI", 24, "bold")
FUENTE_SUBTITULO_ENCABEZADO = ("Segoe UI", 11)
FUENTE_TITULO_SECCION = ("Segoe UI", 16, "bold")
FUENTE_ETIQUETA = ("Segoe UI", 11)
FUENTE_ENTRADA = ("Segoe UI", 13)
FUENTE_VALOR = ("Segoe UI", 16, "bold")
FUENTE_VECTOR = ("Consolas", 18, "bold")
FUENTE_MONOESPACIADA = ("Consolas", 10)


@dataclass
class FilaCarga:
    contenedor: tk.Frame
    titulo: tk.Label
    indicador: tk.Canvas
    variable_q: tk.StringVar
    variable_x: tk.StringVar
    variable_y: tk.StringVar


def configurar_ttk() -> None:
    estilo = ttk.Style()
    try:
        estilo.theme_use("clam")
    except tk.TclError:
        pass

    estilo.configure("Steps.TCombobox", padding=8, fieldbackground=TARJETA, background=TARJETA, foreground=TEXTO)
    estilo.map("Steps.TCombobox", fieldbackground=[("readonly", TARJETA)], foreground=[("readonly", TEXTO)])


def crear_tarjeta(contenedor_padre: tk.Widget, color_fondo: str = TARJETA) -> tk.Frame:
    return tk.Frame(
        contenedor_padre,
        bg=color_fondo,
        highlightthickness=1,
        highlightbackground=BORDE,
        bd=0,
    )


def crear_encabezado_seccion(
    contenedor_padre: tk.Frame,
    titulo: str,
    boton: tuple[str, Callable[[], None]] | None = None,
) -> None:
    fila = tk.Frame(contenedor_padre, bg=contenedor_padre.cget("bg"))
    fila.pack(fill="x", padx=14, pady=(12, 6))
    tk.Label(
        fila,
        text=titulo,
        font=FUENTE_TITULO_SECCION,
        fg=TEXTO,
        bg=fila.cget("bg"),
    ).pack(side="left")

    if boton:
        crear_boton_primario(fila, boton[0], boton[1], padx=14, pady=6).pack(side="right")


def crear_entrada_etiquetada(
    contenedor_padre: tk.Frame,
    etiqueta: str,
    fila: int,
    columna: int,
    variable: tk.StringVar | None = None,
) -> tk.Entry:
    contenedor = tk.Frame(contenedor_padre, bg=contenedor_padre.cget("bg"))
    contenedor.grid(row=fila, column=columna, sticky="ew", padx=6, pady=3)
    tk.Label(
        contenedor,
        text=etiqueta,
        font=FUENTE_ETIQUETA,
        fg=TEXTO_SUAVE,
        bg=contenedor.cget("bg"),
    ).pack(anchor="w")

    contenedor_campo = tk.Frame(
        contenedor,
        bg=CAMPO,
        highlightthickness=1,
        highlightbackground=BORDE_CAMPO,
        bd=0,
    )
    contenedor_campo.pack(fill="x", pady=(5, 0))

    entrada = tk.Entry(
        contenedor_campo,
        textvariable=variable,
        bg=CAMPO,
        fg=TEXTO,
        insertbackground=TEXTO,
        relief="flat",
        bd=0,
        highlightthickness=0,
        font=FUENTE_ENTRADA,
    )
    entrada.pack(fill="x", padx=10, pady=8)
    entrada.bind("<FocusIn>", lambda _evento: contenedor_campo.config(highlightbackground=ACTIVO))
    entrada.bind("<FocusOut>", lambda _evento: contenedor_campo.config(highlightbackground=BORDE_CAMPO))
    return entrada


def crear_boton_primario(
    contenedor_padre: tk.Widget,
    texto: str,
    comando: Callable[[], None],
    padx: int = 16,
    pady: int = 10,
) -> tk.Button:
    return tk.Button(
        contenedor_padre,
        text=texto,
        command=comando,
        bg=ROSA,
        fg="#ffffff",
        activebackground="#ff4b6e",
        activeforeground="#ffffff",
        relief="flat",
        bd=0,
        padx=padx,
        pady=pady,
        font=("Segoe UI", 12, "bold"),
        cursor="hand2",
    )


class AplicacionCoulomb:
    def __init__(self, raiz: tk.Tk) -> None:
        self.raiz = raiz
        self.raiz.title("Calculadora de Fuerza Electrica")
        self.raiz.geometry("1120x760")
        self.raiz.minsize(980, 680)
        self.raiz.configure(bg=FONDO)

        self.filas: list[FilaCarga] = []
        self.pasos = pasos_iniciales()

        configurar_ttk()
        self._construir_interfaz()
        self._agregar_fila()

    def _construir_interfaz(self) -> None:
        encabezado = tk.Frame(self.raiz, bg=ROSA, padx=22, pady=18)
        encabezado.pack(fill="x")
        tk.Label(
            encabezado,
            text="Calculadora de Fuerza Electrica",
            font=FUENTE_TITULO_ENCABEZADO,
            fg="#ffffff",
            bg=ROSA,
        ).pack(anchor="w")
        tk.Label(
            encabezado,
            text="Ley de Coulomb y principio de superposicion",
            font=FUENTE_SUBTITULO_ENCABEZADO,
            fg="#ffe3ef",
            bg=ROSA,
        ).pack(anchor="w", pady=(6, 0))

        cuerpo = tk.Frame(self.raiz, bg=FONDO, padx=14, pady=14)
        cuerpo.pack(fill="both", expand=True)
        cuerpo.grid_columnconfigure(0, weight=1)
        cuerpo.grid_columnconfigure(1, weight=1)
        cuerpo.grid_rowconfigure(0, weight=1)

        columna_izquierda = tk.Frame(cuerpo, bg=FONDO)
        columna_derecha = tk.Frame(cuerpo, bg=FONDO)
        columna_izquierda.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        columna_derecha.grid(row=0, column=1, sticky="nsew", padx=(10, 0))

        self._construir_tarjeta_objetivo(columna_izquierda)
        self._construir_tarjeta_fuentes(columna_izquierda)
        crear_boton_primario(columna_izquierda, "Calcular Fuerza Neta", self._calcular).pack(fill="x")

        self._construir_tarjeta_resultados(columna_derecha)
        self._construir_tarjeta_pasos(columna_derecha)

    def _construir_tarjeta_objetivo(self, contenedor_padre: tk.Frame) -> None:
        tarjeta = crear_tarjeta(contenedor_padre)
        tarjeta.pack(fill="x", pady=(0, 10))
        crear_encabezado_seccion(tarjeta, "Carga Objetivo")

        cuadricula = tk.Frame(tarjeta, bg=TARJETA)
        cuadricula.pack(fill="x", padx=14, pady=(0, 14))
        for columna in range(3):
            cuadricula.grid_columnconfigure(columna, weight=1)

        campos: dict[str, tk.Entry] = {}
        especificaciones = [
            ("q", "Magnitud (C)"),
            ("x", "Posicion X (m)"),
            ("y", "Posicion Y (m)"),
        ]
        for columna, (clave, etiqueta) in enumerate(especificaciones):
            campos[clave] = crear_entrada_etiquetada(cuadricula, etiqueta, 0, columna)

        self.entrada_objetivo_q = campos["q"]
        self.entrada_objetivo_x = campos["x"]
        self.entrada_objetivo_y = campos["y"]

    def _construir_tarjeta_fuentes(self, contenedor_padre: tk.Frame) -> None:
        tarjeta = crear_tarjeta(contenedor_padre)
        tarjeta.pack(fill="x", pady=(0, 10))
        crear_encabezado_seccion(tarjeta, "Cargas Puntuales", ("Agregar", self._agregar_fila))

        self.contenedor_filas = tk.Frame(tarjeta, bg=TARJETA)
        self.contenedor_filas.pack(fill="x", padx=14, pady=(0, 14))

    def _construir_tarjeta_resultados(self, contenedor_padre: tk.Frame) -> None:
        tarjeta = crear_tarjeta(contenedor_padre, ROSA_SUAVE)
        tarjeta.pack(fill="x", pady=(0, 10))
        crear_encabezado_seccion(tarjeta, "Resultados")

        resumen = tk.Frame(tarjeta, bg=TARJETA, highlightthickness=1, highlightbackground="#f4d4e1")
        resumen.pack(fill="x", padx=14, pady=(0, 10))
        tk.Label(
            resumen,
            text="Vector Fuerza Neta",
            font=FUENTE_ETIQUETA,
            fg=TEXTO_SUAVE,
            bg=TARJETA,
        ).pack(pady=(10, 4))
        self.etiqueta_vector = tk.Label(
            resumen,
            text="< -, - > N",
            font=FUENTE_VECTOR,
            fg=ROSA,
            bg=TARJETA,
        )
        self.etiqueta_vector.pack(pady=(0, 10))

        metricas = tk.Frame(tarjeta, bg=ROSA_SUAVE)
        metricas.pack(fill="x", padx=14, pady=(0, 10))
        for columna in range(4):
            metricas.grid_columnconfigure(columna, weight=1)

        self.etiqueta_fx = self._crear_metrica(metricas, 0, 0, "Componente X", "N")
        self.etiqueta_fy = self._crear_metrica(metricas, 0, 1, "Componente Y", "N")
        self.etiqueta_magnitud = self._crear_metrica(metricas, 0, 2, "Magnitud", "N")
        self.etiqueta_angulo = self._crear_metrica(metricas, 0, 3, "Angulo", "grados")

        caja_ayuda = tk.Frame(
            tarjeta,
            bg=AZUL,
            highlightthickness=1,
            highlightbackground=BORDE_CAMPO,
        )
        caja_ayuda.pack(fill="x", padx=14, pady=(0, 14))
        tk.Label(
            caja_ayuda,
            text=(
                "F = k |q1 q2| / r^2    u = a / |a|\n"
                "F_vector = |F| u    r = punto final - punto inicial\n"
                f"K = {TEXTO_CONSTANTE_K} N m^2 / C^2"
            ),
            justify="left",
            anchor="w",
            font=FUENTE_ETIQUETA,
            fg="#355070",
            bg=AZUL,
        ).pack(fill="x", padx=14, pady=10)

    def _construir_tarjeta_pasos(self, contenedor_padre: tk.Frame) -> None:
        tarjeta = crear_tarjeta(contenedor_padre)
        tarjeta.pack(fill="both", expand=True)
        crear_encabezado_seccion(tarjeta, "Pasos del Algoritmo")

        self.selector_pasos = ttk.Combobox(tarjeta, state="readonly", style="Steps.TCombobox")
        self.selector_pasos.pack(fill="x", padx=14, pady=(0, 8))
        self.selector_pasos.bind("<<ComboboxSelected>>", self._mostrar_paso)

        contenedor_texto = tk.Frame(tarjeta, bg=TARJETA)
        contenedor_texto.pack(fill="both", expand=True, padx=14, pady=(0, 14))

        barra_pasos = tk.Scrollbar(contenedor_texto, orient="vertical")
        barra_pasos.pack(side="right", fill="y")

        self.texto_pasos = tk.Text(
            contenedor_texto,
            height=18,
            wrap="word",
            bg="#f8fbff",
            fg=TEXTO,
            relief="flat",
            bd=0,
            highlightthickness=1,
            highlightbackground=BORDE_CAMPO,
            highlightcolor=ACTIVO,
            font=FUENTE_MONOESPACIADA,
            padx=12,
            pady=12,
            yscrollcommand=barra_pasos.set,
        )
        self.texto_pasos.pack(side="left", fill="both", expand=True)
        barra_pasos.config(command=self.texto_pasos.yview)
        self._actualizar_pasos()

    def _crear_metrica(
        self,
        contenedor_padre: tk.Frame,
        fila: int,
        columna: int,
        titulo: str,
        unidad: str,
    ) -> tk.Label:
        contenedor = tk.Frame(
            contenedor_padre,
            bg=TARJETA,
            highlightthickness=1,
            highlightbackground=BORDE,
        )
        contenedor.grid(row=fila, column=columna, sticky="nsew", padx=4, pady=4)
        tk.Label(
            contenedor,
            text=titulo,
            font=FUENTE_ETIQUETA,
            fg=TEXTO_SUAVE,
            bg=TARJETA,
        ).pack(pady=(10, 4))
        valor = tk.Label(contenedor, text="-", font=FUENTE_VALOR, fg=TEXTO, bg=TARJETA)
        valor.pack()
        tk.Label(
            contenedor,
            text=unidad,
            font=FUENTE_ETIQUETA,
            fg=TEXTO_SUAVE,
            bg=TARJETA,
        ).pack(pady=(2, 10))
        return valor

    def _agregar_fila(self, valores_iniciales: tuple[str, str, str] | None = None) -> None:
        variable_q = tk.StringVar(value="" if valores_iniciales is None else valores_iniciales[0])
        variable_x = tk.StringVar(value="" if valores_iniciales is None else valores_iniciales[1])
        variable_y = tk.StringVar(value="" if valores_iniciales is None else valores_iniciales[2])

        tarjeta = tk.Frame(
            self.contenedor_filas,
            bg=TARJETA,
            highlightthickness=1,
            highlightbackground="#edf1f7",
            bd=0,
        )
        tarjeta.pack(fill="x", pady=(0, 10))

        encabezado = tk.Frame(tarjeta, bg=TARJETA)
        encabezado.pack(fill="x", padx=12, pady=(10, 5))

        indicador = tk.Canvas(encabezado, width=14, height=14, bg=TARJETA, highlightthickness=0)
        indicador.pack(side="left")
        titulo = tk.Label(encabezado, text="Carga", font=("Segoe UI", 14, "bold"), fg=TEXTO, bg=TARJETA)
        titulo.pack(side="left", padx=8)

        fila = FilaCarga(
            contenedor=tarjeta,
            titulo=titulo,
            indicador=indicador,
            variable_q=variable_q,
            variable_x=variable_x,
            variable_y=variable_y,
        )
        tk.Button(
            encabezado,
            text="X",
            command=lambda actual=fila: self._eliminar_fila(actual),
            bg=TARJETA,
            fg="#94a3b8",
            activebackground=TARJETA,
            activeforeground=ROSA,
            relief="flat",
            bd=0,
            padx=6,
            pady=2,
            font=("Segoe UI", 12, "bold"),
            cursor="hand2",
        ).pack(side="right")

        cuadricula = tk.Frame(tarjeta, bg=TARJETA)
        cuadricula.pack(fill="x", padx=12, pady=(0, 12))
        for columna in range(3):
            cuadricula.grid_columnconfigure(columna, weight=1)

        crear_entrada_etiquetada(cuadricula, "Magnitud (C)", 0, 0, variable_q)
        crear_entrada_etiquetada(cuadricula, "X (m)", 0, 1, variable_x)
        crear_entrada_etiquetada(cuadricula, "Y (m)", 0, 2, variable_y)

        variable_q.trace_add("write", lambda *_args, actual=fila: self._pintar_fila(actual))
        self.filas.append(fila)
        self._reindexar()
        self._pintar_fila(fila)

    def _eliminar_fila(self, fila: FilaCarga) -> None:
        if len(self.filas) <= 1:
            messagebox.showwarning("Carga requerida", "Debe existir al menos una carga puntual.")
            return

        fila.contenedor.destroy()
        self.filas = [actual for actual in self.filas if actual is not fila]
        self._reindexar()

    def _reindexar(self) -> None:
        for indice, fila in enumerate(self.filas, start=1):
            fila.titulo.config(text=f"Carga {indice}")

    def _pintar_fila(self, fila: FilaCarga) -> None:
        color, signo = ROJO_CARGA, "+"
        try:
            if fila.variable_q.get().strip() and float(fila.variable_q.get()) < 0:
                color, signo = AZUL_CARGA, "-"
        except ValueError:
            color, signo = COLOR_RESULTADO, "?"

        fila.indicador.delete("all")
        fila.indicador.create_oval(1, 1, 13, 13, fill=color, outline=color)
        fila.indicador.create_text(7, 7, text=signo, fill="#ffffff", font=("Segoe UI", 8, "bold"))

    def _actualizar_pasos(self) -> None:
        self.selector_pasos["values"] = [titulo for titulo, _ in self.pasos]
        self.selector_pasos.current(0)
        self._escribir_paso(self.pasos[0][1])

    def _escribir_paso(self, contenido: str) -> None:
        self.texto_pasos.config(state="normal")
        self.texto_pasos.delete("1.0", "end")
        self.texto_pasos.insert("1.0", contenido)
        self.texto_pasos.config(state="disabled")

    def _mostrar_paso(self, _evento: tk.Event) -> None:
        indice = self.selector_pasos.current()
        if 0 <= indice < len(self.pasos):
            self._escribir_paso(self.pasos[indice][1])

    def _recopilar_datos(self) -> tuple[CargaPuntual, list[CargaPuntual]]:
        objetivo = CargaPuntual(
            validar_flotante(self.entrada_objetivo_q.get(), "Magnitud de la carga objetivo"),
            validar_flotante(self.entrada_objetivo_x.get(), "Posicion X de la carga objetivo"),
            validar_flotante(self.entrada_objetivo_y.get(), "Posicion Y de la carga objetivo"),
        )

        fuentes: list[CargaPuntual] = []
        for indice, fila in enumerate(self.filas, start=1):
            q = fila.variable_q.get().strip()
            x = fila.variable_x.get().strip()
            y = fila.variable_y.get().strip()

            if not q and not x and not y:
                continue
            if not q or not x or not y:
                raise ValueError(f"Completa todos los campos de la Carga {indice}.")

            fuentes.append(
                CargaPuntual(
                    validar_flotante(q, f"Magnitud de la Carga {indice}"),
                    validar_flotante(x, f"Posicion X de la Carga {indice}"),
                    validar_flotante(y, f"Posicion Y de la Carga {indice}"),
                )
            )

        if not fuentes:
            raise ValueError("Agrega al menos una carga puntual.")
        return objetivo, fuentes

    def _calcular(self) -> None:
        try:
            objetivo, fuentes = self._recopilar_datos()
            reporte = construir_reporte_calculo(objetivo, fuentes)

            self.pasos = reporte.pasos

            self.etiqueta_vector.config(
                text=f"< {formatear_valor_resultado(reporte.fx)}, {formatear_valor_resultado(reporte.fy)} > N"
            )
            self.etiqueta_fx.config(text=formatear_valor_resultado(reporte.fx))
            self.etiqueta_fy.config(text=formatear_valor_resultado(reporte.fy))
            self.etiqueta_magnitud.config(text=formatear_valor_resultado(reporte.magnitud))
            self.etiqueta_angulo.config(text=f"{reporte.angulo:.2f}")

            self._actualizar_pasos()
        except ValueError as error:
            messagebox.showerror("Datos invalidos", str(error))
        except Exception:
            messagebox.showerror(
                "Error inesperado",
                "No se pudo completar el calculo. Revisa que todos los campos esten completos.",
            )
