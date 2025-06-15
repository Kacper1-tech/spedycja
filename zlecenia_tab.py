import tkinter as tk
from tkinter import ttk, messagebox
import requests

API_URL = 'https://spedycja.onrender.com/zlecenia'  # Adres Twojego serwera Flask

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
        self.after(10000, self.auto_odswiez_tabele)  # Odświeżaj co 10 sekund


    def tworz_formularz(self):
        self.frame_form = tk.Frame(self)
        self.frame_form.pack(padx=10, pady=10)

        cols = 4
        rows_per_col = 3

        for idx, col_name in enumerate(COLUMNS):
            col = idx // rows_per_col
            row = idx % rows_per_col

            lbl = tk.Label(self.frame_form, text=col_name)
            lbl.grid(row=row*2, column=col, sticky="ew", pady=(5,0), padx=10)
            entry = tk.Entry(self.frame_form, width=30, justify='center')
            entry.grid(row=row*2+1, column=col, pady=(0,5), sticky="ew", padx=10)
            self.entries[col_name] = entry

        for col in range(cols):
            self.frame_form.grid_columnconfigure(col, weight=1)

        self.frame_buttons = tk.Frame(self)
        self.frame_buttons.pack(padx=10, pady=(0,15))

        btn_add = tk.Button(self.frame_buttons, text="Dodaj zlecenie", width=15, command=self.dodaj_zlecenie)
        btn_edit = tk.Button(self.frame_buttons, text="Edytuj zlecenie", width=15, command=self.edytuj_zlecenie)
        btn_delete = tk.Button(self.frame_buttons, text="Usuń zlecenie", width=15, command=self.usun_zlecenie)

        btn_add.grid(row=0, column=0, padx=5)
        btn_edit.grid(row=0, column=1, padx=5)
        btn_delete.grid(row=0, column=2, padx=5)

    def tworz_tabele(self):
        self.tree = ttk.Treeview(self, columns=COLUMNS, show="headings", height=10)
        for col in COLUMNS:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120, anchor='center')
        self.tree.pack(padx=10, pady=5, fill="both", expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)

    def odswiez_tabele(self):
        try:
            response = requests.get(API_URL)
            response.raise_for_status()
            data = response.json()
        except Exception as e:
            messagebox.showerror("Błąd", f"Nie można pobrać danych z serwera:\n{e}")
            data = []

        self.tree.delete(*self.tree.get_children())
        for index, zlecenie in enumerate(data):
            lp = zlecenie.get("lp")
            if not isinstance(lp, int) or lp <= 0:
                continue  # pomiń zlecenia bez poprawnego lp
            values = [zlecenie.get(col, "") for col in COLUMNS]
            iid = str(lp)
            if self.tree.exists(iid):
                self.tree.delete(iid)
            self.tree.insert("", "end", iid=iid, values=values)

        self.selected_id = None
        self.czysc_formularz()

        if self.transport_tab:
            self.transport_tab.aktualizuj_tabele_zlecen(data)

    def dodaj_zlecenie(self):
        dane = {col: self.entries[col].get() for col in COLUMNS}
        if not dane["Numer zlecenia"] or not dane["Nazwa zleceniodawcy"]:
            messagebox.showwarning("Brak danych", "Wprowadź przynajmniej numer zlecenia i nazwę zleceniodawcy.")
            return
        try:
            response = requests.post(API_URL, json=dane)
            response.raise_for_status()
            messagebox.showinfo("Sukces", "Zlecenie dodane na serwerze")
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
        if self.selected_id is None:
            messagebox.showwarning("Brak zaznaczenia", "Wybierz zlecenie do edycji.")
            return
        
        if not self.selected_id.isdigit():
            messagebox.showerror("Błąd", "To zlecenie nie może być edytowane – nie ma przypisanego ID (lp).")
            return

        dane = {col: self.entries[col].get() for col in COLUMNS}
        dane["lp"] = int(self.selected_id)  # dodaj pole lp!
        
        try:
            url = f"{API_URL}/{self.selected_id}"
            response = requests.put(url, json=dane)
            response.raise_for_status()
            messagebox.showinfo("Sukces", "Zlecenie zaktualizowane na serwerze")
            self.odswiez_tabele()
        except Exception as e:
            messagebox.showerror("Błąd", f"Nie można edytować zlecenia:\n{e}")

    def usun_zlecenie(self):
        if self.selected_id is None:
            messagebox.showwarning("Brak zaznaczenia", "Wybierz zlecenie do usunięcia.")
            return
        if not self.selected_id.isdigit():
            messagebox.showerror("Błąd", "To zlecenie nie może być usunięte – brak ID (lp).")
            return

        if messagebox.askyesno("Potwierdzenie", "Czy na pewno chcesz usunąć zaznaczone zlecenie?"):
            try:
                url = f"{API_URL}/{self.selected_id}"
                response = requests.delete(url)
                response.raise_for_status()
                messagebox.showinfo("Sukces", "Zlecenie usunięte na serwerze")
                self.odswiez_tabele()
            except Exception as e:
                messagebox.showerror("Błąd", f"Nie można usunąć zlecenia:\n{e}")

    def czysc_formularz(self):
        for entry in self.entries.values():
            entry.delete(0, tk.END)
            
    def auto_odswiez_tabele(self):
        try:
            response = requests.get(API_URL)
            response.raise_for_status()
            data = response.json()

            self.tree.delete(*self.tree.get_children())
            for index, zlecenie in enumerate(data):
                lp = zlecenie.get("lp")
                if not isinstance(lp, int) or lp <= 0:
                    continue  # pomiń zlecenia bez poprawnego lp
                values = [zlecenie.get(col, "") for col in COLUMNS]
                iid = str(lp)
                if self.tree.exists(iid):
                    self.tree.delete(iid)
                self.tree.insert("", "end", iid=iid, values=values)

            self.selected_id = None
            if self.transport_tab:
                self.transport_tab.aktualizuj_tabele_zlecen(data)
            print("🔄 Automatyczne odświeżenie zleceń")
        except Exception as e:
            print("❌ Błąd automatycznego odświeżania:", e)
        finally:
            self.after(10000, self.auto_odswiez_tabele)
