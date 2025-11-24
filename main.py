from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sqlite3

app = FastAPI()

def get_db_connection():
    conn = sqlite3.connect("books.db")
    conn.row_factory = sqlite3.Row
    return conn

conn = get_db_connection()
conn.execute("""
CREATE TABLE IF NOT EXISTS books (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    book_name TEXT NOT NULL,
    author TEXT NOT NULL,
    publisher TEXT NOT NULL
);
""")
conn.commit()
conn.close()

class Book(BaseModel):
    book_name: str
    author: str
    publisher: str

@app.get("/")
def home():
    return {"message": "Book API is running!"}

@app.post("/books")
def create_book(book: Book):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO books (book_name, author, publisher) VALUES (?, ?, ?)",
        (book.book_name, book.author, book.publisher),
    )
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return {"id": new_id, **book.dict()}

@app.get("/books")
def get_books():
    conn = get_db_connection()
    books = conn.execute("SELECT * FROM books").fetchall()
    conn.close()
    return [dict(book) for book in books]

@app.get("/books/{book_id}")
def get_book(book_id: int):
    conn = get_db_connection()
    book = conn.execute("SELECT * FROM books WHERE id = ?", (book_id,)).fetchone()
    conn.close()
    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return dict(book)

@app.put("/books/{book_id}")
def update_book(book_id: int, book: Book):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE books SET book_name = ?, author = ?, publisher = ? WHERE id = ?",
        (book.book_name, book.author, book.publisher, book_id),
    )
    conn.commit()
    if cursor.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="Book not found")
    conn.close()
    return {"id": book_id, **book.dict()}

@app.delete("/books/{book_id}")
def delete_book(book_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM books WHERE id = ?", (book_id,))
    conn.commit()
    if cursor.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="Book not found")
    conn.close()
    return {"message": f"Book with id {book_id} deleted successfully"}
