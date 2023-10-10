import bcrypt
import sqlite3
import logging
import time
import re
from flask import Flask, render_template, request, redirect, url_for, session
from payment_gateway import make_payment
from order_management import update_order_status

# Rest of your code


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

def encrypt_password(password):
    # Hash the password securely using bcrypt
    hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt(rounds=12))
    return hashed_password

def store_seller(username, password, email, verification_code):
    try:
        # Hash the password securely
        hashed_password = encrypt_password(password)

        # Store the seller information in the database
        cursor.execute("INSERT INTO sellers (username, password_hash, email, verification_code) VALUES (?, ?, ?, ?)",
                       (username, hashed_password, email, verification_code))
        conn.commit()

        logger.info("Seller registration successful.")
        return True

    except Exception as e:
        logger.error("An error occurred during seller registration: %s", str(e))
        return False

def retrieve_seller(username):
    try:
        # Retrieve seller information from the database
        cursor.execute("SELECT username, password_hash, email, is_verified FROM sellers WHERE username = ?", (username,))
        result = cursor.fetchone()

        if result:
            username, password_hash, email, is_verified = result
            return username, password_hash, email, is_verified

    except Exception as e:
        logger.error("An error occurred during seller retrieval: %s", str(e))

    return None

def send_verification_email(email, verification_code):
    # Implement your email sending functionality here
    pass

def verify_seller_account(username):
    try:
        # Update the seller's account as verified
        cursor.execute("UPDATE sellers SET is_verified = 1 WHERE username = ?", (username,))
        conn.commit()

        logger.info("Seller account verified successfully.")
        return True

    except Exception as e:
        logger.error("An error occurred during seller account verification: %s", str(e))
        return False

# Routes

@app.route('/register-seller', methods=['GET', 'POST'])
def register_seller():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        verification_code = generate_verification_code()  # Generate a verification code

        try:
            # Check if the username already exists in the database
            if retrieve_seller(username):
                logger.info("Username already exists. Please choose a different username.")
                return redirect(url_for('register_seller'))

            # Check password complexity
            if not is_password_complex(password):
                logger.info("Password must be at least 8 characters long and contain at least one uppercase letter, one lowercase letter, and one digit.")
                return redirect(url_for('register_seller'))

            # Store the seller information in the database
            if store_seller(username, password, email, verification_code):
                # Send verification email to the seller
                send_verification_email(email, verification_code)

                logger.info("Seller registration successful. Please check your email for verification.")
                return redirect(url_for('verification', verification_code=verification_code))
            else:
                logger.error("An error occurred during seller registration.")
                return redirect(url_for('register_seller'))

        except Exception as e:
            logger.error("An error occurred during seller registration: %s", str(e))
            return redirect(url_for('register_seller'))

    return render_template('register_seller.html')

@app.route('/verification/<verification_code>')
def verification(verification_code):
    try:
        # Retrieve the seller based on the verification code
        cursor.execute("SELECT username FROM sellers WHERE verification_code = ?", (verification_code,))
        result = cursor.fetchone()

        if result:
            username = result[0]
            if verify_seller_account(username):
                logger.info("Seller account verified successfully.")
                return redirect(url_for('login'))
            else:
                logger.error("An error occurred during seller account verification.")
                return redirect(url_for('register_seller'))
        else:
            logger.error("Invalid verification code.")
            return redirect(url_for('register_seller'))

    except Exception as e:
        logger.error("An error occurred during seller account verification: %s", str(e))
        return redirect(url_for('register_seller'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        seller = retrieve_seller(username)
        if seller:
            _, password_hash, _, is_verified = seller
            if bcrypt.checkpw(password.encode(), password_hash):
                if is_verified:
                    session['username'] = username
                    logger.info("Seller logged in: %s", username)
                    return redirect(url_for('dashboard'))
                else:
                    logger.info("Seller account not verified.")
                    return redirect(url_for('register_seller'))
        logger.info("Invalid username or password.")
        return redirect(url_for('login'))

    return render_template('login.html')

# Add the new routes for the recently created HTML pages

@app.route('/home')
def home():
    # Render the home.html template
    return render_template('home.html')

@app.route('/cart')
def cart():
    # Render the cart.html template
    return render_template('cart.html')

@app.route('/checkout', methods=['POST'])
def checkout():
    # Implement the checkout route logic here
    pass

@app.route('/order_listing')
def order_listing():
    # Implement the order listing route logic here
    pass

@app.route('/dashboard')
def dashboard():
    if 'username' in session:
        username = session['username']
        return render_template('dashboard.html', username=username)
    return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

# Run the application
if __name__ == '__main__':
    app.run()
