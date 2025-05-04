from flask import Flask, render_template, request
import sqlite3
import time
import pandas as pd

app = Flask(__name__)

user_requests = {}
RATE_LIMIT = 5  # max 5 requests
WINDOW_SIZE = 1  # per 1 second window


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        print('Inside POST method')

        customer_id = request.form['customer_id']
        action = request.form['action'].lower()

        current_time = time.time()
        timestamps = user_requests.get(customer_id, [])
        timestamps = [t for t in timestamps if current_time - t < WINDOW_SIZE]

        if len(timestamps) >= RATE_LIMIT:
            return "Rate limit exceeded. Please try again later.", 429

        timestamps.append(current_time)
        user_requests[customer_id] = timestamps

        # Connect once here
        conn = sqlite3.connect('disputes.db')
        c = conn.cursor()
        print(f"Action requested: {action}")

        if action == 'retrieve_disputes':
            print('Retrieving disputes...')
            c.execute(
                "SELECT customer_id, transaction_id, amount, description FROM disputes WHERE customer_id = ?",
                (customer_id,))
            rows = c.fetchall()
            conn.close()

            if not rows:
                return "No past interactions found."

            df = pd.DataFrame(rows, columns=['CustomerID', 'TransactionId', 'Amount', 'Description'])
            table_html = "<h2>Past Interactions</h2>" + df.to_html(index=False)
            return table_html

        elif action == 'submit_dispute':
            transaction_id = request.form['transaction_id']
            try:
                amount = float(request.form['amount'])
            except ValueError:
                conn.close()
                return "Invalid amount. Please enter a number."

            description = request.form['description']
            timestamp = time.strftime('%Y-%m-%d %H:%M:%S')

            c.execute(
                "INSERT INTO disputes (customer_id, transaction_id, amount, description, timestamp) VALUES (?, ?, ?, ?, ?)",
                (customer_id, transaction_id, amount, description, timestamp))
            conn.commit()
            conn.close()
            print('Dispute submitted successfully.')
            return "Dispute submitted successfully."

        else:
            conn.close()
            return "Invalid action selected.", 400

    return render_template('form4.html')


if __name__ == '__main__':
    app.run(debug=True, port=5001)
