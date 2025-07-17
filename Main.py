import mysql.connector
from datetime import datetime, timedelta
import hashlib
import json
import os

# Get MySQL password from user
User_input_PW = input('ENTER YOUR MYSQL PASSWORD: ')

# --- Database Configuration ---
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root', 
    'password': User_input_PW, 
    'database': 'vms_system'
}

# --- Permissions Configuration ---
# Define specific permissions for granular control
PERMISSIONS = {
    'ADMIN': [
        'CREATE_USER', 'VIEW_USERS', 'UNLOCK_USER','APPROVE_VISITOR','VIEW_ALL_VISITORS', 'CHECKOUT_VISITOR', 'VIEW_REPORTS','CREATE_VISITOR_ENTRY', 'MANAGE_MASTER_DATA', 'LOCK_USER'
    ],
    'HR': [
        'CREATE_USER', 'VIEW_USERS', 'UNLOCK_USER', 'LOCK_USER', 'UNACTIVE_USER', 'APPROVE_VISITOR','VIEW_MY_ENTRIES',
    ],
    'SECURITY': [
        'CREATE_VISITOR_ENTRY', 'VIEW_ALL_VISITORS',
        'CHECKOUT_VISITOR', 'VIEW_PENDING_APPROVALS','VIEW_REPORTS',
    ],
    'USER': [
         'APPROVE_VISITOR','VIEW_MY_ENTRIES'
    ]
}

# --- Helper Functions (if any, placed here for modularity) ---

# --- Database Class ---
class VMSDatabase:
    def __init__(self):
        self.config = DB_CONFIG

    def get_connection(self):
        """Establishes and returns a new database connection."""
        try:
            conn = mysql.connector.connect(**self.config)
            return conn
        except mysql.connector.Error as err:
            print(f"Error connecting to database: {err}")
            return None

    def create_database_if_not_exists(self):
        """Creates the VMS database if it doesn't exist."""
        # Connect without specifying a database to create it
        temp_config = self.config.copy()
        db_name = temp_config.pop('VMS_System')
        try:
            conn = mysql.connector.connect(**temp_config)
            cursor = conn.cursor()
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
            print(f"Database '{db_name}' ensured to exist.")
            cursor.close()
            conn.close()
        except mysql.connector.Error as err:
            print(f"Error creating database: {err}")

