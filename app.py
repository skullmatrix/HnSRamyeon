
import os
import csv
from flask import Flask, request, render_template, redirect, url_for, send_file, Response
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
        quantity INTEGER NOT NULL DEFAULT 100
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
            ("SOON Ramen", 99, "Soup Base", 100),
            ("JIN Ramen", 69, "Soup Base", 100),
            ("Buldak 2X Spicy", 129, "Stir Fry", 100),
            ("Buldak Black", 119, "Stir Fry", 100),
            ("Buldak Carbonara", 109, "Stir Fry", 100),
            ("Cheese Ramen Stir Fry", 109, "Stir Fry", 100),
            ("JIN Ramen Cup", 63, "Cups", 100),
            ("Nongshim Squid Jampong Cup", 55, "Cups", 100),
            ("Paldo Pororo Cup", 59, "Cups", 100),
            ("Shrimp Cup Ramen Small", 52, "Cups", 100),
            ("Boiled Egg", 19, "Toppings", 100),
            ("Crab Stick", 15, "Toppings", 100),
            ("Fish Cake", 15, "Toppings", 100),
            ("Fishball", 15, "Toppings", 100),
            ("Golden Cheese Ball", 15, "Toppings", 100),
            ("Ham", 15, "Toppings", 100),
            ("Kimchi", 10, "Toppings", 100),
            ("Lobster Ball", 19, "Toppings", 100),
            ("Lobster Stick", 15, "Toppings", 100),
            ("Lotte Luncheon Meat", 119, "Toppings", 100),
            ("Namkwang Seaweed", 19, "Toppings", 100),
            ("Raw Egg", 15, "Toppings", 100),
            ("Sajo Gochujang", 76, "Toppings", 100),
            ("Sanjo Doenjang", 68, "Toppings", 100),
            ("Shabu2x Mix", 15, "Toppings", 100),
            ("Sliced Cheese", 19, "Toppings", 100),
            ("Ssamjang", 78, "Toppings", 100),
            ("Almond Choco Ball", 69, "Sweets", 100),
            ("Ice Cream Cone", 10, "Sweets", 100),
            ("Pepero", 59, "Sweets", 100),
            ("Binggrae Milk", 59, "Drinks", 100),
            ("Caffee Latte Can", 49, "Drinks", 100),
            ("Chupa Chups", 69, "Drinks", 100),
            ("Flavored Yakult", 49, "Drinks", 100),
            ("Ice Talk", 60, "Drinks", 100),
            ("Jinro Soju", 110, "Drinks", 100),
            ("Milkis", 49, "Drinks", 100),
            ("Welch’s", 70, "Drinks", 100),
            ("Yakult Orig", 39, "Drinks", 100),
        ]
        cursor.executemany('INSERT INTO items (name, price, type, quantity) VALUES (?, ?, ?, ?)', items)
        conn.commit()
    conn.close()

# Initialize the database
initialize_database()

@app.route('/')
def index():
    conn = get_db_connection()
    items = conn.execute('SELECT * FROM items ORDER BY type, name').fetchall()
    conn.close()
    return render_template('index.html', items=items)

@app.route('/add_item', methods=['GET', 'POST'])
def add_item():
    conn = get_db_connection()
    if request.method == 'POST':
        item_id = request.form.get('item_id')
        name = request.form['name']
        price = int(request.form['price'])
        type = request.form['type']
        
        if item_id:
            conn.execute('UPDATE items SET name = ?, price = ?, type = ? WHERE id = ?', (name, price, type, item_id))
        else:
            conn.execute('INSERT INTO items (name, price, type) VALUES (?, ?, ?)', (name, price, type))
        
        conn.commit()
        conn.close()
        return redirect(url_for('add_item'))

    items = conn.execute('SELECT * FROM items ORDER BY type, name').fetchall()
    conn.close()
    return render_template('add_item.html', items=items)

@app.route('/edit_item/<int:item_id>', methods=['GET'])
def edit_item(item_id):
    conn = get_db_connection()
    item = conn.execute('SELECT * FROM items WHERE id = ?', (item_id,)).fetchone()
    items = conn.execute('SELECT * FROM items ORDER BY type, name').fetchall()
    conn.close()
    return render_template('add_item.html', item=item, items=items)
