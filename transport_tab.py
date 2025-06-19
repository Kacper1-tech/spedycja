import tkinter as tk
from tkinter import ttk, messagebox
import tkinter.simpledialog
import uuid

from supabase_client import supabase
TABLE_NAME = "transport"

class TransportTab(ttk.Frame):
    def __init__(self, master, zlecenia_lista, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.zlecenia_lista = zlecenia_lista
        self.ukryte_zlecenia = []
        self.SZEROKOSC_LEWEJ = 600
        self.SZEROKOSC_PRAWEJ = 600

        # GUI — pola i przyciski
        main_frame = ttk.Frame(self, padding=10)
        main_frame.pack(fill="both", expand=True)
        fields_frame = ttk.Frame(main_frame)
        fields_frame.pack(fill="x", pady=(0, 5))
        fields_frame.columnconfigure((0, 1, 2, 3), weight=1)

        col1 = ttk.Frame(fields_frame)
        col1.grid(row=0, column=0, padx=20, sticky="n")
        ttk.Label(col1, text="Kierowca:").grid(row=0, column=0, sticky="w")
        self.kierowca_entry = ttk.Entry(col1, width=18)
        self.kierowca_entry.grid(row=0, column=1, padx=5, pady=2)
        ttk.Button(col1, text="Dodaj", command=self.dodaj_transport_z_kierowca).grid(row=0, column=2)
        ttk.Label(col1, text="Edytuj kierowcę:").grid(row=1, column=0, sticky="w")
        ttk.Button(col1, text="Usuń", command=self.usun_kierowce).grid(row=0, column=3, padx=(5, 0))
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

        data_frame = ttk.Frame(main_frame)
        data_frame.pack(pady=(5, 0))

        ttk.Label(data_frame, text="Data:").pack(side="left", padx=(0, 5))
        self.data_entry = ttk.Entry(data_frame, width=18)
        self.data_entry.pack(side="left", padx=5)
        ttk.Button(data_frame, text="Dodaj datę", command=self.dodaj_date).pack(side="left", padx=5)
        ttk.Button(data_frame, text="Edytuj datę", command=self.edytuj_date).pack(side="left", padx=5)
        ttk.Button(data_frame, text="Usuń datę", command=self.usun_date).pack(side="left", padx=5)

        main = ttk.Frame(main_frame)
        main.pack(fill="both", expand=True, pady=(0, 0))

        # Pole filtrowania kierowców + przycisk Usuń zlecenie
        filter_frame = ttk.Frame(main)
        filter_frame.pack(fill="x", padx=(0, 0), pady=(5, 10))

        left_filter = ttk.Frame(filter_frame)
        left_filter.pack(side="left")
        ttk.Label(left_filter, text="Filtruj kierowców:").pack(side="left")
        self.filter_entry = ttk.Entry(left_filter)
        self.filter_entry.pack(side="left", padx=5)
        self.filter_entry.bind("<KeyRelease>", self.filtruj_kierowcow)

        right_filter = ttk.Frame(filter_frame)
        right_filter.pack(side="right")
        ttk.Button(right_filter, text="Usuń zlecenie", command=self.usun_zlecenie_z_transportu).pack()

        left = ttk.LabelFrame(main, text="Transporty", width=self.SZEROKOSC_LEWEJ)
        left.pack(side="left", fill="y", padx=(10, 5))
        left.pack_propagate(False)

        transport_scroll_frame = ttk.Frame(left)
        transport_scroll_frame.pack(fill="both", expand=True)
        transport_scroll_frame.pack_propagate(False)

        scrollbar_left = ttk.Scrollbar(transport_scroll_frame, orient="vertical")
        scrollbar_left.pack(side="right", fill="y")

        self.transport_table = ttk.Treeview(
            transport_scroll_frame,
            columns=("Kierowca", "Export", "Import", "Uwagi"),
            show="headings",
            height=25,
            yscrollcommand=scrollbar_left.set
        )
        scrollbar_left.config(command=self.transport_table.yview)

        for col, width in [("Kierowca", 120), ("Export", 185), ("Import", 185), ("Uwagi", 90)]:
            self.transport_table.heading(col, text=col)
            self.transport_table.column(col, anchor="center", width=width)

        self.transport_table.pack(fill="both", expand=True)

        right_wrapper = ttk.Frame(main, width=self.SZEROKOSC_PRAWEJ)
        right_wrapper.pack(side="left", fill="both", expand=True, padx=(5, 10))
        right_wrapper.pack_propagate(False)

        right = ttk.LabelFrame(right_wrapper, text="Zlecenia")
        right.config(width=self.SZEROKOSC_PRAWEJ)
        right.pack(fill="both", expand=True)
        right.pack_propagate(False)

        right.config(width=self.SZEROKOSC_PRAWEJ)
        right.pack(fill="both", expand=True)
        right.pack_propagate(False)

        self.zlecenia_table = ttk.Treeview(right, columns=("D.zał", "Zleceniodawca", "LDM", "Waga", "M.rozł.", "D.rozł.", "Cena"),
                                           show="headings", height=25)
        for col in ("D.zał", "Zleceniodawca", "LDM", "Waga", "M.rozł.", "D.rozł.", "Cena"):
            self.zlecenia_table.heading(col, text=col)
            self.zlecenia_table.column(col, anchor="center", width=80)
        self.zlecenia_table.pack(fill="both", expand=True)

        self.dragging_item = None
        self.transport_table.bind("<ButtonPress-1>", self.start_drag)
        self.transport_table.bind("<B1-Motion>", self.drag_motion)
        self.transport_table.bind("<ButtonRelease-1>", self.stop_drag)

        self.odswiez_zlecenia()
        self.wczytaj_transporty_z_pliku()
        self.after(100, self.wyrownaj_wysokosc_tabel)

    def pobierz_transporty_z_serwera(self):
        try:
            response = supabase.table(TABLE_NAME).select("*").order("kolejnosc").execute()
            return response.data
        except Exception as e:
            messagebox.showerror("Błąd", f"Nie można pobrać transportów z Supabase:\n{e}")
            return []

    def zapisz_transporty_na_serwerze(self, transporty):
        try:
            # 🧹 Usuń wszystkie rekordy z wyjątkiem zabezpieczenia
            supabase.table(TABLE_NAME).delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()

            # ✅ Dodaj pole 'kolejnosc' do każdego rekordu
            for idx, t in enumerate(transporty):
                t["kolejnosc"] = idx
                supabase.table(TABLE_NAME).insert(t).execute()

        except Exception as e:
            messagebox.showerror("Błąd", f"Nie można zapisać transportów do Supabase:\n{e}")

    def wczytaj_transporty_z_pliku(self):
        transporty = self.pobierz_transporty_z_serwera()
        self.transport_table.delete(*self.transport_table.get_children())
        for t in transporty:
            tags = ("separator",) if t.get("separator", False) else ()
            self.transport_table.insert(
                "", "end", iid=t["id"],
                values=(
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

    def zapisz_transporty_do_pliku(self):
        transporty = []
        for row_id in self.transport_table.get_children():
            values = self.transport_table.item(row_id, "values")
            tags = self.transport_table.item(row_id, "tags")
            transport = {
                "kierowca": values[0],
                "export": values[1],
                "import": values[2],
                "uwagi": values[3],
                "separator": "separator" in tags
            }
            
            try:
                uuid.UUID(row_id)  # sprawdź, czy to prawidłowy UUID
                transport["id"] = row_id
            except ValueError:
                # jeśli nie jest UUID, wygeneruj nowy
                transport["id"] = str(uuid.uuid4())

            transporty.append(transport)

        self.zapisz_transporty_na_serwerze(transporty)

    def dodaj_transport_z_kierowca(self):
        kierowca = self.kierowca_entry.get().strip()
        if not kierowca:
            messagebox.showwarning("Brak danych", "Wpisz imię i nazwisko kierowcy.")
            return

        nowy = {
            "id": str(uuid.uuid4()),
            "kierowca": kierowca,
            "export": "",
            "import": "",
            "uwagi": "",
            "separator": False
        }
        transporty = self.pobierz_transporty_z_serwera()

        selected = self.transport_table.selection()
        if selected:
            selected_id = selected[0]
            tags = self.transport_table.item(selected_id, "tags")
            if "separator" in tags:
                # Znalezienie indexu w tabeli
                row_ids = self.transport_table.get_children()
                index_in_table = row_ids.index(selected_id)

                # Teraz znajdź ten sam obiekt w liście transportów
                selected_values = self.transport_table.item(selected_id, "values")
                selected_export = selected_values[1]  # bo separator = data w kolumnie "Export"

                for i, t in enumerate(transporty):
                    if t.get("separator") and t.get("export") == selected_export:
                        transporty.insert(i + 1, nowy)  # dodaj tuż po separatorze
                        break
                else:
                    transporty.append(nowy)  # fallback: dodaj na koniec
            else:
                transporty.append(nowy)  # kliknięto coś innego – dodaj na koniec
        else:
            transporty.append(nowy)  # nic nie zaznaczone – dodaj na koniec

        self.zapisz_transporty_na_serwerze(transporty)
        self.wczytaj_transporty_z_pliku()
        self.after(10000, self.auto_odswiez_tabela)

    def dodaj_date(self):
        data = self.data_entry.get().strip()
        if not data:
            return
        transporty = self.pobierz_transporty_z_serwera()

        # 🔒 zapobiegaj duplikatom
        if any(t.get("export") == data and t.get("separator") for t in transporty):
            messagebox.showinfo("Duplikat", f"Data '{data}' już istnieje.")
            return

        nowy = {
            "id": str(uuid.uuid4()),
            "kierowca": "",
            "export": data,
            "import": "",
            "uwagi": "",
            "separator": True
        }

        transporty.append(nowy)

        # 🔧 To zapisuje całą listę (z nowym wpisem) do Supabase
        self.zapisz_transporty_na_serwerze(transporty)

        # 🧼 I odświeża GUI
        self.wczytaj_transporty_z_pliku()

    def aktualizuj_pole(self, kolumna, wartosc):
        selected = self.transport_table.selection()
        if not selected:
            messagebox.showwarning("Brak zaznaczenia", "Zaznacz transport do edycji.")
            return

        item_id = selected[0]
        wartosc = wartosc.strip()

        # 🔄 Pobierz aktualny wiersz i jego dane
        wartosci = self.transport_table.item(item_id, "values")
        tags = self.transport_table.item(item_id, "tags")
        separator = "separator" in tags

        # 🔄 Zaktualizuj GUI
        nowe_wartosci = list(wartosci)
        kolumny = ["Kierowca", "Export", "Import", "Uwagi"]
        if kolumna in kolumny:
            indeks = kolumny.index(kolumna)
            nowe_wartosci[indeks] = wartosc
            self.transport_table.item(item_id, values=nowe_wartosci)

        # 🔄 Zaktualizuj tylko ten rekord w Supabase bez zmiany kolejności
        try:
            update_data = {
                kolumna.lower(): wartosc,
                "separator": separator  # zachowaj oznaczenie separatora
            }
            supabase.table(TABLE_NAME).update(update_data).eq("id", item_id).execute()
        except Exception as e:
            messagebox.showerror("Błąd", f"Nie udało się zapisać zmiany do Supabase:\n{e}")

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
            rekord = (
                zlec.get("Data załadunku", ""),
                zlec.get("Nazwa zleceniodawcy", ""),
                zlec.get("LDM", ""),
                zlec.get("Waga", ""),
                zlec.get("Miejsce rozładunku", ""),
                zlec.get("Data rozładunku", ""),
                zlec.get("Cena", "")
            )
            if rekord not in self.ukryte_zlecenia:
                self.zlecenia_table.insert("", "end", values=rekord)

    def aktualizuj_tabele_zlecen(self, lista_zlecen):
        self.zlecenia_lista.clear()
        self.zlecenia_table.delete(*self.zlecenia_table.get_children())

        for zlec in lista_zlecen:
            # Mapowanie pól z bazy na te, które wyświetlamy
            rekord = {
                "Data załadunku": zlec.get("data_zaladunku", ""),
                "Nazwa zleceniodawcy": zlec.get("nazwa_zleceniodawcy", ""),
                "LDM": zlec.get("ldm", ""),
                "Waga": zlec.get("waga", ""),
                "Miejsce rozładunku": zlec.get("miejsce_rozladunku", ""),
                "Data rozładunku": zlec.get("data_rozladunku", ""),
                "Cena": zlec.get("cena", "")
            }
            rekord_tuple = tuple(rekord.values())
            if rekord_tuple not in self.ukryte_zlecenia:
                self.zlecenia_table.insert("", "end", values=rekord_tuple)
            if rekord_tuple not in self.ukryte_zlecenia:
                self.zlecenia_lista.append(rekord)

    def start_drag(self, event):
        region = self.transport_table.identify("region", event.x, event.y)
        if region == "cell":
            self.dragging_item = self.transport_table.identify_row(event.y)
            if not self.dragging_item:
                return  # kliknięto w puste miejsce – nie inicjuj przeciągania

    def drag_motion(self, event):
        if self.dragging_item and self.transport_table.exists(self.dragging_item):
            self.transport_table.selection_set(self.dragging_item)

    def stop_drag(self, event):
        if self.dragging_item and self.transport_table.exists(self.dragging_item):
            target_item = self.transport_table.identify_row(event.y)
            if target_item and target_item != self.dragging_item:
                dragged_values = self.transport_table.item(self.dragging_item, "values")
                dragged_tags = self.transport_table.item(self.dragging_item, "tags")
                index = self.transport_table.index(target_item)
                self.transport_table.delete(self.dragging_item)
                self.transport_table.insert("", index, iid=self.dragging_item, values=dragged_values, tags=dragged_tags)
                self.transport_table.selection_set(self.dragging_item)
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
                self.transport_table.insert(
                    "", "end", iid=t["id"],
                    values=(
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

    def usun_kierowce(self):
        selected = self.transport_table.selection()
        if not selected:
            messagebox.showwarning("Brak zaznaczenia", "Zaznacz kierowcę do usunięcia.")
            return

        confirm = messagebox.askyesno("Potwierdzenie", "Czy na pewno chcesz usunąć zaznaczonego kierowcę?")
        if not confirm:
            return

        transporty = self.pobierz_transporty_z_serwera()
        nowe_transporty = []

        zaznaczone_id = set(selected)

        for t in transporty:
            if t.get("id") not in zaznaczone_id:

                nowe_transporty.append(t)

        for t in transporty:
            if t.get("id") in zaznaczone_id:
                supabase.table(TABLE_NAME).delete().eq("id", t["id"]).execute()
        self.wczytaj_transporty_z_pliku()

    def filtruj_kierowcow(self, event=None):
        filtr = self.filter_entry.get().strip().lower()

        wszystkie_transporty = self.pobierz_transporty_z_serwera()
        self.transport_table.delete(*self.transport_table.get_children())

        for t in wszystkie_transporty:
            if t.get("separator", False):
                continue  # Pomijamy separatory (np. daty)
            kierowca = t.get("kierowca", "").lower()
            if filtr in kierowca:
                self.transport_table.insert("", "end", iid=t["id"], values=(
                    t.get("kierowca", ""),
                    t.get("export", ""),
                    t.get("import", ""),
                    t.get("uwagi", "")
                ))

    def edytuj_date(self):
        selected = self.transport_table.selection()
        if not selected:
            messagebox.showwarning("Brak zaznaczenia", "Zaznacz separator daty do edycji.")
            return

        item_id = selected[0]
        tags = self.transport_table.item(item_id, "tags")
        if "separator" not in tags:
            messagebox.showwarning("Błąd", "Można edytować tylko daty (separatory).")
            return

        nowa_data = self.data_entry.get().strip()
        if not nowa_data:
            nowa_data = tk.simpledialog.askstring("Nowa data", "Wpisz nową datę:")
            if not nowa_data:
                return

        # 🔄 Zaktualizuj w GUI
        self.transport_table.set(item_id, column="Export", value=nowa_data)

        # ✅ Zaktualizuj tylko ten jeden rekord w Supabase
        try:
            supabase.table(TABLE_NAME).update({"export": nowa_data}).eq("id", item_id).execute()
        except Exception as e:
            messagebox.showerror("Błąd", f"Nie można zaktualizować daty w Supabase:\n{e}")

    def usun_date(self):
        selected = self.transport_table.selection()
        if not selected:
            messagebox.showwarning("Brak zaznaczenia", "Zaznacz separator daty do usunięcia.")
            return

        item_id = selected[0]
        tags = self.transport_table.item(item_id, "tags")
        if "separator" not in tags:
            messagebox.showwarning("Błąd", "Można usunąć tylko daty (separatory).")
            return

        self.transport_table.delete(item_id)
        supabase.table(TABLE_NAME).delete().eq("id", item_id).execute()

    def usun_zlecenie_z_transportu(self):
        selected = self.zlecenia_table.selection()
        if not selected:
            messagebox.showwarning("Brak zaznaczenia", "Zaznacz zlecenie do usunięcia.")
            return

        for item in selected:
            wartosci = self.zlecenia_table.item(item, "values")
            self.ukryte_zlecenia.append(wartosci)
            self.zlecenia_table.delete(item)
      
    def wyrownaj_wysokosc_tabel(self):
        self.update_idletasks()  # Upewnij się, że wszystko się załadowało
        transport_height = self.transport_table.winfo_height()
        row_height = 20  # typowa wysokość wiersza (można dostosować)
        rows = int(transport_height / row_height)
        self.zlecenia_table.configure(height=max(rows - 1, 5))
