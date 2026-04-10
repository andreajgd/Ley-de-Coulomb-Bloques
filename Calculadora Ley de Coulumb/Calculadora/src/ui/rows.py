from __future__ import annotations

from dataclasses import dataclass
import tkinter as tk


@dataclass
class ChargeRow:
    frame: tk.Frame
    title: tk.Label
    dot: tk.Canvas
    q_var: tk.StringVar
    x_var: tk.StringVar
    y_var: tk.StringVar
