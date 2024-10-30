import os
import csv
from flask import Flask, request, render_template, redirect, url_for, send_file
import sqlite3
from datetime import datetime
import pytz

app = Flask(__name__)

# Database connection
def get_db_connection():
    conn = sqlite3.connect('pos_database.db')
    conn.row_factory = sqlite3.Row
    return conn

# Initialize the database and add items if not present
def initialize_database():
    conn = get_db_connection()
    conn.execute('''
    CREATE TABLE IF NOT EXISTS items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        price INTEGER NOT NULL,
        type TEXT NOT NULL,
        quantity INTEGER DEFAULT 0  -- New column for inventory quantity
    );
    ''')
    conn.execute('''
    CREATE TABLE IF NOT EXISTS invoices (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        total INTEGER NOT NULL,
        money_received INTEGER NOT NULL,
        change INTEGER NOT NULL,
        time TEXT NOT NULL,
        items TEXT NOT NULL
    );
    ''')
    conn.commit()

    # Populate items if the table is empty
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM items")
    if cursor.fetchone()[0] == 0:
        items = [
            ("Cheese Ramen Spicy", 99, "Soup Base", 100),
            ("Nongshim", 89, "Soup Base", 100),
            ("Ottogi Cheese Ramen", 99, "Soup Base", 100),
            ("Nongshim JJWANG", 129, "Soup Base", 100),
            # Add quantity as the fourth element for each item
            # ... (additional items here)
        ]
        cursor.executemany('INSERT INTO items (name, price, type, quantity) VALUES (?, ?, ?, ?)', items)
        conn.commit()
    conn.close()

# Initialize the database
initialize_database()

@app.route('/', methods=['GET', 'POST'])
def index():
    conn = get_db_connection()
    if request.method == 'POST':
        search_query = request.form.get('search_query')
        if search_query:
            items = conn.execute('SELECT * FROM items WHERE name LIKE ?', ('%' + search_query + '%',)).fetchall()
        else:
            items = conn.execute('SELECT * FROM items ORDER BY type, name').fetchall()
    else:
        items = conn.execute('SELECT * FROM items ORDER BY type, name').fetchall()
    
    conn.close()
    return render_template('index.html', items=items)

@app.route('/inventory', methods=['GET', 'POST'])
def inventory():
    conn = get_db_connection()
    if request.method == 'POST':
        # Update item quantities from form submission
        for item_id, quantity in request.form.items():
            conn.execute('UPDATE items SET quantity = ? WHERE id = ?', (quantity, item_id))
        conn.commit()
        return redirect(url_for('inventory'))

    items = conn.execute('SELECT * FROM items ORDER BY type, name').fetchall()
    conn.close()
    return render_template('inventory.html', items=items)

@app.route('/export_inventory', methods=['GET'])
def export_inventory():
    conn = get_db_connection()
    items = conn.execute('SELECT * FROM items ORDER BY type, name').fetchall()
    conn.close()

    # Create CSV file for inventory
    current_time = datetime.now(pytz.timezone('Asia/Manila'))
    filename = current_time.strftime('%Y-%m-%d_%H-%M-%S_inventory.csv')
    csv_file = f'/tmp/{filename}'

    with open(csv_file, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['ID', 'Name', 'Price', 'Type', 'Quantity'])
        for item in items:
            writer.writerow([item['id'], item['name'], item['price'], item['type'], item['quantity']])

    return send_file(csv_file, as_attachment=True, download_name=filename)

@app.route('/make_transaction', methods=['POST'])
def make_transaction():
    quantities = request.form.to_dict(flat=False)
    money_received = int(request.form['money_received'])
    conn = get_db_connection()
    total = 0
    items_purchased = []

    for item_id, qty_list in quantities.items():
        if "quantity[" in item_id:
            real_id = int(item_id.split('[')[1].split(']')[0])
            quantity = int(qty_list[0])
            item = conn.execute('SELECT * FROM items WHERE id = ?', (real_id,)).fetchone()
            item_total = item['price'] * quantity
            total += item_total
            items_purchased.append((item['name'], item['price'], quantity, item_total))

            # Update inventory by reducing quantity
            conn.execute('UPDATE items SET quantity = quantity - ? WHERE id = ?', (quantity, real_id))

    change = max(0, money_received - total)

    philippine_tz = pytz.timezone('Asia/Manila')
    purchase_time = datetime.now(philippine_tz).strftime('%Y-%m-%d %H:%M:%S')

    items_details = ', '.join([f"{name} (x{quantity}) P{item_total}" for name, price, quantity, item_total in items_purchased])
    conn.execute('INSERT INTO invoices (total, money_received, change, time, items) VALUES (?, ?, ?, ?, ?)',
                 (total, money_received, change, purchase_time, items_details))

    conn.commit()
    conn.close()
    
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