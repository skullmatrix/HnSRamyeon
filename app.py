import os
from flask import Flask, request, render_template, redirect, url_for
import sqlite3
from datetime import datetime
import pytz  # To handle timezone

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
        total REAL NOT NULL,
        money_received REAL NOT NULL,
        change REAL NOT NULL,
        time TEXT NOT NULL,
        items TEXT NOT NULL
    );
    ''')
    conn.commit()
    conn.close()

# Initialize the database
initialize_database()

@app.route('/', methods=['GET', 'POST'])
def index():
    conn = get_db_connection()
    
    # Fetch all items from the database, sorted by type
    items = conn.execute('SELECT * FROM items ORDER BY type, name').fetchall()
    conn.close()
    return render_template('index.html', items=items)

@app.route('/add_item', methods=['GET', 'POST'])
def add_item():
    conn = get_db_connection()
    
    if request.method == 'POST':
        name = request.form['name']
        price = float(request.form['price'])
        type = request.form['type']
        item_id = request.form.get('item_id')  # Get the item ID if it exists
        
        if item_id:  # If editing an existing item
            conn.execute('UPDATE items SET name = ?, price = ?, type = ? WHERE id = ?', (name, price, type, item_id))
        else:  # If adding a new item
            conn.execute('INSERT INTO items (name, price, type) VALUES (?, ?, ?)', (name, price, type))
        
        conn.commit()
        conn.close()
        return redirect(url_for('index'))  # Redirect back to the main page
    
    # Fetch existing items for display on the Add Item page
    items = conn.execute('SELECT * FROM items ORDER BY type, name').fetchall()
    conn.close()
    return render_template('add_item.html', items=items)  # Render the add/edit item page

@app.route('/edit_item/<int:item_id>', methods=['GET'])
def edit_item(item_id):
    conn = get_db_connection()
    item = conn.execute('SELECT * FROM items WHERE id = ?', (item_id,)).fetchone()
    conn.close()
    if item:
        return render_template('add_item.html', item=item)  # Populate the form with item data
    return redirect(url_for('index'))

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
        items_purchased.append((item['name'], item['price']))

    change = max(0, money_received - total)

    # Get the current time in the Philippines timezone
    philippine_tz = pytz.timezone('Asia/Manila')
    purchase_time = datetime.now(philippine_tz).strftime('%Y-%m-%d %H:%M:%S')

    # Insert transaction into the database
    conn.execute('INSERT INTO transactions (total, money_received, change, time) VALUES (?, ?, ?, ?)',
                 (total, money_received, change, purchase_time))
    
    # Save invoice details into the invoices table
    items_details = ', '.join([f"{item[0]} (${item[1]})" for item in items_purchased])
    conn.execute('INSERT INTO invoices (total, money_received, change, time, items) VALUES (?, ?, ?, ?, ?)',
                 (total, money_received, change, purchase_time, items_details))

    conn.commit()
    conn.close()

    # Redirect back to the index page after making the transaction
    return redirect(url_for('index'))

@app.route('/invoices', methods=['GET'])
def invoices():
    conn = get_db_connection()
    invoices = conn.execute('SELECT * FROM invoices ORDER BY time DESC').fetchall()
    conn.close()
    return render_template('invoices.html', invoices=invoices)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)