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
    # Connect to the database
    conn = get_db_connection()
    
    # Create tables if they don't exist
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

    # List of items to be added to the database if they don't already exist
    items = [
        # Soup Base
        ("Cheese Ramen Spicy", 99, "Soup Base"),
        ("Nongshim", 89, "Soup Base"),
        ("Ottogi Cheese Ramen", 91, "Soup Base"),
        ("Nongshim JJWANG", 129, "Soup Base"),
        ("SOON Ramen", 99, "Soup Base"),
        ("JIN Ramen", 89, "Soup Base"),
        # Stir Fry
        ("Buldak Carbonara", 129, "Stir Fry"),
        ("Buldak Black", 129, "Stir Fry"),
        ("Buldak 2X Spicy", 129, "Stir Fry"),
        ("Cheese Ramen Stir Fry", 129, "Stir Fry"),
        # Cups
        ("JIN Ramen Cup", 63, "Cups"),
        ("Shrimp Cup Ramen Small", 52, "Cups"),
        ("Nongshim Squid Jampong Cup", 59, "Cups"),
        ("Paldo Pororo Cup", 59, "Cups"),
        # Toppings
        ("Raw Egg", 15, "Toppings"),
        ("Boiled Egg", 19, "Toppings"),
        ("Sliced Cheese", 15, "Toppings"),
        ("Lobster Ball", 19, "Toppings"),
        ("Lobster Stick", 15, "Toppings"),
        ("Fish Cake", 15, "Toppings"),
        ("Ham", 15, "Toppings"),
        ("Golden Cheese Ball", 15, "Toppings"),
        ("Crab Stick", 19, "Toppings"),
        ("Fishball", 15, "Toppings"),
        ("Kimchi", 19, "Toppings"),
        ("Namkwang Seaweed", 19, "Toppings"),
        ("Shabu2x Mix", 29, "Toppings"),
        ("Sajo Gochujang", 76, "Toppings"),
        ("Ssamjang", 68, "Toppings"),
        ("Sanjo Doenjang", 68, "Toppings"),
        ("Lotte Luncheon Meat", 119, "Toppings"),
        # Sweets
        ("Ice Cream Cone", 11, "Sweets"),
        ("Pepero", 59, "Sweets"),
        ("Almond Choco Ball", 69, "Sweets"),
        # Drinks
        ("Ice Talk", 59, "Drinks"),
        ("Welch’s", 70, "Drinks"),
        ("Jinro Soju", 110, "Drinks"),
        ("Binggrae Milk", 59, "Drinks"),
        ("Flavored Yakult", 59, "Drinks"),
        ("Yakult Orig", 39, "Drinks"),
        ("Milkis", 49, "Drinks"),
        ("Chupa Chups", 69, "Drinks"),
        ("Caffee Latte Can", 49, "Drinks")
    ]

    # Insert items into the database if they don't already exist
    for name, price, type_ in items:
        cursor = conn.execute("SELECT * FROM items WHERE name = ? AND price = ? AND type = ?", (name, price, type_))
        if cursor.fetchone() is None:
            conn.execute("INSERT INTO items (name, price, type) VALUES (?, ?, ?)", (name, price, type_))

    conn.commit()  # Commit the changes
    conn.close()  # Close the connection

# Initialize the database
initialize_database()

# Remaining routes for index, add_item, make_transaction, and invoices as previously defined
# (You can copy the rest of the app code as provided in previous steps)