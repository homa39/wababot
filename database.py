import sqlite3

# Создание базы данных и таблицы
conn = sqlite3.connect('whatsapp_numbers.db')
c = conn.cursor()
c.execute('''
    CREATE TABLE IF NOT EXISTS numbers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        phone_number INTEGER NOT NULL,
        messenger TEXT NOT NULL,
        price INTEGER NOT NULL
    )
''')
conn.commit()
conn.close()
