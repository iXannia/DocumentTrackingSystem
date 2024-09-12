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
    if request.method == 'POST':
        firstname = request.form.get('firstname')
        middlename = request.form.get('middlename')
        lastname = request.form.get('lastname')
        idnumber = request.form.get('idnumber')
        email = request.form.get('email')
        school_id = request.form.get('school')
        password = request.form.get('password')
        hashed_password = generate_password_hash(password)

        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            insert_query = """
            INSERT INTO USERS (RoleID, SchoolID, Firstname, Middlename, Lastname, IDNumber, Email, Password)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(insert_query, (2, school_id, firstname, middlename, lastname, idnumber, email, hashed_password))
            conn.commit()

            return redirect(url_for('login'))

        except Exception as e:
            return jsonify({"error": str(e)}), 500

        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    # Query the schools from the database
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT SchoolID, SchoolName FROM SCHOOLS")
        schools = cursor.fetchall()
    except Exception as e:
        schools = []
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    return render_template('register.html', schools=schools)

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

        school_id = get_user_school_id(user_id)

        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO DOCUMENTS (UserID, DocTypeID, SchoolID, OfficeID, DocDetails, DocPurpose, DateEncoded, DateReceived, Status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (user_id, doc_type_id, school_id, office_id, doc_details, doc_purpose, date_encoded, date_received, status))
            conn.commit()

            # Generate TrackingNumber here
            tracking_number = generate_tracking_number()
            
            # Update document with TrackingNumber
            cursor.execute("""
                UPDATE DOCUMENTS 
                SET TrackingNumber = %s 
                WHERE DocNo = (SELECT DocNo FROM DOCUMENTS WHERE UserID = %s ORDER BY DateEncoded DESC LIMIT 1)
            """, (tracking_number, user_id))
            conn.commit()

            return redirect(url_for('document_tracking'))  # Redirect to the same page to show the new data

        except Exception as e:
            return jsonify({"error": str(e)}), 500

        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
    
    # Fetch documents for display
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
    characters = string.ascii_letters + string.digits
    tracking_number = ''.join(random.choice(characters) for _ in range(8))  # 8-character random string
    return tracking_number

@app.route('/add_document', methods=['POST'])
@login_required
def add_document():
    user_id = session.get('user_id')
    doc_type_id = request.form['doctype']
    office_id = request.form['office']
    doc_details = request.form['docdetails']
    doc_purpose = request.form['docpurpose']
    date_encoded = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    date_received = request.form.get('datereceived')
    status = 'Pending'

    school_id = get_user_school_id(user_id)

    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Get the next DocNo
        cursor.execute("SELECT COALESCE(MAX(DocNo), 0) + 1 FROM DOCUMENTS")
        next_doc_no = cursor.fetchone()[0]

        # Insert new document
        cursor.execute("""
            INSERT INTO DOCUMENTS (DocNo, UserID, DocTypeID, SchoolID, OfficeID, DocDetails, DocPurpose, DateEncoded, DateReceived, Status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (next_doc_no, user_id, doc_type_id, school_id, office_id, doc_details, doc_purpose, date_encoded, date_received, status))
        conn.commit()

        # Generate TrackingNumber here
        tracking_number = generate_tracking_number()

        # Update document with TrackingNumber
        cursor.execute("""
            UPDATE DOCUMENTS 
            SET TrackingNumber = %s 
            WHERE DocNo = %s
        """, (tracking_number, next_doc_no))
        conn.commit()

        return redirect(url_for('_users_dashboard'))

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
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




if __name__ == '__main__':
    app.run(debug=True)
