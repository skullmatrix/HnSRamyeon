import os
from flask import Flask, request, render_template, redirect, url_for
import sqlite3
from datetime import datetime
import pytz

app = Flask(__name__)

# Database setup - connects to SQLite and creates tables if they don't exist
def get_db_connection():
    conn = sqlite3.connect('pos_database.db')
    conn.row_factory = sqlite3.Row
    return conn

# Route to display and handle adding/updating items
@app.route('/add_item', methods=['GET', 'POST'])
def add_item():
    conn = get_db_connection()

    # Handle form submission for adding or updating items
    if request.method == 'POST':
        item_id = request.form.get('item_id')
        name = request.form['name']
        price = int(request.form['price'])
        type = request.form['type']
        
        if item_id:  # Update existing item
            conn.execute('UPDATE items SET name = ?, price = ?, type = ? WHERE id = ?', (name, price, type, item_id))
        else:  # Add new item
            conn.execute('INSERT INTO items (name, price, type) VALUES (?, ?, ?)', (name, price, type))
        
        conn.commit()
        conn.close()
        return redirect(url_for('add_item'))

    # Fetch all items to display on the Edit Items page
    items = conn.execute('SELECT * FROM items ORDER BY type, name').fetchall()
    conn.close()
    return render_template('add_item.html', items=items)

# Route to load an item for editing
@app.route('/edit_item/<int:item_id>', methods=['GET'])
def edit_item(item_id):
    conn = get_db_connection()
    item = conn.execute('SELECT * FROM items WHERE id = ?', (item_id,)).fetchone()
    items = conn.execute('SELECT * FROM items ORDER BY type, name').fetchall()
    conn.close()
    return render_template('add_item.html', item=item, items=items)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)