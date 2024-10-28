import os
from flask import Flask, request, jsonify, render_template, redirect, url_for
import sqlite3
from datetime import datetime

app = Flask(__name__)

# Database setup - connects to SQLite and creates tables if they don't exist
def get_db_connection():
    conn = sqlite3.connect('pos_database.db')
    conn.row_factory = sqlite3.Row
    return conn

def initialize_database():
    # Create required tables if they don't exist
    conn = get_db_connection()
    conn.execute('''
    CREATE TABLE IF NOT EXISTS items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        price REAL NOT NULL,
        type TEXT NOT NULL
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
        total REAL NOT NULL,
        money_received REAL NOT NULL,
        change REAL NOT NULL,
        time TEXT NOT NULL
    );
    ''')
    conn.execute('''
    CREATE TABLE IF NOT EXISTS transaction_items (
        transaction_id INTEGER,
        item_id INTEGER,
        item_name TEXT,
        item_price REAL,
        FOREIGN KEY (transaction_id) REFERENCES transactions (id)
    );
    ''')
    conn.commit()
    conn.close()

# Initialize the database
initialize_database()

@app.route('/', methods=['GET', 'POST'])
def index():
    conn = get_db_connection()
    
    # If form submitted, add item to the database
    if request.method == 'POST':
        name = request.form['name']
        price = float(request.form['price'])
        type = request.form['type']
        conn.execute('INSERT INTO items (name, price, type) VALUES (?, ?, ?)', (name, price, type))
        conn.commit()
    
    # Fetch the updated list of items, sorted by type
    items = conn.execute('SELECT * FROM items ORDER BY type, name').fetchall()
    conn.close()
    return render_template('index.html', items=items)

@app.route('/make_transaction', methods=['POST'])
def make_transaction():
    # Endpoint to process transaction, calculate total and change, and store purchase details
    item_ids = request.form.getlist('item_id')
    money_received = float(request.form['money_received'])
    conn = get_db_connection()
    total = 0
    items_purchased = []

    # Calculate total and gather item details
    for item_id in item_ids:
        item = conn.execute('SELECT * FROM items WHERE id = ?', (item_id,)).fetchone()
        total += item['price']
        items_purchased.append((item_id, item['name'], item['price']))

    # Calculate change
    change = max(0, money_received - total)
    purchase_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Insert transaction details
    conn.execute('INSERT INTO transactions (total, money_received, change, time) VALUES (?, ?, ?, ?)',
                 (total, money_received, change, purchase_time))
    transaction_id = conn.execute('SELECT last_insert_rowid()').fetchone()[0]

    # Insert each purchased item in transaction_items
    for item in items_purchased:
        conn.execute('INSERT INTO transaction_items (transaction_id, item_id, item_name, item_price) VALUES (?, ?, ?, ?)',
                     (transaction_id, item[0], item[1], item[2]))

    conn.commit()
    conn.close()
    return render_template('transaction.html', total=total, change=change, purchase_time=purchase_time, items=items_purchased)

# Start the Flask application with the port provided by Render
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
