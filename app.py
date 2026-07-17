import os
from datetime import datetime
from flask import Flask, request, jsonify, session
from flask_bcrypt import Bcrypt
from flask_cors import CORS
import mysql.connector
from mysql.connector import Error

app = Flask(__name__, static_folder="static", static_url_path="")

# Requirements: Secure application key and session configs
app.secret_key = "super_secret_session_encryption_key_change_me"
app.config['SESSION_COOKIE_HTTPONLY'] = True  # Protects against XSS session theft
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'   # CSRF mitigation

bcrypt = Bcrypt(app)
CORS(app, supports_credentials=True) # Allows session cookies across requests

# Database Connection Helper
def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",          # Update with your local MySQL username
            password="Devdb@0220",  # Update with your local MySQL password
            database="auth_system"
        )
        return connection
    except Error as e:
        print(f"Database Connection Error: {e}")
        return None

# Root Route: Automatically serve login.html as the landing page
@app.route('/')
def home():
    return app.send_static_file('login.html')

# ==========================================
# AUTHENTICATION ROUTES
# ==========================================

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json() or {}
    username = data.get('username', '').strip()
    email = data.get('email', '').strip()
    password = data.get('password', '')

    if not username or not email or not password:
        return jsonify({"error": "All fields are required"}), 400

    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failure"}), 500
    
    cursor = conn.cursor(dictionary=True)
    try:
        # Check if user already exists
        cursor.execute("SELECT id FROM users WHERE username = %s OR email = %s", (username, email))
        if cursor.fetchone():
            return jsonify({"error": "Username or email already registered"}), 409

        # Hash password safely using bcrypt
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        # Insert user
        query = "INSERT INTO users (username, email, password) VALUES (%s, %s, %s)"
        cursor.execute(query, (username, email, hashed_password))
        conn.commit()
        
        return jsonify({"message": "User registered successfully"}), 201
    except Error as e:
        return jsonify({"error": f"Database execution error: {str(e)}"}), 500
    finally:
        cursor.close()
        conn.close()


@app.route('/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    username = data.get('username', '').strip()
    password = data.get('password', '')

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failure"}), 500

    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()

        # Securely verify password with safe constant-time comparison
        if user and bcrypt.check_password_hash(user['password'], password):
            # Establish server-side session
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['role'] = user['role']
            
            return jsonify({
                "message": "Login successful",
                "username": user['username'],
                "role": user['role']
            }), 200
        else:
            # Generic error to avoid user enumeration attacks
            return jsonify({"error": "Invalid username or password"}), 401
    except Error as e:
        return jsonify({"error": f"Database error: {str(e)}"}), 500
    finally:
        cursor.close()
        conn.close()


@app.route('/logout', methods=['GET'])
def logout():
    session.clear()
    return jsonify({"message": "Logout successful"}), 200


@app.route('/dashboard', methods=['GET'])
def dashboard():
    if 'user_id' not in session:
        return jsonify({"error": "Unauthorized access. Please log in."}), 401
    
    return jsonify({
        "message": f"Welcome, {session['username']}!",
        "username": session['username'],
        "role": session['role']
    }), 200


@app.route('/profile', methods=['GET'])
def profile():
    if 'user_id' not in session:
        return jsonify({"error": "Unauthorized access. Please log in."}), 401

    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failure"}), 500

    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT username, email, role, created_at FROM users WHERE id = %s", (session['user_id'],))
        user = cursor.fetchone()
        
        if not user:
            return jsonify({"error": "User profile not found"}), 404

        # Convert timestamp to clean string formatting
        if isinstance(user['created_at'], datetime):
            user['created_at'] = user['created_at'].strftime('%Y-%m-%d %H:%M:%S')

        return jsonify(user), 200
    except Error as e:
        return jsonify({"error": f"Database error: {str(e)}"}), 500
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    app.run(debug=True, port=5000)