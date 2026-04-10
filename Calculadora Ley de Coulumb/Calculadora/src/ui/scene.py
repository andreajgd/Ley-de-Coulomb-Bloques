from __future__ import annotations

import tkinter as tk

from models.charge import PointCharge
from physics.coulomb import vector_magnitude
from ui import theme


def draw_force_scene(
    canvas: tk.Canvas,
    target: PointCharge | None,
    sources: list[PointCharge],
    net: tuple[float, float],
) -> None:
    canvas.delete("all")

    width = max(canvas.winfo_width(), 500)
    height = max(canvas.winfo_height(), 320)
    center_x, center_y = width / 2, height / 2

    for x in range(0, width + 44, 44):
        canvas.create_line(x, 0, x, height, fill="#edf1f7")
    for y in range(0, height + 44, 44):
        canvas.create_line(0, y, width, y, fill="#edf1f7")

    canvas.create_line(0, center_y, width, center_y, fill="#7b8596", width=2)
    canvas.create_line(center_x, 0, center_x, height, fill="#7b8596", width=2)
    canvas.create_text(center_x + 10, 18, text="Y", fill=theme.MUTED, anchor="nw", font=("Segoe UI", 10, "bold"))
    canvas.create_text(width - 26, center_y - 18, text="X", fill=theme.MUTED, anchor="nw", font=("Segoe UI", 10, "bold"))

    canvas.create_rectangle(18, 18, 190, 118, fill="#ffffff", outline=theme.BORDER)
    canvas.create_text(40, 38, text="Leyenda:", anchor="w", fill=theme.TXT, font=("Segoe UI", 11, "bold"))
    canvas.create_oval(36, 54, 50, 68, fill=theme.RED_Q, outline=theme.RED_Q)
    canvas.create_text(60, 61, text="Carga positiva (+)", anchor="w", fill="#475569", font=("Segoe UI", 10))
    canvas.create_oval(36, 76, 50, 90, fill=theme.BLUE_Q, outline=theme.BLUE_Q)
    canvas.create_text(60, 83, text="Carga negativa (-)", anchor="w", fill="#475569", font=("Segoe UI", 10))
    canvas.create_line(36, 102, 60, 102, fill=theme.NET, width=3)
    canvas.create_text(72, 102, text="Fuerza neta", anchor="w", fill="#475569", font=("Segoe UI", 10))

    if not target:
        canvas.create_text(
            width / 2,
            height / 2,
            text="Ingresa datos y calcula para ver el diagrama.",
            font=("Segoe UI", 14),
            fill=theme.MUTED,
        )
        return

    points = [(target.x, target.y)] + [(source.x, source.y) for source in sources]
    extent = max(max(abs(x), abs(y)) for x, y in points) if points else 1.0
    scale = (0.34 * min(width, height)) / max(extent, 1.0)

    def to_canvas(x: float, y: float) -> tuple[float, float]:
        return center_x + x * scale, center_y - y * scale

    target_x, target_y = to_canvas(target.x, target.y)
    for index, source in enumerate(sources, start=1):
        source_x, source_y = to_canvas(source.x, source.y)
        canvas.create_line(source_x, source_y, target_x, target_y, fill="#ced8fb", width=2, dash=(4, 4))
        color = theme.RED_Q if source.q >= 0 else theme.BLUE_Q
        sign = "+" if source.q >= 0 else "-"
        canvas.create_oval(source_x - 16, source_y - 16, source_x + 16, source_y + 16, fill=color, outline="#ffffff", width=2)
        canvas.create_text(source_x, source_y, text=sign, fill="#ffffff", font=("Segoe UI", 16, "bold"))
        canvas.create_text(source_x, source_y + 28, text=f"q{index}", fill=color, font=("Segoe UI", 10, "bold"))

    sign = "+" if target.q >= 0 else "-"
    canvas.create_oval(
        target_x - 22,
        target_y - 22,
        target_x + 22,
        target_y + 22,
        fill=theme.TARGET,
        outline=theme.TARGET_EDGE,
        width=3,
    )
    canvas.create_text(target_x, target_y, text=sign, fill="#ffffff", font=("Segoe UI", 18, "bold"))
    canvas.create_text(target_x, target_y + 36, text="q0 (objetivo)", fill=theme.TARGET, font=("Segoe UI", 11, "bold"))

    fx, fy = net
    magnitude = vector_magnitude(fx, fy)
    if magnitude <= 0:
        return

    factor = 88 / magnitude
    end_x, end_y = target_x + fx * factor, target_y - fy * factor
    canvas.create_line(target_x, target_y, end_x, end_y, fill=theme.NET, width=4, arrow=tk.LAST)
    canvas.create_text(
        (target_x + end_x) / 2,
        (target_y + end_y) / 2 - 12,
        text="F_net",
        fill=theme.NET,
        font=("Segoe UI", 11, "bold"),
    )
