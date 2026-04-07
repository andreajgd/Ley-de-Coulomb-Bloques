import tkinter as tk
from tkinter import messagebox, ttk

from models.charge import PointCharge
from physics.coulomb import K_COULOMB, force_detail_on_target_from_source, vector_angle_degrees, vector_magnitude
from utils.formatting import format_scientific

BG = "#f4f6fb"
CARD = "#ffffff"
BORDER = "#e7ebf2"
FIELD = "#f6f8fc"
FIELD_BORDER = "#e2e8f0"
ACTIVE = "#ff5b87"
TXT = "#122033"
MUTED = "#64748b"
PINK = "#ff2d55"
PINK_SOFT = "#fff2f7"
YELLOW = "#fff7e2"
BLUE = "#eef4ff"
RED_Q = "#ff4d5d"
BLUE_Q = "#3b82f6"
TARGET = "#f7a813"
TARGET_EDGE = "#ff5b3a"
NET = "#f59e0b"
K_TEXT = "9 x 10^9"
STEP_TITLES = [
    "1. Los puntos",
    "2. Calcular distancias entre los puntos",
    "3. Formula F para cada punto",
    "4. Calcular v",
    "5. Calcular u",
    "6. F = |F| u para cada combinacion",
    "7. Sumatoria de vectores fuerza",
]


class CoulombApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Calculadora de Fuerza Electrica")
        self.root.geometry("1380x920")
        self.root.minsize(1180, 820)
        self.root.configure(bg=BG)
        self.rows: list[dict[str, object]] = []
        self.target: PointCharge | None = None
        self.sources: list[PointCharge] = []
        self.details: list[dict[str, object]] = []
        self.net = (0.0, 0.0)
        self.steps = [(t, "Completa los datos y presiona 'Calcular Fuerza Neta'.") for t in STEP_TITLES]
        self._style()
        self._ui()
        self._add_row()
        self._draw_scene()

    def _style(self) -> None:
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("Steps.TCombobox", padding=8, fieldbackground=CARD, background=CARD, foreground=TXT)
        style.map("Steps.TCombobox", fieldbackground=[("readonly", CARD)], foreground=[("readonly", TXT)])

    def _card(self, parent: tk.Widget, bg: str = CARD) -> tk.Frame:
        return tk.Frame(parent, bg=bg, highlightthickness=1, highlightbackground=BORDER, bd=0)

    def _title(self, parent: tk.Frame, text: str, color: str, btn: tuple[str, object] | None = None) -> None:
        row = tk.Frame(parent, bg=parent["bg"])
        row.pack(fill="x", padx=18, pady=(16, 8))
        tk.Label(row, text=text, font=("Segoe UI", 16, "bold"), fg=TXT, bg=parent["bg"]).pack(side="left")
        if btn:
            tk.Button(
                row, text=btn[0], command=btn[1], bg=PINK, fg="#fff", activebackground="#ff4b6e",
                activeforeground="#fff", relief="flat", bd=0, padx=16, pady=8,
                font=("Segoe UI", 11, "bold"), cursor="hand2"
            ).pack(side="right")

    def _entry(self, parent: tk.Frame, label: str, row: int, col: int, var: tk.StringVar | None = None) -> tk.Entry:
        box = tk.Frame(parent, bg=parent["bg"])
        box.grid(row=row, column=col, sticky="ew", padx=8, pady=4)
        tk.Label(box, text=label, font=("Segoe UI", 11), fg=MUTED, bg=box["bg"]).pack(anchor="w")
        entry = tk.Entry(
            box, textvariable=var, bg=FIELD, fg=TXT, insertbackground=TXT, relief="flat", bd=0,
            highlightthickness=1, highlightbackground=FIELD_BORDER, highlightcolor=ACTIVE, font=("Segoe UI", 13)
        )
        entry.pack(fill="x", pady=(6, 0), ipady=10)
        return entry

    def _ui(self) -> None:
        wrap = tk.Frame(self.root, bg=BG)
        wrap.pack(fill="both", expand=True)

        scrollbar = tk.Scrollbar(wrap, orient="vertical")
        scrollbar.pack(side="right", fill="y")

        self.scroll_canvas = tk.Canvas(wrap, bg=BG, highlightthickness=0, yscrollcommand=scrollbar.set)
        self.scroll_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.scroll_canvas.yview)

        page = tk.Frame(self.scroll_canvas, bg=BG)
        self.page_window = self.scroll_canvas.create_window((0, 0), window=page, anchor="nw")
        page.bind("<Configure>", self._sync_page_scroll)
        self.scroll_canvas.bind("<Configure>", self._resize_page)
        self.scroll_canvas.bind_all("<MouseWheel>", self._on_mousewheel)

        self.header = tk.Canvas(page, height=128, bg=PINK, highlightthickness=0)
        self.header.pack(fill="x")
        self.header.bind("<Configure>", self._draw_header)

        body = tk.Frame(page, bg=BG, padx=18, pady=18)
        body.pack(fill="both", expand=True)

        graph = self._card(body)
        graph.pack(fill="x", pady=(0, 16))
        self._title(graph, "Plano Cartesiano", "#7c3aed")
        self.canvas = tk.Canvas(graph, height=360, bg="#fbfcfe", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True, padx=18, pady=(0, 18))
        self.canvas.bind("<Configure>", self._draw_scene)

        area = tk.Frame(body, bg=BG)
        area.pack(fill="both", expand=True)
        left = tk.Frame(area, bg=BG)
        right = tk.Frame(area, bg=BG)
        left.pack(side="left", fill="both", expand=True, padx=(0, 10))
        right.pack(side="left", fill="both", expand=True, padx=(10, 0))

        tcard = self._card(left)
        tcard.pack(fill="x", pady=(0, 14))
        self._title(tcard, "Carga Objetivo", BLUE_Q)
        tgrid = tk.Frame(tcard, bg=CARD)
        tgrid.pack(fill="x", padx=18, pady=(0, 18))
        for i in range(3):
            tgrid.grid_columnconfigure(i, weight=1)
        self.target_q = self._entry(tgrid, "Magnitud (C)", 0, 0)
        self.target_x = self._entry(tgrid, "Posicion X (m)", 0, 1)
        self.target_y = self._entry(tgrid, "Posicion Y (m)", 0, 2)

        scard = self._card(left)
        scard.pack(fill="both", expand=True, pady=(0, 14))
        self._title(scard, "Cargas Puntuales", NET, ("Agregar", self._add_row))
        self.rows_box = tk.Frame(scard, bg=CARD)
        self.rows_box.pack(fill="both", expand=True, padx=18, pady=(0, 18))

        tk.Button(
            left, text="Calcular Fuerza Neta", command=self._calculate, bg=PINK, fg="#fff",
            activebackground="#ff4b6e", activeforeground="#fff", relief="flat", bd=0,
            padx=18, pady=14, font=("Segoe UI", 15, "bold"), cursor="hand2"
        ).pack(fill="x")

        vcard = self._card(right, PINK_SOFT)
        vcard.pack(fill="x", pady=(0, 14))
        self._title(vcard, "Vector Fuerza Neta", PINK)
        vbox = tk.Frame(vcard, bg=CARD, highlightthickness=1, highlightbackground="#f4d4e1")
        vbox.pack(fill="x", padx=18, pady=(0, 18))
        self.vec = tk.Label(vbox, text="< -, - > N", font=("Consolas", 28, "bold"), fg=PINK, bg=CARD)
        self.vec.pack(pady=18)

        row = tk.Frame(right, bg=BG)
        row.pack(fill="x", pady=(0, 14))
        self.fx = self._metric(row, "Componente X")
        self.fy = self._metric(row, "Componente Y")

        self.mag = self._big_metric(right, "Magnitud", YELLOW, "#ff5c00", "-")
        self.ang = self._big_metric(right, "Angulo", CARD, TXT, "-")
        self.ang[1].config(font=("Segoe UI", 28, "bold"))
        tk.Label(self.ang[0], text="respecto al eje X positivo", font=("Segoe UI", 11), fg=MUTED, bg="#f8fafc").pack(pady=(0, 14))

        fcard, flabel = self._big_metric(right, "Ley de Coulomb", BLUE, "#2563eb", "F = k |q1 q2| / r^2")
        flabel.config(font=("Consolas", 22, "bold"), bg=CARD, fg="#2563eb")
        tk.Label(
            fcard,
            text=f"u = a / |a|\nF_vector = |F| u\nr = punto final - punto inicial\nK = {K_TEXT} N m^2 / C^2",
            justify="left", anchor="w", font=("Segoe UI", 12), fg="#355070", bg=BLUE
        ).pack(fill="x", padx=18, pady=(0, 18))

        steps = self._card(body)
        steps.pack(fill="both", expand=True, pady=(16, 0))
        self._title(steps, "Pasos del Algoritmo", "#6366f1")
        self.combo = ttk.Combobox(steps, state="readonly", style="Steps.TCombobox")
        self.combo.pack(fill="x", padx=18, pady=(0, 10))
        self.combo.bind("<<ComboboxSelected>>", self._show_step)
        self.text = tk.Text(
            steps, height=13, wrap="word", bg="#f8fbff", fg=TXT, relief="flat", bd=0,
            highlightthickness=1, highlightbackground=FIELD_BORDER, highlightcolor=ACTIVE,
            font=("Consolas", 10), padx=12, pady=12
        )
        self.text.pack(fill="both", expand=True, padx=18, pady=(0, 18))
        self._steps_ui()

    def _metric(self, parent: tk.Frame, title: str) -> tk.Label:
        card = self._card(parent)
        card.pack(side="left", fill="both", expand=True, padx=8)
        tk.Label(card, text=title, font=("Segoe UI", 12), fg=MUTED, bg=CARD).pack(pady=(18, 6))
        value = tk.Label(card, text="-", font=("Segoe UI", 22, "bold"), fg=TXT, bg=CARD)
        value.pack()
        tk.Label(card, text="Newtons", font=("Segoe UI", 11), fg=MUTED, bg=CARD).pack(pady=(2, 18))
        return value

    def _big_metric(self, parent: tk.Frame, title: str, bg: str, color: str, value: str) -> tuple[tk.Frame, tk.Label]:
        card = self._card(parent, bg)
        card.pack(fill="x", pady=(0, 14))
        self._title(card, title, color)
        box = tk.Frame(card, bg="#f8fafc" if title == "Angulo" else CARD, highlightthickness=1, highlightbackground=FIELD_BORDER)
        box.pack(fill="x", padx=18, pady=(0, 18))
        label = tk.Label(box, text=value, font=("Segoe UI", 28, "bold"), fg=color, bg=box["bg"])
        label.pack(pady=16)
        return card, label

    def _add_row(self, preset: tuple[str, str, str] | None = None) -> None:
        row: dict[str, object] = {}
        card = tk.Frame(self.rows_box, bg=CARD, highlightthickness=1, highlightbackground="#edf1f7", bd=0)
        card.pack(fill="x", pady=(0, 12))
        head = tk.Frame(card, bg=CARD)
        head.pack(fill="x", padx=16, pady=(12, 6))
        dot = tk.Canvas(head, width=14, height=14, bg=CARD, highlightthickness=0)
        dot.pack(side="left")
        title = tk.Label(head, text="Carga", font=("Segoe UI", 14, "bold"), fg=TXT, bg=CARD)
        title.pack(side="left", padx=8)
        tk.Button(
            head, text="X", command=lambda r=row: self._remove_row(r), bg=CARD, fg="#94a3b8",
            activebackground=CARD, activeforeground=PINK, relief="flat", bd=0, padx=6,
            pady=2, font=("Segoe UI", 12, "bold"), cursor="hand2"
        ).pack(side="right")
        grid = tk.Frame(card, bg=CARD)
        grid.pack(fill="x", padx=16, pady=(0, 14))
        for i in range(3):
            grid.grid_columnconfigure(i, weight=1)
        qv = tk.StringVar(value="" if preset is None else preset[0])
        xv = tk.StringVar(value="" if preset is None else preset[1])
        yv = tk.StringVar(value="" if preset is None else preset[2])
        self._entry(grid, "Magnitud (C)", 0, 0, qv)
        self._entry(grid, "X (m)", 0, 1, xv)
        self._entry(grid, "Y (m)", 0, 2, yv)
        row.update({"frame": card, "title": title, "dot": dot, "qv": qv, "xv": xv, "yv": yv})
        qv.trace_add("write", lambda *_a, r=row: self._paint_row(r))
        self.rows.append(row)
        self._reindex()
        self._paint_row(row)

    def _remove_row(self, row: dict[str, object]) -> None:
        if len(self.rows) <= 1:
            messagebox.showwarning("Carga requerida", "Debe existir al menos una carga puntual.")
            return
        frame = row["frame"]
        if isinstance(frame, tk.Frame):
            frame.destroy()
        self.rows = [r for r in self.rows if r is not row]
        self._reindex()

    def _reindex(self) -> None:
        for i, row in enumerate(self.rows, start=1):
            title = row["title"]
            if isinstance(title, tk.Label):
                title.config(text=f"Carga {i}")

    def _paint_row(self, row: dict[str, object]) -> None:
        dot, qv = row["dot"], row["qv"]
        if not isinstance(dot, tk.Canvas) or not isinstance(qv, tk.StringVar):
            return
        color, sign = RED_Q, "+"
        try:
            if qv.get().strip() and float(qv.get()) < 0:
                color, sign = BLUE_Q, "-"
        except ValueError:
            color, sign = NET, "?"
        dot.delete("all")
        dot.create_oval(1, 1, 13, 13, fill=color, outline=color)
        dot.create_text(7, 7, text=sign, fill="#fff", font=("Segoe UI", 8, "bold"))

    def _steps_ui(self) -> None:
        self.combo["values"] = [t for t, _ in self.steps]
        self.combo.current(0)
        self._write(self.steps[0][1])

    def _write(self, text: str) -> None:
        self.text.config(state="normal")
        self.text.delete("1.0", "end")
        self.text.insert("1.0", text)
        self.text.config(state="disabled")

    def _show_step(self, _event: tk.Event) -> None:
        i = self.combo.current()
        if 0 <= i < len(self.steps):
            self._write(self.steps[i][1])

    def _fmtp(self, value: float) -> str:
        if abs(value) >= 10000 or (0 < abs(value) < 0.001):
            return format_scientific(value, 4)
        text = f"{value:.4f}".rstrip("0").rstrip(".")
        return text if text not in {"", "-0"} else "0"

    def _fmts(self, value: float) -> str:
        return format_scientific(value, 4)

    def _sync_page_scroll(self, _event: tk.Event | None = None) -> None:
        self.scroll_canvas.configure(scrollregion=self.scroll_canvas.bbox("all"))

    def _resize_page(self, event: tk.Event) -> None:
        self.scroll_canvas.itemconfigure(self.page_window, width=event.width)

    def _on_mousewheel(self, event: tk.Event) -> None:
        if event.delta:
            self.scroll_canvas.yview_scroll(int(-event.delta / 120), "units")

    def _draw_header(self, _event: tk.Event | None = None) -> None:
        w = max(self.header.winfo_width(), 900)
        h = max(self.header.winfo_height(), 128)
        self.header.delete("all")
        colors = ["#f72585", "#fa287f", "#fc2b78", "#ff2d6b", "#ff305c"]
        step = max(w // len(colors), 1)
        for i, color in enumerate(colors):
            x0 = i * step
            x1 = w if i == len(colors) - 1 else (i + 1) * step
            self.header.create_rectangle(x0, 0, x1, h, fill=color, outline=color)
        self.header.create_text(w / 2, 42, text="Calculadora de Fuerza Electrica", font=("Segoe UI", 28, "bold"), fill="#fff")
        self.header.create_text(w / 2, 84, text="Ley de Coulomb y Principio de Superposicion", font=("Segoe UI", 14), fill="#ffe3ef")

    def _draw_scene(self, _event: tk.Event | None = None) -> None:
        c = self.canvas
        c.delete("all")
        w = max(c.winfo_width(), 500)
        h = max(c.winfo_height(), 320)
        cx, cy = w / 2, h / 2
        for x in range(0, w + 44, 44):
            c.create_line(x, 0, x, h, fill="#edf1f7")
        for y in range(0, h + 44, 44):
            c.create_line(0, y, w, y, fill="#edf1f7")
        c.create_line(0, cy, w, cy, fill="#7b8596", width=2)
        c.create_line(cx, 0, cx, h, fill="#7b8596", width=2)
        c.create_text(cx + 10, 18, text="Y", fill=MUTED, anchor="nw", font=("Segoe UI", 10, "bold"))
        c.create_text(w - 26, cy - 18, text="X", fill=MUTED, anchor="nw", font=("Segoe UI", 10, "bold"))
        c.create_rectangle(18, 18, 190, 118, fill="#fff", outline=BORDER)
        c.create_text(40, 38, text="Leyenda:", anchor="w", fill=TXT, font=("Segoe UI", 11, "bold"))
        c.create_oval(36, 54, 50, 68, fill=RED_Q, outline=RED_Q)
        c.create_text(60, 61, text="Carga positiva (+)", anchor="w", fill="#475569", font=("Segoe UI", 10))
        c.create_oval(36, 76, 50, 90, fill=BLUE_Q, outline=BLUE_Q)
        c.create_text(60, 83, text="Carga negativa (-)", anchor="w", fill="#475569", font=("Segoe UI", 10))
        c.create_line(36, 102, 60, 102, fill=NET, width=3)
        c.create_text(72, 102, text="Fuerza neta", anchor="w", fill="#475569", font=("Segoe UI", 10))
        if not self.target:
            c.create_text(w / 2, h / 2, text="Ingresa datos y calcula para ver el diagrama.", font=("Segoe UI", 14), fill=MUTED)
            return
        pts = [(self.target.x, self.target.y)] + [(s.x, s.y) for s in self.sources]
        extent = max(max(abs(x), abs(y)) for x, y in pts) if pts else 1.0
        scale = (0.34 * min(w, h)) / max(extent, 1.0)

        def to_canvas(x: float, y: float) -> tuple[float, float]:
            return cx + x * scale, cy - y * scale

        tx, ty = to_canvas(self.target.x, self.target.y)
        for i, source in enumerate(self.sources, start=1):
            sx, sy = to_canvas(source.x, source.y)
            c.create_line(sx, sy, tx, ty, fill="#ced8fb", width=2, dash=(4, 4))
            color = RED_Q if source.q >= 0 else BLUE_Q
            sign = "+" if source.q >= 0 else "-"
            c.create_oval(sx - 16, sy - 16, sx + 16, sy + 16, fill=color, outline="#fff", width=2)
            c.create_text(sx, sy, text=sign, fill="#fff", font=("Segoe UI", 16, "bold"))
            c.create_text(sx, sy + 28, text=f"q{i}", fill=color, font=("Segoe UI", 10, "bold"))
        ts = "+" if self.target.q >= 0 else "-"
        c.create_oval(tx - 22, ty - 22, tx + 22, ty + 22, fill=TARGET, outline=TARGET_EDGE, width=3)
        c.create_text(tx, ty, text=ts, fill="#fff", font=("Segoe UI", 18, "bold"))
        c.create_text(tx, ty + 36, text="q0 (objetivo)", fill=TARGET, font=("Segoe UI", 11, "bold"))
        fx, fy = self.net
        mag = vector_magnitude(fx, fy)
        if mag > 0:
            factor = 88 / mag
            ex, ey = tx + fx * factor, ty - fy * factor
            c.create_line(tx, ty, ex, ey, fill=NET, width=4, arrow=tk.LAST)
            c.create_text((tx + ex) / 2, (ty + ey) / 2 - 12, text="F_net", fill=NET, font=("Segoe UI", 11, "bold"))

    def _collect(self) -> tuple[PointCharge, list[PointCharge]]:
        def parse(value: str, label: str) -> float:
            if not value:
                raise ValueError(f"{label} es obligatorio.")
            try:
                return float(value)
            except ValueError as exc:
                raise ValueError(f"{label} debe ser un numero valido.") from exc

        target = PointCharge(
            parse(self.target_q.get().strip(), "Magnitud de la carga objetivo"),
            parse(self.target_x.get().strip(), "Posicion X de la carga objetivo"),
            parse(self.target_y.get().strip(), "Posicion Y de la carga objetivo"),
        )
        sources: list[PointCharge] = []
        for i, row in enumerate(self.rows, start=1):
            qv, xv, yv = row["qv"], row["xv"], row["yv"]
            if not isinstance(qv, tk.StringVar) or not isinstance(xv, tk.StringVar) or not isinstance(yv, tk.StringVar):
                continue
            q, x, y = qv.get().strip(), xv.get().strip(), yv.get().strip()
            if not q and not x and not y:
                continue
            if not q or not x or not y:
                raise ValueError(f"Completa todos los campos de la Carga {i}.")
            sources.append(PointCharge(parse(q, f"Magnitud de la Carga {i}"), parse(x, f"Posicion X de la Carga {i}"), parse(y, f"Posicion Y de la Carga {i}")))
        if not sources:
            raise ValueError("Agrega al menos una carga puntual.")
        return target, sources

    def _build_steps(self, target: PointCharge, details: list[dict[str, object]], fx: float, fy: float) -> list[tuple[str, str]]:
        lines = [[
            f"K = {K_TEXT} N m^2 / C^2",
            f"q0 (objetivo) = {self._fmtp(target.q)} C en ({self._fmtp(target.x)}, {self._fmtp(target.y)})",
        ], [], [], [], [], [], []]
        for i, d in enumerate(details, start=1):
            sx, sy = d["source_pos"]  # type: ignore[misc]
            tx, ty = d["target_pos"]  # type: ignore[misc]
            vx, vy = d["v_vector"]  # type: ignore[misc]
            ax, ay = d["a_vector"]  # type: ignore[misc]
            ux, uy = d["u_vector"]  # type: ignore[misc]
            fvx, fvy = d["force_vector"]  # type: ignore[misc]
            sq = float(d["source_q"])
            dist = float(d["distance"])
            fm = float(d["force_magnitude"])
            lines[0].append(f"q{i} = {self._fmtp(sq)} C en ({self._fmtp(float(sx))}, {self._fmtp(float(sy))})")
            lines[0].append(f"Combinacion {i}: punto inicial = q{i}, punto final = q0.")
            lines[1].append(
                f"q{i} -> q0: d{i} = sqrt(({self._fmtp(float(tx))} - {self._fmtp(float(sx))})^2 + ({self._fmtp(float(ty))} - {self._fmtp(float(sy))})^2) = {self._fmtp(dist)} m"
            )
            lines[2].append(
                f"|F{i}| = k |q{i} q0| / d{i}^2 = {K_TEXT} |{self._fmtp(sq)} x {self._fmtp(target.q)}| / ({self._fmtp(dist)})^2 = {self._fmts(fm)} N"
            )
            lines[3].append(
                f"v{i} = punto final - punto inicial = ({self._fmtp(float(tx))} - {self._fmtp(float(sx))}, {self._fmtp(float(ty))} - {self._fmtp(float(sy))}) = ({self._fmtp(float(vx))}, {self._fmtp(float(vy))})"
            )
            rel = "repulsion, por eso a = v" if d["interaction"] == "repulsion" else "atraccion, por eso a = -v"
            lines[4].append(
                f"q{i} -> q0: {rel}\na{i} = ({self._fmtp(float(ax))}, {self._fmtp(float(ay))})\nu{i} = a{i} / |a{i}| = ({self._fmts(float(ux))}, {self._fmts(float(uy))})"
            )
            lines[5].append(
                f"F{i} = |F{i}| u{i} = {self._fmts(fm)} ({self._fmts(float(ux))}, {self._fmts(float(uy))}) = ({self._fmts(float(fvx))}, {self._fmts(float(fvy))}) N"
            )
            lines[6].append(f"F{i} = ({self._fmts(float(fvx))}, {self._fmts(float(fvy))}) N")
        lines[6].append(f"F_neta = ({self._fmts(fx)}, {self._fmts(fy)}) N")
        lines[6].append(f"|F_neta| = {self._fmts(vector_magnitude(fx, fy))} N")
        lines[6].append(f"Angulo = {vector_angle_degrees(fx, fy):.2f} grados")
        return [(STEP_TITLES[i], "\n\n".join(block) if i else "\n".join(block)) for i, block in enumerate(lines)]

    def _calculate(self) -> None:
        try:
            target, sources = self._collect()
            details = [force_detail_on_target_from_source(target, s, label=f"q{i}") for i, s in enumerate(sources, start=1)]
            fx = sum(float(d["force_vector"][0]) for d in details)  # type: ignore[index]
            fy = sum(float(d["force_vector"][1]) for d in details)  # type: ignore[index]
            self.target, self.sources, self.details, self.net = target, sources, details, (fx, fy)
            self.steps = self._build_steps(target, details, fx, fy)
            self.vec.config(text=f"< {self._fmts(fx)}, {self._fmts(fy)} > N")
            self.fx.config(text=self._fmts(fx))
            self.fy.config(text=self._fmts(fy))
            self.mag[1].config(text=f"{self._fmts(vector_magnitude(fx, fy))} N")
            self.ang[1].config(text=f"{vector_angle_degrees(fx, fy):.2f} grados")
            self._steps_ui()
            self._draw_scene()
        except ValueError as exc:
            messagebox.showerror("Datos invalidos", str(exc))
        except Exception:
            messagebox.showerror("Error inesperado", "No se pudo completar el calculo. Revisa que todos los campos esten completos.")
