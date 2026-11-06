import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
from baza_danych import df, zapisz_zmiany_w_bazie
from edycja.walidacja import waliduj_wartosc


class EdytorBazyGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Edytor Bazy D_UKR")
        self.root.geometry("1000x700")
        self.root.configure(bg="#f4f5f7")  # Nowoczesne, lekko szare tło aplikacji

        # --- KONFIGURACJA STYLÓW ---
        style = ttk.Style()
        if "vista" in style.theme_names():
            style.theme_use("vista")
        elif "clam" in style.theme_names():
            style.theme_use("clam")

        czcionka_domyslna = ("Segoe UI", 10)

        # Główne style dla gładkiego wyglądu
        style.configure(".", background="#f4f5f7", font=czcionka_domyslna)
        style.configure("White.TFrame", background="#ffffff")
        style.configure("White.TLabel", background="#ffffff")

        # Styl tabeli - wyższe wiersze, brak grubych ramek
        style.configure("Treeview", rowheight=32, font=czcionka_domyslna, borderwidth=0)
        style.configure("Treeview.Heading", font=("Segoe UI", 11, "bold"), padding=6)
        style.map("Treeview", background=[('selected', '#005a9e')], foreground=[('selected', 'white')])

        # Duże, wyraźne przyciski
        style.configure("Akcja.TButton", font=("Segoe UI", 10, "bold"), padding=6)

        # --- GÓRNY BANNER (DASHBOARD) ---
        banner = ttk.Frame(root, style="White.TFrame")
        banner.pack(fill=tk.X, side=tk.TOP)

        ttk.Label(banner, text="Zarządzanie Bazą D_UKR", font=("Segoe UI", 18, "bold"), style="White.TLabel",
                  foreground="#1e1e1e").pack(side=tk.LEFT, padx=(25, 10), pady=(20, 5))
        ttk.Label(banner, text="Wybierz wskaźnik i zedytuj dane dla wybranych rekordów.", font=("Segoe UI", 11),
                  style="White.TLabel", foreground="#6e6e6e").pack(side=tk.LEFT, padx=10, pady=(26, 5))

        # --- GŁÓWNY KONTENER ---
        main_frame = ttk.Frame(root, padding="25 20 25 25")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # --- WYSZUKIWANIE ---
        search_frame = ttk.Frame(main_frame)
        search_frame.pack(fill=tk.X, pady=(0, 20))

        ttk.Label(search_frame, text="Wybierz wskaźnik z listy:").pack(side=tk.LEFT, padx=(0, 15))

        self.indicator_var = tk.StringVar()
        self.combo_indicators = ttk.Combobox(search_frame, textvariable=self.indicator_var, state="readonly",
                                             font=czcionka_domyslna)
        self.combo_indicators['values'] = list(df['indicator_name'].drop_duplicates())
        self.combo_indicators.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.combo_indicators.bind("<<ComboboxSelected>>", self.zaladuj_tabelke)

        # --- TABELA (TREEVIEW) ---
        # Ramka otaczająca tabelę, by wyglądała jak karta
        table_card = ttk.Frame(main_frame)
        table_card.pack(fill=tk.BOTH, expand=True)

        tree_scroll = ttk.Scrollbar(table_card)
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        kolumny = ("index", "rok", "opis")
        self.tree = ttk.Treeview(table_card, columns=kolumny, show="headings", yscrollcommand=tree_scroll.set)
        tree_scroll.config(command=self.tree.yview)

        self.tree.heading("index", text="Index")
        self.tree.heading("rok", text="Rok")
        self.tree.heading("opis", text="Opis wskaźnika (description_pl)")

        self.tree.column("index", width=100, anchor=tk.CENTER)
        self.tree.column("rok", width=120, anchor=tk.CENTER)
        self.tree.column("opis", width=650, anchor=tk.W)

        # Konfiguracja tagów "zebry" (naprzemienne kolory)
        self.tree.tag_configure('parzysty', background="#ffffff")
        self.tree.tag_configure('nieparzysty', background="#f9fafb")

        self.tree.pack(fill=tk.BOTH, expand=True)

        # --- DOLNY PANEL ---
        bottom_frame = ttk.Frame(main_frame)
        bottom_frame.pack(fill=tk.X, pady=(20, 0))

        self.btn_edit = ttk.Button(bottom_frame, text="Edytuj wybrany rekord", style="Akcja.TButton",
                                   command=self.otworz_okno_edycji)
        self.btn_edit.pack(side=tk.RIGHT)

    def zaladuj_tabelke(self, event=None):
        wybrany_wskaznik = self.indicator_var.get()

        for row in self.tree.get_children():
            self.tree.delete(row)

        filtered_df = df[df['indicator_name'] == wybrany_wskaznik]

        for i, (index, row) in enumerate(filtered_df.iterrows()):
            rok = row.get('year', '')
            opis = row.get('description_pl', '')

            # Przypisywanie tagu w zależności od tego, czy wiersz jest parzysty
            tag = 'parzysty' if i % 2 == 0 else 'nieparzysty'
            self.tree.insert("", tk.END, values=(index, rok, opis), tags=(tag,))

    def otworz_okno_edycji(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Brak wyboru", "Wybierz najpierw rekord z tabeli, klikając na niego.")
            return

        item_values = self.tree.item(selected_item[0], "values")
        row_idx = int(item_values[0])

        okno_edycji = tk.Toplevel(self.root)
        okno_edycji.title("Formularz Edycji")
        okno_edycji.geometry("650x750")
        okno_edycji.configure(bg="#ffffff")
        okno_edycji.transient(self.root)
        okno_edycji.grab_set()

        # Baner w oknie edycji
        header = tk.Frame(okno_edycji, bg="#005a9e", height=60)
        header.pack(fill=tk.X, side=tk.TOP)
        header.pack_propagate(False)
        tk.Label(header, text=f"Edytujesz rekord (Index: {row_idx})", font=("Segoe UI", 14, "bold"), bg="#005a9e",
                 fg="white").pack(side=tk.LEFT, padx=20)

        # Zawartość ze scrollem
        form_container = ttk.Frame(okno_edycji, padding="20 20 20 10", style="White.TFrame")
        form_container.pack(fill=tk.BOTH, expand=True)

        canvas = tk.Canvas(form_container, highlightthickness=0, bg="#ffffff")
        scrollbar = ttk.Scrollbar(form_container, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas, style="White.TFrame")

        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        window_id = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.bind("<Configure>", lambda e: canvas.itemconfig(window_id, width=e.width))

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        slownik_pol = {}
        for i, col in enumerate(df.columns):
            # Etykiety wyrównane do prawej dla czystszego układu
            ttk.Label(scrollable_frame, text=col + ":", font=("Segoe UI", 10, "bold"), style="White.TLabel",
                      foreground="#444444").grid(row=i, column=0, sticky=tk.E, padx=(0, 15), pady=10)

            obecna_wartosc = str(df.at[row_idx, col]) if not pd.isna(df.at[row_idx, col]) else ""

            pole_tekstowe = ttk.Entry(scrollable_frame, font=("Segoe UI", 10))
            pole_tekstowe.insert(0, obecna_wartosc)

            if col.lower() == 'id':
                pole_tekstowe.config(state="readonly")

            pole_tekstowe.grid(row=i, column=1, sticky=tk.EW, pady=10, ipady=4)
            scrollable_frame.columnconfigure(1, weight=1)
            slownik_pol[col] = pole_tekstowe

        def zapisz_dane():
            try:
                for col, pole in slownik_pol.items():
                    if col.lower() == 'id':
                        continue
                    nowa_wartosc = pole.get()
                    col_type = df[col].dtype
                    parsed_value = waliduj_wartosc(nowa_wartosc, col, col_type)
                    df.at[row_idx, col] = parsed_value

                zapisz_zmiany_w_bazie(df, row_idx)

                messagebox.showinfo("Sukces", "Zmiany zostały trwale zapisane na serwerze.")
                okno_edycji.destroy()
                self.zaladuj_tabelke()

            except ValueError as e:
                messagebox.showerror("Błąd danych", f"Niepoprawny format danych:\n{e}")
            except Exception as e:
                messagebox.showerror("Błąd", f"Wystąpił problem:\n{e}")

        # Stopka z przyciskami
        footer = tk.Frame(okno_edycji, bg="#f4f5f7", height=70)
        footer.pack(fill=tk.X, side=tk.BOTTOM)
        footer.pack_propagate(False)

        ttk.Button(footer, text="Zapisz zmiany", style="Akcja.TButton", command=zapisz_dane).pack(side=tk.RIGHT,
                                                                                                  padx=20, pady=15)
        ttk.Button(footer, text="Anuluj", command=okno_edycji.destroy).pack(side=tk.RIGHT, pady=15)


def uruchom_gui():
    root = tk.Tk()
    app = EdytorBazyGUI(root)
    root.mainloop()