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
    conn.close()

initialize_database()

@app.route('/', methods=['GET'])
def index():
    conn = get_db_connection()
    items = conn.execute('SELECT * FROM items ORDER BY type, name').fetchall()
    conn.close()
    return render_template('index.html', items=items)

@app.route('/invoices', methods=['GET'])
def invoices():
    conn = get_db_connection()
    invoices = conn.execute('SELECT * FROM invoices ORDER BY time DESC').fetchall()
    conn.close()
    return render_template('invoices.html', invoices=invoices)

@app.route('/add_item', methods=['GET', 'POST'])
def add_item():
    conn = get_db_connection()
    if request.method == 'POST':
        item_id = request.form.get('item_id')
        name = request.form['name']
        price = int(request.form['price'])
        type = request.form['type']
        quantity = int(request.form.get('quantity', 100))

        if item_id:
            conn.execute('UPDATE items SET name = ?, price = ?, type = ?, quantity = ? WHERE id = ?', 
                         (name, price, type, quantity, item_id))
        else:
            conn.execute('INSERT INTO items (name, price, type, quantity) VALUES (?, ?, ?, ?)', 
                         (name, price, type, quantity))
        
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

if __name__ == '__main__':
    app.run(debug=True)