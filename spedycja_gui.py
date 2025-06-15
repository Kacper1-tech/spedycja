import os
import sys
import tkinter as tk
import subprocess
import time
import requests
from tkinter import ttk

from naczepy_tab import NaczepyTab
from ciezarowki_tab import CiezarowkiTab
from kierowcy_tab import KierowcyTab
from transport_tab import TransportTab
from zlecenia_tab import ZleceniaTab
from kontrahenci_tab import KontrahenciTab

class SpedycjaApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Program Spedycyjny")
        self.state("zoomed")

        self.lp_counter = {
            "naczepy": 1,
            "ciezarowki": 1,
            "kierowcy": 1,
            "kontrahenci": 1,
            "zlecenia": 1,
            "transport": 1
        }

        self.kontrahenci_lista = []
        self.zlecenia_lista = []

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill='both', expand=True)

        # Dodawanie zakładek z obsługą błędów
        try:
            print("🔄 Ładowanie zakładki: Transport")
            self.transport_tab = TransportTab(self.notebook, self.lp_counter, self.zlecenia_lista)
            self.notebook.add(self.transport_tab, text="Transport")
        except Exception as e:
            print("❌ Błąd w zakładce Transport:", e)

        try:
            print("🔄 Ładowanie zakładki: Zlecenia")
            self.zlecenia_tab = ZleceniaTab(self.notebook, transport_tab=self.transport_tab)
            self.notebook.add(self.zlecenia_tab, text="Zlecenia")
        except Exception as e:
            print("❌ Błąd w zakładce Zlecenia:", e)

        try:
            print("🔄 Ładowanie zakładki: Kontrahenci")
            self.kontrahenci_tab = KontrahenciTab(self.notebook, lp_counter=self.lp_counter)
            self.notebook.add(self.kontrahenci_tab, text="Kontrahenci")
        except Exception as e:
            print("❌ Błąd w zakładce Kontrahenci:", e)

        try:
            print("🔄 Ładowanie zakładki: Kierowcy")
            self.kierowcy_tab = KierowcyTab(self.notebook, self.lp_counter)
            self.notebook.add(self.kierowcy_tab, text="Kierowcy")
        except Exception as e:
            print("❌ Błąd w zakładce Kierowcy:", e)

        try:
            print("🔄 Ładowanie zakładki: Ciężarówki")
            self.ciezarowki_tab = CiezarowkiTab(self.notebook, self.lp_counter)
            self.notebook.add(self.ciezarowki_tab, text="Ciężarówki")
        except Exception as e:
            print("❌ Błąd w zakładce Ciężarówki:", e)

        try:
            print("🔄 Ładowanie zakładki: Naczepy")
            self.naczepy_tab = NaczepyTab(self.notebook, self.lp_counter)
            self.notebook.add(self.naczepy_tab, text="Naczepy")
        except Exception as e:
            print("❌ Błąd w zakładce Naczepy:", e)


if __name__ == "__main__":
    app = SpedycjaApp()
    app.mainloop()

