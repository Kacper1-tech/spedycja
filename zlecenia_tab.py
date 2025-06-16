import tkinter as tk
from tkinter import ttk, messagebox
from supabase_client import supabase

TABELA = "zlecenia"

COLUMNS = [
    "Numer zlecenia", "Nazwa zleceniodawcy", "Data załadunku", "Miejsce załadunku",
    "Cło", "Wymiar towaru", "LDM", "Waga", "Miejsce rozładunku",
    "Data rozładunku", "Cena"
]

class ZleceniaTab(tk.Frame):
    def __init__(self, parent, transport_tab=None):
        super().__init__(parent)
        self.entries = {}
        self.selected_id = None
        self.transport_tab = transport_tab

        self.tworz_formularz()
        self.tworz_tabele()
        self.odswiez_tabele()
        self.after(10000, self.auto_odswiez_tabele)

    def tworz_formularz(self):
        self.frame_form = tk.Frame(self)
        self.frame_form.pack(padx=10, pady=10)

        cols = 4
        rows_per_col = 3

        for idx, col_name in enumerate(COLUMNS):
            col = idx // rows_per_col
            row = idx % rows_per_col

            tk.Label(self.frame_form, text=col_name).grid(row=row*2, column=col, sticky="ew", pady=(5,0), padx=10)
            entry = tk.Entry(self.frame_form, width=30, justify='center')
            entry.grid(row=row*2+1, column=col, pady=(0,5), sticky="ew", padx=10)
            self.entries[col_name] = entry

        for col in range(cols):
            self.frame_form.grid_columnconfigure(col, weight=1)

        self.frame_buttons = tk.Frame(self)
        self.frame_buttons.pack(padx=10, pady=(0,15))

        tk.Button(self.frame_buttons, text="Dodaj zlecenie", width=15, command=self.dodaj_zlecenie).grid(row=0, column=0, padx=5)
        tk.Button(self.frame_buttons, text="Edytuj zlecenie", width=15, command=self.edytuj_zlecenie).grid(row=0, column=1, padx=5)
        tk.Button(self.frame_buttons, text="Usuń zlecenie", width=15, command=self.usun_zlecenie).grid(row=0, column=2, padx=5)

    def tworz_tabele(self):
        self.tree = ttk.Treeview(self, columns=COLUMNS, show="headings", height=10)
        for col in COLUMNS:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120, anchor='center')
        self.tree.pack(padx=10, pady=5, fill="both", expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)

    def odswiez_tabele(self):
        try:
            response = supabase.table(TABELA).select("*").execute()
            data = response.data
        except Exception as e:
            messagebox.showerror("Błąd", f"Nie można pobrać danych z Supabase:\n{e}")
            return

        self.tree.delete(*self.tree.get_children())
        for zlecenie in data:
            lp = zlecenie.get("lp")
            if not isinstance(lp, int) or lp <= 0:
                continue
            values = [zlecenie.get(col, "") for col in COLUMNS]
            self.tree.insert("", "end", iid=str(lp), values=values)

        self.selected_id = None
        self.czysc_formularz()

        if self.transport_tab:
            self.transport_tab.aktualizuj_tabele_zlecen(data)

    def dodaj_zlecenie(self):
        dane = {col: self.entries[col].get() for col in COLUMNS}
        if not dane["Numer zlecenia"] or not dane["Nazwa zleceniodawcy"]:
            messagebox.showwarning("Brak danych", "Wprowadź numer zlecenia i nazwę zleceniodawcy.")
            return
        try:
            # Pobierz najwyższe LP i nadaj nowe
            res = supabase.table(TABELA).select("lp").order("lp", desc=True).limit(1).execute()
            max_lp = res.data[0]["lp"] if res.data else 0
            dane["lp"] = max_lp + 1

            supabase.table(TABELA).insert(dane).execute()
            messagebox.showinfo("Sukces", "Zlecenie dodane.")
            self.odswiez_tabele()
        except Exception as e:
            messagebox.showerror("Błąd", f"Nie można dodać zlecenia:\n{e}")

    def on_tree_select(self, event):
        selected = self.tree.selection()
        if selected:
            self.selected_id = selected[0]
            values = self.tree.item(self.selected_id, "values")
            for col, val in zip(COLUMNS, values):
                self.entries[col].delete(0, tk.END)
                self.entries[col].insert(0, val)
        else:
            self.selected_id = None
            self.czysc_formularz()

    def edytuj_zlecenie(self):
        if not self.selected_id:
            messagebox.showwarning("Brak zaznaczenia", "Wybierz zlecenie do edycji.")
            return

        dane = {col: self.entries[col].get() for col in COLUMNS}
        dane["lp"] = int(self.selected_id)

        try:
            supabase.table(TABELA).update(dane).eq("lp", dane["lp"]).execute()
            messagebox.showinfo("Sukces", "Zlecenie zaktualizowane.")
            self.odswiez_tabele()
        except Exception as e:
            messagebox.showerror("Błąd", f"Nie można edytować zlecenia:\n{e}")

    def usun_zlecenie(self):
        if not self.selected_id:
            messagebox.showwarning("Brak zaznaczenia", "Wybierz zlecenie do usunięcia.")
            return

        if messagebox.askyesno("Potwierdzenie", "Czy na pewno chcesz usunąć zlecenie?"):
            try:
                supabase.table(TABELA).delete().eq("lp", self.selected_id).execute()
                messagebox.showinfo("Sukces", "Zlecenie usunięte.")
                self.odswiez_tabele()
            except Exception as e:
                messagebox.showerror("Błąd", f"Nie można usunąć zlecenia:\n{e}")

    def czysc_formularz(self):
        for entry in self.entries.values():
            entry.delete(0, tk.END)

    def auto_odswiez_tabele(self):
        try:
            self.odswiez_tabele()
            print("🔄 Automatyczne odświeżenie zleceń")
        except Exception as e:
            print("❌ Błąd automatycznego odświeżania:", e)
        finally:
            self.after(10000, self.auto_odswiez_tabele)
