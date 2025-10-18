from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
import sqlite3
import os
import uvicorn
from typing import Optional

app = FastAPI()
app.mount("/static", StaticFiles(directory=os.path.join(os.path.dirname(__file__), "static")), name="static")

DB_NAME = "/tmp/books.db"

class BookIn(BaseModel):
    title: str = Field(..., min_length=1)
    author: str = Field(..., min_length=1)
    year: int
    genre: str = Field(..., min_length=1)
    rating: float

def ensure_columns():
    """
    Если таблица существует, проверим колонки и добавим недостающие.
    SQLite поддерживает ADD COLUMN, поэтому просто добавляем.
    """
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    # Создадим таблицу (если не существует) с нужными колонками
    cur.execute('''CREATE TABLE IF NOT EXISTS books (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        author TEXT NOT NULL,
        year INTEGER,
        genre TEXT,
        rating REAL
    )''')

    # Проверим существование колонок (на случай старой БД)
    cur.execute("PRAGMA table_info(books)")
    cols = [row[1] for row in cur.fetchall()]
    if 'genre' not in cols:
        cur.execute("ALTER TABLE books ADD COLUMN genre TEXT")
    if 'rating' not in cols:
        cur.execute("ALTER TABLE books ADD COLUMN rating REAL")
    conn.commit()
    conn.close()

def init_db():
    ensure_columns()
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM books")
    if cur.fetchone()[0] == 0:
        cur.executemany(
            "INSERT INTO books (title, author, year, genre, rating) VALUES (?, ?, ?, ?, ?)",
            [
                ("A Game of Thrones", "George R. R. Martin", 1996, "Fantasy", 9.5),
                ("Dune", "Frank Herbert", 1965, "Sci-Fi", 9.0),
                ("The Green Mile", "Stephen King", 1996, "Drama", 8.8)
            ]
        )
    conn.commit()
    conn.close()

init_db()

@app.get("/")
def root():
    return FileResponse("static/index.html")

@app.get("/books")
def get_books():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("SELECT id, title, author, year, genre, rating FROM books")
    books = [
        {"id": r[0], "title": r[1], "author": r[2], "year": r[3], "genre": r[4], "rating": r[5]}
        for r in cur.fetchall()
    ]
    conn.close()
    return books

@app.post("/books")
def add_book(book: BookIn):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO books (title, author, year, genre, rating) VALUES (?, ?, ?, ?, ?)",
        (book.title, book.author, book.year, book.genre, book.rating)
    )
    conn.commit()
    conn.close()
    return {"message": "Book added successfully"}

@app.put("/books/{book_id}")
def update_book(book_id: int, book: BookIn):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute(
        "UPDATE books SET title=?, author=?, year=?, genre=?, rating=? WHERE id=?",
        (book.title, book.author, book.year, book.genre, book.rating, book_id)
    )
    if cur.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="Book not found")
    conn.commit()
    conn.close()
    return {"message": "Book updated successfully"}

@app.delete("/books/{book_id}")
def delete_book(book_id: int):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("DELETE FROM books WHERE id=?", (book_id,))
    if cur.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="Book not found")
    conn.commit()
    conn.close()
    return {"message": "Book deleted successfully"}

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
