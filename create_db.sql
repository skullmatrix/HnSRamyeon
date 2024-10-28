import sqlite3

# Connect to SQLite database (this will create it if it doesn't exist)
conn = sqlite3.connect('pos_database.db')

# Create tables
conn.execute('''
CREATE TABLE IF NOT EXISTS items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    price REAL NOT NULL
);
''')

conn.execute('''
CREATE TABLE IF NOT EXISTS inventory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    FOREIGN KEY (item_id) REFERENCES items (id)
);
''')

conn.execute('''
CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    total REAL NOT NULL
);
''')

# Commit and close the connection
conn.commit()
conn.close()

print("Database initialized successfully.")
