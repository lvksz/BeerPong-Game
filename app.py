import sqlite3
import tkinter as tk
from tkinter import messagebox
from ttkbootstrap import Style, ttk

RANGI = ["Żelazo", "Brąz", "Srebro", "Złoto", "Platyna", "Diament", "Mistrz"]

class Gracz:
    def __init__(self, imie, ranga="Żelazo", punkty=0, seria_zwyciestw=0, seria_porazek=0, wygrane=0, rozegrane=0, passa=0):
        self.imie = imie
        self.ranga = ranga
        self.punkty = punkty
        self.seria_zwyciestw = seria_zwyciestw
        self.seria_porazek = seria_porazek
        self.wygrane = wygrane
        self.rozegrane = rozegrane
        self.passa = passa

    def aktualizuj_rangę(self):
        if self.ranga == "Mistrz":
            return
        while self.punkty >= 150 and self.ranga != "Mistrz":
            current_rank_index = RANGI.index(self.ranga)
            if current_rank_index + 1 < len(RANGI):
                self.punkty -= 150
                self.ranga = RANGI[current_rank_index + 1]
            else:
                self.ranga = "Mistrz"
                break
        while self.punkty < 0:
            if self.ranga == "Żelazo":
                self.punkty = 0
                break
            else:
                current_rank_index = RANGI.index(self.ranga)
                self.ranga = RANGI[current_rank_index - 1]
                self.punkty += 150

def stworz_baze_danych():
    conn = sqlite3.connect('dane_gry.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS gracze (
            imie TEXT PRIMARY KEY,
            ranga TEXT,
            punkty INTEGER,
            seria_zwyciestw INTEGER,
            seria_porazek INTEGER,
            wygrane INTEGER,
            rozegrane INTEGER,
            passa INTEGER
        )
    ''')
    conn.commit()
    conn.close()

def dodaj_gracza(gracz):
    conn = sqlite3.connect('dane_gry.db')
    c = conn.cursor()
    c.execute('''
        INSERT OR IGNORE INTO gracze (imie, ranga, punkty, seria_zwyciestw, seria_porazek, wygrane, rozegrane, passa)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (gracz.imie, gracz.ranga, gracz.punkty, gracz.seria_zwyciestw, gracz.seria_porazek, gracz.wygrane, gracz.rozegrane, gracz.passa))
    conn.commit()
    conn.close()

def pobierz_gracza(imie):
    conn = sqlite3.connect('dane_gry.db')
    c = conn.cursor()
    c.execute('SELECT * FROM gracze WHERE imie = ?', (imie,))
    wynik = c.fetchone()
    conn.close()
    if wynik:
        return Gracz(*wynik)
    else:
        return None

def zaktualizuj_gracza(gracz):
    conn = sqlite3.connect('dane_gry.db')
    c = conn.cursor()
    c.execute('''
        UPDATE gracze
        SET ranga = ?, punkty = ?, seria_zwyciestw = ?, seria_porazek = ?, wygrane = ?, rozegrane = ?, passa = ?
        WHERE imie = ?
    ''', (gracz.ranga, gracz.punkty, gracz.seria_zwyciestw, gracz.seria_porazek, gracz.wygrane, gracz.rozegrane, gracz.passa, gracz.imie))
    conn.commit()
    conn.close()

def pobierz_wszystkich_graczy():
    conn = sqlite3.connect('dane_gry.db')
    c = conn.cursor()
    c.execute('SELECT * FROM gracze')
    gracze = c.fetchall()
    conn.close()
    return [Gracz(*g) for g in gracze]

def waliduj_int(wejscie, nazwa_pola):
    try:
        wartosc = int(wejscie)
        if wartosc < 0:
            raise ValueError
        return wartosc
    except ValueError:
        messagebox.showerror("Błąd", f"Nieprawidłowa wartość w polu '{nazwa_pola}'. Wprowadź liczbę całkowitą nieujemną.")
        return None

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
        conn = sqlite3.connect('dane_gry.db')
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
    gracz_przegrany.aktualizuj_rangę()

    zaktualizuj_gracza(gracz_wygrany)
    zaktualizuj_gracza(gracz_przegrany)

    wyczysc_pola()
    wyswietl_statystyki()

def wyswietl_statystyki():
    gracze = pobierz_wszystkich_graczy()
    gracze.sort(key=lambda x: (-RANGI.index(x.ranga), -x.punkty))

    for item in tree_statystyki.get_children():
        tree_statystyki.delete(item)

    for gracz in gracze:
        procent_wygranych = (gracz.wygrane / gracz.rozegrane) * 100 if gracz.rozegrane > 0 else 0
        passa = f"{gracz.seria_zwyciestw}W" if gracz.seria_zwyciestw > 0 else f"{gracz.seria_porazek}L" if gracz.seria_porazek > 0 else ''
        tree_statystyki.insert('', 'end', values=(gracz.imie, gracz.ranga, gracz.punkty, gracz.rozegrane, f"{procent_wygranych:.2f}%", passa))

if __name__ == "__main__":
    stworz_baze_danych()

    style = Style(theme="darkly")
    root = style.master
    root.title("Beerpong Ranking")

    style.configure('TButton', background='#6A0DAD', foreground='white')
    style.configure('TCombobox', fieldbackground='#3C3F41', background='#6A0DAD')
    style.configure('Treeview.Heading', background='#6A0DAD', foreground='white')
    
    frame_nowy_gracz = ttk.LabelFrame(root, text="Dodaj nowego gracza")
    frame_nowy_gracz.pack(fill="x", padx=10, pady=5)

    ttk.Label(frame_nowy_gracz, text="Imię:").pack(side="left", padx=5, pady=5)
    entry_nowy_gracz = ttk.Entry(frame_nowy_gracz)
    entry_nowy_gracz.pack(side="left", padx=5, pady=5)
    ttk.Button(frame_nowy_gracz, text="Dodaj", command=dodaj_nowego_gracza).pack(side="left", padx=5, pady=5)

    frame_usun_gracza = ttk.LabelFrame(root, text="Usuń gracza")
    frame_usun_gracza.pack(fill="x", padx=10, pady=5)

    ttk.Label(frame_usun_gracza, text="Wybierz gracza:").pack(side="left", padx=5, pady=5)
    combo_usun_gracza = ttk.Combobox(frame_usun_gracza, state="readonly")
    combo_usun_gracza.pack(side="left", padx=5, pady=5)
    ttk.Button(frame_usun_gracza, text="Usuń", command=usun_gracza).pack(side="left", padx=5, pady=5)

    frame_wynik = ttk.LabelFrame(root, text="Wprowadź wynik meczu")
    frame_wynik.pack(fill="x", padx=10, pady=5)

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

    frame_statystyki = ttk.LabelFrame(root, text="Statystyki graczy")
    frame_statystyki.pack(fill="both", expand=True, padx=10, pady=5)

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

    root.mainloop()
