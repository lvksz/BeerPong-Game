import sqlite3
import tkinter as tk
from tkinter import messagebox
from ttkbootstrap import Style, ttk
from modules.db import stworz_baze_danych, dodaj_gracza, pobierz_gracza, zaktualizuj_gracza, pobierz_wszystkich_graczy, get_match_history, add_match_history
from modules.game_logic import RANGI, Gracz, waliduj_int
from modules.db import DB_PATH

def odswiez_liste_graczy():
    imiona = [gracz.imie for gracz in pobierz_wszystkich_graczy()]
    combo_wygrany['values'] = imiona
    combo_przegrany['values'] = imiona
    combo_usun_gracza['values'] = imiona

def wyczysc_pola():
    entry_nowy_gracz.delete(0, tk.END)
    combo_usun_gracza.set('')
    combo_wygrany.set('')
    combo_przegrany.set('')
    combo_pozostale_kubki.set('')
    var_domowy_wygrany.set(False)

def dodaj_nowego_gracza():
    imie = entry_nowy_gracz.get().strip()
    if not imie:
        messagebox.showerror("Błąd", "Imię gracza nie może być puste.")
        return
    if pobierz_gracza(imie):
        messagebox.showerror("Błąd", "Gracz o tym imieniu już istnieje.")
        return
    nowy_gracz = Gracz(imie)
    dodaj_gracza(nowy_gracz)
    messagebox.showinfo("Sukces", f"Gracz '{imie}' został dodany.")
    wyczysc_pola()
    odswiez_liste_graczy()

def usun_gracza():
    imie = combo_usun_gracza.get()
    if not imie:
        messagebox.showerror("Błąd", "Wybierz gracza do usunięcia.")
        return
    if messagebox.askyesno("Potwierdzenie", f"Czy na pewno chcesz usunąć gracza '{imie}'?"):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('DELETE FROM gracze WHERE imie = ?', (imie,))
        conn.commit()
        conn.close()
        messagebox.showinfo("Sukces", f"Gracz '{imie}' został usunięty.")
        wyczysc_pola()
        odswiez_liste_graczy()
        wyswietl_statystyki()

def zatwierdz_wynik():
    imie_wygranego = combo_wygrany.get()
    imie_przegranego = combo_przegrany.get()
    if not imie_wygranego or not imie_przegranego:
        messagebox.showerror("Błąd", "Wybierz obu graczy.")
        return
    if imie_wygranego == imie_przegranego:
        messagebox.showerror("Błąd", "Gracz nie może grać przeciwko sobie.")
        return
    pozostale_kubki = waliduj_int(combo_pozostale_kubki.get(), "Pozostałe kubki")
    if pozostale_kubki is None:
        return
    mecz_domowy_wygranego = var_domowy_wygrany.get()
    gracz_wygrany = pobierz_gracza(imie_wygranego)
    gracz_przegrany = pobierz_gracza(imie_przegranego)
    if not gracz_wygrany or not gracz_przegrany:
        messagebox.showerror("Błąd", "Jeden z graczy nie istnieje w bazie danych.")
        return
    przyrost = max(20 + (RANGI.index(gracz_przegrany.ranga) - RANGI.index(gracz_wygrany.ranga)) * 2 + pozostale_kubki, 1)
    if not mecz_domowy_wygranego and gracz_wygrany.seria_zwyciestw < 3:
        przyrost += 3
    gracz_wygrany.punkty += przyrost
    gracz_wygrany.seria_zwyciestw += 1
    gracz_wygrany.seria_porazek = 0
    gracz_wygrany.rozegrane += 1
    gracz_wygrany.wygrane += 1
    gracz_przegrany.punkty -= przyrost
    gracz_przegrany.seria_porazek += 1
    gracz_przegrany.seria_zwyciestw = 0
    gracz_przegrany.rozegrane += 1
    gracz_wygrany.aktualizuj_rangę()
    gracz_przegrany.aktualizuj_rangę()  # replaced gracz_przegranego with gracz_przegrany
    zaktualizuj_gracza(gracz_wygrany)
    zaktualizuj_gracza(gracz_przegrany)
    
    # Store only the remaining cups number without extra text.
    details = combo_pozostale_kubki.get()
    add_match_history(imie_wygranego, imie_przegranego, details)
    
    wyczysc_pola()
    wyswietl_statystyki()
    update_match_history()

