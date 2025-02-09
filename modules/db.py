import sqlite3
from modules.game_logic import Gracz

def stworz_baze_danych():
    conn = sqlite3.connect('./dane_gry.db')
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
    conn = sqlite3.connect('./dane_gry.db')
    c = conn.cursor()
    c.execute('''
        INSERT OR IGNORE INTO gracze (imie, ranga, punkty, seria_zwyciestw, seria_porazek, wygrane, rozegrane, passa)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (gracz.imie, gracz.ranga, gracz.punkty, gracz.seria_zwyciestw, gracz.seria_porazek, gracz.wygrane, gracz.rozegrane, gracz.passa))
    conn.commit()
    conn.close()

def pobierz_gracza(imie):
    conn = sqlite3.connect('./dane_gry.db')
    c = conn.cursor()
    c.execute('SELECT * FROM gracze WHERE imie = ?', (imie,))
    wynik = c.fetchone()
    conn.close()
    if wynik:
        return Gracz(*wynik)
    else:
        return None

def zaktualizuj_gracza(gracz):
    conn = sqlite3.connect('./dane_gry.db')
    c = conn.cursor()
    c.execute('''
        UPDATE gracze
        SET ranga = ?, punkty = ?, seria_zwyciestw = ?, seria_porazek = ?, wygrane = ?, rozegrane = ?, passa = ?
        WHERE imie = ?
    ''', (gracz.ranga, gracz.punkty, gracz.seria_zwyciestw, gracz.seria_porazek, gracz.wygrane, gracz.rozegrane, gracz.passa, gracz.imie))
    conn.commit()
    conn.close()

def pobierz_wszystkich_graczy():
    conn = sqlite3.connect('./dane_gry.db')
    c = conn.cursor()
    c.execute('SELECT * FROM gracze')
    gracze = c.fetchall()
    conn.close()
    return [Gracz(*g) for g in gracze]