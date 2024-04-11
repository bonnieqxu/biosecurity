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

from flask import jsonify

hashing = Hashing(app)  # create an instance of hashing

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


################ HOME PAGE ################
@app.route('/')
def home():
    return render_template('index.html')                                 # Render the 'base.html' template when the root URL is accessed

@app.route('/sources')                                                  # Sources and references
def sources():
    return render_template('sources.html') 



################ LOGIN & LOGOUT #############
@app.route('/login', methods=['GET', 'POST'])                           # login form
def login():
    if 'email' in session:  
        
        # if user already logged in, redirect to dashboard.html
        return render_template('dashboard.html')

    if request.method == 'POST':

        email = request.form['email']
        password = request.form['password']
   
        connection = getCursor()                                        
        
        
        

        # combining all 3 tables
        sql = """SELECT usergroup, first_name, last_name, email, password, status FROM (
            SELECT 'mariners' AS usergroup, first_name, last_name, email, password, status FROM mariners
            UNION
            SELECT 'staff' AS usergroup, first_name, last_name, email, password, status FROM staff
            UNION
            SELECT 'admin' AS usergroup, first_name, last_name, email, password, status FROM admin
        ) AS all_users WHERE email = %s;"""





        # searching in the database to locate a user
        connection.execute(sql, (email,))
        user = connection.fetchone()

        
        # for successful login, passing the info onto dashboard.html
        if user:

            hashed_password = user[4]
            if hashing.check_value(hashed_password, password, salt='bbb'):


                
                # Check if user status is active
                if user[5] == 'Inactive':
                    # print("User status:", user[5]) 
                    return render_template('login.html', message='Your account is inactive. Please contact the administrator.')

               
                # User is active, proceed with login

                session['usergroup'] = user[0]
                session['first_name'] = user[1]
                session['last_name'] = user[2]
                session['email'] = user[3]
            

                # Sending list of Mariner ID to dashboards.html

                connection = getCursor()
                connection.execute("SELECT mariner_id, first_name, last_name FROM mariners;")
                mariner_ids = connection.fetchall()

                # Sending list of Staff ID Number to dashboards.html

                connection = getCursor()
                connection.execute("SELECT staff_number, first_name, last_name FROM staff;")
                staff_numbers = connection.fetchall()

                # Sending list of Ocean ID to dashboards.html

                connection = getCursor()
                connection.execute("SELECT oceanID, CommonName FROM oceanpestsdiseases;")
                ocean_ids = connection.fetchall()



                return render_template('dashboard.html', usergroup=session['usergroup'], username=session['first_name'], ocean_ids=ocean_ids, mariner_ids=mariner_ids, staff_numbers=staff_numbers)  
        
            # if login fails
            
            else:
                return render_template('login.html', message='Invalid password')
            
        else:
            return render_template('login.html', message='Invalid username')

    return render_template('login.html')




# Logout route
@app.route('/logout')
def logout():
    session.clear()
    message = "You have successfully logged out."
    return render_template('message.html', message = message)
### -------------------------------------------------###





############# NEW MEMBER REGISTER #################

@app.route('/register', methods=['GET', 'POST'])                              # new member registration
def register():
    if request.method == 'POST':

        # getting data from form

        first_name = request.form['first_name']
        last_name = request.form['last_name']
        address = request.form['address']
        email = request.form['email']
        phone_number = request.form['phone_number']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        date_joined = datetime.now().date()                                      # real time
        status = 'active'                                                        # default value is active

       

        if password != confirm_password:
            message = "Passwords do not match."
            return render_template('message.html', message=message)



        # connect to the database
        connection = getCursor()   

        # check if this email has been registered before
        sql_check_email = "SELECT * FROM mariners WHERE email = %s"
        parameters = (email,)
        connection.execute(sql_check_email, parameters)
        existing_user = connection.fetchone()

        if existing_user:
            message = "This email has already been registered. Please use a different email address."
            return render_template('message.html', message=message)
        

        else:

            # Hash the password with salt
            hashed_password = hashing.hash_value(password, salt="bbb")


            # Adding new user info into database
            
            sql = "INSERT INTO mariners (first_name, last_name, address, email, phone_number, password, date_joined, status) VALUES (%s, %s, %s, %s, %s, %s, %s, %s);"
            parameters = (first_name, last_name, address, email, phone_number, hashed_password, date_joined, status)
                
            connection.execute(sql, parameters)

            message = """Congratulations!
            You are successfully registered as a new member of Mariners!"""
                
            return render_template('message.html', message = message)
            
    return render_template('register.html')


# #---------------------------------------------------------

# validate email availability

@app.route("/check_email_availability", methods=["POST"])
def check_email_availability():
    data = request.json
    email = data["email"]
    connection = getCursor()
    sql_check_email = "SELECT * FROM mariners WHERE email = %s"
    parameters = (email,)
    connection.execute(sql_check_email, parameters)
    existing_user = connection.fetchone()
    if existing_user:
        return jsonify({"available": False})
    else:
        return jsonify({"available": True})