def wyswietl_statystyki():
    gracze = pobierz_wszystkich_graczy()
    gracze.sort(key=lambda x: (-RANGI.index(x.ranga), -x.punkty))
    for item in tree_statystyki.get_children():
        tree_statystyki.delete(item)
    for gracz in gracze:
        procent_wygranych = (gracz.wygrane / gracz.rozegrane) * 100 if gracz.rozegrane > 0 else 0
        passa = f"{gracz.seria_zwyciestw}W" if gracz.seria_zwyciestw > 0 else f"{gracz.seria_porazek}L" if gracz.seria_porazek > 0 else ''
        tree_statystyki.insert('', 'end', values=(gracz.imie, gracz.ranga, gracz.punkty, gracz.rozegrane, f"{procent_wygranych:.2f}%", passa))

def update_match_history():
    # Clear the match history tree view and insert latest records
    for item in tree_match_history.get_children():
        tree_match_history.delete(item)
    history = get_match_history()
    for rec in history:
        tree_match_history.insert('', 'end', values=rec)

def run_interface():
    global combo_wygrany, combo_przegrany, combo_usun_gracza, combo_pozostale_kubki
    global entry_nowy_gracz, var_domowy_wygrany, tree_statystyki, tree_match_history

    stworz_baze_danych()
    style = Style(theme="darkly")
    root = style.master
    root.title("Beerpong Ranking")
    root.geometry("1400x600")  # Smaller window size
    style.configure('TButton', background='#6A0DAD', foreground='white')
    style.configure('TCombobox', fieldbackground='#3C3F41', background='#6A0DAD')
    style.configure('Treeview.Heading', background='#6A0DAD', foreground='white')
    
    # Updated: function to show game rules with markdown conversion and styled header
    def show_info():
        import os, re
        info_window = tk.Toplevel(root)
        info_window.title("Game Rules")
        info_window.geometry("900x600")
        info_window.config(bg='#3C3F41')  # Set same gray background
        try:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            readme_path = os.path.join(base_dir, "README.md")
            with open(readme_path, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            content = "Could not load rules."
        # Minimal markdown conversion: remove headers and bold/italic markers
        content = re.sub(r'\*\*(.*?)\*\*', r'\1', content)
        content = re.sub(r'\*(.*?)\*', r'\1', content)
        content = re.sub(r'#+\s*', '', content)
        # Add violet header like in the main interface
        header_label = tk.Label(info_window, text="Game Rules", bg='#6A0DAD', font=("TkDefaultFont", 14, "bold"))
        header_label.pack(fill="x", padx=5, pady=(5,2))
        # Use larger font for content and apply same gray background
        text = tk.Text(info_window, wrap="word", bg='#3C3F41', fg='white', font=("TkDefaultFont", 12))
        text.insert("1.0", content)
        text.config(state="disabled")
        text.pack(fill="both", expand=True, padx=5, pady=(2,5))
    
    # Main container with two rows: row0 for top sections, row1 for statistics
    main_frame = ttk.Frame(root)
    main_frame.pack(fill="both", expand=True)
    main_frame.rowconfigure(0, weight=0)
    main_frame.rowconfigure(1, weight=1)
    main_frame.columnconfigure(0, weight=1)
    
    # Row 0: Two columns for player management/result (left) and match history (right)
    top_frame = ttk.Frame(main_frame)
    top_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=5)
    top_frame.columnconfigure(0, weight=3)
    top_frame.columnconfigure(1, weight=1)
    
    # Left column: Fixed height container for Add, Remove, and Match Result sections
    left_top_frame = ttk.Frame(top_frame, height=300)
    left_top_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
    left_top_frame.grid_propagate(False)
    
    # New: Info Button Section
    ttk.Button(left_top_frame, text="Info", command=show_info).pack(fill="x", padx=5, pady=2)

    # Add New Player Section
    frame_nowy_gracz = ttk.LabelFrame(left_top_frame, text="Dodaj nowego gracza")
    frame_nowy_gracz.pack(fill="x", pady=2)
    ttk.Label(frame_nowy_gracz, text="Imię:").pack(side="left", padx=5, pady=5)
    entry_nowy_gracz = ttk.Entry(frame_nowy_gracz)
    entry_nowy_gracz.pack(side="left", padx=5, pady=5)
    ttk.Button(frame_nowy_gracz, text="Dodaj", command=dodaj_nowego_gracza).pack(side="left", padx=5, pady=5)
    
    # Delete Player Section
    frame_usun_gracza = ttk.LabelFrame(left_top_frame, text="Usuń gracza")
    frame_usun_gracza.pack(fill="x", pady=2)
    ttk.Label(frame_usun_gracza, text="Wybierz gracza:").pack(side="left", padx=5, pady=5)
    combo_usun_gracza = ttk.Combobox(frame_usun_gracza, state="readonly")
    combo_usun_gracza.pack(side="left", padx=5, pady=5)
    ttk.Button(frame_usun_gracza, text="Usuń", command=usun_gracza).pack(side="left", padx=5, pady=5)
    
    # Match Result Section
    frame_wynik = ttk.LabelFrame(left_top_frame, text="Wprowadź wynik meczu")
    frame_wynik.pack(fill="x", pady=2)
    ttk.Label(frame_wynik, text="Zwycięzca:").grid(row=0, column=0, padx=5, pady=5)
    combo_wygrany = ttk.Combobox(frame_wynik, state="readonly")
    combo_wygrany.grid(row=0, column=1, padx=5, pady=5)
    ttk.Label(frame_wynik, text="Przegrany:").grid(row=1, column=0, padx=5, pady=5)
    combo_przegrany = ttk.Combobox(frame_wynik, state="readonly")
    combo_przegrany.grid(row=1, column=1, padx=5, pady=5)
    ttk.Label(frame_wynik, text="Pozostałe kubki u zwycięzcy:").grid(row=2, column=0, padx=5, pady=5)
    combo_pozostale_kubki = ttk.Combobox(frame_wynik, values=list(range(1, 10)), state="readonly")
    combo_pozostale_kubki.grid(row=2, column=1, padx=5, pady=5)
    var_domowy_wygrany = tk.BooleanVar()
    ttk.Checkbutton(frame_wynik, text="Zwycięzca grał u siebie", variable=var_domowy_wygrany).grid(row=0, column=2, padx=5, pady=5)
    ttk.Button(frame_wynik, text="Zatwierdź wynik", command=zatwierdz_wynik).grid(row=3, column=0, columnspan=3, padx=5, pady=10)
    
    # Right column: Match History with same fixed height as left_top_frame
    right_top_frame = ttk.Frame(top_frame, height=300)
    right_top_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
    right_top_frame.grid_propagate(False)
    frame_match_history = ttk.LabelFrame(right_top_frame, text="Historia meczów")
    frame_match_history.pack(fill="both", expand=True)
    columns_history = ('Zwycięzca', 'Przegrany', 'Pozostałe kubki', 'Data')  # changed header
    tree_match_history = ttk.Treeview(frame_match_history, columns=columns_history, show='headings', selectmode="browse")
    for col in columns_history:
        tree_match_history.heading(col, text=col)
        tree_match_history.column(col, anchor='center')
    tree_match_history.pack(fill="both", expand=True, padx=5, pady=5)
    
    # Row 1: Player Statistics spans full width
    frame_statystyki = ttk.LabelFrame(main_frame, text="Statystyki graczy")
    frame_statystyki.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
    columns = ('Imię', 'Ranga', 'Punkty', 'Rozegrane', 'Win%', 'Passa')
    tree_statystyki = ttk.Treeview(frame_statystyki, columns=columns, show='headings', selectmode="browse")
    for col in columns:
        tree_statystyki.heading(col, text=col)
        tree_statystyki.column(col, anchor='center')
    style.configure('Treeview', background='#3C3F41', fieldbackground='#3C3F41', foreground='white')
    style.configure('Treeview', bordercolor='#6A0DAD')
    tree_statystyki.pack(fill="both", expand=True, padx=5, pady=5)
    
    odswiez_liste_graczy()
    wyswietl_statystyki()
    update_match_history()
    root.mainloop()