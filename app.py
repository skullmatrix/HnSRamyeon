
import os
from flask import Flask, request, jsonify, render_template, redirect, url_for
import sqlite3

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
        conn.execute('INSERT INTO items (name, price) VALUES (?, ?)', (name, price))
        conn.commit()
    
    # Fetch the updated list of items
    items = conn.execute('SELECT * FROM items').fetchall()
    conn.close()
    return render_template('index.html', items=items)

@app.route('/add_to_inventory', methods=['POST'])
def add_to_inventory():
    # Endpoint to add item quantity to inventory
    item_id = int(request.form['item_id'])
    quantity = int(request.form['quantity'])
    conn = get_db_connection()
    conn.execute('INSERT INTO inventory (item_id, quantity) VALUES (?, ?)', (item_id, quantity))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

@app.route('/make_transaction', methods=['POST'])
def make_transaction():
    # Endpoint to make a transaction and calculate the total
    item_ids = request.form.getlist('item_id')
    conn = get_db_connection()
    total = 0
    for item_id in item_ids:
        item = conn.execute('SELECT price FROM items WHERE id = ?', (item_id,)).fetchone()
        total += item['price']
    conn.execute('INSERT INTO transactions (total) VALUES (?)', (total,))
    conn.commit()
    conn.close()
    return render_template('transaction.html', total=total)

# Start the Flask application with the port provided by Render
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
