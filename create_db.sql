import sqlite3

def add_items_to_database():
    conn = sqlite3.connect('pos_database.db')  # Ensure this path matches your database file's location
    cursor = conn.cursor()

    # List of items from the image, formatted as (name, price, type)
    items = [
        # Soup Base
        ("Cheese Ramen Spicy", 99, "Soup Base"),
        ("Nongshim", 89, "Soup Base"),
        ("Ottogi Cheese Ramen", 99, "Soup Base"),
        ("Nongshim Jjwang", 129, "Soup Base"),
        ("Soon Ramen", 129, "Soup Base"),
        ("Jin Ramen", 89, "Soup Base"),
        # Stir Fry
        ("Buldak Black", 129, "Stir Fry"),
        ("Buldak 2X Spicy", 129, "Stir Fry"),
        ("Cheese Ramen Stir Fry", 129, "Stir Fry"),
        # Cups
        ("Jin Ramen Cup", 63, "Cups"),
        ("Shrimp Cup Ramen Small", 52, "Cups"),
        ("Nongshim Squid Jjampong Cup", 55, "Cups"),
        ("Paldo Pororo Cup", 59, "Cups"),
        # Toppings
        ("Raw Egg", 15, "Toppings"),
        ("Boiled Egg", 19, "Toppings"),
        ("Sliced Cheese", 19, "Toppings"),
        ("Lobster Ball", 19, "Toppings"),
        ("Lobster Stick", 19, "Toppings"),
        ("Fish Cake", 15, "Toppings"),
        ("Ham", 15, "Toppings"),
        ("Golden Cheese Ball", 15, "Toppings"),
        ("Crab Stick", 19, "Toppings"),
        ("Fishball", 19, "Toppings"),
        ("Kimchi", 16, "Toppings"),
        ("Jjamkwang Seaweed", 29, "Toppings"),
        ("Shabuzz Mix", 19, "Toppings"),
        # Sweets
        ("Ice Cream Cone", 11, "Sweets"),
        ("Pepero", 59, "Sweets"),
        ("Almond Choco Ball", 69, "Sweets"),
        # Drinks
        ("Ice Talk", 60, "Drinks"),
        ("Welch's", 70, "Drinks"),
        ("Jinro Soju", 68, "Drinks"),
        ("Binggrae Milk", 110, "Drinks"),
        ("Flavored Yakult", 59, "Drinks"),
        ("Yakult Orig", 49, "Drinks"),
        ("Milkis", 39, "Drinks"),
        ("Chupa Chups", 69, "Drinks"),
        ("Caffee Latte Can", 49, "Drinks")
    ]

    # Insert items into the database
    cursor.executemany('INSERT INTO items (name, price, type) VALUES (?, ?, ?)', items)
    conn.commit()  # Commit the changes
    conn.close()  # Close the connection

if __name__ == "__main__":
    add_items_to_database()