from app import app


from flask_hashing import Hashing
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for
import re
from datetime import datetime, date
import mysql.connector
from mysql.connector import FieldType
import connect

import hashlib
import os
from flask import session

hashing = Hashing(app)

app.secret_key = '111'


dbconn = None
connection = None

def getCursor():
    global dbconn
    global connection
    connection = mysql.connector.connect(user=connect.dbuser, \
    password=connect.dbpass, host=connect.dbhost, auth_plugin='mysql_native_password',\
    database=connect.dbname, autocommit=True)
    dbconn = connection.cursor()
    return dbconn



# #################### ADMIN VIEW ######################


######## Managing Mariners 

# ADDING

@app.route('/add_mariner', methods=['GET', 'POST'])
def add_mariner():
    if request.method == 'POST':
        
        # obtain data from form
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        address = request.form['address']
        email = request.form['email']
        phone_number = request.form['phone_number']
        status = request.form['status']
        password = request.form['password']
        

        date_joined = datetime.now().date()

        # Hash the password with salt
        hashed_password = hashing.hash_value(password, salt="bbb")


        # connect to the database

        connection = getCursor() 
        
        sql = """INSERT INTO mariners (first_name, last_name, address, email, phone_number, 
            date_joined, status, password) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"""
        
        parameters = (first_name, last_name, address, email, phone_number, date_joined, status, hashed_password)
        connection.execute(sql, parameters)

        return render_template('action_success.html')
    
    return render_template('add_mariner.html')







# DELETING

@app.route('/delete_mariner', methods=['GET', 'POST'])
def delete_mariner():
    if request.method == 'POST':
        item_to_delete = request.form.get('mariner_id')

        connection =  getCursor() 
        sql = "DELETE FROM mariners WHERE mariner_id = %s;"
        connection.execute(sql, (item_to_delete,))

        return render_template('action_success.html')
    

     # Sending list of Mariner ID to html

    connection = getCursor()
    connection.execute("SELECT mariner_id, first_name, last_name FROM mariners;")
    mariner_ids = connection.fetchall()

                
    
    return render_template('delete_mariner.html', mariner_ids=mariner_ids)






# UPDATING mariner

@app.route('/update_mariner', methods=['GET', 'POST'])
def update_mariner():

    if request.method == 'POST':
        # obtain data from form
        mariner_id = request.form.get('mariner_id')

        connection = getCursor()


        # obtain data with the chosen mariner
        sql = "SELECT * FROM mariners WHERE mariner_id = %s;"
        connection.execute(sql, (mariner_id,))
        original_data = connection.fetchone()

        today_date = date.today().isoformat()


        return render_template('update_mariner.html', original_data=original_data, today_date=today_date)
    
    
    return render_template('dashboard.html')


@app.route('/submit_update_mariner', methods=['POST'])
def submit_update_mariner():
    if request.method == 'POST':
        # Get updated data from the form
        
        mariner_id = request.form.get('mariner_id')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        address = request.form.get('address')
        email = request.form.get('email')
        phone_number = request.form.get('phone_number')
        date_joined = request.form.get('date_joined')
        status = request.form.get('status')
        password = request.form.get('password')



        # Establish database connection
        connection = getCursor()

        # Update the database with the new data
        sql = """UPDATE mariners SET first_name = %s, last_name = %s, address = %s, email = %s, 
            phone_number = %s, date_joined = %s, status = %s WHERE mariner_id = %s;"""
        parameters = (first_name, last_name, address, email, phone_number, date_joined, status, mariner_id)
        connection.execute(sql, parameters)
        

        
        return render_template('action_success.html')



# # ---------------------------------------------------------------------



######### managing staff


# ADDING

@app.route('/add_staff', methods=['GET', 'POST'])
def add_staff():
    if request.method == 'POST':
        
        # obtain data from form
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        
        email = request.form['email']
        work_phone = request.form['work_phone']
        position = request.form['position']
        department = request.form['department']
        status = request.form['status']
        password = request.form['password']
        

        hire_date = datetime.now().date()

        # Hash the password with salt
        hashed_password = hashing.hash_value(password, salt="bbb")


        # connect to the database

        connection = getCursor() 
        
        sql = """INSERT INTO staff (first_name, last_name, email, work_phone, hire_date, position, 
            department, status, password) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"""
        
        parameters = (first_name, last_name, email, work_phone, hire_date, position, department, status, hashed_password)
        connection.execute(sql, parameters)

        return render_template('action_success.html')
    
    return render_template('add_staff.html')



# viewing

@app.route('/view_staff', methods=['GET', 'POST'])
def view_staff():
    
    connection = getCursor() 
    connection.execute("SELECT * FROM staff;")
    staff = connection.fetchall()

    # Sending list of Staff ID Number to dashboards.html

    connection = getCursor()
    connection.execute("SELECT staff_number, first_name, last_name FROM staff;")
    staff_numbers = connection.fetchall()
    
    return render_template('view_staff.html', staff=staff, staff_numbers=staff_numbers)


# DELETING

@app.route('/delete_staff', methods=['GET', 'POST'])
def delete_staff():
    if request.method == 'POST':
        item_to_delete = request.form.get('staff_number')

        connection =  getCursor() 
        sql = "DELETE FROM staff WHERE staff_number = %s;"
        connection.execute(sql, (item_to_delete,))

        return render_template('action_success.html')
    
    # Sending list of Staff ID Number to dashboards.html

    connection = getCursor()
    connection.execute("SELECT staff_number, first_name, last_name FROM staff;")
    staff_numbers = connection.fetchall()
    
    return render_template('delete_staff.html', staff_numbers=staff_numbers)






# UPDATING staff info

@app.route('/update_staff', methods=['GET', 'POST'])
def update_staff():

    if request.method == 'POST':
        # obtain data from form
        staff_number = request.form.get('staff_number')

        connection = getCursor()


        # obtain data with the chosen staff_number
        sql = "SELECT * FROM staff WHERE staff_number = %s;"
        connection.execute(sql, (staff_number,))
        original_data = connection.fetchone()

        today_date = date.today().isoformat()


        return render_template('update_staff.html', original_data=original_data, today_date=today_date)
    
    
    return render_template('dashboard.html')


@app.route('/submit_update_staff', methods=['POST'])
def submit_update_staff():
    if request.method == 'POST':
        # Get updated data from the form
        
        staff_number = request.form.get('staff_number')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        email = request.form.get('email')
        work_phone = request.form.get('work_phone')
        hire_date = request.form.get('hire_date')
        position = request.form.get('position')
        department = request.form.get('department')
        status = request.form.get('status')
        password = request.form.get('password')



        # Establish database connection
        connection = getCursor()

        # Update the database with the new data
        sql = """UPDATE staff SET first_name = %s, last_name = %s, email = %s, 
        work_phone = %s, hire_date = %s, position = %s, department = %s, status = %s 
        WHERE staff_number = %s;"""
        parameters = (first_name, last_name, email, work_phone, hire_date, position, department, status, staff_number)
        connection.execute(sql, parameters)
        

        
        return render_template('action_success.html')
