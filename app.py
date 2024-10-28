from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os

@app.route('/make_transaction', methods=['POST'])
def make_transaction():
    item_ids = request.form.getlist('item_id')
    money_received = float(request.form['money_received'])
    conn = get_db_connection()
    total = 0
    items_purchased = []

    for item_id in item_ids:
        item = conn.execute('SELECT * FROM items WHERE id = ?', (item_id,)).fetchone()
        total += item['price']
        items_purchased.append((item_id, item['name'], item['price']))

    change = max(0, money_received - total)
    purchase_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    try:
        conn.execute('INSERT INTO transactions (total, money_received, change, time) VALUES (?, ?, ?, ?)',
                     (total, money_received, change, purchase_time))
        transaction_id = conn.execute('SELECT last_insert_rowid()').fetchone()[0]

        for item in items_purchased:
            conn.execute('INSERT INTO invoices (transaction_id, item_name, item_price) VALUES (?, ?, ?)',
                         (transaction_id, item[1], item[2]))

        conn.commit()

        # Create PDF for the transaction
        pdf_file = f'transaction_{transaction_id}.pdf'
        c = canvas.Canvas(pdf_file, pagesize=letter)
        width, height = letter
        c.drawString(100, height - 50, f'Transaction ID: {transaction_id}')
        c.drawString(100, height - 70, f'Time: {purchase_time}')
        c.drawString(100, height - 90, f'Money Received: ${money_received:.2f}')
        c.drawString(100, height - 110, f'Total: ${total:.2f}')
        c.drawString(100, height - 130, f'Change: ${change:.2f}')
        c.drawString(100, height - 150, 'Items Purchased:')

        y = height - 170
        for item in items_purchased:
            c.drawString(100, y, f'{item[1]}: ${item[2]:.2f}')
            y -= 20

        c.save()

        return send_file(pdf_file, as_attachment=True)
    except Exception as e:
        print(f"Error during transaction processing: {e}")
        return "An error occurred while processing the transaction.", 500
    finally:
        conn.close()