@app.route('/inventory', methods=['GET', 'POST'])
def inventory():
    conn = get_db_connection()
    if request.method == 'POST':
        item_id = request.form['item_id']
        new_quantity = int(request.form['new_quantity'])
        conn.execute('UPDATE items SET quantity = ? WHERE id = ?', (new_quantity, item_id))
        conn.commit()
    items = conn.execute('SELECT * FROM items ORDER BY type, name').fetchall()
    conn.close()
    return render_template('inventory.html', items=items)

if __name__ == '__main__':
    app.run(debug=True)

@app.route('/make_transaction', methods=['POST'])
def make_transaction():
    item_ids = request.form.getlist('item_id')
    quantities = request.form.getlist('quantity')
    money_received = int(request.form['money_received'])
    payment_mode = request.form['payment_mode']  # Capture the mode of payment
    conn = get_db_connection()
    total = 0
    items_purchased = []

    # Calculate total and build items purchased details
    for i, item_id in enumerate(item_ids):
        item = conn.execute('SELECT * FROM items WHERE id = ?', (item_id,)).fetchone()
        
        # Ensure the item was fetched successfully
        if item is None:
            print(f"Error: Item with ID {item_id} not found in database.")
            continue  # Skip this item if not found

        quantity = int(quantities[i])
        item_total = item['price'] * quantity
        total += item_total
        items_purchased.append((item['name'], item['price'], quantity, item_total))

        # Update inventory: subtract quantity from each item in stock
        conn.execute('UPDATE items SET quantity = quantity - ? WHERE id = ?', (quantity, item_id))

    # Calculate change
    change = max(0, money_received - total)

    # Timestamp in Philippine timezone
    philippine_tz = pytz.timezone('Asia/Manila')
    purchase_time = datetime.now(philippine_tz).strftime('%Y-%m-%d %H:%M:%S')

    # Prepare items details for invoice
    items_details = ', '.join([f"{name} (x{quantity}) P{item_total}" for name, price, quantity, item_total in items_purchased])

    # Insert invoice record with payment mode
    conn.execute('INSERT INTO invoices (total, money_received, change, time, items, payment_mode) VALUES (?, ?, ?, ?, ?, ?)',
                 (total, money_received, change, purchase_time, items_details, payment_mode))

    # Commit and close connection
    conn.commit()
    conn.close()
    
    return redirect(url_for('index'))

@app.route('/invoices', methods=['GET'])
def invoices():
    conn = get_db_connection()
    invoices = conn.execute('SELECT * FROM invoices ORDER BY time DESC').fetchall()
    conn.close()
    return render_template('invoices.html', invoices=invoices)

@app.route('/export_invoices')
def export_invoices():
    from_date = request.args.get('from')
    to_date = request.args.get('to')

    conn = get_db_connection()
    if from_date and to_date:
        invoices = conn.execute('SELECT * FROM invoices WHERE date(time) BETWEEN ? AND ?', (from_date, to_date)).fetchall()
    else:
        invoices = conn.execute('SELECT * FROM invoices').fetchall()  # Fallback to all invoices

    conn.close()

    # Create a CSV file as before
    current_time = datetime.now(pytz.timezone('Asia/Manila'))
    filename = current_time.strftime('%Y-%m-%d_%H-%M-%S_invoices.csv')
    csv_file = f'/tmp/{filename}'

    with open(csv_file, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['ID', 'Date & Time', 'Total', 'Money Received', 'Change', 'Items Purchased'])
        for invoice in invoices:
            writer.writerow([
                invoice['id'], 
                invoice['time'], 
                invoice['total'], 
                invoice['money_received'], 
                invoice['change'], 
                invoice['items']
            ])

    return send_file(csv_file, as_attachment=True, download_name=filename)

@app.route('/export_inventory')
def export_inventory():
    conn = get_db_connection()
    inventory = conn.execute('SELECT * FROM items').fetchall()  # Fetch inventory items
    conn.close()

    # Create a CSV file with a filename based on the current date and time
    current_time = datetime.now(pytz.timezone('Asia/Manila'))
    filename = current_time.strftime('%Y-%m-%d_%H-%M-%S_inventory.csv')  # Create a filename
    csv_file = f'/tmp/{filename}'

    with open(csv_file, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Item Name', 'Price', 'Type', 'Quantity'])  # Header row
        for item in inventory:
            writer.writerow([
                item['name'],         # Item Name
                item['price'],       # Price
                item['type'],        # Type
                item['quantity']     # Quantity
            ])

    # Send the file as a download
    return send_file(csv_file, as_attachment=True, download_name=filename)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)