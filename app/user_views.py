from app import app

from flask_hashing import Hashing
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for
from flask import jsonify
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


@app.route('/guide')                                # view the biosecurity guide
def guide():
    connection = getCursor()
    connection.execute("SELECT * FROM oceanpestsdiseases;")
    list = connection.fetchall()

    # Sending list of Ocean ID to dashboards.html

    connection = getCursor()
    connection.execute("SELECT oceanID, CommonName FROM oceanpestsdiseases;")
    ocean_ids = connection.fetchall()
    return render_template('guide.html', list = list, ocean_ids=ocean_ids)



# view full info of selected pest/disease

@app.route('/full_info')
def full_info():
    species = request.args.get('species')

    connection = getCursor()
    sql = "SELECT * FROM oceanpestsdiseases WHERE PrimaryImage = %s;"
    connection.execute(sql, (species,))
    full_info = connection.fetchone()
    return render_template('full_info.html', full_info = full_info)





# ############### MARINER VIEW #################

# mariner users manage their own profile

# send existing data to display
@app.route('/manage_mariner')
def manage_mariner():

    connection = getCursor()
    email = session['email']
    sql = "SELECT * FROM mariners WHERE email = %s;"
    connection.execute(sql, (email,))
    original_data = connection.fetchone()

 
    return render_template('manage_mariner.html', original_data=original_data)
    

# update database
@app.route('/manage_mariner_submit', methods=['POST'])
def manage_mariner_submit():
    if request.method == 'POST':

        # getting data from form

        mariner_id = request.form['mariner_id']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        address = request.form['address']
        email = request.form['email']
        phone_number = request.form['phone_number']
        date_joined = request.form['date_joined']
        status = request.form['status']

        connection = getCursor()

        sql = """UPDATE mariners SET first_name=%s, last_name=%s, address=%s, email=%s,
                 phone_number=%s, date_joined=%s, status=%s WHERE mariner_id = %s"""
        parameters = (first_name, last_name, address, email, phone_number, date_joined, status, mariner_id)
        connection.execute(sql, parameters)

        return render_template('action_success.html')
    


# changing own password
@app.route('/change_password', methods=['GET','POST'])
def change_password():

    

    if 'email' in session:
        email = session['email']
    
        if request.method == 'POST':
            # obtain new password from form
            new_password = request.form['new_password']

            # hashing new passwords
            hashed_password = hashing.hash_value(new_password, salt="bbb")

            # update database
            connection = getCursor()
            
            sql = """SELECT 'mariners' AS usergroup, email FROM mariners WHERE email = %s
                    UNION ALL
                    SELECT 'staff' AS usergroup, email FROM staff WHERE email = %s
                    UNION ALL
                    SELECT 'admin' AS usergroup, email FROM admin WHERE email = %s"""
            parameters = (email, email, email)
            connection.execute(sql, parameters)
            user = connection.fetchone()

            if user:
    
                usergroup = user[0]

                if usergroup == 'mariners':
                    connection.execute('UPDATE mariners SET password = %s WHERE email = %s', (hashed_password, email))
                elif usergroup == 'staff':
                    connection.execute('UPDATE staff SET password = %s WHERE email = %s', (hashed_password, email))
                elif usergroup == 'admin':
                    connection.execute('UPDATE admin SET password = %s WHERE email = %s', (hashed_password, email))

            
            return render_template('action_success.html')
    
        return render_template('change_password.html')
    return redirect(url_for('login'))
    





# validate user input 

@app.route('/validate_current_password', methods=['POST'])
def validate_current_password():
    if 'email' in session:
        email = session['email']
        current_password = request.json['current_password']

        # Retrieve hashed password from the database
        connection = getCursor()
        sql = "SELECT password FROM mariners WHERE email = %s"
        connection.execute(sql, (email,))
        mariners_db_password = connection.fetchone()

        # Retrieve hashed password from the database for staff
        sql = "SELECT password FROM staff WHERE email = %s"
        connection.execute(sql, (email,))
        staff_db_password = connection.fetchone()

        # Retrieve hashed password from the database for admin
        sql = "SELECT password FROM admin WHERE email = %s"
        connection.execute(sql, (email,))
        admin_db_password = connection.fetchone()

        # Check if the entered current password matches the one in the database
        if mariners_db_password and hashing.check_value(mariners_db_password[0], current_password, salt='bbb'):
            return jsonify({"valid": True})
        elif staff_db_password and hashing.check_value(staff_db_password[0], current_password, salt='bbb'):
            return jsonify({"valid": True})
        elif admin_db_password and hashing.check_value(admin_db_password[0], current_password, salt='bbb'):
            return jsonify({"valid": True})
        else:
            return jsonify({"valid": False})
    
    # If user is not logged in, return unauthorized status
    return jsonify({"valid": False}), 401
