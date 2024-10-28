<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>H & S Ramyeon</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #f3e5f5;
            color: #4a148c;
            max-width: 800px;
            margin: auto;
            padding: 20px;
        }
        h1 {
            text-align: center;
            font-size: 32px;
            color: #6a1b9a;
        }
        nav {
            display: flex;
            justify-content: center;
            gap: 20px;
            margin-bottom: 20px;
        }
        nav a {
            padding: 10px 15px;
            background-color: #8e24aa;
            color: white;
            text-decoration: none;
            border-radius: 5px;
        }
        nav a:hover {
            background-color: #7b1fa2;
        }
        .item-type {
            margin-top: 10px;
            padding: 8px;
            background-color: #e1bee7;
            border-radius: 8px;
        }
        .item-type h3 {
            color: #4a148c;
            font-size: 18px;
            margin: 0;
        }
        #review-section {
            background-color: #e0e0e0;
            padding: 10px;
            border-radius: 8px;
            margin-top: 10px;
        }
        button {
            background-color: #8e24aa;
            color: white;
            border: none;
            cursor: pointer;
            border-radius: 5px;
            padding: 10px 20px;
        }
        button:hover {
            background-color: #7b1fa2;
        }
        .quantity-input {
            width: 4ch;
            text-align: center;
        }
    </style>
    <script>
        function updateReview() {
            const reviewSection = document.getElementById('review-section');
            reviewSection.innerHTML = '';
            let total = 0;

            document.querySelectorAll('.item-row').forEach(row => {
                const checkbox = row.querySelector('input[type="checkbox"]');
                if (checkbox.checked) {
                    const price = parseFloat(checkbox.getAttribute('data-price'));
                    const quantityInput = document.createElement('input');
                    quantityInput.type = 'number';
                    quantityInput.name = 'quantity';
                    quantityInput.value = 1;
                    quantityInput.min = 1;
                    quantityInput.className = 'quantity-input';
                    quantityInput.onchange = calculateTotal;

                    const quantityContainer = document.createElement('div');
                    quantityContainer.textContent = `${checkbox.dataset.name}: ₱${price} `;
                    quantityContainer.appendChild(quantityInput);
                    reviewSection.appendChild(quantityContainer);
                }
            });
            calculateTotal();
        }

        function calculateTotal() {
            let total = 0;
            document.querySelectorAll('#review-section input[type="number"]').forEach(input => {
                const price = parseFloat(input.parentElement.textContent.split('₱')[1]);
                total += price * (parseInt(input.value) || 1);
            });
            document.getElementById('total').innerText = 'Total: ₱' + total.toFixed(2);
            calculateChange();
        }

        function calculateChange() {
            const total = parseFloat(document.getElementById('total').innerText.replace('Total: ₱', '')) || 0;
            const moneyReceived = parseFloat(document.getElementById('money_received').value) || 0;
            const change = Math.max(0, moneyReceived - total);
            document.getElementById('change').innerText = 'Change: ₱' + change.toFixed(2);
        }
    </script>
</head>
<body>
    <h1>H & S Ramyeon</h1>

    <nav>
        <a href="/add_item">Edit Items</a>
        <a href="/invoices">View Invoices</a>
    </nav>

    <h2>Available Items</h2>

    <form action="/make_transaction" method="POST">
        {% for type in ['Soup Base', 'Stir Fry', 'Cups', 'Toppings', 'Sweets', 'Drinks'] %}
        <div class="item-type">
            <h3>{{ type }}</h3>
            <ul>
                {% for item in items %}
                {% if item['type'] == type %}
                <li class="item-row">
                    <input type="checkbox" name="item_id" value="{{ item['id'] }}" data-name="{{ item['name'] }}" data-price="{{ item['price'] }}" onchange="updateReview()">
                    {{ item['name'] }}: ₱{{ item['price'] }}
                </li>
                {% endif %}
                {% endfor %}
            </ul>
        </div>
        {% endfor %}

        <div id="review-section">
            <!-- Selected items with quantities will appear here -->
        </div>

        <div id="total">Total: ₱0.00</div>

        <label for="money_received">Money:</label>
        <input type="number" step="0.01" id="money_received" name="money_received" oninput="calculateChange()">
        <div id="change">Change: ₱0.00</div>

        <button type="submit">Make Transaction</button>
    </form>
</body>
</html>