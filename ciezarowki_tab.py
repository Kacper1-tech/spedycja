import tkinter as tk
from tkinter import ttk, messagebox
import requests

API_URL = 'https://spedycja.onrender.com/ciezarowki'

class CiezarowkiTab(ttk.Frame):
    def __init__(self, master, lp_counter, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.lp_counter = lp_counter
        self.selected_item = None

        self.rej_var = tk.StringVar()
        self.marka_var = tk.StringVar()
        self.model_var = tk.StringVar()
        self.vin_var = tk.StringVar()
        self.przeglad_var = tk.StringVar()
        self.ubezpieczenie_var = tk.StringVar()
        self.poj_l_var = tk.StringVar()
        self.poj_p_var = tk.StringVar()

        self.create_widgets()
        self.load_from_server()
        self.after(10000, self.auto_odswiez_ciezarowki)  # Odświeżanie co 10 sek.

    def create_widgets(self):
        form_wrapper = ttk.Frame(self)
        form_wrapper.pack(fill="x", anchor="n", pady=10)

        form_frame = ttk.Frame(form_wrapper, padding=20)
        form_frame.pack()

        def create_field(label, var, row, col):
            ttk.Label(form_frame, text=label + ":").grid(row=row, column=col * 2, sticky="e", padx=5, pady=2)
            ttk.Entry(form_frame, textvariable=var, width=30).grid(row=row, column=col * 2 + 1, sticky="w", padx=5, pady=2)

        # Układ: 2 rzędy, 4 kolumny
        create_field("Rejestracja", self.rej_var, 0, 0)
        create_field("Marka", self.marka_var, 0, 1)
        create_field("Model", self.model_var, 0, 2)
        create_field("Nr VIN", self.vin_var, 0, 3)
        create_field("Data przeglądu", self.przeglad_var, 1, 0)
        create_field("Data ubezpieczenia", self.ubezpieczenie_var, 1, 1)
        create_field("Poj. L baku", self.poj_l_var, 1, 2)
        create_field("Poj. P baku", self.poj_p_var, 1, 3)

        btn_frame = ttk.Frame(self)
        btn_frame.pack(pady=10)

        ttk.Button(btn_frame, text="Dodaj ciężarówkę", command=self.dodaj).grid(row=0, column=0, padx=5)
        ttk.Button(btn_frame, text="Edytuj", command=self.edytuj).grid(row=0, column=1, padx=5)
        ttk.Button(btn_frame, text="Zapisz zmiany", command=self.zapisz).grid(row=0, column=2, padx=5)
        ttk.Button(btn_frame, text="Usuń zaznaczoną", command=self.usun).grid(row=0, column=3, padx=5)

        table_frame = ttk.Frame(self)
        table_frame.pack(fill="both", expand=True)

        columns = ["LP", "Rejestracja", "Marka", "Model", "VIN", "Przegląd", "Ubezpieczenie", "Poj. L", "Poj. P"]
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=10)

        tree_scroll = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=tree_scroll.set)
        tree_scroll.pack(side="right", fill="y")
        self.tree.pack(fill="both", expand=True)

        for col in columns:
            self.tree.heading(col, text=col)
            width = 60 if col == "LP" else 120
            self.tree.column(col, anchor="center", width=width)

    def load_from_server(self):
        try:
            response = requests.get(API_URL)
            response.raise_for_status()
            data = response.json()

            self.tree.delete(*self.tree.get_children())
            max_lp = 0

            for row in data:
                if not isinstance(row, dict):
                    continue
                values = (
                    row.get("lp", ""),
                    row.get("rejestracja", ""),
                    row.get("marka", ""),
                    row.get("model", ""),
                    row.get("vin", ""),
                    row.get("przeglad", ""),
                    row.get("ubezpieczenie", ""),
                    row.get("poj_l", ""),
                    row.get("poj_p", "")
                )
                self.tree.insert("", "end", values=values)

                try:
                    max_lp = max(max_lp, int(row.get("lp", 0)))
                except Exception:
                    pass

            self.lp_counter["ciezarowki"] = max_lp + 1

        except Exception as e:
            messagebox.showerror("Błąd", f"Nie można wczytać danych z serwera:\n{e}")

    def dodaj(self):
        if not all([self.rej_var.get(), self.marka_var.get(), self.model_var.get(), self.vin_var.get(),
                    self.przeglad_var.get(), self.ubezpieczenie_var.get(), self.poj_l_var.get(), self.poj_p_var.get()]):
            messagebox.showwarning("Błąd", "Wszystkie pola muszą być wypełnione.")
            return
        lp = self.lp_counter.get("ciezarowki", 1)
        data = {
            "lp": lp,
            "rejestracja": self.rej_var.get(),
            "marka": self.marka_var.get(),
            "model": self.model_var.get(),
            "vin": self.vin_var.get(),
            "przeglad": self.przeglad_var.get(),
            "ubezpieczenie": self.ubezpieczenie_var.get(),
            "poj_l": self.poj_l_var.get(),
            "poj_p": self.poj_p_var.get(),
        }
        try:
            response = requests.post(API_URL, json=data)
            response.raise_for_status()
            self.lp_counter["ciezarowki"] = lp + 1
            self.load_from_server()
            self.czysc()
        except Exception as e:
            messagebox.showerror("Błąd", f"Nie można dodać ciężarówki:\n{e}")

    def edytuj(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Błąd", "Zaznacz wiersz do edycji.")
            return
        item = selected[0]
        self.selected_item = item
        values = self.tree.item(item, "values")
        self.rej_var.set(values[1])
        self.marka_var.set(values[2])
        self.model_var.set(values[3])
        self.vin_var.set(values[4])
        self.przeglad_var.set(values[5])
        self.ubezpieczenie_var.set(values[6])
        self.poj_l_var.set(values[7])
        self.poj_p_var.set(values[8])

    def zapisz(self):
        if not self.selected_item:
            return
        values = self.tree.item(self.selected_item, "values")
        data = {
            "lp": values[0],
            "rejestracja": self.rej_var.get(),
            "marka": self.marka_var.get(),
            "model": self.model_var.get(),
            "vin": self.vin_var.get(),
            "przeglad": self.przeglad_var.get(),
            "ubezpieczenie": self.ubezpieczenie_var.get(),
            "poj_l": self.poj_l_var.get(),
            "poj_p": self.poj_p_var.get(),
        }
        try:
            url = f"{API_URL}/{data['lp']}"
            response = requests.put(url, json=data)
            response.raise_for_status()
            self.selected_item = None
            self.load_from_server()
            self.czysc()
        except Exception as e:
            messagebox.showerror("Błąd", f"Nie można zapisać zmian:\n{e}")

    def usun(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Błąd", "Zaznacz ciężarówkę do usunięcia.")
            return
        if not messagebox.askyesno("Potwierdzenie", "Czy na pewno chcesz usunąć zaznaczoną ciężarówkę?"):
            return
        try:
            for item in selected:
                values = self.tree.item(item, "values")
                lp = values[0]
                url = f"{API_URL}/{lp}"
                response = requests.delete(url)
                response.raise_for_status()
            self.load_from_server()
        except Exception as e:
            messagebox.showerror("Błąd", f"Nie można usunąć ciężarówki:\n{e}")

    def czysc(self):
        for var in [self.rej_var, self.marka_var, self.model_var, self.vin_var,
                    self.przeglad_var, self.ubezpieczenie_var, self.poj_l_var, self.poj_p_var]:
            var.set("")

    def auto_odswiez_ciezarowki(self):
        try:
            response = requests.get(API_URL)
            response.raise_for_status()
            data = response.json()

            self.tree.delete(*self.tree.get_children())
            max_lp = 0

            for row in data:
                if not isinstance(row, dict):
                    continue
                values = (
                    row.get("lp", ""),
                    row.get("rejestracja", ""),
                    row.get("marka", ""),
                    row.get("model", ""),
                    row.get("vin", ""),
                    row.get("przeglad", ""),
                    row.get("ubezpieczenie", ""),
                    row.get("poj_l", ""),
                    row.get("poj_p", "")
                )
                self.tree.insert("", "end", values=values)

                try:
                    max_lp = max(max_lp, int(row.get("lp", 0)))
                except Exception:
                    pass

            self.lp_counter["ciezarowki"] = max_lp + 1

            print("🔄 Automatyczne odświeżenie ciężarówek")
        except Exception as e:
            print("❌ Błąd auto-odświeżania ciężarówek:", e)
        finally:
            self.after(10000, self.auto_odswiez_ciezarowki)
