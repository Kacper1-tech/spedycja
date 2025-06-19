import tkinter as tk
from tkinter import ttk, messagebox

from supabase_client import supabase
TABLE_NAME = "kierowcy"

class KierowcyTab(ttk.Frame):
    def __init__(self, master, lp_counter, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.lp_counter = lp_counter
        self.selected_item = None
        self.editing = False 

        self.imie_nazwisko_var = tk.StringVar()
        self.tel_sluzbowy_var = tk.StringVar()
        self.tel_prywatny_var = tk.StringVar()
        self.dowod_var = tk.StringVar()

        self.create_widgets()
        self.load_from_server()
        self.after(10000, self.auto_odswiez_kierowcow)  # Odświeżanie co 10 sek.

    def create_widgets(self):
        content = ttk.Frame(self, padding=10)
        content.pack(fill="both", expand=True)

        form_wrapper = ttk.Frame(content)
        form_wrapper.pack(fill="x", anchor="n", pady=5)

        form_frame = ttk.Frame(form_wrapper, padding=5)
        form_frame.pack()

        def create_field(label, var, row, col):
            ttk.Label(form_frame, text=label + ":").grid(row=row, column=col * 2, sticky="e", padx=5, pady=2)
            ttk.Entry(form_frame, textvariable=var, width=30).grid(row=row, column=col * 2 + 1, sticky="w", padx=5, pady=2)

        create_field("Imię i nazwisko", self.imie_nazwisko_var, 0, 0)
        create_field("Telefon służbowy", self.tel_sluzbowy_var, 0, 1)
        create_field("Telefon prywatny", self.tel_prywatny_var, 1, 0)
        create_field("Nr dowodu osobistego", self.dowod_var, 1, 1)

        btn_frame = ttk.Frame(content)
        btn_frame.pack(pady=10)

        ttk.Button(btn_frame, text="Dodaj kierowcę", command=self.dodaj).grid(row=0, column=0, padx=5)
        ttk.Button(btn_frame, text="Edytuj", command=self.edytuj).grid(row=0, column=1, padx=5)
        ttk.Button(btn_frame, text="Zapisz zmiany", command=self.zapisz).grid(row=0, column=2, padx=5)
        ttk.Button(btn_frame, text="Usuń zaznaczonego", command=self.usun).grid(row=0, column=3, padx=5)

        table_frame = ttk.Frame(content)
        table_frame.pack(fill="both", expand=True)

        columns = ["LP", "Imię i nazwisko", "Tel. służbowy", "Tel. prywatny", "Nr dowodu"]
        tree_scroll = ttk.Scrollbar(table_frame)
        tree_scroll.pack(side="right", fill="y")

        self.tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            yscrollcommand=tree_scroll.set,
            height=25
        )
        tree_scroll.config(command=self.tree.yview)
        self.tree.pack(fill="both", expand=True)

        for col in columns:
            self.tree.heading(col, text=col)
            if col == "LP":
                self.tree.column(col, anchor="center", width=50, stretch=False)
            else:
                self.tree.column(col, anchor="center", width=120)

    def load_from_server(self):
        try:
            response = supabase.table(TABLE_NAME).select("*").execute()
            data = response.data

            self.tree.delete(*self.tree.get_children())
            max_lp = 0

            for row in data:
                values = (
                    row.get("lp", ""),
                    row.get("imie_nazwisko", ""),
                    row.get("tel_sluzbowy", ""),
                    row.get("tel_prywatny", ""),
                    row.get("nr_dowodu", "")
                )
                self.tree.insert("", "end", values=values)

                try:
                    max_lp = max(max_lp, int(row.get("lp", 0)))
                except Exception:
                    pass

            if self.lp_counter is not None:
                self.lp_counter["kierowcy"] = max_lp + 1

        except Exception as e:
            messagebox.showerror("Błąd", f"Nie można wczytać danych z Supabase:\n{e}")

    def dodaj(self):
        imie_nazwisko = self.imie_nazwisko_var.get().strip()
        tel_sluzbowy = self.tel_sluzbowy_var.get().strip()
        tel_prywatny = self.tel_prywatny_var.get().strip()
        dowod = self.dowod_var.get().strip()

        if not all([imie_nazwisko, tel_sluzbowy, tel_prywatny, dowod]):
            messagebox.showwarning("Błąd", "Wypełnij wszystkie pola.")
            return

        lp = self.lp_counter.get("kierowcy", 1)
        data = {
            "lp": lp,
            "imie_nazwisko": imie_nazwisko,
            "tel_sluzbowy": tel_sluzbowy,
            "tel_prywatny": tel_prywatny,
            "nr_dowodu": dowod
        }

        try:
            supabase.table(TABLE_NAME).insert(data).execute()
            self.lp_counter["kierowcy"] = lp + 1
            self.load_from_server()
            self.czysc()
        except Exception as e:
            messagebox.showerror("Błąd", f"Nie można dodać kierowcy:\n{e}")

    def edytuj(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Błąd", "Zaznacz wiersz do edycji.")
            return
        item = selected[0]
        self.selected_item = item
        values = self.tree.item(item, "values")
        self.imie_nazwisko_var.set(values[1])
        self.tel_sluzbowy_var.set(values[2])
        self.tel_prywatny_var.set(values[3])
        self.dowod_var.set(values[4])
        self.editing = True 

    def zapisz(self):
        if not self.selected_item:
            return
        values = self.tree.item(self.selected_item, "values")
        data = {
            "lp": values[0],
            "imie_nazwisko": self.imie_nazwisko_var.get(),
            "tel_sluzbowy": self.tel_sluzbowy_var.get(),
            "tel_prywatny": self.tel_prywatny_var.get(),
            "nr_dowodu": self.dowod_var.get()
        }
        try:
            supabase.table(TABLE_NAME).update(data).eq("lp", data["lp"]).execute()
            self.selected_item = None
            self.editing = False
            self.load_from_server()
            self.czysc()
        except Exception as e:
            messagebox.showerror("Błąd", f"Nie można zapisać zmian:\n{e}")

    def usun(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Błąd", "Zaznacz kierowcę do usunięcia.")
            return
        if not messagebox.askyesno("Potwierdzenie", "Czy na pewno chcesz usunąć zaznaczonego kierowcę?"):
            return
        try:
            for item in selected:
                values = self.tree.item(item, "values")
                lp = values[0]
                supabase.table(TABLE_NAME).delete().eq("lp", lp).execute()
            self.load_from_server()
        except Exception as e:
            messagebox.showerror("Błąd", f"Nie można usunąć kierowcy:\n{e}")

    def czysc(self):
        self.imie_nazwisko_var.set("")
        self.tel_sluzbowy_var.set("")
        self.tel_prywatny_var.set("")
        self.dowod_var.set("")

    def auto_odswiez_kierowcow(self):
        if self.editing:
            print("⏸️ Pominięto odświeżenie – trwa edycja kierowcy")
            self.after(10000, self.auto_odswiez_kierowcow)
            return
        try:
            response = supabase.table(TABLE_NAME).select("*").execute()
            data = response.data

            self.tree.delete(*self.tree.get_children())
            max_lp = 0

            for row in data:
                values = (
                    row.get("lp", ""),
                    row.get("imie_nazwisko", ""),
                    row.get("tel_sluzbowy", ""),
                    row.get("tel_prywatny", ""),
                    row.get("nr_dowodu", "")
                )
                self.tree.insert("", "end", values=values)

                try:
                    max_lp = max(max_lp, int(row.get("lp", 0)))
                except Exception:
                    pass

            if self.lp_counter is not None:
                self.lp_counter["kierowcy"] = max_lp + 1

            print("🔄 Automatyczne odświeżenie kierowców")
        except Exception as e:
            print("❌ Błąd auto-odświeżania kierowców:", e)
        finally:
            self.after(10000, self.auto_odswiez_kierowcow)
