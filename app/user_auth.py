import bcrypt
import sqlite3
import logging
import time
import re
from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
db = SQLAlchemy(app)


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask application
app = Flask(__name__)
app.secret_key = 'your-secret-key'

# Establish database connection
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# Helper functions

def is_password_complex(password):
    # Check password complexity using a regular expression
    # At least 8 characters, one uppercase, one lowercase, and one digit
    pattern = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$"
    return bool(re.match(pattern, password))

def is_account_locked(login_attempts, last_login_attempt):
    # Check if the account is locked based on login attempts and time elapsed
    max_login_attempts = 5
    lockout_duration = 300  # 5 minutes
    current_time = int(time.time())
    return login_attempts >= max_login_attempts and (current_time - last_login_attempt) < lockout_duration

def increment_login_attempts(username):
    try:
        # Increment the login_attempts column by 1 and update the last_login_attempt timestamp
        cursor.execute("UPDATE users SET login_attempts = login_attempts + 1, last_login_attempt = ? WHERE username = ?",
                       (int(time.time()), username))
        conn.commit()

    except Exception as e:
        logger.error("An error occurred during login attempt increment: %s", str(e))

def reset_login_attempts(username):
    try:
        # Reset the login_attempts and last_login_attempt columns to their initial values
        cursor.execute("UPDATE users SET login_attempts = 0, last_login_attempt = 0 WHERE username = ?", (username,))
        conn.commit()

    except Exception as e:
        logger.error("An error occurred during login attempt reset: %s", str(e))

def encrypt_data(data):
    # Add encryption logic here (e.g., using cryptography library)
    return data

def decrypt_data(data):
    # Add decryption logic here (e.g., using cryptography library)
    return data

# Routes

@app.route('/')
def home():
    return "Welcome to Second-Hand Mart!"

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']

        try:
            # Check if the username already exists in the database
            cursor.execute("SELECT username FROM users WHERE username = ?", (username,))
            if cursor.fetchone():
                logger.info("Username already exists. Please choose a different username.")
                return redirect(url_for('register'))

            # Check password complexity
            if not is_password_complex(password):
                logger.info("Password must be at least 8 characters long and contain at least one uppercase letter, one lowercase letter, and one digit.")
                return redirect(url_for('register'))

            # Hash the password securely using bcrypt
            hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt(rounds=12))

            # Encrypt the email before storing it in the database
            encrypted_email = encrypt_data(email)

            # Insert the user into the database
            cursor.execute("INSERT INTO users (username, password_hash, email) VALUES (?, ?, ?)",
                           (username, hashed_password, encrypted_email))
            conn.commit()
            logger.info("Registration successful. You can now log in.")
            return redirect(url_for('login'))

        except Exception as e:
            logger.error("An error occurred during user registration: %s", str(e))
            return redirect(url_for('register'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        try:
            # Retrieve the hashed password and other user information from the database for the given username
            cursor.execute("SELECT password_hash, email, login_attempts, last_login_attempt FROM users WHERE username = ?", (username,))
            result = cursor.fetchone()
            if result:
                stored_password = result[0]
                email = result[1]
                login_attempts = result[2]
                last_login_attempt = result[3]

                # Check if the account is locked due to too many failed login attempts
                if is_account_locked(login_attempts, last_login_attempt):
                    logger.info("Account locked due to too many failed login attempts. Please try again later or reset your password.")
                    return redirect(url_for('login'))

                # Verify the password using bcrypt
                if bcrypt.checkpw(password.encode(), stored_password.encode()):
                    logger.info("Authentication successful. Welcome, " + username + "!")
                    # Reset login attempts on successful login
                    reset_login_attempts(username)
                    # Store the username in the session
                    session['username'] = username
                    return redirect(url_for('home'))
                else:
                    # Increment login attempts on failed login
                    increment_login_attempts(username)
                    logger.info("Invalid password.")

            else:
                logger.info("Invalid username.")

        except Exception as e:
            logger.error("An error occurred during user authentication: %s", str(e))
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/logout')
def logout():
    # Clear the session and redirect to the login page
    session.clear()
    return redirect(url_for('login'))

# ...

if __name__ == '__main__':
    app.run()