# --- Setup Class ---
class VMSSetup:
    def __init__(self, db):
        self.db = db

    def create_database(self):
        self.db.create_database_if_not_exists()

    def create_tables(self):
    #!#Create table for Id dropdown 

        """Creates necessary tables for the VMS."""
        mycon = self.db.get_connection()
        if not mycon:
            return

        cursor = mycon.cursor()

        tables = {}

        # Users table
        #!# Add Mobile no, and card_no to user master
        tables['users'] = """
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            empid VARCHAR(50) UNIQUE NOT NULL,
            empname VARCHAR(100) NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            user_role VARCHAR(20) NOT NULL,
            status CHAR(1) DEFAULT 'A',
            failed_attempts INT DEFAULT 0,
            last_login DATETIME,
            created_by VARCHAR(50) NOT NULL,
            created_date DATETIME DEFAULT CURRENT_TIMESTAMP,
            modify_by VARCHAR(50),
            modify_date DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """

        # Visitor Entries table
        #!# remove in_time, emp_id and Add Emp_Mobile_no, card_no to vms, Modify person_details(fellow person_details) will have name and mobile
        tables['vms'] = """
        CREATE TABLE IF NOT EXISTS vms (
            seq_no INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            mobile VARCHAR(15) NOT NULL,
            email VARCHAR(100),
            id_type VARCHAR(50),
            id_number VARCHAR(100),
            representing VARCHAR(100),
            purpose VARCHAR(100),
            entry_date DATETIME DEFAULT CURRENT_TIMESTAMP,
            in_time DATETIME,
            out_time DATETIME,
            approve CHAR(1) DEFAULT 'P',
            approve_dt DATETIME, 
            approve_dt VARCHAR(), 
            approved_by VARCHAR(50), 
            site_code VARCHAR(20),
            plant_code VARCHAR(20),
            emp_id VARCHAR(50), 
            emp_name VARCHAR(100),
            fellow_visitors INT DEFAULT 0,
            person_details JSON,
            visitor_category VARCHAR(100),
            created_by VARCHAR(50) NOT NULL,
            created_date DATETIME DEFAULT CURRENT_TIMESTAMP,
            modify_by VARCHAR(50),
            modify_date DATETIME
        )
        """

        # Visitor Category Master
        tables['visitor_category_master'] = """
        CREATE TABLE IF NOT EXISTS visitor_category_master (
            id INT AUTO_INCREMENT PRIMARY KEY,
            category_name VARCHAR(100) NOT NULL,
            status CHAR(1) DEFAULT 'A',
            created_by VARCHAR(50) NOT NULL,
            created_date DATETIME DEFAULT CURRENT_TIMESTAMP,
            modify_by VARCHAR(50),
            modify_date DATETIME
        )
        """

        # Purpose Master
        tables['purpose_master'] = """
        CREATE TABLE IF NOT EXISTS purpose_master (
            id INT AUTO_INCREMENT PRIMARY KEY,
            purpose_name VARCHAR(100) NOT NULL,
            status CHAR(1) DEFAULT 'A',
            created_by VARCHAR(50) NOT NULL,
            created_date DATETIME DEFAULT CURRENT_TIMESTAMP,
            modify_by VARCHAR(50),
            modify_date DATETIME
        )
        """
        
        for table_name, table_sql in tables.items():
            try:
                print(f"Creating table {table_name}...", end='')
                cursor.execute(table_sql)
                print("OK")
            except mysql.connector.Error as err:
                print(f"FAILED: {err}")

        mycon.commit()
        cursor.close()
        mycon.close()

    def insert_default_data(self):
    #!# add default data for Id 

        """Inserts default data into master tables if they are empty."""
        mycon = self.db.get_connection()
        if not mycon:
            return

        cursor = mycon.cursor()

        # Default Users
        admin_empid = "ADMIN001"
        admin_password = "admin123"
        hr_empid = "HR_MAIN"
        hr_password = "hr123"
        security_empid = "SEC_MAIN"
        security_password = "sec123"

        default_users = [
            (admin_empid, "System Admin", hashlib.sha256(admin_password.encode()).hexdigest(), "ADMIN", "SYSTEM"),
            (hr_empid, "HR Manager", hashlib.sha256(hr_password.encode()).hexdigest(), "HR", "SYSTEM"),
            (security_empid, "Security Guard", hashlib.sha256(security_password.encode()).hexdigest(), "SECURITY", "SYSTEM")
        ]

        try:
            cursor.execute("SELECT COUNT(*) FROM users WHERE empid IN (%s, %s, %s)", (admin_empid, hr_empid, security_empid))
            if cursor.fetchone()[0] == 0:
                print("Inserting default users...")
                insert_user_sql = """
                INSERT INTO users (empid, empname, password_hash, user_role, created_by, created_date)
                VALUES (%s, %s, %s, %s, %s, NOW())
                """
                cursor.executemany(insert_user_sql,default_users)
                mycon.commit()
                print("Default users inserted.")
            else:
                print("Default users already exist.")
        except mysql.connector.Error as err:
            print(f"Error inserting default users: {err}")

        # Default Visitor Categories
        default_categories = [
            "Vendor",
            "Client",
            "Government Official",
            "Personal Visit",
            "Maintenance Service",
            "Joinning"
        ]
        try:
            cursor.execute("SELECT COUNT(*) FROM visitor_category_master")
            if cursor.fetchone()[0] == 0:
                print("Inserting default visitor categories...")
                insert_category_sql = "INSERT INTO visitor_category_master (category_name, created_by, created_date) VALUES (%s, %s, NOW())"
                cursor.executemany(insert_category_sql, [(cat, "SYSTEM") for cat in default_categories])
                mycon.commit()
                print("Default visitor categories inserted.")
            else:
                print("Default visitor categories already exist.")
        except mysql.connector.Error as err:
            print(f"Error inserting default categories: {err}")

        # Default Purposes
        default_purposes = [
            "Meeting",
            "Delivery",
            "Inspection",
            "Training",
            "Internship",
            "Audit",
            "Maintenance"
        ]
        try:
            cursor.execute("SELECT COUNT(*) FROM purpose_master")
            if cursor.fetchone()[0] == 0:
                print("Inserting default purposes...")
                insert_purpose_sql = "INSERT INTO purpose_master (purpose_name, created_by, created_date) VALUES (%s, %s, NOW())"
                cursor.executemany(insert_purpose_sql, [(purp, "SYSTEM") for purp in default_purposes])
                mycon.commit()
                print("Default purposes inserted.")
            else:
                print("Default purposes already exist.")
        except mysql.connector.Error as err:
            print(f"Error inserting default purposes: {err}")


        cursor.close()
        mycon.close()

# --- Authentication Class ---
class Authentication:
    def __init__(self, db):
        self.db = db
        self.current_user = None
        self.max_failed_attempts = 3

    def hash_password(self, password):
        """Hashes a password using SHA256."""
        return hashlib.sha256(password.encode()).hexdigest()

    def verify_password(self, password, hashed_password):
        """Verifies a password against its hash."""
        return self.hash_password(password) == hashed_password

    def login(self):
        """Handles user login."""
        print('\n----- LOGIN -----')
        empid = input("Enter Employee ID: ").strip().upper()
        password = input("Enter Password: ").strip()

        mycon = self.db.get_connection()
        if not mycon:
            return False
        cursor = mycon.cursor(dictionary=True)

        try:
            cursor.execute("SELECT * FROM users WHERE empid = %s", (empid,))
            user = cursor.fetchone()

            if user:
                if user['status'] == 'L':
                    print("!!! Account Locked. Please contact administrator. !!!")
                    return False

                if self.verify_password(password, user['password_hash']):
                    self.current_user = user
                    # Reset failed attempts and update last login
                    cursor.execute("UPDATE users SET failed_attempts = 0, last_login = %s WHERE id = %s",
                                   (datetime.now(), user['id']))
                    mycon.commit()
                    print(f"Login successful! Welcome, {user['empname']}.")
                    return True
                else:
                    # Increment failed attempts
                    new_attempts = user['failed_attempts'] + 1
                    cursor.execute("UPDATE users SET failed_attempts = %s WHERE id = %s",
                                   (new_attempts, user['id']))
                    mycon.commit()
                    if new_attempts >= self.max_failed_attempts:
                        cursor.execute("UPDATE users SET status = 'L' WHERE id = %s", (user['id'],))
                        mycon.commit()
                        print("!!! Incorrect password. Account locked due to too many failed attempts. !!!")
                    else:
                        print(f"!!! Incorrect password. {self.max_failed_attempts - new_attempts} attempts remaining. !!!")
            else:
                print("!!! Employee ID not found. !!!")
        except mysql.connector.Error as err:
            print(f"Database error during login: {err}")
        finally:
            cursor.close()
            mycon.close()
        return False

    def logout(self):
        """Logs out the current user."""
        if self.current_user:
            print(f"Logging out {self.current_user['empname']}...")
            self.current_user = None
            print("Logged out successfully.")
        else:
            print("No user is currently logged in.")

    def check_permission(self, permission):
        """Checks if the current user has a specific permission."""
        if not self.current_user:
            return False
        user_role = self.current_user['user_role']
        return permission in PERMISSIONS.get(user_role, [])

