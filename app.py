from flask import Flask, request, jsonify, render_template, redirect, url_for
import sqlite3
import os

app = Flask(__name__)

# Path to the database file
DATABASE_PATH = 'pos_database.db'

# Database connection function
def get_db_connection():
    if not os.path.exists(DATABASE_PATH):
        # If the database doesn't exist, return an error message to initialize it
        raise FileNotFoundError("Database not found. Please run `create_db.py` to initialize the database.")
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    # Main page for creating transactions
    conn = get_db_connection()
    items = conn.execute('SELECT * FROM items').fetchall()
    conn.close()
    return render_template('index.html', items=items)

@app.route('/add_item', methods=['GET', 'POST'])
def add_item():
    # Page for adding new items to the inventory
    if request.method == 'POST':
        name = request.form['name']
        price = request.form['price']
        conn = get_db_connection()
        conn.execute('INSERT INTO items (name, price) VALUES (?, ?)', (name, price))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    return render_template('add_item.html')

@app.route('/inventory')
def inventory():
    # Page to view current inventory levels
    conn = get_db_connection()
    inventory_data = conn.execute("""
        SELECT items.id, items.name, items.price, 
               IFNULL(SUM(inventory.quantity), 0) AS quantity
        FROM items
        LEFT JOIN inventory ON items.id = inventory.item_id
        GROUP BY items.id
    """).fetchall()
    conn.close()
    return render_template('inventory.html', inventory=inventory_data)

@app.route('/add_inventory', methods=['POST'])
def add_inventory():
    data = request.json
    item_id = data['item_id']
    quantity = data['quantity']
    conn = get_db_connection()
    conn.execute('INSERT INTO inventory (item_id, quantity) VALUES (?, ?)', (item_id, quantity))
    conn.commit()
    conn.close()
    return jsonify({'status': 'success'})

@app.route('/create_transaction', methods=['POST'])
def create_transaction():
    data = request.json
    items = data['items']
    total = 0
    conn = get_db_connection()
    for item in items:
        item_id = item['item_id']
        quantity = item['quantity']
        price = conn.execute('SELECT price FROM items WHERE id = ?', (item_id,)).fetchone()['price']
        total += price * int(quantity)
    conn.execute('INSERT INTO transactions (total) VALUES (?)', (total,))
    conn.commit()
    conn.close()
    return jsonify({'status': 'success', 'total': total})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)