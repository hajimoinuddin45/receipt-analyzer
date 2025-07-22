import sqlite3
import os
from typing import List, Tuple

DB_PATH = os.path.join(os.getcwd(), "data", "receipts.db")

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS receipts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            vendor TEXT,
            date TEXT,
            amount REAL,
            category TEXT
        )
    ''')
    conn.commit()
    conn.close()
    print("✅ Database initialized.")

def insert_record(data: dict):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    print("📥 Inserting record:", data)
    cur.execute('''
        INSERT INTO receipts (vendor, date, amount, category)
        VALUES (?, ?, ?, ?)
    ''', (data['vendor'], data['date'], data['amount'], data['category']))
    conn.commit()
    conn.close()
    print("✅ Insert successful.")

def fetch_all_records() -> List[Tuple]:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT * FROM receipts")
    rows = cur.fetchall()
    conn.close()
    print("📤 Fetched records:", rows)
    return rows