# --- User Management Class ---
class UserManagement:
#!# Add a function for Lock_user 

    def __init__(self, db, auth):
        self.db = db
        self.auth = auth

    def create_user(self):
        #!# Add mobile no of user(EMP)

        """Allows authorized users to create new user accounts."""
        if not self.auth.check_permission('CREATE_USER'):
            print("!!! Access Denied: Insufficient privileges !!!")
            return

        print('\n----- CREATE NEW USER -----')
        empid = input("Enter new Employee ID: ").strip().upper()
        empname = input("Enter Employee Name: ").strip()
        password = input("Enter Password for new user: ").strip()
        user_role = input("Enter User Role (ADMIN, HR, SECURITY, USER): ").strip().upper()

        if user_role not in PERMISSIONS:
            print("!!! Invalid User Role. Please choose from ADMIN, HR, SECURITY, USER. !!!")
            return

        mycon = self.db.get_connection()
        if not mycon:
            return
        cursor = mycon.cursor()

        try:
            # Check if Employee ID already exists
            cursor.execute("SELECT COUNT(*) FROM users WHERE empid = %s", (empid,))
            if cursor.fetchone()[0] > 0:
                print("!!! Employee ID already exists. Please choose a different one. !!!")
                return

            hashed_password = self.auth.hash_password(password)
            created_by = self.auth.current_user['empid'] if self.auth.current_user else 'UNKNOWN'

            cursor.execute("""
                INSERT INTO users (empid, empname, password_hash, user_role, created_by, created_date)
                VALUES (%s, %s, %s, %s, %s, NOW())
            """, (empid, empname, hashed_password, user_role, created_by))
            mycon.commit()
            print(f"### User '{empname}' ({empid}) created successfully with role '{user_role}' ###")
        except mysql.connector.Error as err:
            print(f"Error creating user: {err}")
        finally:
            cursor.close()
            mycon.close()

    def view_users(self):
    #!# Mobile no will also be displayed

        """Allows authorized users to view all system users."""
        if not self.auth.check_permission('VIEW_USERS'):
            print("!!! Access Denied: Insufficient privileges !!!")
            return

        print('\n----- ALL SYSTEM USERS -----')
        mycon = self.db.get_connection()
        if not mycon:
            return
        cursor = mycon.cursor()

        try:
            cursor.execute("SELECT empid, empname, user_role, status, failed_attempts, last_login, created_by FROM users ORDER BY empname")
            users = cursor.fetchall()

            if users:
                print(f"{'Emp ID':<15} {'Name':<25} {'Role':<15} {'Status':<10} {'Failed Attempts':<15} {'Last Login':<20} {'Created By':<15}")
                print("-" * 115)
                for user in users:
                    last_login_str = user[5].strftime('%Y-%m-%d %H:%M') if user[5] else 'N/A'
                    print(f"{user[0]:<15} {user[1]:<25} {user[2]:<15} {user[3]:<10} {user[4]:<15} {last_login_str:<20} {user[6]:<15}")
            else:
                print("No users found.")
        except mysql.connector.Error as err:
            print(f"Error viewing users: {err}")
        finally:
            cursor.close()
            mycon.close()

    def unlock_user(self):
        """Allows authorized users to unlock a locked user account."""
        if not self.auth.check_permission('UNLOCK_USER'):
            print("!!! Access Denied: Insufficient privileges !!!")
            return

        print('\n----- UNLOCK USER ACCOUNT -----')
        empid = input("Enter Employee ID of the account to unlock: ").strip().upper()

        mycon = self.db.get_connection()
        if not mycon:
            return
        cursor = mycon.cursor()

        try:
            cursor.execute("SELECT status FROM users WHERE empid = %s", (empid,))
            result = cursor.fetchone()

            if not result:
                print(f"!!! Employee ID '{empid}' not found. !!!")
                return

            if result[0] == 'A':
                print(f"Account '{empid}' is already active (not locked).")
                return

            cursor.execute("""
                UPDATE users SET status = 'A', failed_attempts = 0,
                modify_by = %s, modify_date = NOW()
                WHERE empid = %s
            """, (self.auth.current_user['empid'], empid))
            mycon.commit()
            print(f"### Account '{empid}' unlocked successfully. ###")

        except mysql.connector.Error as err:
            print(f"Error unlocking user: {err}")
        finally:
            cursor.close()
            mycon.close()

