from flask import Flask, render_template, request, redirect , jsonify
import sqlite3 
from datetime import datetime , timezone
import time 
# import jsonify 
from model1 import classify_description, recommend_action

# print('imports are done. ')

app = Flask(__name__) 

def init_db(): 
    conn = sqlite3.connect('disputes.db') 
    c = conn.cursor() #conn.cursor/.execute... not sqlite specific -> they're just following pthon db api
    #in sqlite, REAL refers to float. Also defining data type below is just for clarity.
    c.execute(
            '''
            CREATE TABLE IF NOT EXISTS disputes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id TEXT NOT NULL, 
            transaction_id TEXT NOT NULL, 
            amount REAL NOT NULL,           
            description TEXT NOT NULL,  
            timestamp TEXT NOT NULL,
            dispute_category TEXT,
            priority TEXT, 
            recommended_action TEXT,
            status TEXT DEFAULT 'Pending',
            UNIQUE (customer_id, transaction_id)
            )
            '''
            #the last line ensures duplicate customer id and transaction cant be added.
            )
    conn.commit() 
    conn.close() 

init_db()

#flask code below : 
@app.route('/', methods = ['GET', 'POST'])
def index(): 
    if request.method == 'POST': 
        customer_id = request.form['customer_id']
        transaction_id = request.form['transaction_id']
        try:
            amount = float(request.form['amount'])
        except ValueError:
            return 'Invalid amount! Please enter a number.'
        description = request.form['description']
        timestamp = datetime.now(timezone.utc).isoformat()
        
        #before entering into dataset, ensure these since sqlite doesn't strictly enforce ccolumn types.         

        # Ensure customer_id is alphanumeric
        if not customer_id.isalnum():
            return 'Invalid customer ID! Must be alphanumeric.'

        # Ensure description is not empty
        if not description.strip():
            return 'Description cannot be empty!'

        conn = sqlite3.connect('disputes.db') 
        c = conn.cursor() 
        #c execute is a very important sql command since it actually decided wht we send to the database. 
        c.execute(
                ''' 
                INSERT INTO disputes (customer_id, transaction_id, amount, description, timestamp)
                VALUES (?, ?, ?, ?, ?)
                  ''', (customer_id, transaction_id, amount, description, timestamp)
                  )
        conn.commit() 
        # conn.close() 
        # ==========
        #add code for classifying Dispute and Adding priority to DB HERE. 
        try: #call azure model 
            dispute_category = classify_description(description) 
            
            if amount < 5000: 
                priority = "Low"
            elif 5000 <= amount <= 10000: 
                priority = 'Medium' 
            else: 
                priority = 'High'

            #add this back to db 
            c.execute(
                '''
                UPDATE disputes
                SET dispute_category = ?, priority = ? 
                WHERE customer_id = ? AND transaction_id = ?
                ''', (dispute_category, priority, customer_id, transaction_id)
            )
            conn.commit() 
        except Exception as e:
            print(f"Full error: {str(e)}")  # logs full error to console
            conn.close()
            return "Error classifying dispute (check server logs).", 500

        # ============CODE For Recommendation=========== 
        recommendation = recommend_action(description, priority, dispute_category)

        try: 
            c.execute(
                """ 
                UPDATE disputes 
                SET recommended_action = ?
                WHERE customer_id = ? AND transaction_id = ?
                """, (recommendation, customer_id, transaction_id)
            )
            conn.commit() 

        except Exception as e: 
            conn.close() 
            return "Error getting recommended actions", 500
        
        conn.close() 

        return redirect('/success')
    
    return render_template('form1.html')


@app.route('/success') 
def success(): 
    return 'Dispute submitted successfully'

if __name__ == '__main__':
    app.run(debug = True)