# 📘 Projekt CRUD Book (FastAPI + SQLite)

## 1. Cel systemu
Niniejszy system stanowi aplikację demonstracyjną typu **CRUD** (Create, Read, Update, Delete), przeznaczoną do zarządzania danymi książek i autorów literackich.  
System wykorzystuje środowisko **FastAPI** w języku **Python** oraz bazę danych **SQLite**.  
Interfejs użytkownika został zaimplementowany w technologii **HTML + JavaScript** (plik `static/index.html`).

---

## 2. Funkcjonalność systemu

System zapewnia następujące funkcje operacyjne:

- Pobieranie listy wszystkich książek z bazy danych  
- Dodawanie nowej książki  
- Modyfikowanie istniejącego rekordu książki  
- Usuwanie książki  
- Automatyczna inicjalizacja bazy danych przykładowymi wpisami podczas pierwszego uruchomienia systemu  

---

## 3. Uruchomienie projektu (lokalnie)

```bash
pip install -r requirements.txt
python main.py
