from flask import Flask, request, jsonify, session, redirect, url_for, render_template, abort, make_response, flash
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

                # Check if the user is a staff member and fetch their OfficeID
                if user['RoleID'] == 3:  # STAFF
                    cursor.execute("SELECT OfficeID FROM STAFFS WHERE UserID = %s", (user['UserID'],))
                    staff = cursor.fetchone()

                    if staff:  # User is a staff member
                        office_id = staff['OfficeID']
                        session['office_id'] = office_id  # Store OfficeID in the session

                        # Redirect based on OfficeID
                        if office_id == 8:  # ADMIN OFFICE
                            return redirect(url_for('_admin_dashboard'))
                        elif office_id == 9:  # BUDGET OFFICE
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

                # Redirect based on RoleID for admin and users
                if user['RoleID'] == 1:  # ADMIN
                    return redirect(url_for('_super_admin_dashboard'))
                elif user['RoleID'] == 2:  # USERS
                    return redirect(url_for('_users_dashboard'))

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


#-----SUPER ADMIN DASHBOARD-----#
@app.route('/_super_admin_dashboard')
@login_required
def _super_admin_dashboard():
    # Ensure the user is a super admin
    if session.get('role') != 1:  # Assuming role '1' is for super admin
        return redirect(url_for('index'))  # Redirect unauthorized users

    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('logout'))  # Handle case where user ID is not in session

    # Fetch user details
    user = get_user_by_id(user_id)

    conn = None
    cursor = None
    offices = []
    document_type = []  # To hold document types

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Fetch the list of offices from the database (assuming 'OFFICES' table)
        cursor.execute("SELECT OfficeID, OfficeName FROM OFFICES")
        offices = cursor.fetchall()

        # Fetch the list of document types (assuming 'DOCUMENT_TYPE' table)
        cursor.execute("SELECT DocTypeID, DocTypeName FROM DOCUMENT_TYPE")
        document_type = cursor.fetchall()  # [(DocTypeID1, DocTypeName1), (DocTypeID2, DocTypeName2), ...]

    except Exception as e:
        print(f"Error fetching data: {e}")

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    # Pass document types, offices, and user to the template
    return render_template('super_admin/_super_admin_dashboard.html', user=user, offices=offices, document_type=document_type)

