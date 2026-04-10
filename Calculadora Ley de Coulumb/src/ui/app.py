from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk

from models.charge import PointCharge
from ui import theme
from ui.rows import ChargeRow
from ui.scene import draw_force_scene
from utils.calculator import (
    build_calculation_report,
    format_result_value,
    initial_steps,
    validate_float,
)


class CoulombApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Calculadora de Fuerza Electrica")
        self.root.geometry("1340x900")
        self.root.minsize(1120, 820)
        self.root.configure(bg=theme.BG)

        self.rows: list[ChargeRow] = []
        self.target: PointCharge | None = None
        self.sources: list[PointCharge] = []
        self.details: list[dict[str, object]] = []
        self.net = (0.0, 0.0)
        self.steps = initial_steps()

        theme.configure_ttk()
        self._build_ui()
        self._add_row()
        self._draw_scene()

    def _build_ui(self) -> None:
        wrap = tk.Frame(self.root, bg=theme.BG)
        wrap.pack(fill="both", expand=True)

        scrollbar = tk.Scrollbar(wrap, orient="vertical")
        scrollbar.pack(side="right", fill="y")

        self.scroll_canvas = tk.Canvas(wrap, bg=theme.BG, highlightthickness=0, yscrollcommand=scrollbar.set)
        self.scroll_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.scroll_canvas.yview)

        page = tk.Frame(self.scroll_canvas, bg=theme.BG)
        self.page_window = self.scroll_canvas.create_window((0, 0), window=page, anchor="nw")
        page.bind("<Configure>", self._sync_page_scroll)
        self.scroll_canvas.bind("<Configure>", self._resize_page)
        self.scroll_canvas.bind_all("<MouseWheel>", self._on_mousewheel)

        header = tk.Frame(page, bg=theme.PINK, padx=22, pady=18)
        header.pack(fill="x")
        tk.Label(
            header,
            text="Calculadora de Fuerza Electrica",
            font=theme.HEADER_TITLE_FONT,
            fg="#ffffff",
            bg=theme.PINK,
        ).pack(anchor="w")
        tk.Label(
            header,
            text="Ley de Coulomb y principio de superposicion",
            font=theme.HEADER_SUBTITLE_FONT,
            fg="#ffe3ef",
            bg=theme.PINK,
        ).pack(anchor="w", pady=(6, 0))

        body = tk.Frame(page, bg=theme.BG, padx=14, pady=14)
        body.pack(fill="both", expand=True)

        graph_card = theme.create_card(body)
        graph_card.pack(fill="x", pady=(0, 12))
        theme.create_section_header(graph_card, "Plano Cartesiano")
        self.canvas = tk.Canvas(graph_card, height=360, bg="#fbfcfe", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True, padx=14, pady=(0, 14))
        self.canvas.bind("<Configure>", self._draw_scene)

        content = tk.Frame(body, bg=theme.BG)
        content.pack(fill="both", expand=True)
        left = tk.Frame(content, bg=theme.BG)
        right = tk.Frame(content, bg=theme.BG)
        left.pack(side="left", fill="both", expand=True, padx=(0, 10))
        right.pack(side="left", fill="both", expand=True, padx=(10, 0))

        self._build_target_card(left)
        self._build_sources_card(left)
        theme.create_primary_button(left, "Calcular Fuerza Neta", self._calculate).pack(fill="x")

        self._build_results_card(right)
        self._build_steps_card(right)

    def _build_target_card(self, parent: tk.Frame) -> None:
        card = theme.create_card(parent)
        card.pack(fill="x", pady=(0, 10))
        theme.create_section_header(card, "Carga Objetivo")

        grid = tk.Frame(card, bg=theme.CARD)
        grid.pack(fill="x", padx=14, pady=(0, 14))
        for column in range(3):
            grid.grid_columnconfigure(column, weight=1)

        fields: dict[str, tk.Entry] = {}
        specs = [
            ("q", "Magnitud (C)"),
            ("x", "Posicion X (m)"),
            ("y", "Posicion Y (m)"),
        ]
        for column, (key, label) in enumerate(specs):
            fields[key] = theme.create_labeled_entry(grid, label, 0, column)

        self.target_q = fields["q"]
        self.target_x = fields["x"]
        self.target_y = fields["y"]

    def _build_sources_card(self, parent: tk.Frame) -> None:
        card = theme.create_card(parent)
        card.pack(fill="x", pady=(0, 10))
        theme.create_section_header(card, "Cargas Puntuales", ("Agregar", self._add_row))
        self.rows_box = tk.Frame(card, bg=theme.CARD)
        self.rows_box.pack(fill="x", padx=14, pady=(0, 14))

    def _build_results_card(self, parent: tk.Frame) -> None:
        card = theme.create_card(parent, theme.PINK_SOFT)
        card.pack(fill="x", pady=(0, 10))
        theme.create_section_header(card, "Resultados")

        summary = tk.Frame(card, bg=theme.CARD, highlightthickness=1, highlightbackground="#f4d4e1")
        summary.pack(fill="x", padx=14, pady=(0, 10))
        tk.Label(summary, text="Vector Fuerza Neta", font=theme.LABEL_FONT, fg=theme.MUTED, bg=theme.CARD).pack(
            pady=(12, 6)
        )
        self.vec = tk.Label(summary, text="< -, - > N", font=theme.VECTOR_FONT, fg=theme.PINK, bg=theme.CARD)
        self.vec.pack(pady=(0, 12))

        metrics = tk.Frame(card, bg=theme.PINK_SOFT)
        metrics.pack(fill="x", padx=14, pady=(0, 10))
        for column in range(2):
            metrics.grid_columnconfigure(column, weight=1)

        self.fx = self._create_metric(metrics, 0, 0, "Componente X", "Newtons")
        self.fy = self._create_metric(metrics, 0, 1, "Componente Y", "Newtons")
        self.mag = self._create_metric(metrics, 1, 0, "Magnitud", "Newtons")
        self.ang = self._create_metric(metrics, 1, 1, "Angulo", "grados")

        help_box = tk.Frame(card, bg=theme.BLUE, highlightthickness=1, highlightbackground=theme.FIELD_BORDER)
        help_box.pack(fill="x", padx=14, pady=(0, 14))
        tk.Label(
            help_box,
            text=(
                "F = k |q1 q2| / r^2\n"
                "u = a / |a|\n"
                "F_vector = |F| u\n"
                "r = punto final - punto inicial\n"
                f"K = {theme.K_TEXT} N m^2 / C^2"
            ),
            justify="left",
            anchor="w",
            font=theme.LABEL_FONT,
            fg="#355070",
            bg=theme.BLUE,
        ).pack(fill="x", padx=14, pady=12)

    def _build_steps_card(self, parent: tk.Frame) -> None:
        card = theme.create_card(parent)
        card.pack(fill="both", expand=True)
        theme.create_section_header(card, "Pasos del Algoritmo")

        self.combo = ttk.Combobox(card, state="readonly", style="Steps.TCombobox")
        self.combo.pack(fill="x", padx=14, pady=(0, 8))
        self.combo.bind("<<ComboboxSelected>>", self._show_step)

        self.text = tk.Text(
            card,
            height=15,
            wrap="word",
            bg="#f8fbff",
            fg=theme.TXT,
            relief="flat",
            bd=0,
            highlightthickness=1,
            highlightbackground=theme.FIELD_BORDER,
            highlightcolor=theme.ACTIVE,
            font=theme.MONO_FONT,
            padx=12,
            pady=12,
        )
        self.text.pack(fill="both", expand=True, padx=14, pady=(0, 14))
        self._refresh_steps()

    def _create_metric(self, parent: tk.Frame, row: int, column: int, title: str, unit: str) -> tk.Label:
        box = tk.Frame(parent, bg=theme.CARD, highlightthickness=1, highlightbackground=theme.BORDER)
        box.grid(row=row, column=column, sticky="nsew", padx=5, pady=5)
        tk.Label(box, text=title, font=theme.LABEL_FONT, fg=theme.MUTED, bg=theme.CARD).pack(pady=(12, 6))
        value = tk.Label(box, text="-", font=theme.VALUE_FONT, fg=theme.TXT, bg=theme.CARD)
        value.pack()
        tk.Label(box, text=unit, font=theme.LABEL_FONT, fg=theme.MUTED, bg=theme.CARD).pack(pady=(4, 12))
        return value

    def _add_row(self, preset: tuple[str, str, str] | None = None) -> None:
        q_var = tk.StringVar(value="" if preset is None else preset[0])
        x_var = tk.StringVar(value="" if preset is None else preset[1])
        y_var = tk.StringVar(value="" if preset is None else preset[2])

        card = tk.Frame(self.rows_box, bg=theme.CARD, highlightthickness=1, highlightbackground="#edf1f7", bd=0)
        card.pack(fill="x", pady=(0, 10))

        head = tk.Frame(card, bg=theme.CARD)
        head.pack(fill="x", padx=12, pady=(10, 5))

        dot = tk.Canvas(head, width=14, height=14, bg=theme.CARD, highlightthickness=0)
        dot.pack(side="left")
        title = tk.Label(head, text="Carga", font=("Segoe UI", 14, "bold"), fg=theme.TXT, bg=theme.CARD)
        title.pack(side="left", padx=8)

        row = ChargeRow(frame=card, title=title, dot=dot, q_var=q_var, x_var=x_var, y_var=y_var)
        tk.Button(
            head,
            text="X",
            command=lambda current=row: self._remove_row(current),
            bg=theme.CARD,
            fg="#94a3b8",
            activebackground=theme.CARD,
            activeforeground=theme.PINK,
            relief="flat",
            bd=0,
            padx=6,
            pady=2,
            font=("Segoe UI", 12, "bold"),
            cursor="hand2",
        ).pack(side="right")

        grid = tk.Frame(card, bg=theme.CARD)
        grid.pack(fill="x", padx=12, pady=(0, 12))
        for column in range(3):
            grid.grid_columnconfigure(column, weight=1)

        theme.create_labeled_entry(grid, "Magnitud (C)", 0, 0, q_var)
        theme.create_labeled_entry(grid, "X (m)", 0, 1, x_var)
        theme.create_labeled_entry(grid, "Y (m)", 0, 2, y_var)

        q_var.trace_add("write", lambda *_args, current=row: self._paint_row(current))
        self.rows.append(row)
        self._reindex()
        self._paint_row(row)

    def _remove_row(self, row: ChargeRow) -> None:
        if len(self.rows) <= 1:
            messagebox.showwarning("Carga requerida", "Debe existir al menos una carga puntual.")
            return

        row.frame.destroy()
        self.rows = [current for current in self.rows if current is not row]
        self._reindex()

    def _reindex(self) -> None:
        for index, row in enumerate(self.rows, start=1):
            row.title.config(text=f"Carga {index}")

    def _paint_row(self, row: ChargeRow) -> None:
        color, sign = theme.RED_Q, "+"
        try:
            if row.q_var.get().strip() and float(row.q_var.get()) < 0:
                color, sign = theme.BLUE_Q, "-"
        except ValueError:
            color, sign = theme.NET, "?"

        row.dot.delete("all")
        row.dot.create_oval(1, 1, 13, 13, fill=color, outline=color)
        row.dot.create_text(7, 7, text=sign, fill="#ffffff", font=("Segoe UI", 8, "bold"))

    def _refresh_steps(self) -> None:
        self.combo["values"] = [title for title, _ in self.steps]
        self.combo.current(0)
        self._write_step(self.steps[0][1])

    def _write_step(self, text: str) -> None:
        self.text.config(state="normal")
        self.text.delete("1.0", "end")
        self.text.insert("1.0", text)
        self.text.config(state="disabled")

    def _show_step(self, _event: tk.Event) -> None:
        index = self.combo.current()
        if 0 <= index < len(self.steps):
            self._write_step(self.steps[index][1])

    def _sync_page_scroll(self, _event: tk.Event | None = None) -> None:
        self.scroll_canvas.configure(scrollregion=self.scroll_canvas.bbox("all"))

    def _resize_page(self, event: tk.Event) -> None:
        self.scroll_canvas.itemconfigure(self.page_window, width=event.width)

    def _on_mousewheel(self, event: tk.Event) -> None:
        if event.delta:
            self.scroll_canvas.yview_scroll(int(-event.delta / 120), "units")

    def _draw_scene(self, _event: tk.Event | None = None) -> None:
        draw_force_scene(self.canvas, self.target, self.sources, self.net)

    def _collect(self) -> tuple[PointCharge, list[PointCharge]]:
        target = PointCharge(
            validate_float(self.target_q.get(), "Magnitud de la carga objetivo"),
            validate_float(self.target_x.get(), "Posicion X de la carga objetivo"),
            validate_float(self.target_y.get(), "Posicion Y de la carga objetivo"),
        )

        sources: list[PointCharge] = []
        for index, row in enumerate(self.rows, start=1):
            q = row.q_var.get().strip()
            x = row.x_var.get().strip()
            y = row.y_var.get().strip()

            if not q and not x and not y:
                continue
            if not q or not x or not y:
                raise ValueError(f"Completa todos los campos de la Carga {index}.")

            sources.append(
                PointCharge(
                    validate_float(q, f"Magnitud de la Carga {index}"),
                    validate_float(x, f"Posicion X de la Carga {index}"),
                    validate_float(y, f"Posicion Y de la Carga {index}"),
                )
            )

        if not sources:
            raise ValueError("Agrega al menos una carga puntual.")
        return target, sources

    def _calculate(self) -> None:
        try:
            target, sources = self._collect()
            report = build_calculation_report(target, sources)

            self.target = report.target
            self.sources = report.sources
            self.details = report.details
            self.net = (report.fx, report.fy)
            self.steps = report.steps

            self.vec.config(text=f"< {format_result_value(report.fx)}, {format_result_value(report.fy)} > N")
            self.fx.config(text=format_result_value(report.fx))
            self.fy.config(text=format_result_value(report.fy))
            self.mag.config(text=format_result_value(report.magnitude))
            self.ang.config(text=f"{report.angle:.2f}")

            self._refresh_steps()
            self._draw_scene()
        except ValueError as exc:
            messagebox.showerror("Datos invalidos", str(exc))
        except Exception:
            messagebox.showerror(
                "Error inesperado",
                "No se pudo completar el calculo. Revisa que todos los campos esten completos.",
            )
