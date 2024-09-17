from flask import Flask, request, jsonify, session, redirect, url_for, render_template, abort, make_response
from functools import wraps
import mysql.connector
from datetime import datetime
from flask_session import Session
from werkzeug.security import generate_password_hash, check_password_hash
import string
import random


app = Flask(__name__)

# Flask session configuration
app.config['SECRET_KEY'] = 'your_secret_key'  # Replace with a strong secret key
app.config['SESSION_TYPE'] = 'filesystem'  # Store sessions on the filesystem
Session(app)

# Database Configuration
db_config = {
    'user': 'root',  # Replace with your MySQL username
    'password': '',  # Replace with your MySQL password
    'host': 'localhost',  # Replace with your MySQL host
    'database': 'documenttrackingsystem'
}

# Create a database connection
def get_db_connection():
    conn = mysql.connector.connect(**db_config)
    return conn

def nocache(view):
    @wraps(view)
    def no_cache(*args, **kwargs):
        response = make_response(view(*args, **kwargs))
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '-1'
        return response
    return no_cache

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

# Decorator to check if the user is an admin
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'role' not in session or session['role'] != 1:
            return abort(403)
        return f(*args, **kwargs)
    return decorated_function

# Endpoint for user registration
@app.route('/register', methods=['GET', 'POST'])
def register():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Fetch all schools and offices for dropdown selection
    cursor.execute('SELECT SchoolID, SchoolName FROM SCHOOLS')
    schools = cursor.fetchall()  # Fetch all rows

    cursor.execute('SELECT OfficeID, OfficeName FROM OFFICES')
    offices = cursor.fetchall()  # Fetch all rows

    if request.method == 'POST':
        firstname = request.form['firstname']
        middlename = request.form.get('middlename', None)
        lastname = request.form['lastname']
        idnumber = request.form['idnumber']
        email = request.form['email']
        password = request.form['password']
        role = request.form.get('roles')

        # Hash the password
        hashed_password = generate_password_hash(password)

        # Role-specific handling
        if role == 'admin':
            # Admin registration logic
            try:
                cursor.execute("""
                    INSERT INTO USERS (Firstname, Middlename, Lastname, IDNumber, Email, Password, RoleID)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (firstname, middlename, lastname, idnumber, email, hashed_password, 1))  # Assuming RoleID=1 for Admin
                conn.commit()
                flash('Admin registered successfully!', 'success')
                return redirect(url_for('login'))
            except Exception as e:
                conn.rollback()
                flash(f'Error during admin registration: {e}', 'danger')

        elif role == 'staff':
            office_id = request.form['office']
            try:
                cursor.execute("""
                    INSERT INTO USERS (Firstname, Middlename, Lastname, IDNumber, Email, Password, RoleID, OfficeID)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (firstname, middlename, lastname, idnumber, email, hashed_password, 3, office_id))  # Assuming RoleID=2 for Staff
                conn.commit()
                flash('Staff registered successfully!', 'success')
                return redirect(url_for('login'))
            except Exception as e:
                conn.rollback()
                flash(f'Error during staff registration: {e}', 'danger')

        elif role == 'user':
            school_id = request.form['school']
            if school_id == 'others':
                other_school = request.form.get('other_school')
                # Insert the new school into the SCHOOLS table and get the ID
                cursor.execute("INSERT INTO SCHOOLS (SchoolName) VALUES (%s)", (other_school,))
                conn.commit()
                cursor.execute("SELECT LAST_INSERT_ID()")  # Get the inserted SchoolID
                school_id = cursor.fetchone()[0]

            try:
                cursor.execute("""
                    INSERT INTO USERS (Firstname, Middlename, Lastname, IDNumber, Email, Password, RoleID, SchoolID)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (firstname, middlename, lastname, idnumber, email, hashed_password, 2, school_id))  # Assuming RoleID=3 for User
                conn.commit()
                flash('User registered successfully!', 'success')
                return redirect(url_for('login'))
            except Exception as e:
                conn.rollback()
                flash(f'Error during user registration: {e}', 'danger')

    cursor.close()  # Close the cursor after usage
    conn.close()  # Close the connection after usage
    return render_template('register.html', schools=schools, offices=offices)


# Endpoint for user login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)

            cursor.execute("SELECT * FROM USERS WHERE Email = %s", (email,))
            user = cursor.fetchone()

            if user and check_password_hash(user['Password'], password):
                session['user_id'] = user['UserID']
                session['username'] = user['Firstname']
                session['role'] = int(user['RoleID'])

                # Check the RoleID and redirect accordingly
                if user['RoleID'] == 1:
                    return redirect(url_for('_admin_dashboard'))
                elif user['RoleID'] == 3:  # Replace 2 with the actual RoleID for STAFF
                    return redirect(url_for('_staff_dashboard'))
                else:
                    return redirect(url_for('_users_dashboard'))
            else:
                return "Invalid email or password", 401

        except Exception as e:
            return jsonify({"error": str(e)}), 500

        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    return render_template('login.html')


# Users route to display after login
@app.route('/_users_dashboard')
@login_required
@nocache
def _users_dashboard():
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Fetch document types
        cursor.execute("SELECT DocTypeID, DocTypeName FROM DOCUMENT_TYPE")
        document_types = cursor.fetchall()

        # Fetch offices
        cursor.execute("SELECT OfficeID, OfficeName FROM OFFICES")
        offices = cursor.fetchall()

        # Fetch user details using the user_id from the session
        cursor.execute("SELECT Firstname, Middlename, Lastname FROM USERS WHERE UserID = %s", (session['user_id'],))
        user = cursor.fetchone()

        return render_template('_users_dashboard.html', document_type=document_types, office=offices, user=user)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@app.route('/_admin_dashboard')
@login_required
@admin_required
@nocache
def _admin_dashboard():
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT UserID, Firstname, Lastname, Email, RoleID FROM USERS")
        users = cursor.fetchall()

        return render_template('_admin_dashboard.html', users=users)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@app.route('/_staff_dashboard', methods=['GET'])
def _staff_dashboard():
    # Check if the user is logged in and has a STAFF role
    if 'user_id' in session and session.get('role') == 3:  # Assuming 3 is your STAFF RoleID
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)

            # Fetch user details for the greeting
            cursor.execute("SELECT Firstname, Middlename, Lastname FROM USERS WHERE UserID = %s", (session['user_id'],))
            user = cursor.fetchone()

            # Fetch documents related to the STAFF user
            cursor.execute("SELECT * FROM DOCUMENTS WHERE UserID = %s", (session['user_id'],))
            documents = cursor.fetchall()

            return render_template('_staff_dashboard.html', documents=documents, user=user)

        except Exception as e:
            return jsonify({"error": str(e)}), 500

        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
    else:
        # Redirect to login if the user is not logged in or does not have the STAFF role
        return redirect(url_for('login'))


@app.route('/track_navigation', methods=['POST'])
def track_navigation():
    try:
        data = request.json
        action = data.get('action')
        url = data.get('url')
        user_id = session.get('user_id', 'Unknown User')
        
        print(f"User {user_id}: {action} to {url}")

        return jsonify({"status": "success"}), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# Endpoint to handle document tracking form
@app.route('/document_tracking', methods=['GET', 'POST'])
@login_required
def document_tracking():
    if request.method == 'POST':
        user_id = session.get('user_id')
        doc_type_id = request.form['doctype']
        office_id = request.form['office']
        doc_details = request.form['docdetails']
        doc_purpose = request.form['docpurpose']
        date_encoded = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        date_received = request.form.get('datereceived')
        status = 'Pending'

        # Get user's school ID
        school_id = get_user_school_id(user_id)

        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Insert the new document into the DOCUMENTS table
            cursor.execute("""
                INSERT INTO DOCUMENTS (UserID, DocTypeID, SchoolID, OfficeID, DocDetails, DocPurpose, DateEncoded, DateReceived, Status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (user_id, doc_type_id, school_id, office_id, doc_details, doc_purpose, date_encoded, date_received, status))
            conn.commit()

            # Generate a tracking number
            tracking_number = generate_tracking_number()

            # Update the document with the generated tracking number
            cursor.execute("""
                UPDATE DOCUMENTS 
                SET TrackingNumber = %s 
                WHERE DocNo = (SELECT DocNo FROM DOCUMENTS WHERE UserID = %s ORDER BY DateEncoded DESC LIMIT 1)
            """, (tracking_number, user_id))
            conn.commit()

            return redirect(url_for('document_tracking'))

        except Exception as e:
            return jsonify({"error": str(e)}), 500

        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    # For GET method: Fetch user's documents for display
    user_id = session.get('user_id')
    conn = None
    cursor = None
    documents = []

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT d.DocNo, d.DocDetails, d.DocPurpose, d.DateEncoded, d.DateReceived, d.Status, d.TrackingNumber,
                   u.Firstname, u.Lastname,
                   dt.DocTypeName, s.SchoolName, o.OfficeName
            FROM DOCUMENTS d
            JOIN USERS u ON d.UserID = u.UserID
            JOIN DOCUMENT_TYPE dt ON d.DocTypeID = dt.DocTypeID
            JOIN SCHOOLS s ON d.SchoolID = s.SchoolID
            JOIN OFFICES o ON d.OfficeID = o.OfficeID
            WHERE d.UserID = %s
        """, (user_id,))
        documents = cursor.fetchall()

    except Exception as e:
        print(f"Error fetching documents: {e}")

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    return render_template('document_tracking.html', documents=documents)

def get_user_school_id(user_id):
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT SchoolID FROM USERS WHERE UserID = %s", (user_id,))
        school_id = cursor.fetchone()
        return school_id[0] if school_id else None
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def generate_tracking_number():
    # Define the fixed prefix
    prefix = 'TRCK-'
    
    # Define the length of each segment
    segment_lengths = [4, 4, 4]  # Three segments of lengths 4 each
    
    # Function to generate a random alphanumeric string of given length
    def random_segment(length):
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))
    
    # Generate each segment
    segments = [random_segment(length) for length in segment_lengths]
    
    # Combine the segments with dashes
    tracking_number = prefix + '-'.join(segments)
    
    return tracking_number


@app.route('/add_document', methods=['POST'])
@login_required
def add_document():
    user_id = session.get('user_id')
    doc_type_id = request.form['doctype']
    doc_details = request.form['docdetails']
    doc_purpose = request.form['docpurpose']
    date_encoded = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    date_received = request.form.get('datereceived')
    status = 'Pending'

    # Hardcoded OfficeID for the Records Office
    office_id = 7  # Replace with the actual OfficeID for the Records Office

    # Fetch the SchoolID associated with the user
    school_id = get_user_school_id(user_id)

    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Get the next available DocNo
        cursor.execute("SELECT COALESCE(MAX(DocNo), 0) + 1 FROM DOCUMENTS")
        next_doc_no = cursor.fetchone()[0]

        # Insert the new document details
        cursor.execute("""
            INSERT INTO DOCUMENTS (DocNo, UserID, DocTypeID, SchoolID, OfficeID, DocDetails, DocPurpose, DateEncoded, DateReceived, Status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (next_doc_no, user_id, doc_type_id, school_id, office_id, doc_details, doc_purpose, date_encoded, date_received, status))
        conn.commit()

        # Generate a tracking number for the new document
        tracking_number = generate_tracking_number()

        # Update the document with the generated tracking number
        cursor.execute("""
            UPDATE DOCUMENTS 
            SET TrackingNumber = %s 
            WHERE DocNo = %s
        """, (tracking_number, next_doc_no))
        conn.commit()

        # Redirect back to the user dashboard after adding the document
        return redirect(url_for('_users_dashboard'))

    except Exception as e:
        # Return error response in case of exception
        return jsonify({"error": str(e)}), 500

    finally:
        # Ensure the database connection is properly closed
        if cursor:
            cursor.close()
        if conn:
            conn.close()




@app.route('/logout')
@login_required
def logout():
    # Clear the session
    session.pop('user_id', None)
    session.pop('username', None)
    session.pop('role', None)

    # Redirect to the login page
    return redirect(url_for('login'))

@app.route('/edit_document/<int:doc_no>', methods=['GET', 'POST'])
def edit_document(doc_no):
    # Your code to handle the document editing
    pass

@app.route('/delete_document/<int:doc_no>', methods=['POST'])
def delete_document(doc_no):
    # Your code to handle the document deletion
    pass

@app.route('/view_document/<int:doc_no>', methods=['GET'])
def view_document(doc_no):
    # Your code to handle viewing the document
    pass



if __name__ == '__main__':
    app.run(debug=True)
