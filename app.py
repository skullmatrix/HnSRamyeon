
from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime
import sqlite3

app = Flask(__name__)

# Database connection and setup
def init_db():
    connection = sqlite3.connect("database.db")
    cursor = connection.cursor()

    # Ensure items table exists
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            price REAL,
            type TEXT,
            quantity INTEGER
        )
    """)
    connection.commit()

    # Check if items table is empty and insert default data if needed
    cursor.execute("SELECT COUNT(*) FROM items")
    if cursor.fetchone()[0] == 0:
        items = [
            ("Cheese Ramen Spicy", 99, "Soup Base", 5),
            ("Nongshim", 89, "Soup Base", 5),
            ("Ottogi Cheese Ramen", 99, "Soup Base", 5),
            ("Nongshim JJWANG", 129, "Soup Base", 5),
            ("SOON Ramen", 99, "Soup Base", 5),
            ("JIN Ramen", 69, "Soup Base", 5),
            ("Buldak 2X Spicy", 129, "Stir Fry", 5),
            ("Buldak Black", 119, "Stir Fry", 5),
            ("Buldak Carbonara", 109, "Stir Fry", 5),
            ("Cheese Ramen Stir Fry", 109, "Stir Fry", 5),
            ("JIN Ramen Cup", 63, "Cups", 5),
            ("Nongshim Squid Jampong Cup", 55, "Cups", 5),
            ("Paldo Pororo Cup", 59, "Cups", 5),
            ("Shrimp Cup Ramen Small", 52, "Cups", 5),
            ("Boiled Egg", 19, "Toppings", 5),
            ("Crab Stick", 15, "Toppings", 5),
            ("Fish Cake", 15, "Toppings", 5),
            ("Fishball", 15, "Toppings", 5),
            ("Golden Cheese Ball", 15, "Toppings", 5),
            ("Ham", 15, "Toppings", 5),
            ("Kimchi", 10, "Toppings", 5),
            ("Lobster Ball", 19, "Toppings", 5),
            ("Lobster Stick", 15, "Toppings", 5),
            ("Lotte Luncheon Meat", 119, "Toppings", 5),
            ("Namkwang Seaweed", 19, "Toppings", 5),
            ("Raw Egg", 15, "Toppings", 5),
            ("Sajo Gochujang", 76, "Toppings", 5),
            ("Sanjo Doenjang", 68, "Toppings", 5),
            ("Shabu2x Mix", 15, "Toppings", 5),
            ("Sliced Cheese", 19, "Toppings", 5),
            ("Ssamjang", 78, "Toppings", 5),
            ("Almond Choco Ball", 69, "Sweets", 5),
            ("Ice Cream Cone", 10, "Sweets", 5),
            ("Pepero", 59, "Sweets", 5),
            ("Binggrae Milk", 59, "Drinks", 5),
            ("Caffee Latte Can", 49, "Drinks", 5),
            ("Chupa Chups", 69, "Drinks", 5),
            ("Flavored Yakult", 49, "Drinks", 5),
            ("Ice Talk", 60, "Drinks", 5),
            ("Jinro Soju", 110, "Drinks", 5),
            ("Milkis", 49, "Drinks", 5),
            ("Welch’s", 70, "Drinks", 5),
            ("Yakult Orig", 39, "Drinks", 5),
        ]
        cursor.executemany("INSERT INTO items (name, price, type, quantity) VALUES (?, ?, ?, ?)", items)
        connection.commit()

    connection.close()

# Initialize database
init_db()

# In-memory transaction data storage
transactions = []

@app.route('/')
def index():
    connection = sqlite3.connect("database.db")
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM items")
    items = cursor.fetchall()
    connection.close()
    return render_template('index.html', items=items)

@app.route('/make_transaction', methods=['POST'])
def make_transaction():
    connection = sqlite3.connect("database.db")
    cursor = connection.cursor()

    selected_items = request.form.getlist('item')
    money_received = float(request.form['money_received'])
    
    items_purchased = []
    total = 0

    for item_id in selected_items:
        cursor.execute("SELECT * FROM items WHERE id = ?", (item_id,))
        item = cursor.fetchone()
        if item:
            quantity = int(request.form[f'quantity_{item_id}'])
            if quantity > item[4]:  # Check stock
                return "Not enough stock", 400
            new_quantity = item[4] - quantity
            cursor.execute("UPDATE items SET quantity = ? WHERE id = ?", (new_quantity, item_id))
            connection.commit()
            total += item[2] * quantity
            items_purchased.append({"name": item[1], "quantity": quantity, "price": item[2]})

    transaction = {
        "id": len(transactions) + 1,
        "date": datetime.now(),
        "total": total,
        "money_received": money_received,
        "items_purchased": items_purchased,
    }
    transactions.append(transaction)
    connection.close()
    
    return redirect(url_for('invoices'))

@app.route('/invoices')
def invoices():
    return render_template('invoices.html', transactions=transactions)

@app.route('/inventory')
def inventory():
    connection = sqlite3.connect("database.db")
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM items")
    items = cursor.fetchall()
    connection.close()
    return render_template('inventory.html', items=items)

@app.route('/add_item', methods=['POST'])
def add_item():
    connection = sqlite3.connect("database.db")
    cursor = connection.cursor()

    item_id = int(request.form.get('item_id', 0))
    name = request.form['name']
    price = float(request.form['price'])
    item_type = request.form['type']
    quantity = int(request.form.get('quantity', 0))

    if item_id:
        cursor.execute("UPDATE items SET name = ?, price = ?, type = ?, quantity = ? WHERE id = ?",
                       (name, price, item_type, quantity, item_id))
    else:
        cursor.execute("INSERT INTO items (name, price, type, quantity) VALUES (?, ?, ?, ?)",
                       (name, price, item_type, quantity))
    connection.commit()
    connection.close()

    return redirect(url_for('inventory'))

if __name__ == '__main__':
    app.run(debug=True)
