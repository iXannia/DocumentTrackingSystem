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

#LOGIN REQUIRED
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

# (USER REGISTRATION) Endpoint for user registration
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        firstname = request.form.get('firstname')
        middlename = request.form.get('middlename')
        lastname = request.form.get('lastname')
        idnumber = request.form.get('idnumber')
        email = request.form.get('email')
        school_id = request.form.get('school')
        other_school = request.form.get('other_school')  # Get the 'Other' school input
        password = request.form.get('password')
        hashed_password = generate_password_hash(password)

        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            # If the user selects "Others", insert the new school into the SCHOOLS table
            if school_id == "others" and other_school:
                insert_school_query = """
                INSERT INTO SCHOOLS (SchoolName) VALUES (%s)
                """
                cursor.execute(insert_school_query, (other_school,))
                conn.commit()

                # Get the newly inserted school's ID
                school_id = cursor.lastrowid

            # Insert into USERS table
            insert_user_query = """
            INSERT INTO USERS (RoleID, SchoolID, Firstname, Middlename, Lastname, IDNumber, Email, Password)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(insert_user_query, (2, school_id, firstname, middlename, lastname, idnumber, email, hashed_password))
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


# STAFF REGISTRATION
@app.route('/register_staff', methods=['GET', 'POST'])
def register_staff():
    if request.method == 'POST':
        firstname = request.form.get('firstname')
        middlename = request.form.get('middlename')
        lastname = request.form.get('lastname')
        idnumber = request.form.get('idnumber')
        email = request.form.get('email')
        office_id = request.form.get('office')
        password = request.form.get('password')
        hashed_password = generate_password_hash(password)

        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            # Insert into USERS table with RoleID = 1 (assuming 1 is STAFF)
            insert_query = """
            INSERT INTO USERS (RoleID, Firstname, Middlename, Lastname, IDNumber, Email, Password)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(insert_query, (3, firstname, middlename, lastname, idnumber, email, hashed_password))
            user_id = cursor.lastrowid

            # Insert into STAFFS table
            insert_staff_query = """
            INSERT INTO STAFFS (UserID, OfficeID)
            VALUES (%s, %s)
            """
            cursor.execute(insert_staff_query, (user_id, office_id))
            conn.commit()

            return redirect(url_for('login'))

        except Exception as e:
            return jsonify({"error": str(e)}), 500

        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    # Query the offices from the database
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT OfficeID, OfficeName FROM OFFICES")
        offices = cursor.fetchall()
    except Exception as e:
        offices = []
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    return render_template('register_staff.html', offices=offices)


# (LOGIN FOR USERS & STAFFS) Endpoint for user login 
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = None
        cursor = None
        try:
            # Establish database connection
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)

            # Fetch user information based on email
            cursor.execute("SELECT * FROM USERS WHERE Email = %s", (email,))
            user = cursor.fetchone()

            # Verify password
            if user and check_password_hash(user['Password'], password):
                # Store user information in session
                session['user_id'] = user['UserID']
                session['username'] = user['Firstname']
                session['role'] = int(user['RoleID'])

                # Redirect based on RoleID
                if user['RoleID'] == 1:  # ADMIN
                    return redirect(url_for('_admin_dashboard'))
                elif user['RoleID'] == 2:  # USERS
                    return redirect(url_for('_users_dashboard'))
                elif user['RoleID'] == 3:  # STAFF
                    # Check if the user is a staff member and fetch their OfficeID
                    cursor.execute("SELECT OfficeID FROM STAFFS WHERE UserID = %s", (user['UserID'],))
                    staff = cursor.fetchone()

                    if staff:  # User is a staff member
                        office_id = staff['OfficeID']
                        # Redirect based on OfficeID
                        if office_id == 9:  # BUDGET OFFICE
                            return redirect(url_for('_budget_dashboard'))
                        elif office_id == 10:  # CASHIER OFFICE
                            return redirect(url_for('_cashier_dashboard'))
                        elif office_id == 11:  # HRMU OFFICE
                            return redirect(url_for('_hrmu_dashboard'))
                        elif office_id == 12:  # ICT OFFICE
                            return redirect(url_for('_ict_dashboard'))
                        elif office_id == 13:  # LEGAL OFFICE
                            return redirect(url_for('_legal_dashboard'))
                        elif office_id == 15:  # SDS OFFICE
                            return redirect(url_for('_sds_dashboard'))
                        elif office_id == 16:  # SUPPLY OFFICE
                            return redirect(url_for('_supply_dashboard'))
                        else:
                            return redirect(url_for('_records_dashboard'))  # Default redirect for staff
                    else:
                        return redirect(url_for('_records_dashboard'))  # Default redirect if no office found for staff

            else:
                return "Invalid email or password", 401  # Invalid login credentials

        except Exception as e:
            return jsonify({"error": str(e)}), 500  # Handle exceptions

        finally:
            # Close the cursor and connection
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    return render_template('login.html')  # Render login page for GET requests



