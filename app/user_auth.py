import bcrypt
import psycopg2
import logging
import time
import re
from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = 'your-secret-key'

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Establish database connection
conn = psycopg2.connect(
    dbname='shm',
    user='mac',
    password='Mart7990',
    host='localhost',
    port='5433'
)
cursor = conn.cursor()

# Helper functions

def is_password_complex(password):
    pattern = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$"
    return bool(re.match(pattern, password))

def is_account_locked(login_attempts, last_login_attempt):
    max_login_attempts = 5
    lockout_duration = 300  # 5 minutes
    current_time = int(time.time())
    return login_attempts >= max_login_attempts and (current_time - last_login_attempt) < lockout_duration

def increment_login_attempts(username):
    try:
        cursor.execute("UPDATE users SET login_attempts = login_attempts + 1, last_login_attempt = %s WHERE username = %s",
                       (int(time.time()), username))
        conn.commit()
    except Exception as e:
        logger.error("An error occurred during login attempt increment: %s", str(e))

def reset_login_attempts(username):
    try:
        cursor.execute("UPDATE users SET login_attempts = 0, last_login_attempt = 0 WHERE username = %s", (username,))
        conn.commit()
    except Exception as e:
        logger.error("An error occurred during login attempt reset: %s", str(e))

# ... Add more helper functions here if needed

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
            cursor.execute("SELECT username FROM users WHERE username = %s", (username,))
            if cursor.fetchone():
                logger.info("Username already exists. Please choose a different username.")
                return redirect(url_for('register'))

            if not is_password_complex(password):
                logger.info("Password must be at least 8 characters long and contain at least one uppercase letter, one lowercase letter, and one digit.")
                return redirect(url_for('register'))

            hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt(rounds=12))
            encrypted_email = encrypt_data(email)

            cursor.execute("INSERT INTO users (username, password_hash, email) VALUES (%s, %s, %s)",
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
            cursor.execute("SELECT password_hash, email, login_attempts, last_login_attempt FROM users WHERE username = %s", (username,))
            result = cursor.fetchone()
            if result:
                stored_password = result[0]
                email = result[1]
                login_attempts = result[2]
                last_login_attempt = result[3]

                if is_account_locked(login_attempts, last_login_attempt):
                    logger.info("Account locked due to too many failed login attempts. Please try again later or reset your password.")
                    return redirect(url_for('login'))

                if bcrypt.checkpw(password.encode(), stored_password.encode()):
                    logger.info("Authentication successful. Welcome, " + username + "!")
                    reset_login_attempts(username)
                    session['username'] = username
                    return redirect(url_for('home'))
                else:
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
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run()
