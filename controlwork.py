from abc import ABC, abstractmethod
import json
import sqlite3

def log_decorator(func):
    def wrapper(*args, **kwargs):
        print(f"[LOG] Запуск функции: {func.__name__}")
        return func(*args, **kwargs)
    return wrapper

class JsonExportMixin:
    def to_dict(self):
        return {"title": self.title, "author": self.author, "year": self.year}

    def to_json(self):
        return json.dumps(self.to_dict(), ensure_ascii=False)

class LibraryItem(ABC):
    def __init__(self, title: str):
        self._title = title

    @property
    def title(self) -> str:
        return self._title

    @title.setter
    def title(self, value: str):
        self._title = value

    @abstractmethod
    def get_info(self) -> str:
        pass

class book(LibraryItem, JsonExportMixin):
    def __init__(self, title, author, year):
        super().__init__(title)
        if not self.validate_year(year):
            raise ValueError("Некорректный год выпуска!")
        self.author = author
        self.year = year

    def get_info(self):
        return f"{self.title} написанная {self.author}, опубликованая в {self.year}"

    def __str__(self):
        return f"'{self.title}' — {self.author} ({self.year})"

    def __eq__(self, other):
        if isinstance(other, book):
            return self.title.lower() == other.title.lower()
        return False

    @staticmethod
    def validate_year(year: int) -> bool:
        return 1000 <= year <= 2026

    @classmethod
    @log_decorator
    def from_string(cls, data_str: str):
        title, author, year = [p.strip() for p in data_str.split(",")]
        return cls(title, author, int(year))

class audio_book(book):
    def __init__(self, title, author, year, duration):
        super().__init__(title, author, year)
        self.duration = duration

    def get_info(self):
        return f"{super().info()}, длительность {self.duration} минут"

    def __str__(self):
        return f"'{self.title}' — {self.author} ({self.year}), длительность: {self.duration} мин."

@log_decorator
def search_book(books_list, target):
    checks = 0
    for b in books_list:
        checks += 1
        if b.title.lower() == target.lower():
            print(f"Проверок сделано: {checks}")
            return b
    print(f"Проверок сделано: {checks}")
    return None

conn = sqlite3.connect("library.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS books(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    author TEXT NOT NULL,
    year INTEGER NOT NULL
)
""")
conn.commit()

@log_decorator
def db_add(title, author, year):
    cursor.execute("INSERT INTO books (title, author, year) VALUES (?, ?, ?)", (title, author, year))
    conn.commit()

@log_decorator
def db_get_all():
    cursor.execute("SELECT * FROM books")
    return cursor.fetchall()

@log_decorator
def db_update(book_id, title, author, year):
    cursor.execute("UPDATE books SET title = ?, author = ?, year = ? WHERE id = ?", (title, author, year, book_id))
    conn.commit()

@log_decorator
def db_delete(book_id):
    cursor.execute("DELETE FROM books WHERE id = ?", (book_id,))
    conn.commit()


db_add("Clean Code", "Robert Martin", 2008)
print("БД:", db_get_all())

b1 = book("Clean Code", "Robert Martin", 2008)
b2 = audio_book("The Hobbit", "J.R.R. Tolkien", 1937, 650)
print(b1)
print(b2.to_json())

conn.close()