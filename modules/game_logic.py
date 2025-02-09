from tkinter import messagebox
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

def waliduj_int(wejscie, nazwa_pola):
    try:
        wartosc = int(wejscie)
        if wartosc < 0:
            raise ValueError
        return wartosc
    except ValueError:
        messagebox.showerror("Błąd", f"Nieprawidłowa wartość w polu '{nazwa_pola}'. Wprowadź liczbę całkowitą nieujemną.")
        return None