#SUPER ADMIN REGISTRATION:
@app.route('/register_admin', methods=['GET', 'POST'])
def register_admin():
    if request.method == 'POST':
        firstname = request.form.get('firstname')
        lastname = request.form.get('lastname')
        idnumber = request.form.get('idnumber')
        email = request.form.get('email')
        password = request.form.get('password')
        hashed_password = generate_password_hash(password)

        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            # Insert into USERS table with RoleID = 1 (assuming 1 is ADMIN)
            insert_query = """
            INSERT INTO USERS (RoleID, Firstname, Lastname, IDNumber, Email, Password)
            VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor.execute(insert_query, (1, firstname, lastname, idnumber, email, hashed_password))
            conn.commit()

            return redirect(url_for('login'))

        except Exception as e:
            return jsonify({"error": str(e)}), 500

        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    return render_template('super_admin/register_admin.html')

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

    return render_template('super_admin/register.html', schools=schools)


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

            # Insert into USERS table with RoleID = 3 (assuming 3 is STAFF)
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

    return render_template('super_admin/register_staff.html', offices=offices)
#-----END OF ADMIN DASHBOARD-----#

#REGISTRATION:
@app.route('/registration', methods=['GET'])
def registration():
    return render_template('super_admin/registration.html')

#-----USERS DASHBOARD-----#
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
                INSERT INTO DOCUMENTS (UserID, DocTypeID, SchoolID, OfficeID, DocDetails, DocPurpose, DateEncoded, Status)
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
    document_types = []  # Initialize this list

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Fetch document types for the dropdown
        cursor.execute("SELECT * FROM DOCUMENT_TYPE")
        document_types = cursor.fetchall()

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

    return render_template('users/document_tracking.html', documents=documents, document_types=document_types)

# GET USER ID
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
            INSERT INTO DOCUMENTS (DocNo, UserID, DocTypeID, SchoolID, OfficeID, DocDetails, DocPurpose, DateEncoded, DateReceived, Status, OfficeIDToSend)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (next_doc_no, user_id, doc_type_id, school_id, office_id, doc_details, doc_purpose, date_encoded, date_received, status, office_id))  # Added OfficeIDToSend
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
#----- END OF USERS DASHBOARD -----#



#----- ALL OFFICES DASHBOARDS -----#

#----- ADMIN OFFICE DASHBOARD -----#
# "CREATE DOCUMENTS" FOR ADMIN DASHBOARD / _admin_dashboard.html
@app.route('/_admin_dashboard')
@login_required
def _admin_dashboard():
    # Ensure the user is an admin
    if session.get('role') != 3:  # Assuming role '1' is for admin
        return redirect(url_for('index'))  # Redirect unauthorized users

    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('logout'))  # Handle case where user ID is not in session

    # Fetch user details
    user = get_user_by_id(user_id)

    conn = None
    cursor = None
    offices = []
    document_type = []  # To hold document types

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Fetch the list of offices from the database (assuming 'OFFICES' table)
        cursor.execute("SELECT OfficeID, OfficeName FROM OFFICES")
        offices = cursor.fetchall()

        # Fetch the list of document types (assuming 'DOCUMENT_TYPES' table)
        cursor.execute("SELECT DocTypeID, DocTypeName FROM DOCUMENT_TYPE")
        document_type = cursor.fetchall()  # [(DocTypeID1, DocTypeName1), (DocTypeID2, DocTypeName2), ...]

    except Exception as e:
        print(f"Error fetching data: {e}")

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    # Pass document types, offices, and user to the template
    return render_template('admin_office/_admin_dashboard.html', user=user, offices=offices, document_type=document_type)

# "DOCUMENT FOR RECEIVE" FOR ADMIN OFFICE / admin_document.html
@app.route('/admin_documents')
@login_required
def admin_documents():
    page = request.args.get('page', 1, type=int)  # Get the page number from query params
    per_page = 10  # Documents per page
    offset = (page - 1) * per_page

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        # Fetch paginated documents created by USERS and forwarded to the Admin Office
        cursor.execute(""" 
            SELECT d.DocNo,  -- Include the DocNo here
                   d.TrackingNumber, 
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
            WHERE d.OfficeIDToSend = %s  -- Filter by the OfficeID for Admin Office
            ORDER BY d.DateEncoded DESC
            LIMIT %s OFFSET %s
        """, (session.get('office_id'), per_page, offset))  # Assuming office_id is stored in session

        documents = cursor.fetchall()

        # Count total documents forwarded to the Admin Office created by USERS and STAFF
        cursor.execute("""
            SELECT COUNT(*) FROM DOCUMENTS d 
            JOIN USERS u ON d.UserID = u.UserID 
            WHERE d.OfficeIDToSend = %s 
        """, (session.get('office_id'),))
        
        total_documents = cursor.fetchone()['COUNT(*)']
        total_pages = (total_documents + per_page - 1) // per_page

        return render_template(
            'admin_office/admin_documents.html',  # Ensure you have this template
            documents=documents,
            current_page=page,
            total_pages=total_pages
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

# "MY DOCUMENTS" FOR ADMIN OFFICE /admin_encoded.html
@app.route('/admin_encoded', methods=['GET'])
@login_required
def admin_encoded():
    # Ensure the user is a staff member
    if session.get('role') != 3:  # Assuming role '3' is for staff
        return redirect(url_for('index'))  # Redirect unauthorized users

    page = request.args.get('page', 1, type=int)  # Get the page number from query params
    per_page = 10  # Documents per page
    offset = (page - 1) * per_page

    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('logout'))  # Handle case where user ID is not in session

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        # Fetch paginated documents for the user along with document type and school/office details
        cursor.execute("""
            SELECT d.TrackingNumber, 
                   u.Firstname, 
                   u.Lastname, 
                   dt.DocTypeName, 
                   d.DocDetails, 
                   d.DocPurpose, 
                   COALESCE(s.SchoolName, o.OfficeName, 'N/A') AS SchoolOrOffice, 
                   d.DateEncoded, 
                   d.DateReceived, 
                   d.Status,
                   d.OfficeIDToSend
            FROM DOCUMENTS d
            JOIN USERS u ON d.UserID = u.UserID
            JOIN DOCUMENT_TYPE dt ON d.DocTypeID = dt.DocTypeID
            LEFT JOIN SCHOOLS s ON d.SchoolID = s.SchoolID
            LEFT JOIN OFFICES o ON d.OfficeIDToSend = o.OfficeID
            WHERE d.UserID = %s OR d.Status = 'Received'
            ORDER BY d.DateEncoded DESC
            LIMIT %s OFFSET %s
        """, (user_id, per_page, offset))

        documents = cursor.fetchall()

        # Count total documents for the user
        cursor.execute("""
            SELECT COUNT(*) 
            FROM DOCUMENTS 
            WHERE UserID = %s OR Status = 'Received'
        """, (user_id,))
        total_documents = cursor.fetchone()['COUNT(*)']
        total_pages = (total_documents + per_page - 1) // per_page

        return render_template(
            'admin_office/admin_encoded.html',
            documents=documents,
            current_page=page,
            total_pages=total_pages  # Ensure total_pages is defined here
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

# "RECEIVE" ACTION BUTTON FOR ADMIN
@app.route('/admin_receive_document/<int:doc_no>', methods=['POST'])
@login_required
def handle_admin_receive_document(doc_no):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # 1. Update the status of the document to 'Received' and set DateReceived
        cursor.execute("""
            UPDATE DOCUMENTS
            SET Status = %s, DateReceived = NOW()
            WHERE DocNo = %s AND OfficeID = %s
        """, ('Received', doc_no, session.get('office_id')))
        
        if cursor.rowcount == 0:
            return jsonify({"error": "Document not found or already received."}), 404

        # 2. Fetch the TrackingNumber for this document
        cursor.execute("SELECT TrackingNumber FROM DOCUMENTS WHERE DocNo = %s", (doc_no,))
        tracking_number_result = cursor.fetchone()
        tracking_number = tracking_number_result[0] if tracking_number_result else None

        # 3. Insert the transaction into the TRANSACTIONS table
        cursor.execute("""
            INSERT INTO TRANSACTIONS (
                OfficeID, DocNo, UserID, 
                ReceivedDate, Status, TransactionType, TrackingNumber
            )
            VALUES (%s, %s, %s, NOW(), %s, %s, %s)
        """, (
            session.get('office_id'),  # Office receiving the document
            doc_no,                    # Document number being received
            session.get('user_id'),    # The user performing the action
            'Received',                # Status of the transaction
            'Receive',                 # Type of transaction
            tracking_number            # TrackingNumber associated with this document
        ))

        conn.commit()
        return redirect(url_for('admin_documents'))

    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500

    finally:
        cursor.close()
        conn.close()

# "FORWARD" ACTION BUTTON FOR ADMIN OFFICE
@app.route('/admin_forward', methods=['POST'])
def admin_forward():
    tracking_number = request.form.get('tracking_number')
    comments = request.form.get('comments')
    forwarded_to_office_id = request.form.get('forwarded_to_office_id')  # Capture selected office ID

    try:
        # Connect to the database
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # Verify that the document exists
        cursor.execute("SELECT DocNo FROM DOCUMENTS WHERE TrackingNumber = %s", (tracking_number,))
        document = cursor.fetchone()

        if not document:
            flash(f'Document with tracking number {tracking_number} does not exist.', 'error')
            return redirect(url_for('admin_encoded'))

        # Retrieve the document number (DocNo)
        doc_no = document[0]

        # Update document status to 'Forwarded'
        cursor.execute("""
            UPDATE DOCUMENTS
            SET Status = 'Forwarded'
            WHERE TrackingNumber = %s
        """, (tracking_number,))

        # Insert a new transaction record with dynamic ForwardedToOfficeID
        cursor.execute("""
            INSERT INTO TRANSACTIONS (
                OfficeID, DocNo, UserID, ForwardDate, Status, TransactionType, Comments, ForwardedToOfficeID, TrackingNumber
            ) VALUES (%s, %s, %s, NOW(), 'Forwarded', 'Forward', %s, %s, %s)
        """, (
            session.get('office_id'),   # Office initiating the forward
            doc_no,                     # Document number
            session.get('user_id'),     # User performing the action
            comments,                   # Comments from the form
            forwarded_to_office_id,     # Selected office from dropdown
            tracking_number             # Tracking number
        ))

        conn.commit()
        flash(f'Document {tracking_number} forwarded successfully!', 'success')

    except mysql.connector.Error as err:
        conn.rollback()
        print(f"Database error: {err}")
        flash(f'Error forwarding document: {err}', 'error')
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    return redirect(url_for('admin_encoded'))


# "COMPLETE" ACTION BUTTON FOR ADMIN
@app.route('/admin_complete', methods=['POST'])
def admin_complete():
    # Retrieve user ID from session
    user_id = session.get('user_id')
    if not user_id:
        flash("You must be logged in to complete a document.")
        return redirect(url_for('login'))  # Redirect to login if not logged in

    # Get data from the form
    tracking_number = request.form.get('tracking_number')
    comments = request.form.get('comments', '')
    current_date = datetime.now()

    # Connect to the database
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Update the document status to 'Complete'
        update_document_query = """
            UPDATE DOCUMENTS
            SET Status = 'Complete'
            WHERE TrackingNumber = %s
        """
        cursor.execute(update_document_query, (tracking_number,))

        # Insert a new transaction record in TRANSACTIONS
        insert_transaction_query = """
            INSERT INTO TRANSACTIONS (
                OfficeID, DocNo, UserID, CompletedDate,
                ProcessDate, Status, TransactionType, Comments, TrackingNumber
            ) VALUES (
                %s, 
                (SELECT DocNo FROM DOCUMENTS WHERE TrackingNumber = %s), 
                %s, %s, %s, %s, %s, %s, %s
            )
        """
        cursor.execute(insert_transaction_query, (
            session.get('office_id'),  # Assuming 'office_id' is also stored in session
            tracking_number,
            user_id,
            current_date,
            current_date,
            'Completed',
            'Complete',
            comments,
            tracking_number  # Insert the tracking number into the transaction
        ))

        # Commit the transaction
        conn.commit()
        flash("Document marked as complete successfully.")
    except Exception as e:
        conn.rollback()
        flash(f"An error occurred: {e}")
    finally:
        # Close the database connection
        cursor.close()
        conn.close()

    return redirect(url_for('admin_encoded'))  # Redirect to documents page


# "TRACK DOCUMENTS" IN ADMIN OFFICE / track_admin_documents.html
@app.route('/track_admin_documents')
@login_required
def track_admin_documents():
    page = request.args.get('page', 1, type=int)  # Get the page number from query params
    per_page = 10  # Documents per page
    offset = (page - 1) * per_page

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        # Fetch paginated documents for the Admin Office along with user details
        cursor.execute(""" 
            SELECT d.TrackingNumber, 
                   u.Firstname, 
                   u.Lastname, 
                   dt.DocTypeName, 
                   d.DocDetails, 
                   d.DocPurpose, 
                   COALESCE(s.SchoolName, o.OfficeName, 'N/A') AS SchoolOrOffice, 
                   d.DateEncoded, 
                   d.DateReceived, 
                   d.Status
            FROM DOCUMENTS d
            JOIN USERS u ON d.UserID = u.UserID
            JOIN DOCUMENT_TYPE dt ON d.DocTypeID = dt.DocTypeID
            LEFT JOIN SCHOOLS s ON d.SchoolID = s.SchoolID
            LEFT JOIN OFFICES o ON d.OfficeID = o.OfficeID
            WHERE d.OfficeID = %s  -- Filter by the Admin Office
            ORDER BY d.DateEncoded DESC
            LIMIT %s OFFSET %s
        """, (8, per_page, offset))  # Assuming 8 is the OfficeID for the Admin Office

        documents = cursor.fetchall()

        # Count total documents for the Admin Office
        cursor.execute("SELECT COUNT(*) FROM DOCUMENTS WHERE OfficeID = %s", (9,))
        total_documents = cursor.fetchone()['COUNT(*)']
        total_pages = (total_documents + per_page - 1) // per_page

        return render_template(
            'admin_office/track_admin_documents.html',  # Update the path as per your file structure
            documents=documents,
            current_page=page,
            total_pages=total_pages  # Ensure total_pages is defined here
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

#-----RECORDS OFFICE DASHBOARD-----#
# "CREATE DOCUMENTS" FOR RECORDS OFFICE / _records_dashboard.html
@app.route('/_records_dashboard')
@login_required
def _records_dashboard():
    # Ensure the user is a staff member
    if session.get('role') != 3:  # Assuming role '3' is for staff
        return redirect(url_for('index'))  # Redirect unauthorized users

    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('logout'))  # Handle case where user ID is not in session

    # Fetch user details
    user = get_user_by_id(user_id)

    conn = None
    cursor = None
    offices = []
    document_type = []  # To hold document types

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Fetch the list of offices from the database (assuming 'OFFICES' table)
        cursor.execute("SELECT OfficeID, OfficeName FROM OFFICES")
        offices = cursor.fetchall()

        # Fetch the list of document types (assuming 'DOCUMENT_TYPES' table)
        cursor.execute("SELECT DocTypeID, DocTypeName FROM DOCUMENT_TYPE")
        document_type = cursor.fetchall()  # [(DocTypeID1, DocTypeName1), (DocTypeID2, DocTypeName2), ...]

    except Exception as e:
        print(f"Error fetching data: {e}")

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    # Pass document types, offices, and user to the template
    return render_template('records_office/_records_dashboard.html', user=user, offices=offices, document_type=document_type)

# "MY DOCUMENTS" FOR RECORDS OFFICE / enncoded_documents.html
@app.route('/encoded_documents', methods=['GET'])
@login_required
def encoded_documents():
    # Ensure the user is a staff member
    if session.get('role') != 3:  # Assuming role '3' is for staff
        return redirect(url_for('index'))  # Redirect unauthorized users

    page = request.args.get('page', 1, type=int)  # Get the page number from query params
    per_page = 10  # Documents per page
    offset = (page - 1) * per_page

    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('logout'))  # Handle case where user ID is not in session

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        # Fetch paginated documents for the user, excluding those marked as 'Complete' or 'Forwarded'
        cursor.execute("""        
            SELECT d.TrackingNumber, 
                   u.Firstname, 
                   u.Lastname, 
                   dt.DocTypeName, 
                   d.DocDetails, 
                   d.DocPurpose, 
                   COALESCE(s.SchoolName, o.OfficeName, 'N/A') AS SchoolOrOffice, 
                   d.DateEncoded, 
                   d.Status,
                   t.ReceivedDate,  -- Fetch ReceivedDate from TRANSACTIONS table
                   t.Comments  -- Fetch Comments from TRANSACTIONS table
            FROM DOCUMENTS d
            JOIN USERS u ON d.UserID = u.UserID
            JOIN DOCUMENT_TYPE dt ON d.DocTypeID = dt.DocTypeID
            LEFT JOIN SCHOOLS s ON d.SchoolID = s.SchoolID
            LEFT JOIN OFFICES o ON d.OfficeIDToSend = o.OfficeID
            LEFT JOIN TRANSACTIONS t ON d.DocNo = t.DocNo  -- Join with TRANSACTIONS for ReceivedDate and Comments
            WHERE (d.UserID = %s OR d.Status = 'Received') 
              AND d.Status NOT IN ('Complete', 'Forwarded')
            ORDER BY d.DateEncoded DESC
            LIMIT %s OFFSET %s
        """, (user_id, per_page, offset))

        documents = cursor.fetchall()

        # Fetch offices to populate the dropdown
        cursor.execute("SELECT OfficeID, OfficeName FROM OFFICES")
        offices = cursor.fetchall()

        # Count total documents for the user, excluding completed or forwarded documents
        cursor.execute("""
            SELECT COUNT(*) AS total_documents
            FROM DOCUMENTS 
            WHERE (UserID = %s OR Status = 'Received') AND Status NOT IN ('Complete', 'Forward')
        """, (user_id,))
        total_documents = cursor.fetchone()['total_documents']
        total_pages = (total_documents + per_page - 1) // per_page

        return render_template(
            'records_office/encoded_documents.html',
            documents=documents,
            offices=offices,  # Pass the office data to the template
            current_page=page,
            total_pages=total_pages
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

# "DOCUMENTS FOR RECEIVE" FOR RECORDS OFFICE / receive_documents.html
@app.route('/receive_documents')
@login_required
def receive_documents():
    page = request.args.get('page', 1, type=int)  # Get the page number from query params
    per_page = 10  # Documents per page
    offset = (page - 1) * per_page

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        # Fetch paginated documents created by USERS or forwarded to the Records Office
        cursor.execute(""" 
            SELECT d.DocNo,  -- Include the DocNo here
                   d.TrackingNumber, 
                   u.Firstname, 
                   u.Lastname, 
                   dt.DocTypeName, 
                   d.DocDetails, 
                   d.DocPurpose, 
                   s.SchoolName, 
                   o.OfficeName,  -- Fetch the Office Name
                   d.DateEncoded, 
                   d.DateReceived, 
                   d.Status,
                   d.OfficeIDToSend,  -- Include OfficeIDToSend for filtering
                   t.ForwardDate,  -- Fetch ForwardDate from TRANSACTIONS table
                   t.Comments  -- Fetch Comments from TRANSACTIONS table
            FROM DOCUMENTS d
            JOIN USERS u ON d.UserID = u.UserID
            JOIN DOCUMENT_TYPE dt ON d.DocTypeID = dt.DocTypeID
            LEFT JOIN SCHOOLS s ON d.SchoolID = s.SchoolID
            LEFT JOIN OFFICES o ON d.OfficeID = o.OfficeID  -- Join with Offices
            LEFT JOIN TRANSACTIONS t ON d.DocNo = t.DocNo  -- Join with TRANSACTIONS for ForwardDate and Comments
            WHERE (d.OfficeIDToSend = %s  -- Include documents forwarded to the current office
                   OR t.ForwardedToOfficeID = %s  -- Include forwarded documents
                   OR (d.UserID = u.UserID AND d.Status != 'Complete'))  -- Include documents created by the user
              AND d.Status != 'Complete'  -- Exclude completed documents
              AND d.Status != 'Received'  -- Exclude received documents
              AND (t.Status = 'Forwarded'  -- Include forwarded documents
                   OR t.Status IS NULL)  -- Include documents not yet forwarded
              AND (t.ForwardDate IS NULL 
                   OR t.ForwardDate = (  -- Ensure selecting only the latest forward transaction
                      SELECT MAX(t2.ForwardDate)
                      FROM TRANSACTIONS t2
                      WHERE t2.DocNo = t.DocNo
                        AND t2.Status = 'Forwarded'
                   ))
            ORDER BY t.ForwardDate DESC, d.DateEncoded DESC  -- Order by forward date and encoding date
            LIMIT %s OFFSET %s
        """, (session.get('office_id'), session.get('office_id'), per_page, offset))

        documents = cursor.fetchall()

        # Count total documents created by USERS or forwarded to the Records Office
        cursor.execute(""" 
            SELECT COUNT(DISTINCT d.DocNo) AS total_documents
            FROM DOCUMENTS d
            JOIN USERS u ON d.UserID = u.UserID
            LEFT JOIN TRANSACTIONS t ON d.DocNo = t.DocNo
            WHERE (d.OfficeIDToSend = %s
                   OR t.ForwardedToOfficeID = %s
                   OR (d.UserID = u.UserID AND d.Status != 'Complete'))  -- Include documents created by the user
              AND d.Status != 'Complete'  -- Exclude completed documents
              AND d.Status != 'Received'  -- Exclude received documents
              AND (t.Status = 'Forwarded'
                   OR t.Status IS NULL)  -- Include documents not yet forwarded
              AND (t.ForwardDate IS NULL 
                   OR t.ForwardDate = (  -- Ensure counting only the latest forward transaction
                      SELECT MAX(t2.ForwardDate)
                      FROM TRANSACTIONS t2
                      WHERE t2.DocNo = t.DocNo
                        AND t2.Status = 'Forwarded'
                   ))
        """, (session.get('office_id'), session.get('office_id')))

        total_documents = cursor.fetchone()['total_documents']
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


@app.route('/success')
def success_page():
    return "Your details have been submitted successfully!"

# "RECEIVE" ACTION BUTTON FOR RECORDS OFFICE
@app.route('/receive_document/<int:doc_no>', methods=['POST'])
@login_required
def handle_receive_document(doc_no):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # 1. Update the status of the document to 'Received' and set DateReceived
        cursor.execute("""
            UPDATE DOCUMENTS
            SET Status = %s, DateReceived = NOW()
            WHERE DocNo = %s AND OfficeID = %s
        """, ('Received', doc_no, session.get('office_id')))
        
        if cursor.rowcount == 0:
            return jsonify({"error": "Document not found or already received."}), 404

        # 2. Fetch the TrackingNumber for this document
        cursor.execute("SELECT TrackingNumber FROM DOCUMENTS WHERE DocNo = %s", (doc_no,))
        tracking_number_result = cursor.fetchone()
        tracking_number = tracking_number_result[0] if tracking_number_result else None

        # 3. Insert the transaction into the TRANSACTIONS table
        cursor.execute("""
            INSERT INTO TRANSACTIONS (
                OfficeID, DocNo, UserID, 
                ReceivedDate, Status, TransactionType, TrackingNumber
            )
            VALUES (%s, %s, %s, NOW(), %s, %s, %s)
        """, (
            session.get('office_id'),  # Office receiving the document
            doc_no,                    # Document number being received
            session.get('user_id'),    # The user performing the action
            'Received',                # Status of the transaction
            'Receive',                 # Type of transaction
            tracking_number            # TrackingNumber associated with this document
        ))

        conn.commit()
        return redirect(url_for('receive_documents'))

    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500

    finally:
        cursor.close()
        conn.close()


# "FORWARD" ACTION BUTTON FOR RECORDS OFFICE
    @app.route('/forward_document', methods=['POST'])
    def forward_document():
        tracking_number = request.form.get('tracking_number')
        comments = request.form.get('comments')
        forwarded_to_office_id = request.form.get('forwarded_to_office_id')  # Capture selected office ID

        try:
            # Connect to the database
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor()

            # Verify that the document exists
            cursor.execute("SELECT DocNo FROM DOCUMENTS WHERE TrackingNumber = %s", (tracking_number,))
            document = cursor.fetchone()

            if not document:
                flash(f'Document with tracking number {tracking_number} does not exist.', 'error')
                return redirect(url_for('encoded_documents'))

            # Retrieve the document number (DocNo)
            doc_no = document[0]

            # Update document status to 'Forwarded'
            cursor.execute("""
                UPDATE DOCUMENTS
                SET Status = 'Forwarded'
                WHERE TrackingNumber = %s
            """, (tracking_number,))

            # Insert a new transaction record with dynamic ForwardedToOfficeID
            cursor.execute("""
                INSERT INTO TRANSACTIONS (
                    OfficeID, DocNo, UserID, ForwardDate, Status, TransactionType, Comments, ForwardedToOfficeID, TrackingNumber
                ) VALUES (%s, %s, %s, NOW(), 'Forwarded', 'Forward', %s, %s, %s)
            """, (
                session.get('office_id'),   # Office initiating the forward
                doc_no,                     # Document number
                session.get('user_id'),     # User performing the action
                comments,                   # Comments from the form
                forwarded_to_office_id,     # Selected office from dropdown
                tracking_number             # Tracking number
            ))

            conn.commit()
            flash(f'Document {tracking_number} forwarded successfully!', 'success')

        except mysql.connector.Error as err:
            conn.rollback()
            print(f"Database error: {err}")
            flash(f'Error forwarding document: {err}', 'error')
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

        return redirect(url_for('encoded_documents'))

# "COMPLETE" ACTION BUTTON FOR RECORDS OFFICE
@app.route('/complete_document', methods=['POST'])
def complete_document():
    # Retrieve user ID from session
    user_id = session.get('user_id')
    if not user_id:
        flash("You must be logged in to complete a document.")
        return redirect(url_for('login'))  # Redirect to login if not logged in

    # Get data from the form
    tracking_number = request.form.get('tracking_number')
    comments = request.form.get('comments', '')
    current_date = datetime.now()

    # Connect to the database
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Update the document status to 'Complete'
        update_document_query = """
            UPDATE DOCUMENTS
            SET Status = 'Complete'
            WHERE TrackingNumber = %s
        """
        cursor.execute(update_document_query, (tracking_number,))

        # Insert a new transaction record in TRANSACTIONS
        insert_transaction_query = """
            INSERT INTO TRANSACTIONS (
                OfficeID, DocNo, UserID, CompletedDate,
                ProcessDate, Status, TransactionType, Comments, TrackingNumber
            ) VALUES (
                %s, 
                (SELECT DocNo FROM DOCUMENTS WHERE TrackingNumber = %s), 
                %s, %s, %s, %s, %s, %s, %s
            )
        """
        cursor.execute(insert_transaction_query, (
            session.get('office_id'),  # Assuming 'office_id' is also stored in session
            tracking_number,
            user_id,
            current_date,
            current_date,
            'Completed',
            'Complete',
            comments,
            tracking_number  # Insert the tracking number into the transaction
        ))

        # Commit the transaction
        conn.commit()
        flash("Document marked as complete successfully.")
    except Exception as e:
        conn.rollback()
        flash(f"An error occurred: {e}")
    finally:
        # Close the database connection
        cursor.close()
        conn.close()

    return redirect(url_for('encoded_documents'))  # Redirect to documents page


# TRACK DOCUMENTS IN RECORDS OFFICE / track_records_documents.html
@app.route('/track_records_documents')
@login_required
def track_records_documents():
    page = request.args.get('page', 1, type=int)  # Get the page number from query params
    per_page = 10  # Documents per page
    offset = (page - 1) * per_page

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        # Fetch paginated documents for the Records Office along with user, school, and office details
        cursor.execute(""" 
            SELECT d.TrackingNumber, 
                   u.Firstname, 
                   u.Lastname, 
                   dt.DocTypeName, 
                   d.DocDetails, 
                   d.DocPurpose, 
                   COALESCE(s.SchoolName, o.OfficeName, 'N/A') AS SchoolOrOffice, 
                   d.DateEncoded, 
                   d.DateReceived, 
                   d.Status
            FROM DOCUMENTS d
            JOIN USERS u ON d.UserID = u.UserID
            JOIN DOCUMENT_TYPE dt ON d.DocTypeID = dt.DocTypeID
            LEFT JOIN SCHOOLS s ON d.SchoolID = s.SchoolID
            LEFT JOIN OFFICES o ON d.OfficeID = o.OfficeID
            WHERE d.OfficeID = %s  -- Filter by the Records Office
            ORDER BY d.DateEncoded DESC
            LIMIT %s OFFSET %s
        """, (14, per_page, offset))  # Assuming 14 is the OfficeID for the Records Office

        documents = cursor.fetchall()

        # Count total documents for the Records Office
        cursor.execute("SELECT COUNT(*) FROM DOCUMENTS WHERE OfficeID = %s", (14,))
        total_documents = cursor.fetchone()['COUNT(*)']
        total_pages = (total_documents + per_page - 1) // per_page

        return render_template(
            'records_office/track_records_documents.html',
            documents=documents,
            current_page=page,
            total_pages=total_pages  # Ensure total_pages is defined here
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()
#-----END OF RECORDS DASHBOARD-----#

#-----BUDGET OFFICE DASHBOARD-----#
# "CREATE DOCUMENTS" FOR BUDGET OFFICE / _budget_dashboard.html
@app.route('/_budget_dashboard')
@login_required
def _budget_dashboard():
    # Ensure the user is a staff member
    if session.get('role') != 3:  # Assuming role '3' is for staff
        return redirect(url_for('index'))  # Redirect unauthorized users

    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('logout'))  # Handle case where user ID is not in session

    # Fetch user details
    user = get_user_by_id(user_id)

    conn = None
    cursor = None
    offices = []
    document_type = []  # To hold document types

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Fetch the list of offices from the database (assuming 'OFFICES' table)
        cursor.execute("SELECT OfficeID, OfficeName FROM OFFICES")
        offices = cursor.fetchall()

        # Fetch the list of document types (assuming 'DOCUMENT_TYPES' table)
        cursor.execute("SELECT DocTypeID, DocTypeName FROM DOCUMENT_TYPE")
        document_type = cursor.fetchall()  # [(DocTypeID1, DocTypeName1), (DocTypeID2, DocTypeName2), ...]

    except Exception as e:
        print(f"Error fetching data: {e}")

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    # Pass document types, offices, and user to the template
    return render_template('budget_office/_budget_dashboard.html', user=user, offices=offices, document_type=document_type)

# "MY DOCUMENTS" FOR BUDGET OFFICE / budget_encoded.html
@app.route('/budget_encoded', methods=['GET'])
@login_required
def budget_encoded():
    # Ensure the user is a staff member
    if session.get('role') != 3:  # Assuming role '3' is for staff
        return redirect(url_for('index'))  # Redirect unauthorized users

    page = request.args.get('page', 1, type=int)  # Get the page number from query params
    per_page = 10  # Documents per page
    offset = (page - 1) * per_page

    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('logout'))  # Handle case where user ID is not in session

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        # Fetch paginated documents for the user, excluding those marked as 'Complete'
        cursor.execute("""        
            SELECT d.TrackingNumber, 
                   u.Firstname, 
                   u.Lastname, 
                   dt.DocTypeName, 
                   d.DocDetails, 
                   d.DocPurpose, 
                   COALESCE(s.SchoolName, o.OfficeName, 'N/A') AS SchoolOrOffice, 
                   d.DateEncoded, 
                   d.DateReceived, 
                   d.Status
            FROM DOCUMENTS d
            JOIN USERS u ON d.UserID = u.UserID
            JOIN DOCUMENT_TYPE dt ON d.DocTypeID = dt.DocTypeID
            LEFT JOIN SCHOOLS s ON d.SchoolID = s.SchoolID
            LEFT JOIN OFFICES o ON d.OfficeIDToSend = o.OfficeID
            WHERE (d.UserID = %s OR d.Status = 'Received') AND d.Status != 'Complete'
            ORDER BY d.DateEncoded DESC
            LIMIT %s OFFSET %s
        """, (user_id, per_page, offset))

        documents = cursor.fetchall()

        # Fetch offices to populate the dropdown
        cursor.execute("SELECT OfficeID, OfficeName FROM OFFICES")
        offices = cursor.fetchall()

        # Count total documents for the user, excluding completed documents
        cursor.execute("""
            SELECT COUNT(*) AS total_documents
            FROM DOCUMENTS 
            WHERE (UserID = %s OR Status = 'Received') AND Status NOT IN ('Complete', 'Forward')
        """, (user_id,))
        total_documents = cursor.fetchone()['total_documents']
        total_pages = (total_documents + per_page - 1) // per_page

        return render_template(
            'budget_office/budget_encoded.html',
            documents=documents,
            offices=offices,  # Pass the office data to the template
            current_page=page,
            total_pages=total_pages
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()


# "DOCUMENT FOR RECEIVE" FOR BUDGET / budget_documents.html
@app.route('/budget_documents')
@login_required
def budget_documents():
    page = request.args.get('page', 1, type=int)  # Get the page number from query params
    per_page = 10  # Documents per page
    offset = (page - 1) * per_page

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        # Fetch documents that have been forwarded to the Budget Office
        cursor.execute("""
            SELECT d.DocNo, 
                   d.TrackingNumber, 
                   u.Firstname, 
                   u.Lastname, 
                   dt.DocTypeName, 
                   d.DocDetails, 
                   d.DocPurpose, 
                   s.SchoolName, 
                   o.OfficeName, 
                   d.DateEncoded, 
                   t.Status,
                   t.ForwardDate,  -- Fetch ForwardDate from TRANSACTIONS table
                   t.ForwardedToOfficeID,
                   t.Comments
            FROM DOCUMENTS d
            JOIN USERS u ON d.UserID = u.UserID
            JOIN DOCUMENT_TYPE dt ON d.DocTypeID = dt.DocTypeID
            LEFT JOIN SCHOOLS s ON d.SchoolID = s.SchoolID
            LEFT JOIN OFFICES o ON d.OfficeID = o.OfficeID
            JOIN TRANSACTIONS t ON t.DocNo = d.DocNo
            WHERE t.ForwardedToOfficeID = %s AND t.Status = 'Forwarded'
            ORDER BY t.ForwardDate DESC
            LIMIT %s OFFSET %s
        """, (session.get('office_id'), per_page, offset))  # Assuming office_id is stored in session

        documents = cursor.fetchall()

        # Count total documents forwarded to the Budget Office
        cursor.execute("""
            SELECT COUNT(*) 
            FROM TRANSACTIONS t
            JOIN DOCUMENTS d ON t.DocNo = d.DocNo
            WHERE t.ForwardedToOfficeID = %s AND t.Status = 'Forwarded'
        """, (session.get('office_id'),))

        total_documents = cursor.fetchone()['COUNT(*)']
        total_pages = (total_documents + per_page - 1) // per_page

        return render_template(
            'budget_office/budget_documents.html',  # Template path
            documents=documents,
            current_page=page,
            total_pages=total_pages
        )

    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500

    finally:
        cursor.close()
        conn.close()


# "RECEIVE" ACTION BUTTON FOR BUDGET
@app.route('/budget_receive_document/<int:doc_no>', methods=['POST'])
@login_required
def handle_budget_receive_document(doc_no):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # 1. Check if the document is forwarded to the current office and is in 'Forwarded' status
        cursor.execute("""
            SELECT t.TransactionID, d.TrackingNumber 
            FROM TRANSACTIONS t
            JOIN DOCUMENTS d ON t.DocNo = d.DocNo
            WHERE t.DocNo = %s AND t.ForwardedToOfficeID = %s AND t.Status = 'Forwarded'
        """, (doc_no, session.get('office_id')))
        
        transaction = cursor.fetchone()
        if not transaction:
            return jsonify({"error": "Document not found or not forwarded to your office."}), 404

        tracking_number = transaction[1]  # Get the TrackingNumber

        # 2. Update the DOCUMENTS table to set status to 'Received' and record DateReceived
        cursor.execute("""
            UPDATE DOCUMENTS
            SET Status = %s, DateReceived = NOW()
            WHERE DocNo = %s
        """, ('Received', doc_no))

        # 3. Update the TRANSACTIONS table to mark this transaction as 'Received'
        cursor.execute("""
            UPDATE TRANSACTIONS
            SET Status = %s, ReceivedDate = NOW()
            WHERE TransactionID = %s
        """, ('Received', transaction[0]))

        # 4. Insert a new record in the TRANSACTIONS table for the 'Receive' action
        cursor.execute("""
            INSERT INTO TRANSACTIONS (
                OfficeID, DocNo, UserID, 
                ReceivedDate, Status, TransactionType, TrackingNumber
            )
            VALUES (%s, %s, %s, NOW(), %s, %s, %s)
        """, (
            session.get('office_id'),  # Office receiving the document
            doc_no,                    # Document number being received
            session.get('user_id'),    # The user performing the action
            'Received',                # Status of the transaction
            'Receive',                 # Type of transaction
            tracking_number            # TrackingNumber associated with this document
        ))

        # Commit the transaction to save changes
        conn.commit()

        # Redirect to the budget_documents page
        return redirect(url_for('budget_documents'))

    except Exception as e:
        # Rollback the transaction in case of error
        conn.rollback()
        return jsonify({"error": str(e)}), 500

    finally:
        # Always close the database connection
        cursor.close()
        conn.close()


# "FORWARD" ACTION BUTTON FOR BUDGET OFFICE
@app.route('/budget_forward', methods=['POST'])
def budget_forward():
    tracking_number = request.form.get('tracking_number')
    comments = request.form.get('comments')
    forwarded_to_office_id = request.form.get('forwarded_to_office_id')  # Capture selected office ID

    try:
        # Connect to the database
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # Verify that the document exists
        cursor.execute("SELECT DocNo FROM DOCUMENTS WHERE TrackingNumber = %s", (tracking_number,))
        document = cursor.fetchone()

        if not document:
            flash(f'Document with tracking number {tracking_number} does not exist.', 'error')
            return redirect(url_for('budget_encoded'))

        # Retrieve the document number (DocNo)
        doc_no = document[0]

        # Update document status to 'Forwarded'
        cursor.execute("""
            UPDATE DOCUMENTS
            SET Status = 'Forwarded'
            WHERE TrackingNumber = %s
        """, (tracking_number,))

        # Insert a new transaction record with dynamic ForwardedToOfficeID
        cursor.execute("""
            INSERT INTO TRANSACTIONS (
                OfficeID, DocNo, UserID, ForwardDate, Status, TransactionType, Comments, ForwardedToOfficeID, TrackingNumber
            ) VALUES (%s, %s, %s, NOW(), 'Forwarded', 'Forward', %s, %s, %s)
        """, (
            session.get('office_id'),   # Office initiating the forward
            doc_no,                     # Document number
            session.get('user_id'),     # User performing the action
            comments,                   # Comments from the form
            forwarded_to_office_id,     # Selected office from dropdown
            tracking_number             # Tracking number
        ))

        conn.commit()
        flash(f'Document {tracking_number} forwarded successfully!', 'success')

    except mysql.connector.Error as err:
        conn.rollback()
        print(f"Database error: {err}")
        flash(f'Error forwarding document: {err}', 'error')
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    return redirect(url_for('budget_encoded'))


#COMPLETE ACTION BUTTON FOR RECORDS OFFICE
@app.route('/budget_complete', methods=['POST'])
def budget_complete():
    # Retrieve user ID from session
    user_id = session.get('user_id')
    if not user_id:
        flash("You must be logged in to complete a document.")
        return redirect(url_for('login'))  # Redirect to login if not logged in

    # Get data from the form
    tracking_number = request.form.get('tracking_number')
    comments = request.form.get('comments', '')
    current_date = datetime.now()

    # Connect to the database
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Update the document status to 'Complete'
        update_document_query = """
            UPDATE DOCUMENTS
            SET Status = 'Completed'
            WHERE TrackingNumber = %s
        """
        cursor.execute(update_document_query, (tracking_number,))

        # Insert a new transaction record in TRANSACTIONS
        insert_transaction_query = """
            INSERT INTO TRANSACTIONS (
                OfficeID, DocNo, UserID, CompletedDate,
                ProcessDate, Status, TransactionType, Comments, TrackingNumber
            ) VALUES (
                %s, 
                (SELECT DocNo FROM DOCUMENTS WHERE TrackingNumber = %s), 
                %s, %s, %s, %s, %s, %s, %s
            )
        """
        cursor.execute(insert_transaction_query, (
            session.get('office_id'),  # Assuming 'office_id' is also stored in session
            tracking_number,
            user_id,
            current_date,
            current_date,
            'Completed',
            'Complete',
            comments,
            tracking_number  # Insert the tracking number into the transaction
        ))

        # Commit the transaction
        conn.commit()
        flash("Document marked as complete successfully.")
    except Exception as e:
        conn.rollback()
        flash(f"An error occurred: {e}")
    finally:
        # Close the database connection
        cursor.close()
        conn.close()

    return redirect(url_for('budget_encoded'))  # Redirect to documents page

# TRACK DOCUMENTS IN BUDGET OFFICE / track_budget_documents.html
@app.route('/track_budget_documents')
@login_required
def track_budget_documents():
    page = request.args.get('page', 1, type=int)  # Get the page number from query params
    per_page = 10  # Documents per page
    offset = (page - 1) * per_page

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        # Fetch paginated documents for the Budget Office along with user, school, and office details
        cursor.execute(""" 
            SELECT d.TrackingNumber, 
                   u.Firstname, 
                   u.Lastname, 
                   dt.DocTypeName, 
                   d.DocDetails, 
                   d.DocPurpose, 
                   COALESCE(s.SchoolName, o.OfficeName, 'N/A') AS SchoolOrOffice, 
                   d.DateEncoded, 
                   d.DateReceived, 
                   d.Status
            FROM DOCUMENTS d
            JOIN USERS u ON d.UserID = u.UserID
            JOIN DOCUMENT_TYPE dt ON d.DocTypeID = dt.DocTypeID
            LEFT JOIN SCHOOLS s ON d.SchoolID = s.SchoolID
            LEFT JOIN OFFICES o ON d.OfficeID = o.OfficeID
            WHERE d.OfficeID = %s  -- Filter by the Budget Office
            ORDER BY d.DateEncoded DESC
            LIMIT %s OFFSET %s
        """, (9, per_page, offset))  # Assuming 9 is the OfficeID for the Budget Office

        documents = cursor.fetchall()

        # Count total documents for the Budget Office
        cursor.execute("SELECT COUNT(*) FROM DOCUMENTS WHERE OfficeID = %s", (9,))
        total_documents = cursor.fetchone()['COUNT(*)']
        total_pages = (total_documents + per_page - 1) // per_page

        return render_template(
            'budget_office/track_budget_documents.html',
            documents=documents,
            current_page=page,
            total_pages=total_pages  # Ensure total_pages is defined here
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()
#-----END OF BUDGET DASHBOARD-----#

#-----CASHIER OFFICE DASHBOARD------#
# "CREATE DOCUMENTS" FOR CASHIER OFFICE / _cashier_dashboard.html
@app.route('/_cashier_dashboard')
@login_required
def _cashier_dashboard():
    # Ensure the user is a staff member
    if session.get('role') != 3:  # Assuming role '3' is for staff
        return redirect(url_for('index'))  # Redirect unauthorized users

    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('logout'))  # Handle case where user ID is not in session

    # Fetch user details
    user = get_user_by_id(user_id)

    conn = None
    cursor = None
    offices = []
    document_types = []  # To hold document types

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Fetch the list of offices from the database (assuming 'OFFICES' table)
        cursor.execute("SELECT OfficeID, OfficeName FROM OFFICES")
        offices = cursor.fetchall()

        # Fetch the list of document types (assuming 'DOCUMENT_TYPE' table)
        cursor.execute("SELECT DocTypeID, DocTypeName FROM DOCUMENT_TYPE")
        document_types = cursor.fetchall()  # [(DocTypeID1, DocTypeName1), (DocTypeID2, DocTypeName2), ...]

        # Optionally fetch any other data needed for the cashier dashboard here

    except Exception as e:
        print(f"Error fetching data: {e}")

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    # Render the cashier dashboard with the fetched data
    return render_template(
        'cashier_office/_cashier_dashboard.html',  # Render the cashier dashboard
        user=user,
        offices=offices,
        document_type=document_types  # Renamed variable for clarity
    )

# "MY DOCUMENTS" FOR CASHIER OFFICE / cashier_encoded.html
@app.route('/cashier_encoded', methods=['GET'])
@login_required
def cashier_encoded():
    # Ensure the user is a staff member
    if session.get('role') != 3:  # Assuming role '3' is for staff
        return redirect(url_for('index'))  # Redirect unauthorized users

    page = request.args.get('page', 1, type=int)  # Get the page number from query params
    per_page = 10  # Documents per page
    offset = (page - 1) * per_page

    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('logout'))  # Handle case where user ID is not in session

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        # Fetch paginated documents for the user, excluding completed documents
        cursor.execute("""
            SELECT d.TrackingNumber, 
                   u.Firstname, 
                   u.Lastname, 
                   dt.DocTypeName, 
                   d.DocDetails, 
                   d.DocPurpose, 
                   COALESCE(s.SchoolName, o.OfficeName, 'N/A') AS SchoolOrOffice, 
                   d.DateEncoded, 
                   d.DateReceived, 
                   d.Status,
                   d.OfficeIDToSend
            FROM DOCUMENTS d
            JOIN USERS u ON d.UserID = u.UserID
            JOIN DOCUMENT_TYPE dt ON d.DocTypeID = dt.DocTypeID
            LEFT JOIN SCHOOLS s ON d.SchoolID = s.SchoolID
            LEFT JOIN OFFICES o ON d.OfficeIDToSend = o.OfficeID
            WHERE d.UserID = %s AND d.Status != 'Completed'
            ORDER BY d.DateEncoded DESC
            LIMIT %s OFFSET %s
        """, (user_id, per_page, offset))

        documents = cursor.fetchall()

        # Count total documents for the user, excluding completed documents
        cursor.execute("SELECT COUNT(*) FROM DOCUMENTS WHERE UserID = %s AND Status != 'Completed'", (user_id,))
        total_documents = cursor.fetchone()['COUNT(*)']
        total_pages = (total_documents + per_page - 1) // per_page

        return render_template(
            'cashier_office/cashier_encoded.html',
            documents=documents,
            current_page=page,
            total_pages=total_pages  # Ensure total_pages is defined here
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

# "DOCUMENT FOR RECEIVE" FOR CASHIER OFFICE /  cashier_documents.html
@app.route('/cashier_documents')
@login_required
def cashier_documents():
    page = request.args.get('page', 1, type=int)  # Get the page number from query params
    per_page = 10  # Documents per page
    offset = (page - 1) * per_page

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        # Fetch paginated documents created by USERS and forwarded to the Cashier's Office
        cursor.execute(""" 
            SELECT d.DocNo,  -- Include the DocNo here
                   d.TrackingNumber, 
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
            WHERE d.OfficeIDToSend = %s  -- Filter by the OfficeID for Cashier's Office
            ORDER BY d.DateEncoded DESC
            LIMIT %s OFFSET %s
        """, (session.get('office_id'), per_page, offset))  # Assuming office_id is stored in session

        documents = cursor.fetchall()

        # Count total documents forwarded to the Cashier's Office created by USERS and STAFF
        cursor.execute("""
            SELECT COUNT(*) FROM DOCUMENTS d 
            JOIN USERS u ON d.UserID = u.UserID 
            WHERE d.OfficeIDToSend = %s 
        """, (session.get('office_id'),))
        
        total_documents = cursor.fetchone()['COUNT(*)']
        total_pages = (total_documents + per_page - 1) // per_page

        return render_template(
            'cashier_office/cashier_documents.html',  # Ensure you have this template
            documents=documents,
            current_page=page,
            total_pages=total_pages
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

# "RECEIVE" ACTION BUTTON FOR CASHIER OFFICE
@app.route('/cashier_receive_document/<int:doc_no>', methods=['POST'])
@login_required
def handle_cashier_receive_document(doc_no):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # 1. Update the status of the document to 'Received' and set DateReceived
        cursor.execute("""
            UPDATE DOCUMENTS
            SET Status = %s, DateReceived = NOW()
            WHERE DocNo = %s AND OfficeID = %s
        """, ('Received', doc_no, session.get('office_id')))
        
        if cursor.rowcount == 0:
            return jsonify({"error": "Document not found or already received."}), 404

        # 2. Fetch the TrackingNumber for this document
        cursor.execute("SELECT TrackingNumber FROM DOCUMENTS WHERE DocNo = %s", (doc_no,))
        tracking_number_result = cursor.fetchone()
        tracking_number = tracking_number_result[0] if tracking_number_result else None

        # 3. Insert the transaction into the TRANSACTIONS table
        cursor.execute("""
            INSERT INTO TRANSACTIONS (
                OfficeID, DocNo, UserID, 
                ReceivedDate, Status, TransactionType, TrackingNumber
            )
            VALUES (%s, %s, %s, NOW(), %s, %s, %s)
        """, (
            session.get('office_id'),  # Office receiving the document
            doc_no,                    # Document number being received
            session.get('user_id'),    # The user performing the action
            'Received',                # Status of the transaction
            'Receive',                 # Type of transaction
            tracking_number            # TrackingNumber associated with this document
        ))

        conn.commit()
        return redirect(url_for('cashier_documents'))

    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500

    finally:
        cursor.close()
        conn.close()

# "FORWARD" ACTION BUTTON FOR CASHIER OFFICE
@app.route('/cashier_forward', methods=['POST'])
def cashier_forward():
    tracking_number = request.form.get('tracking_number')
    comments = request.form.get('comments')
    forwarded_to_office_id = request.form.get('forwarded_to_office_id')  # Capture selected office ID

    try:
        # Connect to the database
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # Verify that the document exists
        cursor.execute("SELECT DocNo FROM DOCUMENTS WHERE TrackingNumber = %s", (tracking_number,))
        document = cursor.fetchone()

        if not document:
            flash(f'Document with tracking number {tracking_number} does not exist.', 'error')
            return redirect(url_for('encoded_documents'))

        # Retrieve the document number (DocNo)
        doc_no = document[0]

        # Update document status to 'Forwarded'
        cursor.execute("""
            UPDATE DOCUMENTS
            SET Status = 'Forwarded'
            WHERE TrackingNumber = %s
        """, (tracking_number,))

        # Insert a new transaction record with dynamic ForwardedToOfficeID
        cursor.execute("""
            INSERT INTO TRANSACTIONS (
                OfficeID, DocNo, UserID, ForwardDate, Status, TransactionType, Comments, ForwardedToOfficeID, TrackingNumber
            ) VALUES (%s, %s, %s, NOW(), 'Forwarded', 'Forward', %s, %s, %s)
        """, (
            session.get('office_id'),   # Office initiating the forward
            doc_no,                     # Document number
            session.get('user_id'),     # User performing the action
            comments,                   # Comments from the form
            forwarded_to_office_id,     # Selected office from dropdown
            tracking_number             # Tracking number
        ))

        conn.commit()
        flash(f'Document {tracking_number} forwarded successfully!', 'success')

    except mysql.connector.Error as err:
        conn.rollback()
        print(f"Database error: {err}")
        flash(f'Error forwarding document: {err}', 'error')
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    return redirect(url_for('cashier_encoded'))


# "COMPLETE" ACTION BUTTON FOR CASHIER
@app.route('/cashier_complete', methods=['POST'])
def cashier_complete():
    # Retrieve user ID from session
    user_id = session.get('user_id')
    if not user_id:
        flash("You must be logged in to complete a document.")
        return redirect(url_for('login'))  # Redirect to login if not logged in

    # Get data from the form
    tracking_number = request.form.get('tracking_number')
    comments = request.form.get('comments', '')
    current_date = datetime.now()

    # Connect to the database
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Update the document status to 'Complete'
        update_document_query = """
            UPDATE DOCUMENTS
            SET Status = 'Completed'
            WHERE TrackingNumber = %s
        """
        cursor.execute(update_document_query, (tracking_number,))

        # Insert a new transaction record in TRANSACTIONS
        insert_transaction_query = """
            INSERT INTO TRANSACTIONS (
                OfficeID, DocNo, UserID, CompletedDate,
                ProcessDate, Status, TransactionType, Comments, TrackingNumber
            ) VALUES (
                %s, 
                (SELECT DocNo FROM DOCUMENTS WHERE TrackingNumber = %s), 
                %s, %s, %s, %s, %s, %s, %s
            )
        """
        cursor.execute(insert_transaction_query, (
            session.get('office_id'),  # Assuming 'office_id' is also stored in session
            tracking_number,
            user_id,
            current_date,
            current_date,
            'Completed',
            'Complete',
            comments,
            tracking_number  # Insert the tracking number into the transaction
        ))

        # Commit the transaction
        conn.commit()
        flash("Document marked as complete successfully.")
    except Exception as e:
        conn.rollback()
        flash(f"An error occurred: {e}")
    finally:
        # Close the database connection
        cursor.close()
        conn.close()

    return redirect(url_for('cashier_encoded'))  # Redirect to documents page

# "TRACK DOCUMENTS" IN CASHIER OFFICE / track_cashier_documents.html
@app.route('/track_cashier_documents')
@login_required
def track_cashier_documents():
    page = request.args.get('page', 1, type=int)  # Get the page number from query params
    per_page = 10  # Documents per page
    offset = (page - 1) * per_page

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        # Fetch paginated documents for the Cashier Office along with user, school, and office details
        cursor.execute(""" 
            SELECT d.TrackingNumber, 
                   u.Firstname, 
                   u.Lastname, 
                   dt.DocTypeName, 
                   d.DocDetails, 
                   d.DocPurpose, 
                   COALESCE(s.SchoolName, o.OfficeName, 'N/A') AS SchoolOrOffice, 
                   d.DateEncoded, 
                   d.DateReceived, 
                   d.Status
            FROM DOCUMENTS d
            JOIN USERS u ON d.UserID = u.UserID
            JOIN DOCUMENT_TYPE dt ON d.DocTypeID = dt.DocTypeID
            LEFT JOIN SCHOOLS s ON d.SchoolID = s.SchoolID
            LEFT JOIN OFFICES o ON d.OfficeID = o.OfficeID
            WHERE d.OfficeID = %s  -- Filter by the Cashier Office
            ORDER BY d.DateEncoded DESC
            LIMIT %s OFFSET %s
        """, (10, per_page, offset))  # Assuming 10 is the OfficeID for the Cashier Office

        documents = cursor.fetchall()

        # Count total documents for the Cashier Office
        cursor.execute("SELECT COUNT(*) FROM DOCUMENTS WHERE OfficeID = %s", (10,))
        total_documents = cursor.fetchone()['COUNT(*)']
        total_pages = (total_documents + per_page - 1) // per_page

        return render_template(
            'cashier_office/track_cashier_documents.html',
            documents=documents,
            current_page=page,
            total_pages=total_pages  # Ensure total_pages is defined here
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

#DISPLAY FORWARDED DOCUMENTS FOR CASHIER
@app.route('/cashier_forwarded_documents', methods=['GET'])
def cashier_forwarded_documents():
    # Pagination logic
    page = request.args.get('page', 1, type=int)  # Get current page from URL parameters
    per_page = 10  # Set number of documents per page
    offset = (page - 1) * per_page

    # Fetch forwarded documents from the database
    forwarded_documents = get_forwarded_documents(offset, per_page)  # Adjust this function as needed
    total_documents = len(forwarded_documents)  # Adjust this according to your query
    total_pages = (total_documents // per_page) + (total_documents % per_page > 0)  # Calculate total pages

    return render_template('cashier_office/cashier_forwarded_documents.html', 
                           forwarded_documents=forwarded_documents,
                           current_page=page,
                           total_pages=total_pages)
#-----END OF CASHIER DASHOBARD-----#

#-----HRMU OFFICE DASHBOARD-----#
# "CREATE DOCUMENTS " FOR FOR HRMU OFFICE / _hrmu_dashboard.html
@app.route('/_hrmu_dashboard')
@login_required
def _hrmu_dashboard():
    # Ensure the user is an HRMU staff member
    if session.get('role') != 3:  # Assuming role '2' is for HRMU staff
        return redirect(url_for('index'))  # Redirect unauthorized users

    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('logout'))  # Handle case where user ID is not in session

    # Fetch user details
    user = get_user_by_id(user_id)

    conn = None
    cursor = None
    offices = []
    document_type = []  # To hold document types

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Fetch the list of offices from the database (assuming 'OFFICES' table)
        cursor.execute("SELECT OfficeID, OfficeName FROM OFFICES")
        offices = cursor.fetchall()

        # Fetch the list of document types (assuming 'DOCUMENT_TYPES' table)
        cursor.execute("SELECT DocTypeID, DocTypeName FROM DOCUMENT_TYPE")
        document_type = cursor.fetchall()  # [(DocTypeID1, DocTypeName1), (DocTypeID2, DocTypeName2), ...]

    except Exception as e:
        print(f"Error fetching data: {e}")

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    # Pass document types, offices, and user to the template
    return render_template('hrmu_office/_hrmu_dashboard.html', user=user, offices=offices, document_type=document_type)

# "MY DOCUMENTS" FOR HRMU OFFICE / hrmu_encoded.html
@app.route('/hrmu_encoded', methods=['GET'])
@login_required
def hrmu_encoded():
    # Ensure the user is a staff member
    if session.get('role') != 3:  # Assuming role '3' is for staff
        return redirect(url_for('index'))  # Redirect unauthorized users

    page = request.args.get('page', 1, type=int)  # Get the page number from query params
    per_page = 10  # Documents per page
    offset = (page - 1) * per_page

    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('logout'))  # Handle case where user ID is not in session

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        # Fetch paginated documents for the user along with document type and school/office details
        cursor.execute("""
            SELECT d.TrackingNumber, 
                   u.Firstname, 
                   u.Lastname, 
                   dt.DocTypeName, 
                   d.DocDetails, 
                   d.DocPurpose, 
                   COALESCE(s.SchoolName, o.OfficeName, 'N/A') AS SchoolOrOffice, 
                   d.DateEncoded, 
                   d.DateReceived, 
                   d.Status,
                   d.OfficeIDToSend
            FROM DOCUMENTS d
            JOIN USERS u ON d.UserID = u.UserID
            JOIN DOCUMENT_TYPE dt ON d.DocTypeID = dt.DocTypeID
            LEFT JOIN SCHOOLS s ON d.SchoolID = s.SchoolID
            LEFT JOIN OFFICES o ON d.OfficeIDToSend = o.OfficeID
            WHERE d.UserID = %s
            ORDER BY d.DateEncoded DESC
            LIMIT %s OFFSET %s
        """, (user_id, per_page, offset))

        documents = cursor.fetchall()

        # Count total documents for the user
        cursor.execute("SELECT COUNT(*) FROM DOCUMENTS WHERE UserID = %s", (user_id,))
        total_documents = cursor.fetchone()['COUNT(*)']
        total_pages = (total_documents + per_page - 1) // per_page

        return render_template(
            'hrmu_office/hrmu_encoded.html',
            documents=documents,
            current_page=page,
            total_pages=total_pages  # Ensure total_pages is defined here
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

# "DOCUMENT FOR RECEIVE" FOR HRMU OFFICE / hrmu_documents.html
@app.route('/hrmu_documents')
@login_required
def hrmu_documents():
    page = request.args.get('page', 1, type=int)  # Get the page number from query params
    per_page = 10  # Documents per page
    offset = (page - 1) * per_page

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        # Fetch paginated documents created by USERS and forwarded to the HRMU's Office
        cursor.execute(""" 
            SELECT d.DocNo,  -- Include the DocNo here
                   d.TrackingNumber, 
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
            WHERE d.OfficeIDToSend = %s  -- Filter by the OfficeID for HRMU's Office
            ORDER BY d.DateEncoded DESC
            LIMIT %s OFFSET %s
        """, (session.get('office_id'), per_page, offset))  # Assuming office_id is stored in session

        documents = cursor.fetchall()

        # Count total documents forwarded to the HRMU's Office created by USERS and STAFF
        cursor.execute("""
            SELECT COUNT(*) FROM DOCUMENTS d 
            JOIN USERS u ON d.UserID = u.UserID 
            WHERE d.OfficeIDToSend = %s 
        """, (session.get('office_id'),))
        
        total_documents = cursor.fetchone()['COUNT(*)']
        total_pages = (total_documents + per_page - 1) // per_page

        return render_template(
            'hrmu_office/hrmu_documents.html',  # Ensure you have this template
            documents=documents,
            current_page=page,
            total_pages=total_pages
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

# "RECEIVE" ACTION BUTTON FOR HRMU OFFICE
@app.route('/hrmu_receive_document/<int:doc_no>', methods=['POST'])
@login_required
def handle_hrmu_receive_document(doc_no):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # 1. Update the status of the document to 'Received' and set DateReceived
        cursor.execute("""
            UPDATE DOCUMENTS
            SET Status = %s, DateReceived = NOW()
            WHERE DocNo = %s AND OfficeID = %s
        """, ('Received', doc_no, session.get('office_id')))
        
        if cursor.rowcount == 0:
            return jsonify({"error": "Document not found or already received."}), 404

        # 2. Fetch the TrackingNumber for this document
        cursor.execute("SELECT TrackingNumber FROM DOCUMENTS WHERE DocNo = %s", (doc_no,))
        tracking_number_result = cursor.fetchone()
        tracking_number = tracking_number_result[0] if tracking_number_result else None

        # 3. Insert the transaction into the TRANSACTIONS table
        cursor.execute("""
            INSERT INTO TRANSACTIONS (
                OfficeID, DocNo, UserID, 
                ReceivedDate, Status, TransactionType, TrackingNumber
            )
            VALUES (%s, %s, %s, NOW(), %s, %s, %s)
        """, (
            session.get('office_id'),  # Office receiving the document
            doc_no,                    # Document number being received
            session.get('user_id'),    # The user performing the action
            'Received',                # Status of the transaction
            'Receive',                 # Type of transaction
            tracking_number            # TrackingNumber associated with this document
        ))

        conn.commit()
        return redirect(url_for('hrmu_documents'))

    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500

    finally:
        cursor.close()
        conn.close()

# "FORWARD" ACTION BUTTON FOR HRMU OFFICE
@app.route('/hrmu_forward', methods=['POST'])
def hrmu_forward():
    tracking_number = request.form.get('tracking_number')
    comments = request.form.get('comments')
    forwarded_to_office_id = request.form.get('forwarded_to_office_id')  # Capture selected office ID

    try:
        # Connect to the database
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # Verify that the document exists
        cursor.execute("SELECT DocNo FROM DOCUMENTS WHERE TrackingNumber = %s", (tracking_number,))
        document = cursor.fetchone()

        if not document:
            flash(f'Document with tracking number {tracking_number} does not exist.', 'error')
            return redirect(url_for('encoded_documents'))

        # Retrieve the document number (DocNo)
        doc_no = document[0]

        # Update document status to 'Forwarded'
        cursor.execute("""
            UPDATE DOCUMENTS
            SET Status = 'Forwarded'
            WHERE TrackingNumber = %s
        """, (tracking_number,))

        # Insert a new transaction record with dynamic ForwardedToOfficeID
        cursor.execute("""
            INSERT INTO TRANSACTIONS (
                OfficeID, DocNo, UserID, ForwardDate, Status, TransactionType, Comments, ForwardedToOfficeID, TrackingNumber
            ) VALUES (%s, %s, %s, NOW(), 'Forwarded', 'Forward', %s, %s, %s)
        """, (
            session.get('office_id'),   # Office initiating the forward
            doc_no,                     # Document number
            session.get('user_id'),     # User performing the action
            comments,                   # Comments from the form
            forwarded_to_office_id,     # Selected office from dropdown
            tracking_number             # Tracking number
        ))

        conn.commit()
        flash(f'Document {tracking_number} forwarded successfully!', 'success')

    except mysql.connector.Error as err:
        conn.rollback()
        print(f"Database error: {err}")
        flash(f'Error forwarding document: {err}', 'error')
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    return redirect(url_for('hrmu_encoded'))


# "COMPLETE" ACTION BUTTON FOR HRMU OFFICE
@app.route('/hrmu_complete', methods=['POST'])
def hrmu_complete():
    # Retrieve user ID from session
    user_id = session.get('user_id')
    if not user_id:
        flash("You must be logged in to complete a document.")
        return redirect(url_for('login'))  # Redirect to login if not logged in

    # Get data from the form
    tracking_number = request.form.get('tracking_number')
    comments = request.form.get('comments', '')
    current_date = datetime.now()

    # Connect to the database
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Update the document status to 'Complete'
        update_document_query = """
            UPDATE DOCUMENTS
            SET Status = 'Completed'
            WHERE TrackingNumber = %s
        """
        cursor.execute(update_document_query, (tracking_number,))

        # Insert a new transaction record in TRANSACTIONS
        insert_transaction_query = """
            INSERT INTO TRANSACTIONS (
                OfficeID, DocNo, UserID, CompletedDate,
                ProcessDate, Status, TransactionType, Comments, TrackingNumber
            ) VALUES (
                %s, 
                (SELECT DocNo FROM DOCUMENTS WHERE TrackingNumber = %s), 
                %s, %s, %s, %s, %s, %s, %s
            )
        """
        cursor.execute(insert_transaction_query, (
            session.get('office_id'),  # Assuming 'office_id' is also stored in session
            tracking_number,
            user_id,
            current_date,
            current_date,
            'Completed',
            'Complete',
            comments,
            tracking_number  # Insert the tracking number into the transaction
        ))

        # Commit the transaction
        conn.commit()
        flash("Document marked as complete successfully.")
    except Exception as e:
        conn.rollback()
        flash(f"An error occurred: {e}")
    finally:
        # Close the database connection
        cursor.close()
        conn.close()

    return redirect(url_for('hrmu_encoded'))  # Redirect to documents page


#" TRACK DOCUMENTS" IN HRMU OFFICE / track_cashier_documents.html
@app.route('/track_hrmu_documents')
@login_required
def track_hrmu_documents():
    page = request.args.get('page', 1, type=int)  # Get the page number from query params
    per_page = 10  # Documents per page
    offset = (page - 1) * per_page

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        # Fetch paginated documents for the HRMU Office along with user, school, and office details
        cursor.execute(""" 
            SELECT d.TrackingNumber, 
                   u.Firstname, 
                   u.Lastname, 
                   dt.DocTypeName, 
                   d.DocDetails, 
                   d.DocPurpose, 
                   COALESCE(s.SchoolName, o.OfficeName, 'N/A') AS SchoolOrOffice, 
                   d.DateEncoded, 
                   d.DateReceived, 
                   d.Status
            FROM DOCUMENTS d
            JOIN USERS u ON d.UserID = u.UserID
            JOIN DOCUMENT_TYPE dt ON d.DocTypeID = dt.DocTypeID
            LEFT JOIN SCHOOLS s ON d.SchoolID = s.SchoolID
            LEFT JOIN OFFICES o ON d.OfficeID = o.OfficeID
            WHERE d.OfficeID = %s  -- Filter by the HRMU Office
            ORDER BY d.DateEncoded DESC
            LIMIT %s OFFSET %s
        """, (11, per_page, offset))  # Assuming 11 is the OfficeID for HRMU Office

        documents = cursor.fetchall()

        # Count total documents for the HRMU Office
        cursor.execute("SELECT COUNT(*) FROM DOCUMENTS WHERE OfficeID = %s", (11,))
        total_documents = cursor.fetchone()['COUNT(*)']
        total_pages = (total_documents + per_page - 1) // per_page

        return render_template(
            'hrmu_office/track_hrmu_documents.html',
            documents=documents,
            current_page=page,
            total_pages=total_pages  # Ensure total_pages is defined here
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()
#-----END OF HRMU DASHBOARD-----#

#-----ICT OFFICE DASHBOARD-----#
# "CREATE DOCUMENTS" FOR ICT DASHBOARD / _ict_dashboard.html
@app.route('/_ict_dashboard')
@login_required
def _ict_dashboard():
    # Ensure the user is an ICT staff member
    if session.get('role') != 3:  # Assuming role '4' is for ICT staff
        return redirect(url_for('index'))  # Redirect unauthorized users

    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('logout'))  # Handle case where user ID is not in session

    # Fetch user details
    user = get_user_by_id(user_id)

    conn = None
    cursor = None
    offices = []
    document_type = []  # To hold document types

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Fetch the list of offices from the database (assuming 'OFFICES' table)
        cursor.execute("SELECT OfficeID, OfficeName FROM OFFICES")
        offices = cursor.fetchall()

        # Fetch the list of document types (assuming 'DOCUMENT_TYPES' table)
        cursor.execute("SELECT DocTypeID, DocTypeName FROM DOCUMENT_TYPE")
        document_type = cursor.fetchall()  # [(DocTypeID1, DocTypeName1), (DocTypeID2, DocTypeName2), ...]

    except Exception as e:
        print(f"Error fetching data: {e}")

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    # Pass document types, offices, and user to the template
    return render_template('ict_office/_ict_dashboard.html', user=user, offices=offices, document_type=document_type)

# "MY DOCUMENTS" FOR ICT OFFICE / ict_encoded.html
@app.route('/ict_encoded', methods=['GET'])
@login_required
def ict_encoded():
    # Ensure the user is a staff member
    if session.get('role') != 3:  # Assuming role '3' is for staff
        return redirect(url_for('index'))  # Redirect unauthorized users

    page = request.args.get('page', 1, type=int)  # Get the page number from query params
    per_page = 10  # Documents per page
    offset = (page - 1) * per_page

    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('logout'))  # Handle case where user ID is not in session

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        # Fetch paginated documents for the user along with document type and school/office details
        cursor.execute("""
            SELECT d.TrackingNumber, 
                   u.Firstname, 
                   u.Lastname, 
                   dt.DocTypeName, 
                   d.DocDetails, 
                   d.DocPurpose, 
                   COALESCE(s.SchoolName, o.OfficeName, 'N/A') AS SchoolOrOffice, 
                   d.DateEncoded, 
                   d.DateReceived, 
                   d.Status,
                   d.OfficeIDToSend
            FROM DOCUMENTS d
            JOIN USERS u ON d.UserID = u.UserID
            JOIN DOCUMENT_TYPE dt ON d.DocTypeID = dt.DocTypeID
            LEFT JOIN SCHOOLS s ON d.SchoolID = s.SchoolID
            LEFT JOIN OFFICES o ON d.OfficeIDToSend = o.OfficeID
            WHERE d.UserID = %s
            ORDER BY d.DateEncoded DESC
            LIMIT %s OFFSET %s
        """, (user_id, per_page, offset))

        documents = cursor.fetchall()

        # Count total documents for the user
        cursor.execute("SELECT COUNT(*) FROM DOCUMENTS WHERE UserID = %s", (user_id,))
        total_documents = cursor.fetchone()['COUNT(*)']
        total_pages = (total_documents + per_page - 1) // per_page

        return render_template(
            'ict_office/ict_encoded.html',
            documents=documents,
            current_page=page,
            total_pages=total_pages  # Ensure total_pages is defined here
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

# "DOCUMENT FOR RECEIVE" FOR ICT OFFICE /ict_documents.html
@app.route('/ict_documents')
@login_required
def ict_documents():
    page = request.args.get('page', 1, type=int)  # Get the page number from query params
    per_page = 10  # Documents per page
    offset = (page - 1) * per_page

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        # Fetch paginated documents created by USERS and forwarded to the ICT Office
        cursor.execute(""" 
            SELECT d.DocNo,  -- Include the DocNo here
                   d.TrackingNumber, 
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
            WHERE d.OfficeIDToSend = %s  -- Filter by the OfficeID for ICT Office
            ORDER BY d.DateEncoded DESC
            LIMIT %s OFFSET %s
        """, (session.get('office_id'), per_page, offset))  # Assuming office_id is stored in session

        documents = cursor.fetchall()

        # Count total documents forwarded to the ICT Office created by USERS and STAFF
        cursor.execute("""
            SELECT COUNT(*) FROM DOCUMENTS d 
            JOIN USERS u ON d.UserID = u.UserID 
            WHERE d.OfficeIDToSend = %s 
        """, (session.get('office_id'),))
        
        total_documents = cursor.fetchone()['COUNT(*)']
        total_pages = (total_documents + per_page - 1) // per_page

        return render_template(
            'ict_office/ict_documents.html',  # Ensure you have this template
            documents=documents,
            current_page=page,
            total_pages=total_pages
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

# "RECEIVE" ACTION BUTTON FOR ICT OFFICE
@app.route('/ict_receive_document/<int:doc_no>', methods=['POST'])
@login_required
def handle_ict_receive_document(doc_no):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # 1. Update the status of the document to 'Received' and set DateReceived
        cursor.execute("""
            UPDATE DOCUMENTS
            SET Status = %s, DateReceived = NOW()
            WHERE DocNo = %s AND OfficeID = %s
        """, ('Received', doc_no, session.get('office_id')))
        
        if cursor.rowcount == 0:
            return jsonify({"error": "Document not found or already received."}), 404

        # 2. Fetch the TrackingNumber for this document
        cursor.execute("SELECT TrackingNumber FROM DOCUMENTS WHERE DocNo = %s", (doc_no,))
        tracking_number_result = cursor.fetchone()
        tracking_number = tracking_number_result[0] if tracking_number_result else None

        # 3. Insert the transaction into the TRANSACTIONS table
        cursor.execute("""
            INSERT INTO TRANSACTIONS (
                OfficeID, DocNo, UserID, 
                ReceivedDate, Status, TransactionType, TrackingNumber
            )
            VALUES (%s, %s, %s, NOW(), %s, %s, %s)
        """, (
            session.get('office_id'),  # Office receiving the document
            doc_no,                    # Document number being received
            session.get('user_id'),    # The user performing the action
            'Received',                # Status of the transaction
            'Receive',                 # Type of transaction
            tracking_number            # TrackingNumber associated with this document
        ))

        conn.commit()
        return redirect(url_for('ict_documents'))

    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500

    finally:
        cursor.close()
        conn.close()

# "FORWARD" ACTION BUTTON FOR ICT OFFICE
@app.route('/ict_forward', methods=['POST'])
def ict_forward():
    tracking_number = request.form.get('tracking_number')
    comments = request.form.get('comments')
    forwarded_to_office_id = request.form.get('forwarded_to_office_id')  # Capture selected office ID

    try:
        # Connect to the database
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # Verify that the document exists
        cursor.execute("SELECT DocNo FROM DOCUMENTS WHERE TrackingNumber = %s", (tracking_number,))
        document = cursor.fetchone()

        if not document:
            flash(f'Document with tracking number {tracking_number} does not exist.', 'error')
            return redirect(url_for('encoded_documents'))

        # Retrieve the document number (DocNo)
        doc_no = document[0]

        # Update document status to 'Forwarded'
        cursor.execute("""
            UPDATE DOCUMENTS
            SET Status = 'Forwarded'
            WHERE TrackingNumber = %s
        """, (tracking_number,))

        # Insert a new transaction record with dynamic ForwardedToOfficeID
        cursor.execute("""
            INSERT INTO TRANSACTIONS (
                OfficeID, DocNo, UserID, ForwardDate, Status, TransactionType, Comments, ForwardedToOfficeID, TrackingNumber
            ) VALUES (%s, %s, %s, NOW(), 'Forwarded', 'Forward', %s, %s, %s)
        """, (
            session.get('office_id'),   # Office initiating the forward
            doc_no,                     # Document number
            session.get('user_id'),     # User performing the action
            comments,                   # Comments from the form
            forwarded_to_office_id,     # Selected office from dropdown
            tracking_number             # Tracking number
        ))

        conn.commit()
        flash(f'Document {tracking_number} forwarded successfully!', 'success')

    except mysql.connector.Error as err:
        conn.rollback()
        print(f"Database error: {err}")
        flash(f'Error forwarding document: {err}', 'error')
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    return redirect(url_for('ict_encoded'))


# "COMPLETE" ACTION BUTTON FOR ICT OFFICE
@app.route('/ict_complete', methods=['POST'])
def ict_complete():
    # Retrieve user ID from session
    user_id = session.get('user_id')
    if not user_id:
        flash("You must be logged in to complete a document.")
        return redirect(url_for('login'))  # Redirect to login if not logged in

    # Get data from the form
    tracking_number = request.form.get('tracking_number')
    comments = request.form.get('comments', '')
    current_date = datetime.now()

    # Connect to the database
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Update the document status to 'Complete'
        update_document_query = """
            UPDATE DOCUMENTS
            SET Status = 'Completed'
            WHERE TrackingNumber = %s
        """
        cursor.execute(update_document_query, (tracking_number,))

        # Insert a new transaction record in TRANSACTIONS
        insert_transaction_query = """
            INSERT INTO TRANSACTIONS (
                OfficeID, DocNo, UserID, CompletedDate,
                ProcessDate, Status, TransactionType, Comments, TrackingNumber
            ) VALUES (
                %s, 
                (SELECT DocNo FROM DOCUMENTS WHERE TrackingNumber = %s), 
                %s, %s, %s, %s, %s, %s, %s
            )
        """
        cursor.execute(insert_transaction_query, (
            session.get('office_id'),  # Assuming 'office_id' is also stored in session
            tracking_number,
            user_id,
            current_date,
            current_date,
            'Completed',
            'Complete',
            comments,
            tracking_number  # Insert the tracking number into the transaction
        ))

        # Commit the transaction
        conn.commit()
        flash("Document marked as complete successfully.")
    except Exception as e:
        conn.rollback()
        flash(f"An error occurred: {e}")
    finally:
        # Close the database connection
        cursor.close()
        conn.close()

    return redirect(url_for('ict_encoded'))  # Redirect to documents page


#" TRACK DOCUMENTS" IN ICT OFFICE / track_ict_documents.html
@app.route('/track_ict_documents')
@login_required
def track_ict_documents():
    page = request.args.get('page', 1, type=int)  # Get the page number from query params
    per_page = 10  # Documents per page
    offset = (page - 1) * per_page

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        # Fetch paginated documents for the ICT Office along with user, school, and office details
        cursor.execute(""" 
            SELECT d.TrackingNumber, 
                   u.Firstname, 
                   u.Lastname, 
                   dt.DocTypeName, 
                   d.DocDetails, 
                   d.DocPurpose, 
                   COALESCE(s.SchoolName, o.OfficeName, 'N/A') AS SchoolOrOffice, 
                   d.DateEncoded, 
                   d.DateReceived, 
                   d.Status
            FROM DOCUMENTS d
            JOIN USERS u ON d.UserID = u.UserID
            JOIN DOCUMENT_TYPE dt ON d.DocTypeID = dt.DocTypeID
            LEFT JOIN SCHOOLS s ON d.SchoolID = s.SchoolID
            LEFT JOIN OFFICES o ON d.OfficeID = o.OfficeID
            WHERE d.OfficeID = %s  -- Filter by the ICT Office
            ORDER BY d.DateEncoded DESC
            LIMIT %s OFFSET %s
        """, (12, per_page, offset))  # Assuming 12 is the OfficeID for the ICT Office

        documents = cursor.fetchall()

        # Count total documents for the ICT Office
        cursor.execute("SELECT COUNT(*) FROM DOCUMENTS WHERE OfficeID = %s", (12,))
        total_documents = cursor.fetchone()['COUNT(*)']
        total_pages = (total_documents + per_page - 1) // per_page

        return render_template(
            'ict_office/track_ict_documents.html',
            documents=documents,
            current_page=page,
            total_pages=total_pages  # Ensure total_pages is defined here
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()
#-----END OF ICT DASHBOARD-----#

#-----LEGAL OFFICE DASHBOARD-----#
# "CREATE DOCUMENTS" FOR LEGAL OFFICE / _legal_dashboard.html
@app.route('/_legal_dashboard')
@login_required
def _legal_dashboard():
    # Ensure the user is a legal staff member
    if session.get('role') != 3:  # Assuming role '5' is for legal staff
        return redirect(url_for('index'))  # Redirect unauthorized users

    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('logout'))  # Handle case where user ID is not in session

    # Fetch user details
    user = get_user_by_id(user_id)

    conn = None
    cursor = None
    offices = []
    document_type = []  # To hold document types

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Fetch the list of offices from the database (assuming 'OFFICES' table)
        cursor.execute("SELECT OfficeID, OfficeName FROM OFFICES")
        offices = cursor.fetchall()

        # Fetch the list of document types (assuming 'DOCUMENT_TYPES' table)
        cursor.execute("SELECT DocTypeID, DocTypeName FROM DOCUMENT_TYPE")
        document_type = cursor.fetchall()  # [(DocTypeID1, DocTypeName1), (DocTypeID2, DocTypeName2), ...]

    except Exception as e:
        print(f"Error fetching data: {e}")

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    # Pass document types, offices, and user to the template
    return render_template('legal_office/_legal_dashboard.html', user=user, offices=offices, document_type=document_type)

# "MY DOCUMENTS" FOR LEGAL OFFICE / legal_encoded.html
@app.route('/legal_encoded', methods=['GET'])
@login_required
def legal_encoded():
    # Ensure the user is a staff member
    if session.get('role') != 3:  # Assuming role '3' is for staff
        return redirect(url_for('index'))  # Redirect unauthorized users

    page = request.args.get('page', 1, type=int)  # Get the page number from query params
    per_page = 10  # Documents per page
    offset = (page - 1) * per_page

    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('logout'))  # Handle case where user ID is not in session

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        # Fetch paginated documents for the user along with document type and school/office details
        cursor.execute("""
            SELECT d.TrackingNumber, 
                   u.Firstname, 
                   u.Lastname, 
                   dt.DocTypeName, 
                   d.DocDetails, 
                   d.DocPurpose, 
                   COALESCE(s.SchoolName, o.OfficeName, 'N/A') AS SchoolOrOffice, 
                   d.DateEncoded, 
                   d.DateReceived, 
                   d.Status,
                   d.OfficeIDToSend
            FROM DOCUMENTS d
            JOIN USERS u ON d.UserID = u.UserID
            JOIN DOCUMENT_TYPE dt ON d.DocTypeID = dt.DocTypeID
            LEFT JOIN SCHOOLS s ON d.SchoolID = s.SchoolID
            LEFT JOIN OFFICES o ON d.OfficeIDToSend = o.OfficeID
            WHERE d.UserID = %s
            ORDER BY d.DateEncoded DESC
            LIMIT %s OFFSET %s
        """, (user_id, per_page, offset))

        documents = cursor.fetchall()

        # Count total documents for the user
        cursor.execute("SELECT COUNT(*) FROM DOCUMENTS WHERE UserID = %s", (user_id,))
        total_documents = cursor.fetchone()['COUNT(*)']
        total_pages = (total_documents + per_page - 1) // per_page

        return render_template(
            'legal_office/legal_encoded.html',
            documents=documents,
            current_page=page,
            total_pages=total_pages  # Ensure total_pages is defined here
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

# "DOCUMENTS FOR RECEIVE" FOR LEGAL OFFICE / legal_documents.html
@app.route('/legal_documents')
@login_required
def legal_documents():
    page = request.args.get('page', 1, type=int)  # Get the page number from query params
    per_page = 10  # Documents per page
    offset = (page - 1) * per_page

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        # Fetch paginated documents created by USERS and forwarded to the Legal Office
        cursor.execute(""" 
            SELECT d.DocNo,  -- Include the DocNo here
                   d.TrackingNumber, 
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
            WHERE d.OfficeIDToSend = %s  -- Filter by the OfficeID for Legal Office
            ORDER BY d.DateEncoded DESC
            LIMIT %s OFFSET %s
        """, (session.get('office_id'), per_page, offset))  # Assuming office_id is stored in session

        documents = cursor.fetchall()

        # Count total documents forwarded to the Legal Office created by USERS and STAFF
        cursor.execute("""
            SELECT COUNT(*) FROM DOCUMENTS d 
            JOIN USERS u ON d.UserID = u.UserID 
            WHERE d.OfficeIDToSend = %s 
        """, (session.get('office_id'),))
        
        total_documents = cursor.fetchone()['COUNT(*)']
        total_pages = (total_documents + per_page - 1) // per_page

        return render_template(
            'legal_office/legal_documents.html',  # Ensure you have this template
            documents=documents,
            current_page=page,
            total_pages=total_pages
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

# "RECEIVE" ACTION BUTTON IN LEGAL OFFICE
@app.route('/legal_receive_document/<int:doc_no>', methods=['POST'])
@login_required
def handle_legal_receive_document(doc_no):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # 1. Update the status of the document to 'Received' and set DateReceived
        cursor.execute("""
            UPDATE DOCUMENTS
            SET Status = %s, DateReceived = NOW()
            WHERE DocNo = %s AND OfficeID = %s
        """, ('Received', doc_no, session.get('office_id')))
        
        if cursor.rowcount == 0:
            return jsonify({"error": "Document not found or already received."}), 404

        # 2. Fetch the TrackingNumber for this document
        cursor.execute("SELECT TrackingNumber FROM DOCUMENTS WHERE DocNo = %s", (doc_no,))
        tracking_number_result = cursor.fetchone()
        tracking_number = tracking_number_result[0] if tracking_number_result else None

        # 3. Insert the transaction into the TRANSACTIONS table
        cursor.execute("""
            INSERT INTO TRANSACTIONS (
                OfficeID, DocNo, UserID, 
                ReceivedDate, Status, TransactionType, TrackingNumber
            )
            VALUES (%s, %s, %s, NOW(), %s, %s, %s)
        """, (
            session.get('office_id'),  # Office receiving the document
            doc_no,                    # Document number being received
            session.get('user_id'),    # The user performing the action
            'Received',                # Status of the transaction
            'Receive',                 # Type of transaction
            tracking_number            # TrackingNumber associated with this document
        ))

        conn.commit()
        return redirect(url_for('legal_documents'))

    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500

    finally:
        cursor.close()
        conn.close()

# "FORWARD" ACTION BUTTON FOR LEGAL OFFICE
@app.route('/legal_forward', methods=['POST'])
def legal_forward():
    tracking_number = request.form.get('tracking_number')
    comments = request.form.get('comments')
    forwarded_to_office_id = request.form.get('forwarded_to_office_id')  # Capture selected office ID

    try:
        # Connect to the database
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # Verify that the document exists
        cursor.execute("SELECT DocNo FROM DOCUMENTS WHERE TrackingNumber = %s", (tracking_number,))
        document = cursor.fetchone()

        if not document:
            flash(f'Document with tracking number {tracking_number} does not exist.', 'error')
            return redirect(url_for('encoded_documents'))

        # Retrieve the document number (DocNo)
        doc_no = document[0]

        # Update document status to 'Forwarded'
        cursor.execute("""
            UPDATE DOCUMENTS
            SET Status = 'Forwarded'
            WHERE TrackingNumber = %s
        """, (tracking_number,))

        # Insert a new transaction record with dynamic ForwardedToOfficeID
        cursor.execute("""
            INSERT INTO TRANSACTIONS (
                OfficeID, DocNo, UserID, ForwardDate, Status, TransactionType, Comments, ForwardedToOfficeID, TrackingNumber
            ) VALUES (%s, %s, %s, NOW(), 'Forwarded', 'Forward', %s, %s, %s)
        """, (
            session.get('office_id'),   # Office initiating the forward
            doc_no,                     # Document number
            session.get('user_id'),     # User performing the action
            comments,                   # Comments from the form
            forwarded_to_office_id,     # Selected office from dropdown
            tracking_number             # Tracking number
        ))

        conn.commit()
        flash(f'Document {tracking_number} forwarded successfully!', 'success')

    except mysql.connector.Error as err:
        conn.rollback()
        print(f"Database error: {err}")
        flash(f'Error forwarding document: {err}', 'error')
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    return redirect(url_for('legal_encoded'))


# "COMPLETE" ACTION BUTTON IN LEGAL OFFICE
@app.route('/legal_complete', methods=['POST'])
def legal_complete():
    # Retrieve user ID from session
    user_id = session.get('user_id')
    if not user_id:
        flash("You must be logged in to complete a document.")
        return redirect(url_for('login'))  # Redirect to login if not logged in

    # Get data from the form
    tracking_number = request.form.get('tracking_number')
    comments = request.form.get('comments', '')
    current_date = datetime.now()

    # Connect to the database
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Update the document status to 'Complete'
        update_document_query = """
            UPDATE DOCUMENTS
            SET Status = 'Completed'
            WHERE TrackingNumber = %s
        """
        cursor.execute(update_document_query, (tracking_number,))

        # Insert a new transaction record in TRANSACTIONS
        insert_transaction_query = """
            INSERT INTO TRANSACTIONS (
                OfficeID, DocNo, UserID, CompletedDate,
                ProcessDate, Status, TransactionType, Comments, TrackingNumber
            ) VALUES (
                %s, 
                (SELECT DocNo FROM DOCUMENTS WHERE TrackingNumber = %s), 
                %s, %s, %s, %s, %s, %s, %s
            )
        """
        cursor.execute(insert_transaction_query, (
            session.get('office_id'),  # Assuming 'office_id' is also stored in session
            tracking_number,
            user_id,
            current_date,
            current_date,
            'Completed',
            'Complete',
            comments,
            tracking_number  # Insert the tracking number into the transaction
        ))

        # Commit the transaction
        conn.commit()
        flash("Document marked as complete successfully.")
    except Exception as e:
        conn.rollback()
        flash(f"An error occurred: {e}")
    finally:
        # Close the database connection
        cursor.close()
        conn.close()

    return redirect(url_for('legal_encoded'))  # Redirect to documents page


# "TRACK DOCUMENTS" IN LEGAL OFFICE /  track_legal_documents.html
@app.route('/track_legal_documents')
@login_required
def track_legal_documents():
    page = request.args.get('page', 1, type=int)  # Get the page number from query params
    per_page = 10  # Documents per page
    offset = (page - 1) * per_page

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        # Fetch paginated documents for the Legal Office along with user and document type details
        cursor.execute(""" 
            SELECT d.TrackingNumber, 
                   u.Firstname, 
                   u.Lastname, 
                   dt.DocTypeName, 
                   d.DocDetails, 
                   d.DocPurpose, 
                   d.DateEncoded, 
                   d.DateReceived, 
                   d.Status
            FROM DOCUMENTS d
            JOIN USERS u ON d.UserID = u.UserID
            JOIN DOCUMENT_TYPE dt ON d.DocTypeID = dt.DocTypeID
            WHERE d.OfficeID = %s  -- Filter by the Legal Office
            ORDER BY d.DateEncoded DESC
            LIMIT %s OFFSET %s
        """, (13, per_page, offset))  # Assuming 13 is the OfficeID for the Legal Office

        documents = cursor.fetchall()

        # Count total documents for the Legal Office
        cursor.execute("SELECT COUNT(*) FROM DOCUMENTS WHERE OfficeID = %s", (13,))
        total_documents = cursor.fetchone()['COUNT(*)']
        total_pages = (total_documents + per_page - 1) // per_page

        return render_template(
            'legal_office/track_legal_documents.html',
            documents=documents,
            current_page=page,
            total_pages=total_pages  # Ensure total_pages is defined here
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()
#-----END OF LEGAL DASHBOARD-----#

#-----SDS OFFICE DASHBOARD-----#
# "CREATE DOCUMENTS" FOR SDS OFFCICE /  _sds_dashboard.html
@app.route('/_sds_dashboard')
@login_required
def _sds_dashboard():
    # Ensure the user is a staff member for SDS (Schools Division Superintendent)
    if session.get('role') != 3:  # Assuming role '6' is for SDS staff
        return redirect(url_for('index'))  # Redirect unauthorized users

    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('logout'))  # Handle case where user ID is not in session

    # Fetch user details
    user = get_user_by_id(user_id)

    conn = None
    cursor = None
    offices = []
    document_type = []  # To hold document types

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Fetch the list of offices from the database (assuming 'OFFICES' table)
        cursor.execute("SELECT OfficeID, OfficeName FROM OFFICES")
        offices = cursor.fetchall()

        # Fetch the list of document types (assuming 'DOCUMENT_TYPES' table)
        cursor.execute("SELECT DocTypeID, DocTypeName FROM DOCUMENT_TYPE")
        document_type = cursor.fetchall()  # [(DocTypeID1, DocTypeName1), (DocTypeID2, DocTypeName2), ...]

    except Exception as e:
        print(f"Error fetching data: {e}")

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    # Pass document types, offices, and user to the template
    return render_template('sds_office/_sds_dashboard.html', user=user, offices=offices, document_type=document_type)

# "MY DOCUMENTS" FOR SDS OFFCIE / sds_office.html
@app.route('/sds_encoded', methods=['GET'])
@login_required
def sds_encoded():
    # Ensure the user is a staff member
    if session.get('role') != 3:  # Assuming role '3' is for staff
        return redirect(url_for('index'))  # Redirect unauthorized users

    page = request.args.get('page', 1, type=int)  # Get the page number from query params
    per_page = 10  # Documents per page
    offset = (page - 1) * per_page

    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('logout'))  # Handle case where user ID is not in session

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        # Fetch paginated documents for the user along with document type and school/office details
        cursor.execute("""
            SELECT d.TrackingNumber, 
                   u.Firstname, 
                   u.Lastname, 
                   dt.DocTypeName, 
                   d.DocDetails, 
                   d.DocPurpose, 
                   COALESCE(s.SchoolName, o.OfficeName, 'N/A') AS SchoolOrOffice, 
                   d.DateEncoded, 
                   d.DateReceived, 
                   d.Status,
                   d.OfficeIDToSend
            FROM DOCUMENTS d
            JOIN USERS u ON d.UserID = u.UserID
            JOIN DOCUMENT_TYPE dt ON d.DocTypeID = dt.DocTypeID
            LEFT JOIN SCHOOLS s ON d.SchoolID = s.SchoolID
            LEFT JOIN OFFICES o ON d.OfficeIDToSend = o.OfficeID
            WHERE d.UserID = %s
            ORDER BY d.DateEncoded DESC
            LIMIT %s OFFSET %s
        """, (user_id, per_page, offset))

        documents = cursor.fetchall()

        # Count total documents for the user
        cursor.execute("SELECT COUNT(*) FROM DOCUMENTS WHERE UserID = %s", (user_id,))
        total_documents = cursor.fetchone()['COUNT(*)']
        total_pages = (total_documents + per_page - 1) // per_page

        return render_template(
            'sds_office/sds_encoded.html',
            documents=documents,
            current_page=page,
            total_pages=total_pages  # Ensure total_pages is defined here
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

# "DOCUMENT FOR RECEIVE" FOR SDS OFFICE / sds_office.html
@app.route('/sds_documents')
@login_required
def sds_documents():
    page = request.args.get('page', 1, type=int)  # Get the page number from query params
    per_page = 10  # Documents per page
    offset = (page - 1) * per_page

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        # Fetch paginated documents created by USERS and forwarded to the SDS Office
        cursor.execute(""" 
            SELECT d.DocNo,  -- Include the DocNo here
                   d.TrackingNumber, 
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
            WHERE d.OfficeIDToSend = %s  -- Filter by the OfficeID for SDS Office
            ORDER BY d.DateEncoded DESC
            LIMIT %s OFFSET %s
        """, (session.get('office_id'), per_page, offset))  # Assuming office_id is stored in session

        documents = cursor.fetchall()

        # Count total documents forwarded to the SDS Office created by USERS and STAFF
        cursor.execute("""
            SELECT COUNT(*) FROM DOCUMENTS d 
            JOIN USERS u ON d.UserID = u.UserID 
            WHERE d.OfficeIDToSend = %s 
        """, (session.get('office_id'),))
        
        total_documents = cursor.fetchone()['COUNT(*)']
        total_pages = (total_documents + per_page - 1) // per_page

        return render_template(
            'sds_office/sds_documents.html',  # Ensure you have this template
            documents=documents,
            current_page=page,
            total_pages=total_pages
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

# "RECEIVE" ACTION BUTTON FOR SDS OFFICE
@app.route('/sds_receive_document/<int:doc_no>', methods=['POST'])
@login_required
def handle_sds_receive_document(doc_no):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # 1. Update the status of the document to 'Received' and set DateReceived
        cursor.execute("""
            UPDATE DOCUMENTS
            SET Status = %s, DateReceived = NOW()
            WHERE DocNo = %s AND OfficeID = %s
        """, ('Received', doc_no, session.get('office_id')))
        
        if cursor.rowcount == 0:
            return jsonify({"error": "Document not found or already received."}), 404

        # 2. Fetch the TrackingNumber for this document
        cursor.execute("SELECT TrackingNumber FROM DOCUMENTS WHERE DocNo = %s", (doc_no,))
        tracking_number_result = cursor.fetchone()
        tracking_number = tracking_number_result[0] if tracking_number_result else None

        # 3. Insert the transaction into the TRANSACTIONS table
        cursor.execute("""
            INSERT INTO TRANSACTIONS (
                OfficeID, DocNo, UserID, 
                ReceivedDate, Status, TransactionType, TrackingNumber
            )
            VALUES (%s, %s, %s, NOW(), %s, %s, %s)
        """, (
            session.get('office_id'),  # Office receiving the document
            doc_no,                    # Document number being received
            session.get('user_id'),    # The user performing the action
            'Received',                # Status of the transaction
            'Receive',                 # Type of transaction
            tracking_number            # TrackingNumber associated with this document
        ))

        conn.commit()
        return redirect(url_for('sds_documents'))

    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500

    finally:
        cursor.close()
        conn.close()

# "FORWARD" ACTION BUTTON FOR SDS OFFICE
@app.route('/sds_forward', methods=['POST'])
def sds_forward():
    tracking_number = request.form.get('tracking_number')
    comments = request.form.get('comments')
    forwarded_to_office_id = request.form.get('forwarded_to_office_id')  # Capture selected office ID

    try:
        # Connect to the database
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # Verify that the document exists
        cursor.execute("SELECT DocNo FROM DOCUMENTS WHERE TrackingNumber = %s", (tracking_number,))
        document = cursor.fetchone()

        if not document:
            flash(f'Document with tracking number {tracking_number} does not exist.', 'error')
            return redirect(url_for('encoded_documents'))

        # Retrieve the document number (DocNo)
        doc_no = document[0]

        # Update document status to 'Forwarded'
        cursor.execute("""
            UPDATE DOCUMENTS
            SET Status = 'Forwarded'
            WHERE TrackingNumber = %s
        """, (tracking_number,))

        # Insert a new transaction record with dynamic ForwardedToOfficeID
        cursor.execute("""
            INSERT INTO TRANSACTIONS (
                OfficeID, DocNo, UserID, ForwardDate, Status, TransactionType, Comments, ForwardedToOfficeID, TrackingNumber
            ) VALUES (%s, %s, %s, NOW(), 'Forwarded', 'Forward', %s, %s, %s)
        """, (
            session.get('office_id'),   # Office initiating the forward
            doc_no,                     # Document number
            session.get('user_id'),     # User performing the action
            comments,                   # Comments from the form
            forwarded_to_office_id,     # Selected office from dropdown
            tracking_number             # Tracking number
        ))

        conn.commit()
        flash(f'Document {tracking_number} forwarded successfully!', 'success')

    except mysql.connector.Error as err:
        conn.rollback()
        print(f"Database error: {err}")
        flash(f'Error forwarding document: {err}', 'error')
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    return redirect(url_for('sds_encoded'))


# "COMPLETE" ACTION BUTTON FOR SDS OFFICE
@app.route('/sds_complete', methods=['POST'])
def sds_complete():
    # Retrieve user ID from session
    user_id = session.get('user_id')
    if not user_id:
        flash("You must be logged in to complete a document.")
        return redirect(url_for('login'))  # Redirect to login if not logged in

    # Get data from the form
    tracking_number = request.form.get('tracking_number')
    comments = request.form.get('comments', '')
    current_date = datetime.now()

    # Connect to the database
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Update the document status to 'Complete'
        update_document_query = """
            UPDATE DOCUMENTS
            SET Status = 'Completed'
            WHERE TrackingNumber = %s
        """
        cursor.execute(update_document_query, (tracking_number,))

        # Insert a new transaction record in TRANSACTIONS
        insert_transaction_query = """
            INSERT INTO TRANSACTIONS (
                OfficeID, DocNo, UserID, CompletedDate,
                ProcessDate, Status, TransactionType, Comments, TrackingNumber
            ) VALUES (
                %s, 
                (SELECT DocNo FROM DOCUMENTS WHERE TrackingNumber = %s), 
                %s, %s, %s, %s, %s, %s, %s
            )
        """
        cursor.execute(insert_transaction_query, (
            session.get('office_id'),  # Assuming 'office_id' is also stored in session
            tracking_number,
            user_id,
            current_date,
            current_date,
            'Completed',
            'Complete',
            comments,
            tracking_number  # Insert the tracking number into the transaction
        ))

        # Commit the transaction
        conn.commit()
        flash("Document marked as complete successfully.")
    except Exception as e:
        conn.rollback()
        flash(f"An error occurred: {e}")
    finally:
        # Close the database connection
        cursor.close()
        conn.close()

    return redirect(url_for('sds_encoded'))  # Redirect to documents page

# "TRACK DOCUMENTS" IN SDS OFFICE / track_sds_documents.html
@app.route('/track_sds_documents')
@login_required
def track_sds_documents():
    page = request.args.get('page', 1, type=int)  # Get the page number from query params
    per_page = 10  # Documents per page
    offset = (page - 1) * per_page

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        # Fetch paginated documents for the SDS Office along with user, school, and office details
        cursor.execute(""" 
            SELECT d.TrackingNumber, 
                   u.Firstname, 
                   u.Lastname, 
                   dt.DocTypeName, 
                   d.DocDetails, 
                   d.DocPurpose, 
                   COALESCE(s.SchoolName, o.OfficeName, 'N/A') AS SchoolOrOffice, 
                   d.DateEncoded, 
                   d.DateReceived, 
                   d.Status
            FROM DOCUMENTS d
            JOIN USERS u ON d.UserID = u.UserID
            JOIN DOCUMENT_TYPE dt ON d.DocTypeID = dt.DocTypeID
            LEFT JOIN SCHOOLS s ON d.SchoolID = s.SchoolID
            LEFT JOIN OFFICES o ON d.OfficeID = o.OfficeID
            WHERE d.OfficeID = %s  -- Filter by the SDS Office
            ORDER BY d.DateEncoded DESC
            LIMIT %s OFFSET %s
        """, (15, per_page, offset))  # Assuming 15 is the OfficeID for the SDS Office

        documents = cursor.fetchall()

        # Count total documents for the SDS Office
        cursor.execute("SELECT COUNT(*) FROM DOCUMENTS WHERE OfficeID = %s", (15,))
        total_documents = cursor.fetchone()['COUNT(*)']
        total_pages = (total_documents + per_page - 1) // per_page

        return render_template(
            'sds_office/track_sds_documents.html',
            documents=documents,
            current_page=page,
            total_pages=total_pages  # Ensure total_pages is defined here
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()
#-----END OF SDS DASHBOARD-----#

#-----SUPPLY OFFICE DASHBOARD-----#
# "CREATE DOCUMENTS" FOR SUPPLY OFFICE /  _supply_dashboard.html
@app.route('/_supply_dashboard')
@login_required
def _supply_dashboard():
    # Ensure the user is a staff member for the Supply Office
    if session.get('role') != 3:  # Assuming role '7' is for Supply staff
        return redirect(url_for('index'))  # Redirect unauthorized users

    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('logout'))  # Handle case where user ID is not in session

    # Fetch user details
    user = get_user_by_id(user_id)

    conn = None
    cursor = None
    offices = []
    document_type = []  # To hold document types

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Fetch the list of offices from the database (assuming 'OFFICES' table)
        cursor.execute("SELECT OfficeID, OfficeName FROM OFFICES")
        offices = cursor.fetchall()

        # Fetch the list of document types (assuming 'DOCUMENT_TYPES' table)
        cursor.execute("SELECT DocTypeID, DocTypeName FROM DOCUMENT_TYPE")
        document_type = cursor.fetchall()  # [(DocTypeID1, DocTypeName1), (DocTypeID2, DocTypeName2), ...]

    except Exception as e:
        print(f"Error fetching data: {e}")

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    # Pass document types, offices, and user to the template
    return render_template('supply_office/_supply_dashboard.html', user=user, offices=offices, document_type=document_type)

# "MY DOCUMENTS" FOR SUPPLOY OFFICE / supply_encoded.html
@app.route('/supply_encoded', methods=['GET'])
@login_required
def supply_encoded():
    # Ensure the user is a staff member
    if session.get('role') != 3:  # Assuming role '3' is for staff
        return redirect(url_for('index'))  # Redirect unauthorized users

    page = request.args.get('page', 1, type=int)  # Get the page number from query params
    per_page = 10  # Documents per page
    offset = (page - 1) * per_page

    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('logout'))  # Handle case where user ID is not in session

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        # Fetch paginated documents for the user along with document type and school/office details
        cursor.execute("""
            SELECT d.TrackingNumber, 
                   u.Firstname, 
                   u.Lastname, 
                   dt.DocTypeName, 
                   d.DocDetails, 
                   d.DocPurpose, 
                   COALESCE(s.SchoolName, o.OfficeName, 'N/A') AS SchoolOrOffice, 
                   d.DateEncoded, 
                   d.DateReceived, 
                   d.Status,
                   d.OfficeIDToSend
            FROM DOCUMENTS d
            JOIN USERS u ON d.UserID = u.UserID
            JOIN DOCUMENT_TYPE dt ON d.DocTypeID = dt.DocTypeID
            LEFT JOIN SCHOOLS s ON d.SchoolID = s.SchoolID
            LEFT JOIN OFFICES o ON d.OfficeIDToSend = o.OfficeID
            WHERE d.UserID = %s
            ORDER BY d.DateEncoded DESC
            LIMIT %s OFFSET %s
        """, (user_id, per_page, offset))

        documents = cursor.fetchall()

        # Count total documents for the user
        cursor.execute("SELECT COUNT(*) FROM DOCUMENTS WHERE UserID = %s", (user_id,))
        total_documents = cursor.fetchone()['COUNT(*)']
        total_pages = (total_documents + per_page - 1) // per_page

        return render_template(
            'supply_office/supply_encoded.html',
            documents=documents,
            current_page=page,
            total_pages=total_pages  # Ensure total_pages is defined here
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

# "DOCUMENT FOR RECEIVE" FOR SUPPLY OFFICE / supply_documents.html
@app.route('/supply_documents')
@login_required
def supply_documents():
    page = request.args.get('page', 1, type=int)  # Get the page number from query params
    per_page = 10  # Documents per page
    offset = (page - 1) * per_page

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        # Fetch paginated documents created by USERS and forwarded to the Supply Office
        cursor.execute(""" 
            SELECT d.DocNo,  -- Include the DocNo here
                   d.TrackingNumber, 
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
            WHERE d.OfficeIDToSend = %s  -- Filter by the OfficeID for Supply Office
            ORDER BY d.DateEncoded DESC
            LIMIT %s OFFSET %s
        """, (session.get('office_id'), per_page, offset))  # Assuming office_id is stored in session

        documents = cursor.fetchall()

        # Count total documents forwarded to the Supply Office created by USERS and STAFF
        cursor.execute("""
            SELECT COUNT(*) FROM DOCUMENTS d 
            JOIN USERS u ON d.UserID = u.UserID 
            WHERE d.OfficeIDToSend = %s 
        """, (session.get('office_id'),))
        
        total_documents = cursor.fetchone()['COUNT(*)']
        total_pages = (total_documents + per_page - 1) // per_page

        return render_template(
            'supply_office/supply_documents.html',  # Ensure you have this template
            documents=documents,
            current_page=page,
            total_pages=total_pages
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

# "RECEIVE" ACTION BUTTON FOR SUPPLY OFFICE
@app.route('/supply_receive_document/<int:doc_no>', methods=['POST'])
@login_required
def handle_supply_receive_document(doc_no):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # 1. Update the status of the document to 'Received' and set DateReceived
        cursor.execute("""
            UPDATE DOCUMENTS
            SET Status = %s, DateReceived = NOW()
            WHERE DocNo = %s AND OfficeID = %s
        """, ('Received', doc_no, session.get('office_id')))
        
        if cursor.rowcount == 0:
            return jsonify({"error": "Document not found or already received."}), 404

        # 2. Fetch the TrackingNumber for this document
        cursor.execute("SELECT TrackingNumber FROM DOCUMENTS WHERE DocNo = %s", (doc_no,))
        tracking_number_result = cursor.fetchone()
        tracking_number = tracking_number_result[0] if tracking_number_result else None

        # 3. Insert the transaction into the TRANSACTIONS table
        cursor.execute("""
            INSERT INTO TRANSACTIONS (
                OfficeID, DocNo, UserID, 
                ReceivedDate, Status, TransactionType, TrackingNumber
            )
            VALUES (%s, %s, %s, NOW(), %s, %s, %s)
        """, (
            session.get('office_id'),  # Office receiving the document
            doc_no,                    # Document number being received
            session.get('user_id'),    # The user performing the action
            'Received',                # Status of the transaction
            'Receive',                 # Type of transaction
            tracking_number            # TrackingNumber associated with this document
        ))

        conn.commit()
        return redirect(url_for('supply_documents'))

    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500

    finally:
        cursor.close()
        conn.close()

# "FORWARD" ACTION BUTTON FOR SUPPLY OFFICE
@app.route('/supply_forward', methods=['POST'])
def supply_forward():
    tracking_number = request.form.get('tracking_number')
    comments = request.form.get('comments')
    forwarded_to_office_id = request.form.get('forwarded_to_office_id')  # Capture selected office ID

    try:
        # Connect to the database
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # Verify that the document exists
        cursor.execute("SELECT DocNo FROM DOCUMENTS WHERE TrackingNumber = %s", (tracking_number,))
        document = cursor.fetchone()

        if not document:
            flash(f'Document with tracking number {tracking_number} does not exist.', 'error')
            return redirect(url_for('encoded_documents'))

        # Retrieve the document number (DocNo)
        doc_no = document[0]

        # Update document status to 'Forwarded'
        cursor.execute("""
            UPDATE DOCUMENTS
            SET Status = 'Forwarded'
            WHERE TrackingNumber = %s
        """, (tracking_number,))

        # Insert a new transaction record with dynamic ForwardedToOfficeID
        cursor.execute("""
            INSERT INTO TRANSACTIONS (
                OfficeID, DocNo, UserID, ForwardDate, Status, TransactionType, Comments, ForwardedToOfficeID, TrackingNumber
            ) VALUES (%s, %s, %s, NOW(), 'Forwarded', 'Forward', %s, %s, %s)
        """, (
            session.get('office_id'),   # Office initiating the forward
            doc_no,                     # Document number
            session.get('user_id'),     # User performing the action
            comments,                   # Comments from the form
            forwarded_to_office_id,     # Selected office from dropdown
            tracking_number             # Tracking number
        ))

        conn.commit()
        flash(f'Document {tracking_number} forwarded successfully!', 'success')

    except mysql.connector.Error as err:
        conn.rollback()
        print(f"Database error: {err}")
        flash(f'Error forwarding document: {err}', 'error')
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    return redirect(url_for('supply_encoded'))


# "COMPLETE" ACTION BUTTON FOR SUPPLY OFFICE
@app.route('/supply_complete', methods=['POST'])
def supply_complete():
    # Retrieve user ID from session
    user_id = session.get('user_id')
    if not user_id:
        flash("You must be logged in to complete a document.")
        return redirect(url_for('login'))  # Redirect to login if not logged in

    # Get data from the form
    tracking_number = request.form.get('tracking_number')
    comments = request.form.get('comments', '')
    current_date = datetime.now()

    # Connect to the database
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Update the document status to 'Complete'
        update_document_query = """
            UPDATE DOCUMENTS
            SET Status = 'Completed'
            WHERE TrackingNumber = %s
        """
        cursor.execute(update_document_query, (tracking_number,))

        # Insert a new transaction record in TRANSACTIONS
        insert_transaction_query = """
            INSERT INTO TRANSACTIONS (
                OfficeID, DocNo, UserID, CompletedDate,
                ProcessDate, Status, TransactionType, Comments, TrackingNumber
            ) VALUES (
                %s, 
                (SELECT DocNo FROM DOCUMENTS WHERE TrackingNumber = %s), 
                %s, %s, %s, %s, %s, %s, %s
            )
        """
        cursor.execute(insert_transaction_query, (
            session.get('office_id'),  # Assuming 'office_id' is also stored in session
            tracking_number,
            user_id,
            current_date,
            current_date,
            'Completed',
            'Complete',
            comments,
            tracking_number  # Insert the tracking number into the transaction
        ))

        # Commit the transaction
        conn.commit()
        flash("Document marked as complete successfully.")
    except Exception as e:
        conn.rollback()
        flash(f"An error occurred: {e}")
    finally:
        # Close the database connection
        cursor.close()
        conn.close()

    return redirect(url_for('supply_encoded'))  # Redirect to documents page


# "TRACK DOCUMENTS" IN SUPPLY OFFICE / track_supply_documents.html
@app.route('/track_supply_documents')
@login_required
def track_supply_documents():
    page = request.args.get('page', 1, type=int)  # Get the page number from query params
    per_page = 10  # Documents per page
    offset = (page - 1) * per_page

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        # Fetch paginated documents for the Supply Office along with user, school, and office details
        cursor.execute(""" 
            SELECT d.TrackingNumber, 
                   u.Firstname, 
                   u.Lastname, 
                   dt.DocTypeName, 
                   d.DocDetails, 
                   d.DocPurpose, 
                   COALESCE(s.SchoolName, o.OfficeName, 'N/A') AS SchoolOrOffice, 
                   d.DateEncoded, 
                   d.DateReceived, 
                   d.Status
            FROM DOCUMENTS d
            JOIN USERS u ON d.UserID = u.UserID
            JOIN DOCUMENT_TYPE dt ON d.DocTypeID = dt.DocTypeID
            LEFT JOIN SCHOOLS s ON d.SchoolID = s.SchoolID
            LEFT JOIN OFFICES o ON d.OfficeID = o.OfficeID
            WHERE d.OfficeID = %s  -- Filter by the Supply Office
            ORDER BY d.DateEncoded DESC
            LIMIT %s OFFSET %s
        """, (16, per_page, offset))  # Assuming 16 is the OfficeID for the Supply Office

        documents = cursor.fetchall()

        # Count total documents for the Supply Office
        cursor.execute("SELECT COUNT(*) FROM DOCUMENTS WHERE OfficeID = %s", (16,))
        total_documents = cursor.fetchone()['COUNT(*)']
        total_pages = (total_documents + per_page - 1) // per_page

        return render_template(
            'supply_office/track_supply_documents.html',
            documents=documents,
            current_page=page,
            total_pages=total_pages  # Ensure total_pages is defined here
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()
#-----END OF SUPPLY DASHBOARD-----#

# GENERIC OFFICE DASHBOARD FUNCTION
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

# ADD DOCUMENTS FOR ALL OFFICES
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

    # Fetch the SchoolID associated with the user (staff)
    school_id = get_user_school_id(user_id)

    # Get the office ID of the user creating the document
    office_id_of_user = session.get('office_id')  # Assuming the office ID is stored in the session

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
        """, (next_doc_no, user_id, doc_type_id, school_id, office_id_of_user, doc_details, doc_purpose, date_encoded, date_received, status))
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

        # Return success response
        return jsonify({"success": True})

    except Exception as e:
        # Return error response in case of exception
        return jsonify({"error": str(e)}), 500

    finally:
        # Ensure the database connection is properly closed
        if cursor:
            cursor.close()
        if conn:
            conn.close()