# --- VMS Operations Class ---
class VMSOperations:
    def __init__(self, db, auth):
        self.db = db
        self.auth = auth

    def get_dropdown_data(self, table_name, name_column):
    #!# Add ID Dropdown
        """Generic method to fetch data for dropdowns."""
        mycon = self.db.get_connection()
        if not mycon:
            return []
        cursor = mycon.cursor()
        try:
            cursor.execute(f"SELECT {name_column} FROM {table_name} WHERE status = 'A' ORDER BY {name_column}")
            results = [row[0] for row in cursor.fetchall()]
            return results
        except mysql.connector.Error as err:
            print(f"Error fetching data from {table_name}: {err}")
            return []
        finally:
            cursor.close()
            mycon.close()

    def select_from_dropdown(self, prompt, options):
    #!# Add ID Dropdown
        """Presents a numbered list and allows user to select an option."""
        if not options:
            print(f"No {prompt.lower()} available.")
            return None

        for i, option in enumerate(options, 1):
            print(f"{i}. {option}")

        while True:
            try:
                choice = int(input(f"Select {prompt} (enter number): "))
                if 1 <= choice <= len(options):
                    return options[choice-1]
                else:
                    print("Invalid choice. Please enter a number within the range.")
            except ValueError:
                print("Invalid input. Please enter a number.")

    def create_visitor_entry(self):
    #!# Input Emp_mobile_no, card_no, Update modified_by & dont input in approve_dt, emp_id
    #!# There will be also Id dropdown 
    #!# Only created if emp mob no is found and search employ by its mob. number

        """Allows users to create a new visitor entry."""
        if not self.auth.check_permission('CREATE_VISITOR_ENTRY'):
            print("!!! Access Denied: Insufficient privileges !!!")
            return

        print('\n----- NEW VISITOR ENTRY -----')
        name = input("Visitor Name: ").strip()
        mobile = input("Visitor Mobile: ").strip()
        email = input("Visitor Email (optional): ").strip() or None
        representing = input("Representing Company/Organization (optional): ").strip()
        visitor_categories = self.get_dropdown_data('visitor_category_master', 'category_name')
        visitor_category = self.select_from_dropdown("Visitor Category", visitor_categories)
        if not visitor_category:
            print("Visitor entry cancelled.")
            return

        purposes = self.get_dropdown_data('purpose_master', 'purpose_name')
        purpose = self.select_from_dropdown("Purpose of Visit", purposes)
        if not purpose:
            print("Visitor entry cancelled.")
            return

        # Simplified ID type and number, could be dropdowns if needed
        #!# id Will have dropdown option
        id_type = input("ID Type (e.g., Aadhar, Driving License, Passport): ").strip()
        id_number = input("ID Number: ").strip()
        
        emp_id = input("Host Employee ID: ").strip().upper()
        emp_name = input("Host Employee Name: ").strip()
        #!# EMP_MOB_NO will be added and verified
        
        #!# person details are in key value pairs
        fellow_visitors_count = 0
        person_details = {}
        try:
            fellow_visitors_count = int(input("Number of fellow visitors (excluding self, 0 if none): "))
            if fellow_visitors_count > 0:
                print("Enter details for fellow visitors:")
                for i in range(fellow_visitors_count):
                    f_name = input(f"  Fellow Visitor {i+1} Name: ").strip()
                    f_designation = input(f"  Fellow Visitor {i+1} Designation/Role: ").strip()
                    person_details[f"fv_{i+1}"] = {"name": f_name, "designation": f_designation}
        except ValueError:
            print("Invalid number entered for fellow visitors. Assuming 0.")
            fellow_visitors_count = 0

        mycon = self.db.get_connection()
        if not mycon:
            return
        cursor = mycon.cursor()

        try:
            # Determine initial approval status
            # For simplicity, let's say all entries require approval
            approve_status = 'P' # Pending

            created_by = self.auth.current_user['empid'] if self.auth.current_user else 'GUEST'

            cursor.execute("""
                INSERT INTO vms (
                    name, mobile, email, id_type, id_number, representing, purpose,
                    in_time, approve, emp_id, emp_name, fellow_visitors, person_details,
                    visitor_category, created_by, created_date
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
            """, (name, mobile, email, id_type, id_number, representing, purpose,
                  datetime.now(), approve_status, emp_id, emp_name, fellow_visitors_count,
                  json.dumps(person_details) if person_details else None,
                  visitor_category, created_by))
            mycon.commit()
            print(f"### Visitor entry for {name} created successfully. Awaiting approval. ###")
        except mysql.connector.Error as err:
            print(f"Error creating visitor entry: {err}")
        finally:
            cursor.close()
            mycon.close()

    def view_visitor_entries(self):
        print('\n----- VISITOR ENTRIES -----\n')

        # Determine which menu options to show based on permissions
        menu_options = []
        if self.auth.check_permission('VIEW_ALL_VISITORS'):
            menu_options.append("View All Entries")
            menu_options.append("View My Entries")
            menu_options.append("Search by Mobile/Name")
            menu_options.append("View Pending Approvals")

        elif self.auth.check_permission('VIEW_PENDING_APPROVALS'):
            menu_options.append("View My Entries")
            menu_options.append("Search by Mobile/Name")
            menu_options.append("View Pending Approvals")

        else: # Default view for regular users
            menu_options.append("View My Entries")
            menu_options.append("Search by Mobile/Name")

        for i, option_text in enumerate(menu_options, 1):
            print(f"{i}. {option_text}")

        choice_map = {option_text: i for i, option_text in enumerate(menu_options, 1)}

        choice_input = input("Enter choice: ")
        try:
            choice = int(choice_input)
            if not (1 <= choice <= len(menu_options)):
                print("Invalid choice.")
                return
            selected_option_text = menu_options[choice - 1]
        except ValueError:
            print("Invalid input. Please enter a number.")
            return

        mycon = self.db.get_connection()
        if not mycon:
            return
        cursor = mycon.cursor()
        
        #!# add EMP_MoNo, card_no
        sql_query = """
            SELECT seq_no, name, mobile, representing, entry_date, approve, created_by, fellow_visitors,
                   site_code, plant_code, purpose, emp_name, visitor_category
            FROM vms
        """
        where_clauses = []
        params = []
        order_by = "ORDER BY entry_date DESC LIMIT 50"

        if selected_option_text == "View All Entries" and self.auth.check_permission('VIEW_ALL_VISITORS'):
            # No specific WHERE clause needed, just the LIMIT and ORDER BY
            pass

        elif selected_option_text == "View My Entries" or \
             (selected_option_text == "View All Entries" and not self.auth.check_permission('VIEW_ALL_VISITORS')):
            where_clauses.append("created_by=%s")
            params.append(self.auth.current_user['empid'])

        elif selected_option_text == "Search by Mobile/Name":
            search_term = input("Enter mobile number or name to search: ")
            where_clauses.append("(mobile LIKE %s OR name LIKE %s)")
            params.extend([f"%{search_term}%", f"%{search_term}%"])
            if not self.auth.check_permission('VIEW_ALL_VISITORS'):
                where_clauses.append("created_by=%s")
                params.append(self.auth.current_user['empid'])

        elif selected_option_text == "View Pending Approvals" and self.auth.check_permission('VIEW_PENDING_APPROVALS'):
            where_clauses.append("approve='P'")
        else:
            print("Invalid choice or insufficient privileges.")
            cursor.close()
            mycon.close()
            return

        if where_clauses:
            sql_query += " WHERE " + " AND ".join(where_clauses)
        sql_query += " " + order_by

        try:
            cursor.execute(sql_query, tuple(params))
            results = cursor.fetchall()

            if results:
                print(f"{'ID':<8} {'Name':<20} {'Mobile':<12} {'Company':<20} {'Category':<15} {'Purpose':<15} {'Date':<12} {'Status':<10} {'Host':<15}")
                print("-" * 157)
                for row in results:
                    status_map = {'P': 'Pending', 'A': 'Approved', 'R': 'Rejected'}
                    status = status_map.get(row[5], 'Unknown')
                    entry_date = row[4].strftime('%Y-%m-%d') if row[4] else 'N/A'
                    print(f"{row[0]:<8} {row[1]:<20} {row[2]:<12} {row[3]:<20} {row[12]:<15} {row[10]:<15} {entry_date:<12} {status:<10} {row[11]:<15}")
            else:
                print("No entries found.")
        except mysql.connector.Error as err:
            print(f"Error fetching visitor entries: {err}")
        finally:
            cursor.close()
            mycon.close()

    def approve_visitor(self):
    #!# Use card no for approving visitor not seq_no(its for internal use, will be added in vms)and take mo.no for designation in fellow visitors, rejection reason

        if not self.auth.check_permission('APPROVE_VISITOR'):
            print("!!! Access Denied: Insufficient privileges !!!")
            return

        print('\n----- APPROVE/REJECT VISITOR -----\n')

        # First show pending approvals
        mycon = self.db.get_connection()
        if not mycon:
            return
        cursor = mycon.cursor()

        try:
            cursor.execute("""
                SELECT seq_no, name, mobile, representing, entry_date, purpose, emp_name, created_by, visitor_category
                FROM vms WHERE approve='P' ORDER BY entry_date DESC LIMIT 20
            """)

            pending_results = cursor.fetchall()

            if not pending_results:
                print("!!! No pending approvals found !!!")
                return

            print("PENDING APPROVALS:")
            print(f"{'ID':<8} {'Name':<20} {'Mobile':<12} {'Company':<20} {'Category':<15} {'Purpose':<15} {'Host':<15}")
            print("-" * 120)
            for row in pending_results:
                # entry_date = row[4].strftime('%Y-%m-%d') if row[4] else 'N/A' # Not needed for display here
                print(f"{row[0]:<8} {row[1]:<20} {row[2]:<12} {row[3]:<20} {row[8]:<15} {row[5]:<15} {row[7]:<15}")

            seq_no = input("\nEnter Visitor Entry ID to approve/reject: ")

            # Check if entry exists and is pending
            cursor.execute("""
                SELECT name, mobile, approve, representing, purpose, emp_name, fellow_visitors, person_details, visitor_category
                FROM vms WHERE seq_no=%s
            """, (seq_no,))
            result = cursor.fetchone()

            if not result:
                print("!!! Entry not found !!!")
                return

            if result[2] != 'P':
                status_map = {'A': 'Approved', 'R': 'Rejected'}
                print(f"!!! Entry already {status_map.get(result[2], 'processed')} !!!")
                return

            # Display visitor details
            print(f"\nVISITOR DETAILS:")
            print(f"Name: {result[0]}")
            print(f"Mobile: {result[1]}")
            print(f"Company: {result[3]}")
            print(f"Category: {result[8]}")
            print(f"Purpose: {result[4]}")
            print(f"Host Employee: {result[5]}")
            print(f"Fellow Visitors Count: {result[6]}")

            if result[7]:  # person_details
                try:
                    person_details = json.loads(result[7])
                    print(f"Fellow Visitor Details:")
                    for key, person in person_details.items():
                        print(f"  - {person.get('name', 'N/A')} ({person.get('designation', 'N/A')})")
                except json.JSONDecodeError:
                    print("  (Error parsing fellow visitor details)")

            action = input("\nEnter action (A=Approve, R=Reject): ").upper()

            if action in ['A', 'R']:
                cursor.execute("""
                    UPDATE vms SET approve=%s, approve_dt=%s, approved_by=%s, modify_by=%s, modify_date=%s
                    WHERE seq_no=%s
                """, (action, datetime.now(), self.auth.current_user['empid'], self.auth.current_user['empid'], datetime.now(), seq_no))

                mycon.commit()
                action_text = "Approved" if action == 'A' else "Rejected"
                print(f"### Visitor entry {action_text} successfully ###")
            else:
                print("Invalid action. Please enter 'A' or 'R'.")
        except mysql.connector.Error as err:
            print(f"Error during visitor approval: {err}")
        finally:
            cursor.close()
            mycon.close()

    def checkout_visitor(self):
    #!# change seq_no to card_no, using approve_dt for In_time

        if not self.auth.check_permission('CHECKOUT_VISITOR'):
            print("!!! Access Denied: Insufficient privileges !!!")
            return

        print('\n----- VISITOR CHECKOUT -----\n')

        mycon = self.db.get_connection()
        if not mycon:
            returnfd
        cursor = mycon.cursor()

        # Show active visitors based on user permissions
        sql_active_visitors = """
            SELECT seq_no, name, mobile, representing, emp_name, site_code, plant_code
            FROM vms WHERE approve='A' AND out_time IS NULL
        """
        active_params = []

        #Prepairing Query for search 
        if not self.auth.check_permission('VIEW_ALL_VISITORS'):
            sql_active_visitors += " AND created_by=%s"
            active_params.append(self.auth.current_user['empid'])

        sql_active_visitors += " ORDER BY approve_dt DESC LIMIT 20"

        try:
            cursor.execute(sql_active_visitors, tuple(active_params))
            active_visitors = cursor.fetchall()

            # Printing
            if active_visitors:
                print("CURRENTLY CHECKED-IN VISITORS:")
                print(f"{'ID':<8} {'Name':<20} {'Mobile':<12} {'Company':<20} {'In Time':<12} {'Host':<15}")
                print("-" * 100)
                for row in active_visitors:
                    in_time = row[4].strftime('%H:%M') if row[4] else 'N/A'
                    print(f"{row[0]:<8} {row[1]:<20} {row[2]:<12} {row[3]:<20} {in_time:<12} {row[5]:<15}")
            else:
                print("No currently checked-in visitors.")

            search_term = input("\nEnter Visitor Mobile Number, Name, or Entry ID to checkout: ")

            sql_search = """
                SELECT seq_no, name, mobile, in_time, out_time, representing
                FROM vms WHERE approve='A' AND out_time IS NULL
            """
            search_params = []

            if search_term.isdigit():
                if len(search_term) == 10: # Assuming mobile is 10 digits
                    sql_search += " AND mobile=%s"
                    search_params.append(search_term)
                else: # Assume it's a seq_no if it's a longer number
                    sql_search += " AND seq_no=%s"
                    search_params.append(search_term)
            else: # Assume it's a name
                sql_search += " AND name LIKE %s"
                search_params.append(f"%{search_term}%")

            if not self.auth.check_permission('VIEW_ALL_VISITORS'):
                sql_search += " AND created_by=%s"
                search_params.append(self.auth.current_user['empid'])

            sql_search += " ORDER BY entry_date DESC LIMIT 5"

            cursor.execute(sql_search, tuple(search_params))
            results = cursor.fetchall()

            if not results:
                print("!!! No active visitor found matching your search criteria. !!!")
                return

            selected_entry = None
            if len(results) == 1:
                selected_entry = results[0]
            else:
                print("\nMultiple entries found. Please select one:")
                for i, row in enumerate(results, 1):
                    in_time = row[3].strftime('%Y-%m-%d %H:%M') if row[3] else 'N/A'
                    print(f"{i}. ID: {row[0]}, Name: {row[1]}, Mobile: {row[2]}, In Time: {in_time}")

                while True:
                    try:
                        choice = int(input("Select entry (enter number): "))
                        if 1 <= choice <= len(results):
                            selected_entry = results[choice-1]
                            break
                        else:
                            print("Invalid choice. Please enter a valid number.")
                    except ValueError:
                        print("Invalid input. Please enter a number.")

            # Confirm checkout
            print(f"\nConfirm checkout for visitor: {selected_entry[1]} (ID: {selected_entry[0]})?")
            confirm = input("Confirm (Y/N): ").upper()

            if confirm == 'Y':
                # Perform checkout
                cursor.execute("""
                    UPDATE vms SET out_time=%s, modify_by=%s, modify_date=%s
                    WHERE seq_no=%s
                """, (datetime.now(), self.auth.current_user['empid'], datetime.now(), selected_entry[0]))

                mycon.commit()
                print(f"### Visitor {selected_entry[1]} checked out successfully ###")
            else:
                print("Checkout cancelled.")
        except mysql.connector.Error as err:
            print(f"Error during visitor checkout: {err}")
        finally:
            cursor.close()
            mycon.close()

    def view_reports(self):
    #!# change seq_no to card_no

        if not self.auth.check_permission('VIEW_REPORTS'):
            print("!!! Access Denied: Insufficient privileges !!!")
            return

        print('\n----- VISITOR REPORTS -----\n')
        print("1. Daily Visitor Report")
        print("2. Pending Approvals Report")
        print("3. Visitor Status Summary")
        print("4. Most Frequent Visitors")

        choice = input("Enter choice: ")

        mycon = self.db.get_connection()
        if not mycon:
            return
        cursor = mycon.cursor()

        try:
            if choice == '1':
                report_date = input("Enter date (YYYY-MM-DD) or press Enter for today: ")
                if not report_date:
                    report_date = datetime.now().strftime('%Y-%m-%d')

                cursor.execute("""
                    SELECT COUNT(*) as total_visitors,
                           SUM(CASE WHEN approve='A' THEN 1 ELSE 0 END) as approved,
                           SUM(CASE WHEN approve='P' THEN 1 ELSE 0 END) as pending,
                           SUM(CASE WHEN approve='R' THEN 1 ELSE 0 END) as rejected,
                           SUM(CASE WHEN out_time IS NOT NULL THEN 1 ELSE 0 END) as checked_out
                    FROM vms WHERE DATE(entry_date) = %s
                """, (report_date,))

                result = cursor.fetchone()
                if result:
                    print(f"\nDAILY REPORT FOR {report_date}")
                    print(f"Total Visitors: {result[0]}")
                    print(f"Approved: {result[1]}")
                    print(f"Pending: {result[2]}")
                    print(f"Rejected: {result[3]}")
                    print(f"Checked Out: {result[4]}")
                else:
                    print(f"No data found for {report_date}.")

            elif choice == '2':
                cursor.execute("""
                    SELECT seq_no, name, mobile, representing, entry_date, purpose, emp_name, visitor_category
                    FROM vms WHERE approve='P' ORDER BY entry_date DESC
                """)

                results = cursor.fetchall()
                if results:
                    print(f"\nPENDING APPROVALS ({len(results)} entries)")
                    print(f"{'ID':<8} {'Name':<20} {'Mobile':<12} {'Company':<20} {'Category':<15} {'Purpose':<15} {'Host':<15}")
                    print("-" * 120)
                    for row in results:
                        entry_date = row[4].strftime('%Y-%m-%d') if row[4] else 'N/A'
                        print(f"{row[0]:<8} {row[1]:<20} {row[2]:<12} {row[3]:<20} {row[7]:<15} {row[5]:<15} {row[6]:<15}")
                else:
                    print("No pending approvals.")

            elif choice == '3':
                cursor.execute("""
                    SELECT
                        COUNT(*) as total,
                        SUM(CASE WHEN approve='A' THEN 1 ELSE 0 END) as approved,
                        SUM(CASE WHEN approve='P' THEN 1 ELSE 0 END) as pending,
                        SUM(CASE WHEN approve='R' THEN 1 ELSE 0 END) as rejected,
                        SUM(CASE WHEN approve='A' AND out_time IS NULL THEN 1 ELSE 0 END) as currently_in,
                        SUM(CASE WHEN approve='A' AND out_time IS NOT NULL THEN 1 ELSE 0 END) as checked_out
                    FROM vms WHERE entry_date >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
                """)

                result = cursor.fetchone()
                if result:
                    print(f"\nVISITOR STATUS SUMMARY (Last 30 days)")
                    print(f"Total Entries: {result[0]}")
                    print(f"Approved: {result[1]}")
                    print(f"Pending: {result[2]}")
                    print(f"Rejected: {result[3]}")
                    print(f"Currently Inside: {result[4]}")
                    print(f"Checked Out: {result[5]}")
                else:
                    print("No data found for the last 30 days.")

            elif choice == '4':
                cursor.execute("""
                    SELECT name, mobile, representing, COUNT(*) as visit_count
                    FROM vms
                    WHERE entry_date >= DATE_SUB(CURDATE(), INTERVAL 90 DAY)
                    GROUP BY mobile, name, representing
                    HAVING visit_count > 1
                    ORDER BY visit_count DESC
                    LIMIT 10
                """)

                results = cursor.fetchall()
                if results:
                    print(f"\nFREQUENT VISITORS (Last 90 days)")
                    print(f"{'Name':<20} {'Mobile':<12} {'Company':<20} {'Visits':<8}")
                    print("-" * 65)
                    for row in results:
                        print(f"{row[0]:<20} {row[1]:<12} {row[2]:<20} {row[3]:<8}")
                else:
                    print("No frequent visitors found.")

            else:
                print("Invalid choice.")
        except mysql.connector.Error as err:
            print(f"Error generating report: {err}")
        finally:
            cursor.close()
            mycon.close()


