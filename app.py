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
        quantity INTEGER NOT NULL DEFAULT 100  -- Default inventory quantity
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

@app.route('/', methods=['GET'])
def index():
    conn = get_db_connection()
    items = conn.execute('SELECT * FROM items ORDER BY type, name').fetchall()
    
    # Handle search functionality
    search_query = request.args.get('search_query')
    if search_query:
        items = [item for item in items if search_query.lower() in item['name'].lower()]

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
        quantity = int(request.form.get('quantity', 100))  # Optional quantity for adding new items

        if item_id:  # Edit existing item
            conn.execute('UPDATE items SET name = ?, price = ?, type = ?, quantity = ? WHERE id = ?', 
                         (name, price, type, quantity, item_id))
        else:  # Add new item
            conn.execute('INSERT INTO items (name, price, type, quantity) VALUES (?, ?, ?, ?)', 
                         (name, price, type, quantity))
        
        conn.commit()
        conn.close()
        return redirect(url_for('add_item'))

    items = conn.execute('SELECT * FROM items ORDER BY type, name').fetchall()
    conn.close()
    return render_template('edit_item.html', items=items)

@app.route('/edit_item/<int:item_id>', methods=['GET'])
def edit_item(item_id):
    conn = get_db_connection()
    item = conn.execute('SELECT * FROM items WHERE id = ?', (item_id,)).fetchone()
    items = conn.execute('SELECT * FROM items ORDER BY type, name').fetchall()
    conn.close()
    return render_template('edit_item.html', item=item, items=items)

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

@app.route('/export_inventory', methods=['GET'])
def export_inventory():
    conn = get_db_connection()
    items = conn.execute('SELECT * FROM items ORDER BY type, name').fetchall()
    conn.close()

    # Create a CSV file with a filename based on the current date and time
    current_time = datetime.now(pytz.timezone('Asia/Manila'))
    filename = current_time.strftime('%Y-%m-%d_%H-%M-%S_inventory.csv')
    csv_file = f'/tmp/{filename}'

    # Write inventory data to CSV file
    with open(csv_file, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['ID', 'Name', 'Price', 'Type', 'Quantity'])
        for item in items:
            writer.writerow([item['id'], item['name'], item['price'], item['type'], item['quantity']])

    # Send the file as a download
    return send_file(csv_file, as_attachment=True, download_name=filename)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)