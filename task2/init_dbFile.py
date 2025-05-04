from flask import Flask, render_template, request, redirect , jsonify
import sqlite3 
from datetime import datetime , timezone
import time 
# import jsonify 

# print('imports are done. ')

app = Flask(__name__) 

def init_db(): 
    conn = sqlite3.connect('customer_info.db') 
    c = conn.cursor() #conn.cursor/.execute... not sqlite specific -> they're just following pthon db api
    #in sqlite, REAL refers to float. Also defining data type below is just for clarity.
    c.execute(
            '''
            CREATE TABLE IF NOT EXISTS customer_info (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id TEXT NOT NULL, 
            amount REAL NOT NULL,        
            pin INTEGER NOT NULL   
            )
            '''
            #the last line ensures duplicate customer id and transaction cant be added.
            )
    conn.commit() 
    conn.close() 
    print("Database Initialized.")

init_db()

@app.route('/', methods = ['GET', 'POST'])
def index(): 
    if request.method == 'POST': 
        customer_id = request.form['customer_id']
        pin = request.form['pin']
        try:
            amount = float(request.form['amount'])
        except ValueError:
            return 'Invalid amount! Please enter a number.'

        if not customer_id.isalnum():
            return 'Invalid customer ID! Must be alphanumeric.'
        
        if not pin.isdigit(): 
            return "Invalid pin. Must be numeric"
        # Ensure description is not empty
        # if not description.strip():
        #     return 'Description cannot be empty!'

        conn = sqlite3.connect('customer_info.db') 
        c = conn.cursor() 
        #c execute is a very important sql command since it actually decided wht we send to the database. 
        c.execute(
                ''' 
                INSERT INTO customer_info (customer_id, pin, amount)
                VALUES (?, ?, ?)
                  ''', (customer_id, pin, amount)
                  )
        conn.commit() 
    return render_template('htmlForm.html')

if __name__ == '__main__':
    app.run(debug = True)