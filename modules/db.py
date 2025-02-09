import os
import sqlite3
from modules.game_logic import Gracz

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, 'dane_gry.db')

def stworz_baze_danych():
    conn = sqlite3.connect(DB_PATH)
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

    c.execute('''
        CREATE TABLE IF NOT EXISTS match_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            winner TEXT,
            loser TEXT,
            details TEXT,
            match_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def dodaj_gracza(gracz):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        INSERT OR IGNORE INTO gracze (imie, ranga, punkty, seria_zwyciestw, seria_porazek, wygrane, rozegrane, passa)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (gracz.imie, gracz.ranga, gracz.punkty, gracz.seria_zwyciestw, gracz.seria_porazek, gracz.wygrane, gracz.rozegrane, gracz.passa))
    conn.commit()
    conn.close()

def pobierz_gracza(imie):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT * FROM gracze WHERE imie = ?', (imie,))
    wynik = c.fetchone()
    conn.close()
    if wynik:
        return Gracz(*wynik)
    else:
        return None

def zaktualizuj_gracza(gracz):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        UPDATE gracze
        SET ranga = ?, punkty = ?, seria_zwyciestw = ?, seria_porazek = ?, wygrane = ?, rozegrane = ?, passa = ?
        WHERE imie = ?
    ''', (gracz.ranga, gracz.punkty, gracz.seria_zwyciestw, gracz.seria_porazek, gracz.wygrane, gracz.rozegrane, gracz.passa, gracz.imie))
    conn.commit()
    conn.close()

def pobierz_wszystkich_graczy():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT * FROM gracze')
    gracze = c.fetchall()
    conn.close()
    return [Gracz(*g) for g in gracze]

def add_match_history(winner, loser, details):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        INSERT INTO match_history (winner, loser, details)
        VALUES (?, ?, ?)
    ''', (winner, loser, details))
    conn.commit()
    # Enforce a maximum of 5 match history records.
    c.execute('SELECT COUNT(*) FROM match_history')
    count = c.fetchone()[0]
    if count > 5:
        c.execute('''
            DELETE FROM match_history
            WHERE id IN (
                SELECT id FROM match_history
                ORDER BY match_date ASC
                LIMIT ?
            )
        ''', (count - 5,))
        conn.commit()
    conn.close()

def get_match_history():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        SELECT winner, loser, details, strftime('%Y-%m-%d %H:%M', match_date)
        FROM match_history
        ORDER BY match_date DESC
        LIMIT 5
    ''')
    history = c.fetchall()
    conn.close()
    return history