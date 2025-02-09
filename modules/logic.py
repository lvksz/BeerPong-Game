from modules.player import *
from modules.inteface import *
from modules.databse import *
from app import *
from tkinter import messagebox

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

def waliduj_int(wejscie, nazwa_pola):
    try:
        wartosc = int(wejscie)
        if wartosc < 0:
            raise ValueError
        return wartosc
    except ValueError:
        messagebox.showerror("Błąd", f"Nieprawidłowa wartość w polu '{nazwa_pola}'. Wprowadź liczbę całkowitą nieujemną.")
        return None