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

from flask import current_app


import hashlib
import os
from flask import session
import base64
from werkzeug.utils import secure_filename

app.config['UPLOAD_FOLDER'] = '/path/to/upload/folder'

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



# #################### STAFF VIEW ####################

# staff/admin users manage their own profiles

# send existing values to the form

@app.route('/manage_staffadmin')
def manage_staffadmin():

    connection = getCursor()
    email = session['email']
    sql = """SELECT *
            FROM (
                SELECT staff_number, first_name, last_name, email, work_phone, hire_date, position, department, status, password
                FROM staff
                UNION
                SELECT staff_number, first_name, last_name, email, work_phone, hire_date, position, department, status, password
                FROM admin
            ) AS combined_tables
            WHERE email = %s;"""
    connection.execute(sql, (email,))
    original_data = connection.fetchone()



    return render_template('manage_staffadmin.html', original_data=original_data)
    
    
    

# update database with updated values

@app.route('/manage_staffadmin_submit', methods=['POST'])
def manage_staffadmin_submit():
    if request.method == 'POST':

        # getting data from form

        staff_number = request.form['staff_number']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        work_phone = request.form['work_phone']
        hire_date = request.form['hire_date']
        position = request.form['position']
        department = request.form['department']
        status = request.form['status']

        connection = getCursor()

        # try updating staff table
        sql = """UPDATE staff SET first_name=%s, last_name=%s, email=%s, work_phone=%s, 
            hire_date=%s, position=%s, department=%s, status=%s WHERE staff_number = %s;"""
        
        parameters = (first_name, last_name, email, work_phone, hire_date, position, department, status, staff_number)
  
        connection.execute(sql, parameters)
        staff_update_count = connection.rowcount

        if staff_update_count == 0:
            # if it does not exit in staff table, try in admin
            sql = """UPDATE admin SET first_name=%s, last_name=%s, email=%s, work_phone=%s, 
            hire_date=%s, position=%s, department=%s, status=%s WHERE staff_number = %s"""
            parameters = (first_name, last_name, email, work_phone, hire_date, position, department, status, staff_number)
        
            connection.execute(sql, parameters)

        return render_template('action_success.html')
       






## ------------------------------------------------------------

# view a list of mariners 
    
@app.route('/view_mariners')
def view_mariners():
    # connect to the database and get data
    connection = getCursor() 
    connection.execute("SELECT * FROM mariners;")
    mariners_info = connection.fetchall()

    # Sending list of Mariner ID to dashboards.html

    connection = getCursor()
    connection.execute("SELECT mariner_id, first_name, last_name FROM mariners;")
    mariner_ids = connection.fetchall()

   

    return render_template('view_mariners.html', mariners_info = mariners_info, mariner_ids=mariner_ids)




######## Managing the guide 

# ADDING

@app.route('/add_guide', methods=['GET', 'POST'])
def add_guide():
    if request.method == 'POST':
        # ocean_id = request.form.get('ocean_id')
        ocean_item_type = request.form.get('ocean_item_type')
        present_in_nz = request.form.get('present_in_nz')
        common_name = request.form.get('common_name')
        scientific_name = request.form.get('scientific_name')
        key_characteristics = request.form.get('key_characteristics')
        biology_description = request.form.get('biology_description')
        threats = request.form.get('threats')
        location = request.form.get('location')
        primary_image = request.form.get('primary_image')
        secondary_image = request.form.get('secondary_image')


        # connect to the database

        connection = getCursor() 
        
        sql = """INSERT INTO oceanpestsdiseases (OceanItemType, PresentInNZ, CommonName, 
                ScientificName, KeyCharacteristics, BiologyDescription, Threats, Location, 
                PrimaryImage, SecondaryImage) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
        
        parameters = (ocean_item_type, present_in_nz, common_name, scientific_name, key_characteristics, biology_description, threats, location, primary_image, secondary_image)
        connection.execute(sql, parameters)

        return render_template('action_success.html')

    
    static_files = os.listdir(os.path.join(current_app.root_path, 'static'))        # this works both local and pa
       
    
    return render_template('add_guide.html', static_files=static_files)









# DELETING

@app.route('/delete_guide', methods=['GET', 'POST'])
def delete_guide():
    if request.method == 'POST':
        item_to_delete = request.form.get('ocean_id')

        connection = getCursor() 
        sql = "DELETE FROM oceanpestsdiseases WHERE oceanID = %s;"
        connection.execute(sql, (item_to_delete,))

        return render_template('action_success.html')
    

    # Sending list of Ocean ID to dashboards.html

    connection = getCursor()
    connection.execute("SELECT oceanID, CommonName FROM oceanpestsdiseases;")
    ocean_ids = connection.fetchall()
    
    return render_template('delete_guide.html', ocean_ids=ocean_ids)






# UPDATING

# sending existing value to display

@app.route('/update_guide', methods=['GET', 'POST'])
def update_guide():

    if request.method == 'POST':
        # obtain data from form
        ocean_id = request.form.get('ocean_id')

        connection = getCursor()


        # obtain data with the chosen oceanID
        sql = "SELECT * FROM oceanpestsdiseases WHERE oceanID = %s;"
        connection.execute(sql, (ocean_id,))
        original_data = connection.fetchone()

        
        static_files = os.listdir(os.path.join(current_app.root_path, 'static'))                # this works both local and pa


        return render_template('update_guide.html', original_data=original_data, static_files=static_files)
    
    

    return render_template('dashboard.html')

# update database

@app.route('/submit_update_guide', methods=['POST'])
def submit_update_guide():
    if request.method == 'POST':
        # Get updated data from the form
        
        ocean_id = request.form.get('ocean_id')
        ocean_item_type = request.form.get('ocean_item_type')
        present_in_nz = request.form.get('present_in_nz')
        common_name = request.form.get('common_name')
        scientific_name = request.form.get('scientific_name')
        key_characteristics = request.form.get('key_characteristics')
        biology_description = request.form.get('biology_description')
        threats = request.form.get('threats')
        location = request.form.get('location')
        primary_image = request.form.get('primary_image')
        secondary_image = request.form.get('secondary_image')


        # Establish database connection
        connection = getCursor()

        # Update the database with the new data
        sql = """UPDATE oceanpestsdiseases SET OceanItemType = %s, PresentInNZ = %s, CommonName = %s, 
        ScientificName = %s, KeyCharacteristics = %s, BiologyDescription = %s, Threats = %s, 
        Location = %s, PrimaryImage = %s, SecondaryImage = %s WHERE oceanID = %s;"""
        parameters = (ocean_item_type, present_in_nz, common_name, scientific_name, key_characteristics, biology_description, threats, location, primary_image, secondary_image, ocean_id)
        connection.execute(sql, parameters)
        

        
        return render_template('action_success.html')



# DASHBOARD redirection

@app.route('/dashboard')
def dashboard():

    # sending list of mariner_ids to dashboard.html
    connection = getCursor()
    connection.execute("SELECT mariner_id, first_name, last_name FROM mariners;")
    mariner_ids = connection.fetchall()



    # Sending list of Staff ID Number to dashboards.html

    connection = getCursor()
    connection.execute("SELECT staff_number, first_name, last_name FROM staff;")
    staff_numbers = connection.fetchall()



    # sending list of ocean_ids to dashboard.html

    connection = getCursor()
    connection.execute("SELECT oceanID, CommonName FROM oceanpestsdiseases;")
    ocean_ids = connection.fetchall()
    
    return render_template('dashboard.html', mariner_ids=mariner_ids, ocean_ids=ocean_ids, staff_numbers =staff_numbers )


# ---------------------------------------------------