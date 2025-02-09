import sqlite3
import tkinter as tk
from tkinter import messagebox
from ttkbootstrap import Style, ttk
from modules.game_logic import RANGI, Gracz, waliduj_int
from modules.db import (
    stworz_baze_danych,
    dodaj_gracza,
    pobierz_gracza,
    zaktualizuj_gracza,
    pobierz_wszystkich_graczy
)
from modules.interface import run_interface

if __name__ == "__main__":
    run_interface()