# (USERS DASHBOARD) Users route to display after login 
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

        return render_template('users/_users_dashboard.html', document_type=document_types, office=offices, user=user)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

#ADMIN DASHBOARD
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

        return render_template('admin/_admin_dashboard.html', users=users)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# STAFF = RECORDS DASHBOARD
@app.route('/_records_dashboard', methods=['GET'])
def _records_dashboard():
    return office_dashboard(session['user_id'], 'records_office/_records_dashboard.html')

# BUDGET OFFICE DASHBOARD
@app.route('/_budget_dashboard', methods=['GET'])
def _budget_dashboard():
    return office_dashboard(session['user_id'], 'budget_office/_budget_dashboard.html')

# CASHIER OFFICE DASHBOARD
@app.route('/_cashier_dashboard', methods=['GET'])
def _cashier_dashboard():
    return office_dashboard(session['user_id'], 'cashier_office/_cashier_dashboard.html')

# HRMU OFFICE DASHBOARD
@app.route('/_hrmu_dashboard', methods=['GET'])
def _hrmu_dashboard():
    return office_dashboard(session['user_id'], 'hrmu_office/_hrmu_dashboard.html')

# ICT OFFICE DASHBOARD
@app.route('/_ict_dashboard', methods=['GET'])
def _ict_dashboard():
    return office_dashboard(session['user_id'], 'ict_office/_ict_dashboard.html')

# LEGAL OFFICE DASHBOARD
@app.route('/_legal_dashboard', methods=['GET'])
def _legal_dashboard():
    return office_dashboard(session['user_id'], 'legal_office/_legal_dashboard.html')

# SDS OFFICE DASHBOARD
@app.route('/_sds_dashboard', methods=['GET'])
def _sds_dashboard():
    return office_dashboard(session['user_id'], 'sds_office/_sds_dashboard.html')

# SUPPLY OFFICE DASHBOARD
@app.route('/_supply_dashboard', methods=['GET'])
def _supply_dashboard():
    return office_dashboard(session['user_id'], 'supply_office/_supply_dashboard.html')

# Generic office dashboard function
def office_dashboard(user_id, template_name):
    if 'user_id' in session and session.get('role') == 3:  # Assuming 3 is your STAFF RoleID
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)

            # Fetch user details for the greeting
            cursor.execute("SELECT Firstname, Middlename, Lastname FROM USERS WHERE UserID = %s", (user_id,))
            user = cursor.fetchone()

            # Fetch documents related to the STAFF user
            cursor.execute("SELECT * FROM DOCUMENTS WHERE UserID = %s", (user_id,))
            documents = cursor.fetchall()

            # Fetch document types for the dropdown
            cursor.execute("SELECT DocTypeID, DocTypeName FROM DOCUMENT_TYPE")
            document_types = cursor.fetchall()

            return render_template(template_name, documents=documents, user=user, document_type=document_types)

        except Exception as e:
            return jsonify({"error": str(e)}), 500

        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
    else:
        return redirect(url_for('login'))  # Redirect to login if not authorized