# OFFICE USER ID
def get_user_by_id(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT Firstname, Middlename, Lastname FROM USERS WHERE UserID = %s", (user_id,))
    user = cursor.fetchone()  # Assuming it returns a tuple like (Firstname, Middlename, Lastname)

    cursor.close()
    conn.close()

    return {
        'Firstname': user[0],
        'Middlename': user[1],
        'Lastname': user[2]
    }
#-----END OF ALL OFFICES DASHBOARD-----#


# TRACK NAVIGATION
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

# GENERATE RANDOM TRACKING NUMBER
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

# def get_forwarded_documents(offset, limit):
#     # Example query to get forwarded documents (adjust according to your schema)
#     return db.session.query(Document).filter(Document.Status == 'Forwarded') \
#         .order_by(Document.DateEncoded.desc()).offset(offset).limit(limit).all()


#EDIT ACTION BUTTON
@app.route('/edit_document/<string:doc_no>', methods=['GET', 'POST'])
def edit_document(doc_no):
    # Establish a new database connection for this route
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Fetch the document details
    cursor.execute('SELECT * FROM DOCUMENTS WHERE TrackingNumber = %s', (doc_no,))
    document = cursor.fetchone()

    # Check if the document status is 'Received'
    is_received = document['Status'] == 'Received' if document else False

    if request.method == 'POST':
        # Ensure the document is not already received before processing the edit
        if is_received:
            flash('Document cannot be edited because it has already been received.', 'danger')
            return redirect(url_for('document_tracking'))

        new_doc_type_id = request.form['doctype']  # Ensure this matches the name in the form
        new_doc_details = request.form['doc_details']
        new_doc_purpose = request.form['doc_purpose']

        # Update the document in the database
        cursor.execute(''' 
            UPDATE DOCUMENTS 
            SET DocTypeID = %s, DocDetails = %s, DocPurpose = %s
            WHERE TrackingNumber = %s
        ''', (new_doc_type_id, new_doc_details, new_doc_purpose, doc_no))

        conn.commit()
        flash('Document updated successfully!', 'success')
        cursor.close()
        conn.close()
        return redirect(url_for('document_tracking'))

    # Fetch document types for the dropdown
    cursor.execute("SELECT DocTypeID, DocTypeName FROM DOCUMENT_TYPE")
    document_types = cursor.fetchall()

    # Close the cursor and connection before rendering
    cursor.close()
    conn.close()

    return render_template('document_tracking.html', document=document, document_types=document_types, is_received=is_received)


#VIEW ACTION BUTTON
@app.route('/view_document/<string:doc_no>')
def view_document(doc_no):
    # Fetch the document details using the Tracking Number
    document = db.execute('''
        SELECT d.TrackingNumber, d.DocDetails, d.DocPurpose, d.DateEncoded, d.DateReceived,
               d.Status, dt.DocTypeName, s.SchoolName, u.Firstname, u.Lastname
        FROM DOCUMENTS d
        JOIN DOCUMENT_TYPE dt ON d.DocTypeID = dt.DocTypeID
        JOIN SCHOOLS s ON d.SchoolID = s.SchoolID
        JOIN USERS u ON d.UserID = u.UserID
        WHERE d.TrackingNumber = %s
    ''', (doc_no,)).fetchone()

    # Check if document exists
    if document is None:
        flash("Document not found!", "danger")
        return redirect(url_for('document_tracking'))

    # Render the view_document.html template to display the document tracking details
    return render_template('view_document.html', document=document)

#DELETE ACTION BUTTON
@app.route('/delete_document/<string:doc_no>', methods=['POST'])
def delete_document(doc_no):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Check the document status before attempting to delete
        cursor.execute("SELECT Status FROM DOCUMENTS WHERE TrackingNumber = %s", (doc_no,))
        document = cursor.fetchone()

        if document and document[0] == 'Received':
            flash('Error: Document cannot be deleted because it has already been received.', 'danger')
            return redirect(url_for('document_tracking'))  # Redirect after failed deletion

        # Proceed with deletion if the document is not received
        cursor.execute("DELETE FROM DOCUMENTS WHERE TrackingNumber = %s", (doc_no,))
        conn.commit()
        flash('Document deleted successfully!', 'success')  # Show success message

    except Exception as e:
        flash(f'Error deleting document: {str(e)}', 'danger')  # Show error message
    finally:
        cursor.close()
        conn.close()
    
    return redirect(url_for('document_tracking'))  # Redirect after deletion

#RECEIVE ACTION BUTTON
@app.route('/receive_document/<int:doc_no>', methods=['POST'])
@login_required
def receive_document(doc_no):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Get the tracking number from the form data
    tracking_number = request.form.get('tracking_number')

    try:
        # Update the document status to 'Received'
        cursor.execute("""
            UPDATE DOCUMENTS 
            SET Status = 'Received' 
            WHERE DocNo = %s
        """, (doc_no,))
        
        conn.commit()  # Commit the changes

        # Flash a message to indicate success
        flash(f'Document {tracking_number} Received Successfully!', 'success')

        # Redirect to receive documents page
        return redirect(url_for('receive_documents'))

    except Exception as e:
        # Flash an error message or handle the error appropriately
        flash(f'Error receiving document {tracking_number}: {str(e)}', 'error')
        return redirect(url_for('receive_documents'))  # Redirect back to the receive documents page

    finally:
        cursor.close()
        conn.close()

    # This return statement is to satisfy the function requirements, though it should not be reached
    return redirect(url_for('receive_documents'))  # Ensure this is the last line

@app.route('/search_documents', methods=['GET', 'POST'])
@login_required
def search_documents():
    # Ensure the user is a staff member
    if session.get('role') != 3:  # Assuming role '3' is for staff
        return redirect(url_for('index'))  # Redirect unauthorized users

    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('logout'))  # Handle case where user ID is not in session

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    documents = []
    search_query = ''
    filters = {}

    # Get search parameters from the form (if POST request)
    if request.method == 'POST':
        search_query = request.form.get('search_query', '').strip()  # Search query from input form
        doc_type = request.form.get('doc_type', '')  # Document type filter (if any)
        status = request.form.get('status', '')  # Status filter (if any)

        filters['search_query'] = search_query
        filters['doc_type'] = doc_type
        filters['status'] = status

    page = request.args.get('page', 1, type=int)  # Get the page number from query params
    per_page = 10  # Documents per page
    offset = (page - 1) * per_page

    try:
        # Build the search query with optional filters
        sql_query = """
            SELECT d.DocNo, d.TrackingNumber, u.Firstname, u.Lastname, dt.DocTypeName,
                   d.DocDetails, d.DocPurpose, s.SchoolName, o.OfficeName, 
                   d.DateEncoded, d.DateReceived, d.Status
            FROM DOCUMENTS d
            JOIN USERS u ON d.UserID = u.UserID
            JOIN DOCUMENT_TYPE dt ON d.DocTypeID = dt.DocTypeID
            LEFT JOIN SCHOOLS s ON d.SchoolID = s.SchoolID
            LEFT JOIN OFFICES o ON d.OfficeID = o.OfficeID
            WHERE (d.UserID = %s OR d.Status = 'Received') 
              AND d.Status != 'Complete'
        """
        
        # Apply filters based on form input (search query, document type, status)
        if search_query:
            sql_query += " AND (d.TrackingNumber LIKE %s OR u.Firstname LIKE %s OR u.Lastname LIKE %s OR dt.DocTypeName LIKE %s)"
            filters['search_query'] = f"%{search_query}%"

        if doc_type:
            sql_query += " AND d.DocTypeID = %s"
            filters['doc_type'] = doc_type

        if status:
            sql_query += " AND d.Status = %s"
            filters['status'] = status

        # Add pagination
        sql_query += " ORDER BY d.DateEncoded DESC LIMIT %s OFFSET %s"
        
        # Execute the query with the filter values
        cursor.execute(sql_query, (
            user_id, 
            filters.get('search_query'), 
            filters.get('search_query'), 
            filters.get('search_query'),
            filters.get('search_query'),
            filters.get('doc_type'),
            filters.get('status'),
            per_page, offset
        ))

        documents = cursor.fetchall()

        # Count total documents for the user (applying the same filters)
        cursor.execute("""
            SELECT COUNT(*) 
            FROM DOCUMENTS d
            WHERE (d.UserID = %s OR d.Status = 'Received') 
              AND d.Status != 'Complete'
        """, (user_id,))
        
        total_documents = cursor.fetchone()['COUNT(*)']
        total_pages = (total_documents + per_page - 1) // per_page

        return render_template(
            'records_office/search_documents.html',
            documents=documents,
            current_page=page,
            total_pages=total_pages,
            search_query=search_query,
            doc_type=doc_type,
            status=status
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

def get_current_user_id():
    # Logic to retrieve the current user's ID (e.g., from session)
    return 1  # Placeholder

def get_current_office_id():
    # Logic to retrieve the current office's ID (e.g., from session or user data)
    return 1  # Placeholder

def get_doc_no_from_tracking_number(tracking_number):
    # Logic to retrieve the DocNo from the tracking number
    return 1  # Placeholder, implement your logic to get DocNo

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

if __name__ == '__main__':
    app.run(debug=True)