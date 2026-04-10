from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Callable

from utils.calculator import K_TEXT

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

HEADER_TITLE_FONT = ("Segoe UI", 24, "bold")
HEADER_SUBTITLE_FONT = ("Segoe UI", 11)
SECTION_TITLE_FONT = ("Segoe UI", 16, "bold")
LABEL_FONT = ("Segoe UI", 11)
ENTRY_FONT = ("Segoe UI", 13)
VALUE_FONT = ("Segoe UI", 20, "bold")
VECTOR_FONT = ("Consolas", 24, "bold")
MONO_FONT = ("Consolas", 10)


def configure_ttk() -> None:
    style = ttk.Style()
    try:
        style.theme_use("clam")
    except tk.TclError:
        pass

    style.configure("Steps.TCombobox", padding=8, fieldbackground=CARD, background=CARD, foreground=TXT)
    style.map("Steps.TCombobox", fieldbackground=[("readonly", CARD)], foreground=[("readonly", TXT)])


def create_card(parent: tk.Widget, bg: str = CARD) -> tk.Frame:
    return tk.Frame(parent, bg=bg, highlightthickness=1, highlightbackground=BORDER, bd=0)


def create_section_header(
    parent: tk.Frame, title: str, button: tuple[str, Callable[[], None]] | None = None
) -> None:
    row = tk.Frame(parent, bg=parent.cget("bg"))
    row.pack(fill="x", padx=14, pady=(12, 6))
    tk.Label(row, text=title, font=SECTION_TITLE_FONT, fg=TXT, bg=row.cget("bg")).pack(side="left")

    if button:
        create_primary_button(row, button[0], button[1], padx=14, pady=6).pack(side="right")


def create_labeled_entry(
    parent: tk.Frame, label: str, row: int, column: int, var: tk.StringVar | None = None
) -> tk.Entry:
    box = tk.Frame(parent, bg=parent.cget("bg"))
    box.grid(row=row, column=column, sticky="ew", padx=6, pady=3)
    tk.Label(box, text=label, font=LABEL_FONT, fg=MUTED, bg=box.cget("bg")).pack(anchor="w")

    field_shell = tk.Frame(
        box,
        bg=FIELD,
        highlightthickness=1,
        highlightbackground=FIELD_BORDER,
        bd=0,
    )
    field_shell.pack(fill="x", pady=(5, 0))

    entry = tk.Entry(
        field_shell,
        textvariable=var,
        bg=FIELD,
        fg=TXT,
        insertbackground=TXT,
        relief="flat",
        bd=0,
        highlightthickness=0,
        font=ENTRY_FONT,
    )
    entry.pack(fill="x", padx=10, pady=8)
    entry.bind("<FocusIn>", lambda _event: field_shell.config(highlightbackground=ACTIVE))
    entry.bind("<FocusOut>", lambda _event: field_shell.config(highlightbackground=FIELD_BORDER))
    return entry


def create_primary_button(
    parent: tk.Widget, text: str, command: Callable[[], None], padx: int = 16, pady: int = 10
) -> tk.Button:
    return tk.Button(
        parent,
        text=text,
        command=command,
        bg=PINK,
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
