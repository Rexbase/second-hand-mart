import bcrypt
import logging
import re
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = 'your-secret-key'

# Configure SQLAlchemy for PostgreSQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://mac:Mart7990@localhost:5433/shm'  # Replace with your database URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Suppresses a warning

db = SQLAlchemy(app)

# Create the Seller model
class Seller(db.Model):
    __tablename__ = 'sellers'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    password_hash = db.Column(db.String(100))
    email = db.Column(db.String(100))
    is_verified = db.Column(db.Boolean, default=False)

    def reset_password(self, new_password):
        self.password_hash = encrypt_password(new_password)
        db.session.commit()
    
    def __repr__(self):
        return f"<Seller {self.username}>"

    # Additional methods can be added for model-specific operations

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

# Routes

@app.route('/register-seller', methods=['GET', 'POST'])
def register_seller():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']

        if Seller.query.filter_by(username=username).first():
            logging.info("Username already exists. Please choose a different username.")
            return redirect(url_for('register_seller'))

        if not is_password_complex(password):
            logging.info("Password must be at least 8 characters long and contain at least one uppercase letter, one lowercase letter, and one digit.")
            return redirect(url_for('register_seller'))

        hashed_password = encrypt_password(password)
        new_seller = Seller(username=username, password_hash=hashed_password, email=email)
        db.session.add(new_seller)
        db.session.commit()

        # Additional steps for sending verification email, etc.

        logging.info("Seller registration successful.")
        return redirect(url_for('login'))

    return render_template('register_seller.html')

@app.route('/reset-password', methods=['POST'])
def reset_password():
    # Retrieve user input and initiate the password reset process
    username = request.form['username']
    new_password = request.form['new_password']

    seller = Seller.query.filter_by(username=username).first()
    if seller:
        seller.reset_password(new_password)
        # Redirect to login after successful password reset
        return redirect(url_for('login', message="Password reset successful. Please log in with your new password."))

    # Redirect to the password reset page with an error message for an invalid username
    return redirect(url_for('reset_password', error="Invalid username. Please try again."))

# Additional routes for verification, index, favicon, etc.

if __name__ == '__main__':
    app.run()