import tkinter as tk
from tkinter import ttk, messagebox
import requests

API_URL = 'https://spedycja.onrender.com/transport'  # Adres Twojego serwera Flask

class TransportTab(ttk.Frame):
    def __init__(self, master, lp_counter, zlecenia_lista, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.lp_counter = lp_counter
        self.zlecenia_lista = zlecenia_lista

        # GUI — pola i przyciski
        fields_frame = ttk.Frame(self)
        fields_frame.pack(fill="x", pady=10)
        fields_frame.columnconfigure((0, 1, 2, 3), weight=1)

        col1 = ttk.Frame(fields_frame)
        col1.grid(row=0, column=0, padx=20, sticky="n")
        ttk.Label(col1, text="Kierowca:").grid(row=0, column=0, sticky="w")
        self.kierowca_entry = ttk.Entry(col1, width=18)
        self.kierowca_entry.grid(row=0, column=1, padx=5, pady=2)
        ttk.Button(col1, text="Dodaj", command=self.dodaj_transport_z_kierowca).grid(row=0, column=2)
        ttk.Label(col1, text="Edytuj kierowcę:").grid(row=1, column=0, sticky="w")
        self.kierowca_input = ttk.Entry(col1, width=18)
        self.kierowca_input.grid(row=1, column=1, padx=5, pady=2)
        ttk.Button(col1, text="Zapisz", command=self.aktualizuj_kierowce).grid(row=1, column=2)

        col2 = ttk.Frame(fields_frame)
        col2.grid(row=0, column=1, padx=20, sticky="n")
        ttk.Label(col2, text="Export:").grid(row=0, column=0, sticky="w")
        self.export_input = ttk.Entry(col2, width=18)
        self.export_input.grid(row=0, column=1, padx=5, pady=2)
        ttk.Button(col2, text="Zapisz", command=self.aktualizuj_export).grid(row=0, column=2)
        
        col3 = ttk.Frame(fields_frame)
        col3.grid(row=0, column=2, padx=20, sticky="n")
        ttk.Label(col3, text="Import:").grid(row=0, column=0, sticky="w")
        self.import_input = ttk.Entry(col3, width=18)
        self.import_input.grid(row=0, column=1, padx=5, pady=2)
        ttk.Button(col3, text="Zapisz", command=self.aktualizuj_import).grid(row=0, column=2)

        col4 = ttk.Frame(fields_frame)
        col4.grid(row=0, column=3, padx=20, sticky="n")
        ttk.Label(col4, text="Uwagi:").grid(row=0, column=0, sticky="w")
        self.uwagi_input = ttk.Entry(col4, width=18)
        self.uwagi_input.grid(row=0, column=1, padx=5, pady=2)
        ttk.Button(col4, text="Zapisz", command=self.aktualizuj_uwagi).grid(row=0, column=2)

        data_frame = ttk.Frame(self)
        data_frame.pack(pady=(0, 10))
        ttk.Label(data_frame, text="Data:").pack(side="left", padx=(0, 5))
        self.data_entry = ttk.Entry(data_frame, width=30)
        self.data_entry.pack(side="left", padx=5)
        ttk.Button(data_frame, text="Dodaj datę", command=self.dodaj_date).pack(side="left", padx=5)

        main = ttk.Frame(self)
        main.pack(fill="both", expand=True, padx=10, pady=10)

        left = ttk.LabelFrame(main, text="Transporty")
        left.pack(side="left", fill="both", expand=True, padx=(0, 5))

        right = ttk.LabelFrame(main, text="Zlecenia do przypisania")
        right.pack(side="right", fill="both", expand=True, padx=(5, 0))

        self.transport_table = ttk.Treeview(left, columns=("LP", "Kierowca", "Export", "Import", "Uwagi"),
                                            show="headings", height=20)
        for col, width in [("LP", 50), ("Kierowca", 160), ("Export", 160), ("Import", 160), ("Uwagi", 90)]:
            self.transport_table.heading(col, text=col)
            self.transport_table.column(col, anchor="center", width=width)
        self.transport_table.pack(fill="both", expand=True)

        self.zlecenia_table = ttk.Treeview(right, columns=("D.zał", "Zleceniodawca", "LDM", "Waga", "M.rozł.", "D.rozł.", "Cena"),
                                           show="headings", height=20)
        for col in ("D.zał", "Zleceniodawca", "LDM", "Waga", "M.rozł.", "D.rozł.", "Cena"):
            self.zlecenia_table.heading(col, text=col)
            self.zlecenia_table.column(col, anchor="center", width=80)
        self.zlecenia_table.pack(anchor="ne", fill="both", expand=True)

        self.dragging_item = None
        self.transport_table.bind("<ButtonPress-1>", self.start_drag)
        self.transport_table.bind("<B1-Motion>", self.drag_motion)
        self.transport_table.bind("<ButtonRelease-1>", self.stop_drag)

        self.odswiez_zlecenia()
        self.wczytaj_transporty_z_pliku()

    def pobierz_transporty_z_serwera(self):
        try:
            r = requests.get(API_URL)
            r.raise_for_status()
            return r.json()
        except Exception as e:
            messagebox.showerror("Błąd", f"Nie można pobrać transportów:\n{e}")
            return []

    def zapisz_transporty_na_serwerze(self, transporty):
        try:
            r = requests.put(API_URL, json=transporty)
            r.raise_for_status()
        except Exception as e:
            messagebox.showerror("Błąd", f"Nie można zapisać transportów:\n{e}")

    def wczytaj_transporty_z_pliku(self):
        transporty = self.pobierz_transporty_z_serwera()
        self.transport_table.delete(*self.transport_table.get_children())
        for t in transporty:
            tags = ("separator",) if t.get("separator", False) else ()
            item_id = self.transport_table.insert("", "end",
                values=(t.get("lp", ""), t.get("kierowca", ""), t.get("export", ""), t.get("import", ""), t.get("uwagi", "")),
                tags=tags)
            if "separator" in tags:
                self.transport_table.tag_configure("separator", background="#e0e0e0", font=("Helvetica", 10, "bold"))

    def zapisz_transporty_do_pliku(self):
        transporty = []
        for row_id in self.transport_table.get_children():
            values = self.transport_table.item(row_id, "values")
            tags = self.transport_table.item(row_id, "tags")
            transporty.append({
                "lp": values[0],
                "kierowca": values[1],
                "export": values[2],
                "import": values[3],
                "uwagi": values[4],
                "separator": "separator" in tags
            })
        self.zapisz_transporty_na_serwerze(transporty)

    def dodaj_transport_z_kierowca(self):
        kierowca = self.kierowca_entry.get().strip()
        if not kierowca:
            messagebox.showwarning("Brak danych", "Wpisz imię i nazwisko kierowcy.")
            return
        transporty = self.pobierz_transporty_z_serwera()
        lp = max([t.get("lp", 0) for t in transporty if isinstance(t.get("lp", 0), int)] + [0]) + 1
        nowy = {"lp": lp, "kierowca": kierowca, "export": "", "import": "", "uwagi": "", "separator": False}
        transporty.append(nowy)
        self.zapisz_transporty_na_serwerze(transporty)
        self.wczytaj_transporty_z_pliku()
        self.after(10000, self.auto_odswiez_tabela)  # Odświeżanie co 10 sek.

    def dodaj_date(self):
        data = self.data_entry.get().strip()
        if not data:
            return
        transporty = self.pobierz_transporty_z_serwera()
        nowy = {"lp": "", "kierowca": "", "export": data, "import": "", "uwagi": "", "separator": True}
        transporty.append(nowy)
        self.zapisz_transporty_na_serwerze(transporty)
        self.wczytaj_transporty_z_pliku()

    def aktualizuj_pole(self, kolumna, wartosc):
        selected = self.transport_table.selection()
        if not selected:
            messagebox.showwarning("Brak zaznaczenia", "Zaznacz transport do edycji.")
            return
        item_id = selected[0]
        values = list(self.transport_table.item(item_id, "values"))
        kolumny = {"Kierowca":1, "Export":2, "Import":3, "Uwagi":4}
        index = kolumny.get(kolumna)
        if index is None:
            return
        values[index] = wartosc.strip()

        transporty = self.pobierz_transporty_z_serwera()
        for t in transporty:
            if str(t.get("lp")) == str(values[0]):
                t["kierowca"] = values[1]
                t["export"] = values[2]
                t["import"] = values[3]
                t["uwagi"] = values[4]
                break
        else:
            messagebox.showerror("Błąd", "Nie znaleziono transportu do aktualizacji.")
            return

        self.zapisz_transporty_na_serwerze(transporty)
        self.wczytaj_transporty_z_pliku()

    def aktualizuj_kierowce(self):
        self.aktualizuj_pole("Kierowca", self.kierowca_input.get())

    def aktualizuj_export(self):
        wartosc = self.export_input.get().strip() or self.edit_export_entry.get().strip()
        self.aktualizuj_pole("Export", wartosc)

    def aktualizuj_import(self):
        wartosc = self.import_input.get().strip() or self.edit_import_entry.get().strip()
        self.aktualizuj_pole("Import", wartosc)

    def aktualizuj_uwagi(self):
        wartosc = self.uwagi_input.get().strip() or self.edit_uwagi_entry.get().strip()
        self.aktualizuj_pole("Uwagi", wartosc)

    def odswiez_zlecenia(self):
        self.zlecenia_table.delete(*self.zlecenia_table.get_children())
        for zlec in self.zlecenia_lista:
            self.zlecenia_table.insert("", "end", values=(
                zlec.get("Data załadunku", ""),
                zlec.get("Nazwa zleceniodawcy", ""),
                zlec.get("LDM", ""),
                zlec.get("Waga", ""),
                zlec.get("Miejsce rozładunku", ""),
                zlec.get("Data rozładunku", ""),
                zlec.get("Cena", "")
            ))

    def aktualizuj_tabele_zlecen(self, lista_zlecen):
        """
        Aktualizuje zawartość tabeli zleceń w zakładce Transport.
        lista_zlecen - lista słowników z danymi zleceń.
        """
        self.zlecenia_lista.clear()
        self.zlecenia_table.delete(*self.zlecenia_table.get_children())
        for zlec in lista_zlecen:
            self.zlecenia_table.insert("", "end", values=(
                zlec.get("Data załadunku", ""),
                zlec.get("Nazwa zleceniodawcy", ""),
                zlec.get("LDM", ""),
                zlec.get("Waga", ""),
                zlec.get("Miejsce rozładunku", ""),
                zlec.get("Data rozładunku", ""),
                zlec.get("Cena", "")
            ))
            self.zlecenia_lista.append(zlec)

    def start_drag(self, event):
        region = self.transport_table.identify("region", event.x, event.y)
        if region == "cell":
            self.dragging_item = self.transport_table.identify_row(event.y)

    def drag_motion(self, event):
        if self.dragging_item:
            self.transport_table.selection_set(self.dragging_item)

    def stop_drag(self, event):
        if self.dragging_item:
            target_item = self.transport_table.identify_row(event.y)
            if target_item and target_item != self.dragging_item:
                dragged_values = self.transport_table.item(self.dragging_item, "values")
                dragged_tags = self.transport_table.item(self.dragging_item, "tags")
                self.transport_table.delete(self.dragging_item)
                index = self.transport_table.index(target_item)
                new_item = self.transport_table.insert("", index, values=dragged_values, tags=dragged_tags)
                self.transport_table.selection_set(new_item)
                self.zapisz_transporty_do_pliku()
            self.dragging_item = None

    def usun(self):
        selected = self.transport_table.selection()
        if not selected:
            messagebox.showwarning("Brak zaznaczenia", "Zaznacz transport do usunięcia.")
            return
        for item in selected:
            self.transport_table.delete(item)
        self.zapisz_transporty_do_pliku()
        
    def auto_odswiez_tabela(self):
        try:
            transporty = self.pobierz_transporty_z_serwera()
            self.transport_table.delete(*self.transport_table.get_children())
            for t in transporty:
                tags = ("separator",) if t.get("separator", False) else ()
                item_id = self.transport_table.insert(
                    "", "end",
                    values=(
                        t.get("lp", ""),
                        t.get("kierowca", ""),
                        t.get("export", ""),
                        t.get("import", ""),
                        t.get("uwagi", "")
                    ),
                    tags=tags
                )
                if "separator" in tags:
                    self.transport_table.tag_configure(
                        "separator",
                        background="#e0e0e0",
                        font=("Helvetica", 10, "bold")
                    )
            print("🔄 Automatyczne odświeżenie transportu")
        except Exception as e:
            print("❌ Błąd auto-odświeżania transportu:", e)
        finally:
            self.after(10000, self.auto_odswiez_tabela)
