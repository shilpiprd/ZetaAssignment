from flask import Flask, render_template, request, redirect, jsonify
import mysql.connector
from mysql.connector import errorcode
from datetime import datetime, timezone
import mysql.connector


app = Flask(__name__)

# MySQL connection config

# conn = mysql.connector.connect(
#     host='localhost',
#     user='root',
#     password='NewPass123!',
#     database='bank_db'
# )
# c = conn.cursor() 

app = Flask(__name__) 

@app.route('/', methods = ['GET', 'POST']) 
def customer_action(): 

    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='NewPass123!',
        database='bank_db'
    )
    c = conn.cursor() 

    if request.method == 'POST':
        customer_id = request.form['customer_id']
        pin = request.form['pin']
        card_no = request.form['card_no']
        card_type = request.form['card_type'].lower() 

 

        c.execute('SELECT pin FROM bank WHERE customer_id = %s AND card_no = %s AND card_type = %s', (customer_id, card_no, card_type))
        # c.execute('SELECT pin, customer_id, card_type FROM bank WHERE customer_id = %s AND card_no = %s AND card_type = %s', (customer_id,card_no,card_type,))
        #add code to handle case where customerId or card_no doesn't match. 
        
        row = c.fetchone() 
        # conn.close()
        if not row: 
            # print('the not row thing runs')
            conn.close() 
            return "Customer not found", 404 

        # stored_pin, customer_id, card_type = row  
        stored_pin = row[0]

        if pin != str(stored_pin): 
            conn.close()
            return "Invalid Pin", 401 

        #================
        try: 
            # c.execute('BEGIN TRANSACTION')
        #now select actions on basis of credit and debit. 
            if card_type == 'credit': 
                # print( f"Your account balance is : {balance}" )
                credit_action = request.form['credit_action']
                c.execute('SELECT amount FROM bank WHERE customer_id = %s AND card_no = %s', (customer_id, card_no))
                balance = c.fetchone()[0]

                if credit_action == 'check_balance': 
                    balance_current = balance
                    conn.close()
                    return f"Your current debt is: {balance_current}"
                elif credit_action == 'withdrawal': 
                    #implemnt atomicity + concurrency here. 
                    amount_withdrawn = float(request.form['withdraw_amount'])
                    new_balance = float(balance) + amount_withdrawn + 500
                    c.execute('UPDATE bank SET amount = %s WHERE customer_id = %s AND card_no = %s', (new_balance, customer_id, card_no)) #finish balance key with new_balance. 
                    conn.commit() 
                    conn.close() 
                    return f"Withdrawl successful. 500 Fine Applied. New debt: {new_balance}"

            elif card_type == 'debit':
                debit_action = request.form['debit_action']
                c.execute('SELECT amount FROM bank WHERE customer_id = %s AND card_no = %s', (customer_id, card_no))
                balance = c.fetchone()[0]

                if debit_action == 'balance':
                    balance_current = balance 
                    conn.close()
                    return f"Your current saving account balance is: {balance_current}" 
                
                elif debit_action == 'withdrawal': 
                    amount_withdrawn = float(request.form['withdrawn_amount'])
                    if balance < amount_withdrawn: 
                        raise Exception("Insufficient Funds.")
                    
                    new_balance = balance - amount_withdrawn 

                    c.execute('UPDATE bank SET amount = %s WHERE customer_id = %s AND card_no = %s', (new_balance, customer_id, card_no))     #finish the update st. here. 
                    conn.commit() 
                    conn.close() 
                    return f"Withdrawl successful. New balance: {new_balance}"
                
                elif debit_action == 'cash_transfer': 
                    #implemtn rollback , proper update statemnets and atomicity,concurrency heere. 
                    amount_transfer = float(request.form['amount_transfer'])
                    receiver_bankacc_no = request.form['receiver_bankacc_no']

                    if balance < amount_transfer: 
                        raise Exception("Insufficient funds.")
                    
                    new_balance = balance - amount_transfer 

                    c.execute("UPDATE bank SET amount = %s WHERE customer_id = %s AND card_no = %s", (new_balance, customer_id, card_no))
                    
                    #credit to receiver 
                    c.execute("SELECT amount FROM bank WHERE card_no = %s AND card_type = %s", (receiver_bankacc_no, 'debit'))
                    receiver_initial = c.fetchone() 
                    if not receiver_initial: 
                        raise Exception("Receiver account not found")
                    
                    receiver_new_balance = receiver_initial[0] + amount_transfer 
                    c.execute("UPDATE bank SET amount = %s WHERE card_no = %s AND card_type = %s", (receiver_new_balance,receiver_bankacc_no, 'debit'))

                    conn.commit() 
                    conn.close() 
                    
                    return "Amount Credited successfully. "

            else: 
                conn.close() 
                return "invalid action selected.", 400
        except Exception as e: 
            conn.rollback() 
            conn.close() 
            return f"Error: {str(e)}", 500
    else: 
        return render_template('querytask3.html')
    

if __name__ == '__main__':
    app.run(debug = True, port = 5005)
