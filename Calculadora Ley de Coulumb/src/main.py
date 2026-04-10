import tkinter as tk

from ui.app import AplicacionCoulomb

if __name__ == "__main__":
    raiz = tk.Tk()
    aplicacion = AplicacionCoulomb(raiz)
    raiz.mainloop()
