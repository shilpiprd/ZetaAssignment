from flask import Flask, render_template, request, redirect , jsonify
import sqlite3 
from datetime import datetime , timezone
import time 
# import jsonify 
from modelfile import state_eligibility
import pandas as pd 

# print('imports are done. ')

app = Flask(__name__) 

@app.route('/', methods = ['GET', 'POST']) 
def customer_action(): 
    if request.method == 'POST':
        customer_id = request.form['customer_id']
        pin = request.form['pin']
        action = request.form['action'] 

        conn = sqlite3.connect('customer_info.db') 
        c = conn.cursor() 

        #retrieve and store the amount and pin for the customer id provided by user. 
        c.execute('SELECT pin, amount FROM customer_info WHERE customer_id = ?', (customer_id,))

        row = c.fetchone() 
        conn.close() 
        print('this lline runs. ')

        if not row: 
            print('the not row thing runs')
            return "Customer not found", 404 

        stored_pin, balance = row 
        if pin != str(stored_pin) : 
            return "Invalid Pin", 401 

        if action == 'check_balance': 
            # print( f"Your account balance is : {balance}" )
            return f"Your account balance is: {balance}"
        
        elif action == 'apply_loan': 
            applicant_income = request.form['applicant_income']
            no_dependables = request.form['dependables'] 
            additional_income = request.form['additional_income']
            loan_period = request.form['loan_period']
            cibil = request.form['cibil']
            loan_amount = request.form['loan_amount']

            status = state_eligibility(applicant_income, no_dependables, additional_income, loan_period, cibil, loan_amount)
            #fill the following information. 

            # print( f"Your loan status is : {status}")
            return f"Your loan status is: {status}"

        
        elif action == 'retrieve_interactions': 
        
            #retrieve description , status, timestamp from the databasee and return it in the form of output. 
            conn2 = sqlite3.connect('disputes.db') 
            c = conn2.cursor() 
            c.execute('SELECT description, status, timestamp FROM disputes WHERE customer_id = ?',(customer_id,))
            rows = c.fetchall()  #is this right multiple rows could be retrieved corresponding to same customer id. 
            conn2.close() 
            #display the output in form of table. 
            if not rows: 
                return "No past interactions found"
            
            df = pd.DataFrame(rows, columns=['Description', 'Status', 'Timestamp'])
            table_html = "<h2>Past Interactions</h2>" + df.to_html(index=False)
            return table_html
        
        else: 
            return "invalid action selected.", 400
        
        # return redirect('/success')

    else: 
        return render_template('customer_portal.html')

# @app.route('/success') 
# def success(): 
#     return 'Information input successfull'

if __name__ == '__main__':
    app.run(debug=True, port=5010)