#TRACK NAVIGATION
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


#(USERS DOCUMENT TRACKING) Endpoint to handle document tracking form 
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

    return render_template('users/document_tracking.html', documents=documents)

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

# ADD DOCUMENTS FOR USERS
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
    office_id = 14  # Replace with the actual OfficeID for the Records Office

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

# ADD DOCUMENTS FOR STAFF
@app.route('/staff_add_document', methods=['POST'])
@login_required
def staff_add_document():
    # Ensure the user is a staff member
    if session.get('role') != 3:  # Assuming role '3' is for staff
        return redirect(url_for('index'))  # Redirect unauthorized users

    user_id = session.get('user_id')
    doc_type_id = request.form['doctype']
    doc_details = request.form['docdetails']
    doc_purpose = request.form['docpurpose']
    date_encoded = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    date_received = request.form.get('datereceived')
    status = 'Pending'

    # Hardcoded OfficeID for the Records Office or dynamic based on staff role/office
    office_id = 14  # Replace with dynamic OfficeID if needed

    # Fetch the SchoolID associated with the user (staff)
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

        # Redirect back to the staff dashboard after adding the document
        return redirect(url_for('_records_dashboard'))

    except Exception as e:
        # Return error response in case of exception
        return jsonify({"error": str(e)}), 500

    finally:
        # Ensure the database connection is properly closed
        if cursor:
            cursor.close()
        if conn:
            conn.close()


# DISPLAY DOCUMENTS FOR RECORDS
@app.route('/receive_documents')
@login_required
def receive_documents():
    page = request.args.get('page', 1, type=int)  # Get the page number from query params
    per_page = 10  # Documents per page
    offset = (page - 1) * per_page

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        # Fetch paginated documents along with user, school, and office details
        cursor.execute("""
            SELECT d.TrackingNumber, 
                   u.Firstname, 
                   u.Lastname, 
                   dt.DocTypeName, 
                   d.DocDetails, 
                   d.DocPurpose, 
                   s.SchoolName, 
                   o.OfficeName,  -- Fetch the Office Name
                   d.DateEncoded, 
                   d.DateReceived, 
                   d.Status
            FROM DOCUMENTS d
            JOIN USERS u ON d.UserID = u.UserID
            JOIN DOCUMENT_TYPE dt ON d.DocTypeID = dt.DocTypeID
            LEFT JOIN SCHOOLS s ON d.SchoolID = s.SchoolID
            LEFT JOIN OFFICES o ON d.OfficeID = o.OfficeID  -- Join with Offices
            ORDER BY d.DateEncoded DESC
            LIMIT %s OFFSET %s
        """, (per_page, offset))

        documents = cursor.fetchall()

        # Count total documents
        cursor.execute("SELECT COUNT(*) FROM DOCUMENTS")
        total_documents = cursor.fetchone()['COUNT(*)']
        total_pages = (total_documents + per_page - 1) // per_page

        return render_template(
            'records_office/receive_documents.html',
            documents=documents,
            current_page=page,
            total_pages=total_pages
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

# LOG OUT ROUTE
@app.route('/logout')
@login_required
def logout():
    # Clear the session
    session.pop('user_id', None)
    session.pop('username', None)
    session.pop('role', None)

    # Redirect to the login page
    return redirect(url_for('login'))


#EDIT ACTION BUTTON
@app.route('/edit_document/<int:doc_no>', methods=['GET', 'POST'])
def edit_document(doc_no):
    # Your code to handle the document editing
    pass

#DELETE ACTION BUTTON
@app.route('/delete_document/<int:doc_no>', methods=['POST'])
def delete_document(doc_no):
    # Your code to handle the document deletion
    pass

#VIEW ACTION BUTTON
@app.route('/view_document/<int:doc_no>', methods=['GET'])
def view_document(doc_no):
    # Your code to handle viewing the document
    pass

if __name__ == '__main__':
    app.run(debug=True)