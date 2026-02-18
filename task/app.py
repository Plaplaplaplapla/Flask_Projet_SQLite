import os
import sqlite3

DB_PATH = 'tasks.db'

# Crée la base et la table si elle n'existe pas
if not os.path.exists(DB_PATH):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT,
        status TEXT NOT NULL DEFAULT 'pending',
        assigned_to TEXT,
        due_date TEXT
    )
    ''')
    conn.commit()
    conn.close()
    print("Base tasks.db créée avec succès !")
