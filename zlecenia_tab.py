import tkinter as tk
from tkinter import ttk, messagebox
from supabase_client import supabase

TABELA = "zlecenia"

COLUMNS = [
    "numer_zlecenia", "nazwa_zleceniodawcy", "data_zaladunku", "miejsce_zaladunku",
    "clo", "wymiar_towaru", "ldm", "waga", "miejsce_rozladunku",
    "data_rozladunku", "cena"
]

FRIENDLY_NAMES = {
    "numer_zlecenia": "Numer zlecenia",
    "nazwa_zleceniodawcy": "Nazwa zleceniodawcy",
    "data_zaladunku": "Data załadunku",
    "miejsce_zaladunku": "Miejsce załadunku",
    "clo": "Cło",
    "wymiar_towaru": "Wymiar towaru",
    "ldm": "LDM",
    "waga": "Waga",
    "miejsce_rozladunku": "Miejsce rozładunku",
    "data_rozladunku": "Data rozładunku",
    "cena": "Cena"
}

class ZleceniaTab(tk.Frame):
    def __init__(self, parent, transport_tab=None):
        super().__init__(parent)
        self.entries = {}
        self.selected_id = None
        self.transport_tab = transport_tab
        self.formularz_edytowany = False

        self.tworz_formularz()
        self.odswiez_tabele()
        self.after(10000, self.auto_odswiez_tabele)

    def tworz_formularz(self):
        content = tk.Frame(self, padx=10, pady=10)
        content.pack(fill="both", expand=True)

        self.frame_form = tk.Frame(content)
        self.frame_form.pack(pady=5)

        cols = 4
        rows_per_col = 3

        for idx, col_name in enumerate(COLUMNS):
            col = idx // rows_per_col
            row = idx % rows_per_col

            tk.Label(self.frame_form, text=FRIENDLY_NAMES.get(col_name, col_name)).grid(row=row*2, column=col, sticky="ew", pady=(5,0), padx=10)
            entry = tk.Entry(self.frame_form, width=30, justify='center')
            entry.bind("<Key>", lambda event: self.oznacz_edytowanie())  # 👈 dodaj reakcję na klawisze
            entry.grid(row=row*2+1, column=col, pady=(0,5), sticky="ew", padx=10)
            self.entries[col_name] = entry
            
        # ➕ Dodaj 5. kolumnę – Typ zlecenia (Eksport/Import)
        typ_label = tk.Label(self.frame_form, text="Typ zlecenia")
        typ_label.grid(row=0, column=4, sticky="ew", pady=(5, 0), padx=10)

        typ_frame = tk.Frame(self.frame_form)
        typ_frame.grid(row=1, column=4, pady=(0, 5), padx=10)

        self.typ_var = tk.StringVar(value="export")
        tk.Radiobutton(typ_frame, text="Eksport", variable=self.typ_var, value="export").pack(side="left", padx=(0, 5))
        tk.Radiobutton(typ_frame, text="Import", variable=self.typ_var, value="import").pack(side="left", padx=(5, 0))

        for col in range(cols):
            self.frame_form.grid_columnconfigure(col, weight=1)

        self.frame_buttons = tk.Frame(content)
        self.frame_buttons.pack(pady=(0, 15))

        tk.Button(self.frame_buttons, text="Dodaj zlecenie", width=15, command=self.dodaj_zlecenie).grid(row=0, column=0, padx=5)
        tk.Button(self.frame_buttons, text="Edytuj zlecenie", width=15, command=self.edytuj_zlecenie).grid(row=0, column=1, padx=5)
        tk.Button(self.frame_buttons, text="Zapisz zmiany", width=15, command=self.zapisz_zlecenie).grid(row=0, column=2, padx=5)
        tk.Button(self.frame_buttons, text="Usuń zlecenie", width=15, command=self.usun_zlecenie).grid(row=0, column=3, padx=5)

        # 👇 DODAJEMY TABELĘ DO TEGO SAMEGO `content`
        table_frame = tk.Frame(content)
        table_frame.pack(fill="both", expand=True)

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical")
        scrollbar.pack(side="right", fill="y")

        self.tree = ttk.Treeview(table_frame, columns=COLUMNS, show="headings", height=25, yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.tree.yview)
        self.tree.pack(fill="both", expand=True)

        KOLUMNY_Z_SZEROKOSCIA = [
            ("numer_zlecenia", 90),
            ("nazwa_zleceniodawcy", 100),
            ("data_zaladunku", 130),
            ("miejsce_zaladunku", 120),
            ("clo", 100),
            ("wymiar_towaru", 150),
            ("ldm", 50),
            ("waga", 50),
            ("miejsce_rozladunku", 120),
            ("data_rozladunku", 130),
            ("cena", 40)
        ]

        for col, szerokosc in KOLUMNY_Z_SZEROKOSCIA:
            self.tree.heading(col, text=FRIENDLY_NAMES.get(col, col))
            self.tree.column(col, width=szerokosc, anchor='center')

        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)

    def odswiez_tabele(self):
        if self.formularz_edytowany:
            print("⏸️ Pominięto odświeżenie – trwa edycja formularza")
            return
        try:
            response = supabase.table(TABELA).select("*").execute()
            data = response.data
        except Exception as e:
            messagebox.showerror("Błąd", f"Nie można pobrać danych z Supabase:\n{e}")
            return

        # 🔒 Zapamiętaj zaznaczenie
        previously_selected = self.tree.selection()
        previously_selected_id = previously_selected[0] if previously_selected else None

        self.tree.delete(*self.tree.get_children())
        for zlecenie in data:
            lp = zlecenie.get("lp")
            if not isinstance(lp, int) or lp <= 0:
                continue
            values = [zlecenie.get(col, "") for col in COLUMNS]
            self.tree.insert("", "end", iid=str(lp), values=values)

        # 🔁 Przywróć zaznaczenie i zawartość formularza
        if previously_selected_id and self.tree.exists(previously_selected_id):
            self.tree.selection_set(previously_selected_id)
            self.tree.see(previously_selected_id)
            self.selected_id = previously_selected_id
            # 🔄 Odśwież formularz z danymi zaznaczonego wiersza
            values = self.tree.item(previously_selected_id, "values")
            for col, val in zip(COLUMNS, values):
                self.entries[col].delete(0, tk.END)
                self.entries[col].insert(0, val)
        else:
            self.selected_id = None
            # Czyścić formularz tylko, jeśli był pusty
            formularz_pusty = all(entry.get().strip() == "" for entry in self.entries.values())
            if formularz_pusty:
                self.czysc_formularz()

        if self.transport_tab:
            self.transport_tab.aktualizuj_tabele_zlecen(data)

    def dodaj_zlecenie(self):
        print("➡️ Kliknięto DODAJ ZLECENIE")
        dane = {col: self.entries[col].get() for col in COLUMNS}
        dane["typ"] = self.typ_var.get()
        if not dane["numer_zlecenia"] or not dane["nazwa_zleceniodawcy"]:
            messagebox.showwarning("Brak danych", "Wprowadź numer zlecenia i nazwę zleceniodawcy.")
            return
        try:
            # Pobierz najwyższe LP i nadaj nowe
            res = supabase.table(TABELA).select("lp").order("lp", desc=True).limit(1).execute()
            max_lp = res.data[0]["lp"] if res.data else 0
            dane["lp"] = max_lp + 1

            supabase.table(TABELA).insert(dane).execute()
            messagebox.showinfo("Sukces", "Zlecenie dodane.")
            self.after(1000, self.odswiez_zlecenie_po_insert, dane["lp"])
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

        # 🧠 Ustaw typ zlecenia w formularzu (jeśli istnieje)
        try:
            response = supabase.table(TABELA).select("typ").eq("lp", self.selected_id).execute()
            if response.data and "typ" in response.data[0]:
                self.typ_var.set(response.data[0]["typ"])
            else:
                self.typ_var.set("export")
        except Exception:
            self.typ_var.set("export")

    def edytuj_zlecenie(self):
        if not self.selected_id:
            messagebox.showwarning("Brak zaznaczenia", "Wybierz zlecenie do edycji.")
            return

        dane = {col: self.entries[col].get() for col in COLUMNS}
        dane["typ"] = self.typ_var.get()
        dane["lp"] = int(self.selected_id)

        try:
            supabase.table(TABELA).update(dane).eq("lp", dane["lp"]).execute()
            messagebox.showinfo("Sukces", "Zlecenie zaktualizowane.")
            self.formularz_edytowany = False
            self.odswiez_tabele()
        except Exception as e:
            messagebox.showerror("Błąd", f"Nie można edytować zlecenia:\n{e}")

    def zapisz_zlecenie(self):
        if not self.selected_id:
            messagebox.showwarning("Brak zaznaczenia", "Najpierw wybierz zlecenie do edycji.")
            return

        dane = {col: self.entries[col].get() for col in COLUMNS}
        dane["typ"] = self.typ_var.get()
        dane["lp"] = int(self.selected_id)

        try:
            supabase.table(TABELA).update(dane).eq("lp", dane["lp"]).execute()
            messagebox.showinfo("Sukces", "Zlecenie zaktualizowane.")
            self.formularz_edytowany = False
            self.odswiez_tabele()
        except Exception as e:
            messagebox.showerror("Błąd", f"Nie można zapisać zmian:\n{e}")

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
           
    def oznacz_edytowanie(self):
        self.formularz_edytowany = True

    def auto_odswiez_tabele(self):
        try:
            self.odswiez_tabele()
            print("🔄 Automatyczne odświeżenie zleceń")
        except Exception as e:
            print("❌ Błąd automatycznego odświeżania:", e)
        finally:
            self.after(10000, self.auto_odswiez_tabele)
            
    def odswiez_zlecenie_po_insert(self, lp_nowego):
        try:
            response = supabase.table(TABELA).select("*").eq("lp", lp_nowego).execute()
            if response.data:
                print("✅ Nowe zlecenie już widoczne – odświeżamy tabelę")
                self.formularz_edytowany = False
                self.odswiez_tabele()
            else:
                print("⏳ Nowe zlecenie jeszcze niewidoczne – ponawiamy za 1 sekundę")
                self.after(1000, self.odswiez_zlecenie_po_insert, lp_nowego)
        except Exception as e:
            print("❌ Błąd sprawdzania nowego zlecenia:", e)