import tkinter as tk
from tkinter import ttk, messagebox
import requests

API_URL = 'https://spedycja.onrender.com/kontrahenci'

class KontrahenciTab(ttk.Frame):
    def __init__(self, master, lp_counter, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.lp_counter = lp_counter
        self.selected_item = None

        self.nazwa_var = tk.StringVar()
        self.ulica_var = tk.StringVar()
        self.kod_var = tk.StringVar()
        self.miasto_var = tk.StringVar()
        self.panstwo_var = tk.StringVar()
        self.nip_var = tk.StringVar()

        self.create_widgets()
        self.load_from_server()
        self.after(10000, self.auto_odswiez_kontrahentow)  # Odświeżanie co 10 sek.

    def create_widgets(self):
        # ➤ Ramka do wyśrodkowania formularza tylko poziomo
        form_wrapper = ttk.Frame(self)
        form_wrapper.pack(fill="x", anchor="n", pady=10)

        form_frame = ttk.Frame(form_wrapper, padding=20)
        form_frame.pack()

        def create_field(label, var, row, col):
            ttk.Label(form_frame, text=label + ":").grid(row=row, column=col * 2, sticky="e", padx=5, pady=2)
            entry = ttk.Entry(form_frame, textvariable=var, width=30)
            entry.grid(row=row, column=col * 2 + 1, sticky="w", padx=5, pady=2)
            return entry

        create_field("Nazwa firmy", self.nazwa_var, 0, 0)
        create_field("Ulica i nr", self.ulica_var, 0, 1)
        create_field("Kod pocztowy", self.kod_var, 0, 2)
        create_field("Miasto", self.miasto_var, 1, 0)
        create_field("Państwo", self.panstwo_var, 1, 1)
        create_field("NIP", self.nip_var, 1, 2)

        btn_frame = ttk.Frame(self)
        btn_frame.pack(pady=10)

        ttk.Button(btn_frame, text="Dodaj kontrahenta", command=self.dodaj).grid(row=0, column=0, padx=5)
        ttk.Button(btn_frame, text="Edytuj", command=self.edytuj).grid(row=0, column=1, padx=5)
        ttk.Button(btn_frame, text="Zapisz zmiany", command=self.zapisz).grid(row=0, column=2, padx=5)
        ttk.Button(btn_frame, text="Usuń zaznaczonego", command=self.usun).grid(row=0, column=3, padx=5)

        table_frame = ttk.Frame(self)
        table_frame.pack(fill="both", expand=True)

        columns = ["LP", "Nazwa firmy", "Ulica", "Kod", "Miasto", "Państwo", "NIP"]
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=10)

        tree_scroll = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=tree_scroll.set)
        tree_scroll.pack(side="right", fill="y")
        self.tree.pack(fill="both", expand=True)

        for col in columns:
            self.tree.heading(col, text=col)
            if col == "LP":
                self.tree.column(col, width=50, anchor="center", stretch=False)
            else:
                self.tree.column(col, width=120, anchor="center")


    def load_from_server(self):
        try:
            response = requests.get(API_URL)
            response.raise_for_status()
            data = response.json()

            self.tree.delete(*self.tree.get_children())

            for row in data:
                if isinstance(row, dict):
                    values = (
                        row.get("lp", ""),
                        row.get("nazwa", ""),
                        row.get("ulica", ""),
                        row.get("kod", ""),
                        row.get("miasto", ""),
                        row.get("panstwo", ""),
                        row.get("nip", "")
                    )
                    self.tree.insert("", "end", values=values)

            if data and self.lp_counter is not None:
                max_lp = max(int(row.get("lp", 0)) for row in data if isinstance(row, dict))
                self.lp_counter["kontrahenci"] = max_lp + 1

        except Exception as e:
            messagebox.showerror("Błąd", f"Nie można wczytać danych z serwera:\n{e}")

    def dodaj(self):
        if not self.nazwa_var.get().strip():
            messagebox.showwarning("Błąd", "Uzupełnij nazwę firmy.")
            return

        lp = self.lp_counter.get("kontrahenci", 1)
        data = {
            "lp": lp,
            "nazwa": self.nazwa_var.get(),
            "ulica": self.ulica_var.get(),
            "kod": self.kod_var.get(),
            "miasto": self.miasto_var.get(),
            "panstwo": self.panstwo_var.get(),
            "nip": self.nip_var.get()
        }

        try:
            response = requests.post(API_URL, json=data)
            response.raise_for_status()
            self.lp_counter["kontrahenci"] = lp + 1
            self.load_from_server()
            self.czysc()
        except Exception as e:
            messagebox.showerror("Błąd", f"Nie można dodać kontrahenta:\n{e}")

    def edytuj(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Błąd", "Zaznacz wiersz do edycji.")
            return
        item = selected[0]
        self.selected_item = item
        values = self.tree.item(item, "values")
        self.nazwa_var.set(values[1])
        self.ulica_var.set(values[2])
        self.kod_var.set(values[3])
        self.miasto_var.set(values[4])
        self.panstwo_var.set(values[5])
        self.nip_var.set(values[6])

    def zapisz(self):
        if not self.selected_item:
            return
        values = self.tree.item(self.selected_item, "values")
        data = {
            "lp": values[0],
            "nazwa": self.nazwa_var.get(),
            "ulica": self.ulica_var.get(),
            "kod": self.kod_var.get(),
            "miasto": self.miasto_var.get(),
            "panstwo": self.panstwo_var.get(),
            "nip": self.nip_var.get()
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
            messagebox.showwarning("Błąd", "Zaznacz kontrahenta do usunięcia.")
            return
        if not messagebox.askyesno("Potwierdzenie", "Czy na pewno chcesz usunąć zaznaczonego kontrahenta?"):
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
            messagebox.showerror("Błąd", f"Nie można usunąć kontrahenta:\n{e}")

    def czysc(self):
        self.nazwa_var.set("")
        self.ulica_var.set("")
        self.kod_var.set("")
        self.miasto_var.set("")
        self.panstwo_var.set("")
        self.nip_var.set("")
        
    def auto_odswiez_kontrahentow(self):
        try:
            response = requests.get(API_URL)
            response.raise_for_status()
            data = response.json()

            self.tree.delete(*self.tree.get_children())

            for row in data:
                if isinstance(row, dict):
                    values = (
                        row.get("lp", ""),
                        row.get("nazwa", ""),
                        row.get("ulica", ""),
                        row.get("kod", ""),
                        row.get("miasto", ""),
                        row.get("panstwo", ""),
                        row.get("nip", "")
                    )
                    self.tree.insert("", "end", values=values)

            if data and self.lp_counter is not None:
                max_lp = max(int(row.get("lp", 0)) for row in data if isinstance(row, dict))
                self.lp_counter["kontrahenci"] = max_lp + 1

            print("🔄 Automatyczne odświeżenie kontrahentów")
        except Exception as e:
            print("❌ Błąd auto-odświeżania kontrahentów:", e)
        finally:
            self.after(10000, self.auto_odswiez_kontrahentow)

