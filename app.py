import os
from flask import Flask, request, render_template, redirect, url_for
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
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        total REAL NOT NULL,
        money_received REAL NOT NULL,
        change REAL NOT NULL,
        time TEXT NOT NULL
    );
    ''')
    conn.execute('''
    CREATE TABLE IF NOT EXISTS invoices (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        transaction_id INTEGER,
        item_name TEXT,
        item_price REAL,
        FOREIGN KEY(transaction_id) REFERENCES transactions(id)
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

    items = conn.execute('SELECT * FROM items ORDER BY type, name').fetchall()
    conn.close()
    return render_template('index.html', items=items)

@app.route('/add_item', methods=['GET', 'POST'])
@app.route('/edit_item/<int:item_id>', methods=['GET', 'POST'])
def add_item(item_id=None):
    conn = get_db_connection()

    if request.method == 'POST':
        if item_id:  # Editing an existing item
            name = request.form['name']
            price = float(request.form['price'])
            type = request.form['type']
            conn.execute('UPDATE items SET name = ?, price = ?, type = ? WHERE id = ?', (name, price, type, item_id))
            conn.commit()
            return redirect(url_for('index'))  # Redirect back to the main page
        else:  # Adding a new item
            name = request.form['name']
            price = float(request.form['price'])
            type = request.form['type']
            conn.execute('INSERT INTO items (name, price, type) VALUES (?, ?, ?)', (name, price, type))
            conn.commit()
            return redirect(url_for('index'))  # Redirect back to the main page

    if item_id:  # Fetch the item details if we're editing
        item = conn.execute('SELECT * FROM items WHERE id = ?', (item_id,)).fetchone()
        conn.close()
        return render_template('add_item.html', action='Edit', item=item)

    conn.close()
    return render_template('add_item.html', action='Add')

@app.route('/make_transaction', methods=['POST'])
def make_transaction():
    item_ids = request.form.getlist('item_id')
    money_received = float(request.form['money_received'])
    conn = get_db_connection()
    total = 0
    items_purchased = []

    for item_id in item_ids:
        item = conn.execute('SELECT * FROM items WHERE id = ?', (item_id,)).fetchone()
        total += item['price']
        items_purchased.append((item_id, item['name'], item['price']))

    change = max(0, money_received - total)
    purchase_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    try:
        # Insert transaction details
        conn.execute('INSERT INTO transactions (total, money_received, change, time) VALUES (?, ?, ?, ?)',
                     (total, money_received, change, purchase_time))
        transaction_id = conn.execute('SELECT last_insert_rowid()').fetchone()[0]

        # Insert into invoices table
        for item in items_purchased:
            conn.execute('INSERT INTO invoices (transaction_id, item_name, item_price) VALUES (?, ?, ?)',
                         (transaction_id, item[1], item[2]))

        conn.commit()
    except Exception as e:
        print(f"Error during transaction processing: {e}")
        return "An error occurred while processing the transaction.", 500
    finally:
        conn.close()

    return redirect(url_for('invoices'))  # Redirect to the invoices page

@app.route('/invoices')
def invoices():
    conn = get_db_connection()
    invoices = conn.execute('SELECT * FROM invoices').fetchall()
    conn.close()
    return render_template('invoices.html', invoices=invoices)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)