from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import sqlite3
import os

app = FastAPI()
app.mount("/static", StaticFiles(directory=os.path.join(os.path.dirname(__file__), "static")), name="static")

DB_NAME = "/tmp/books.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS books (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        author TEXT NOT NULL,
        year INTEGER
    )''')
    cur.execute("SELECT COUNT(*) FROM books")
    if cur.fetchone()[0] == 0:
        cur.executemany("INSERT INTO books (title, author, year) VALUES (?, ?, ?)", [
            ("1984", "George Orwell", 1949),
            ("A Game of Thrones", "George R. R. Martin", 1996),
            ("Dune", "Frank Herbert", 1965),
            ("The Green Mile", "Stephen King", 1996)
        ])
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
    cur.execute("SELECT * FROM books")
    books = [{"id": r[0], "title": r[1], "author": r[2], "year": r[3]} for r in cur.fetchall()]
    conn.close()
    return books

@app.post("/books")
def add_book(book: dict):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("INSERT INTO books (title, author, year) VALUES (?, ?, ?)", 
                (book["title"], book["author"], book["year"]))
    conn.commit()
    conn.close()
    return {"message": "Book added successfully"}

@app.put("/books/{book_id}")
def update_book(book_id: int, book: dict):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("UPDATE books SET title=?, author=?, year=? WHERE id=?", 
                (book["title"], book["author"], book["year"], book_id))
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