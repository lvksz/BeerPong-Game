from modules.databse import *
from app import *
import tkinter as tk
from ttkbootstrap import Style, ttk

def render_interaface():
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

def wyswietl_statystyki():
    gracze = pobierz_wszystkich_graczy()
    gracze.sort(key=lambda x: (-RANGI.index(x.ranga), -x.punkty))

    for item in tree_statystyki.get_children():
        tree_statystyki.delete(item)

    for gracz in gracze:
        procent_wygranych = (gracz.wygrane / gracz.rozegrane) * 100 if gracz.rozegrane > 0 else 0
        passa = f"{gracz.seria_zwyciestw}W" if gracz.seria_zwyciestw > 0 else f"{gracz.seria_porazek}L" if gracz.seria_porazek > 0 else ''
        tree_statystyki.insert('', 'end', values=(gracz.imie, gracz.ranga, gracz.punkty, gracz.rozegrane, f"{procent_wygranych:.2f}%", passa))