class VMSSystem:
    def __init__(self):
        self.db = VMSDatabase()
        self.auth = Authentication(self.db)
        self.user_mgmt = UserManagement(self.db, self.auth)
        self.vms_ops = VMSOperations(self.db, self.auth)

        # Initialize system
        setup = VMSSetup(self.db)
        setup.create_database()
        setup.create_tables()
        setup.insert_default_data()

    def admin_menu(self):
    #!# lock user function
        while True:
            print('\n===== ADMIN MENU =====\n')
            print("1. Create New User")
            print("2. View All Users")
            print("3. Unlock User Account")
            print("4. Approve/Reject Visitors")
            print("5. View All Visitor Entries")
            print("6. Visitor Checkout")
            print("7. View Reports")
            print("8. New Visitor Entry")
            print("9. Back to Main Menu")

            choice = input("Enter choice: ")
            if choice == '1':
                self.user_mgmt.create_user()
            elif choice == '2':
                self.user_mgmt.view_users()
            elif choice == '3':
                self.user_mgmt.unlock_user()
            elif choice == '4':
                self.vms_ops.approve_visitor()
            elif choice == '5':
                self.vms_ops.view_visitor_entries()
            elif choice == '6':
                self.vms_ops.checkout_visitor()
            elif choice == '7':
                self.vms_ops.view_reports()
            elif choice == '8':
                self.vms_ops.create_visitor_entry()
            elif choice == '9':
                break
            else:
                print("Invalid choice")

    def hr_menu(self):
    #!# Add lock user, Remove checkout, create vistor, view reports
        while True:
            print('\n===== HR MENU =====\n')
            print("1. Create New User")
            print("2. View All Users")
            print("3. Unlock User Account")
            print("4. Approve/Reject Visitors")
            print("5. View Visitor Entries")
            print("6. Visitor Checkout")
            print("7. View Reports")
            print("8. New Visitor Entry")
            print("9. Back to Main Menu")

            choice = input("Enter choice: ")
            if choice == '1':
                self.user_mgmt.create_user()
            elif choice == '2':
                self.user_mgmt.view_users()
            elif choice == '3':
                self.user_mgmt.unlock_user()
            elif choice == '4':
                self.vms_ops.approve_visitor()
            elif choice == '5':
                self.vms_ops.view_visitor_entries()
            elif choice == '6':
                self.vms_ops.checkout_visitor()
            elif choice == '7':
                self.vms_ops.view_reports()
            elif choice == '8':
                self.vms_ops.create_visitor_entry()
            elif choice == '9':
                break
            else:
                print("Invalid choice")

    def security_menu(self):
    #!# remove Approve/Reject Visitors option
        while True:
            print('\n===== SECURITY MENU =====\n')
            print("1. New Visitor Entry")
            print("2. View Visitor Entries")
            print("3. Approve/Reject Visitors")
            print("4. Visitor Checkout")
            print("5. View Pending Approvals") # Kept for explicit option, view_visitor_entries handles it
            print("6. Back to Main Menu")

            choice = input("Enter choice: ")
            if choice == '1':
                self.vms_ops.create_visitor_entry()
            elif choice == '2':
                self.vms_ops.view_visitor_entries()
            elif choice == '3':
                self.vms_ops.approve_visitor()
            elif choice == '4':
                self.vms_ops.checkout_visitor()
            elif choice == '5':
                # This will call view_visitor_entries, which handles pending approvals based on permissions
                self.vms_ops.view_visitor_entries()
            elif choice == '6':
                break
            else:
                print("Invalid choice")

    def user_menu(self):
    #!# remove checkout option
        while True:
            print('\n===== USER MENU =====\n')
            print("1. New Visitor Entry")
            print("2. View My Entries")
            print("3. Search Visitor") # view_visitor_entries handles this
            print("4. Visitor Checkout")
            print("5. Back to Main Menu")

            choice = input("Enter choice: ")
            if choice == '1':
                self.vms_ops.create_visitor_entry()
            elif choice == '2':
                self.vms_ops.view_visitor_entries()
            elif choice == '3':
                self.vms_ops.view_visitor_entries()
            elif choice == '4':
                self.vms_ops.checkout_visitor()
            elif choice == '5':
                break
            else:
                print("Invalid choice")

    def main_menu(self):
        while True:
            if self.auth.current_user:
                print(f"\n===== VMS - LOGGED IN AS: {self.auth.current_user['empname']} ({self.auth.current_user['user_role']}) =====\n")

                print("1. Access Functions")
                print("2. Logout")
                choice = input("Enter choice: ")
                if choice == '1':
                    if self.auth.current_user['user_role'] == 'ADMIN':
                        self.admin_menu()
                    elif self.auth.current_user['user_role'] == 'HR':
                        self.hr_menu()
                    elif self.auth.current_user['user_role'] == 'SECURITY':
                        self.security_menu()
                    else:
                        self.user_menu()
                elif choice == '2':
                    self.auth.logout()
                    # After logout, loop back to the initial login screen
                else:
                    print("Invalid choice")
            else:
                print('\n===== VISITOR MANAGEMENT SYSTEM =====\n')
                print("1. Login")
                print("2. Exit")

                choice = input("Enter choice: ")
                if choice == '1':
                    if self.auth.login():
                        continue # If login successful, re-enter the loop to show main menu for logged-in user
                elif choice == '2':
                    print("Thank you for using VMS!")
                    break
                else:
                    print("Invalid choice")

    def run(self):
        print("=== VMS System Initialized Successfully ===")
        print("Default Credentials:")
        print("ADMIN - Employee ID: ADMIN001, Password: admin123")
        print("HR - Employee ID: HR_MAIN, Password: hr123")
        print("SECURITY - Employee ID: SEC_MAIN, Password: sec123")
        print("=" * 60)
        self.main_menu()

# Initialize and run the system
if __name__ == "__main__":
    vms = VMSSystem()
    vms.run()