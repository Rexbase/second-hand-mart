from flask import Flask, render_template, request, session, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import bcrypt
import stripe

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Configure SQLAlchemy for PostgreSQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://mac:Mart7990@localhost:5433/shm'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    # Define other product fields

# Add more models if needed, e.g., User model for login/register functionality.

# Helper functions

def encrypt_password(password):
    # Hash the password securely using bcrypt
    hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    return hashed_password

def get_product_by_id(product_id):
    # Example function to retrieve a product from the database using SQLAlchemy
    return Product.query.filter_by(id=product_id).first()

def calculate_total_price(cart_items):
    # Example function to calculate the total price of items in the cart
    total_price = 0
    for item in cart_items:
        total_price += item.price  # Assuming 'price' is a field in the Product model
    return total_price

def calculate_discount(total_price):
    # Example function to calculate discounts based on the total price
    # Implement discount calculation logic here
    discount = 0  # Initialize discount as 0

    if total_price > 100:  # Example: Discount for total price above $100
        discount = 10  # $10 discount for total price above $100
    elif total_price > 50:  # Example: Discount for total price above $50
        discount = 5  # $5 discount for total price above $50

    return discount

def calculate_shipping_fee(total_price):
    # Example function to calculate shipping fees based on the total price
    # Implement shipping fee calculation logic here
    shipping_fee = 5  # Initialize shipping fee as $5

    if total_price > 100:  # Example: Free shipping for total price above $100
        shipping_fee = 5  # No shipping fee for total price above $100
    elif total_price > 50:  # Example: Reduced shipping fee for total price above $50
        shipping_fee = 3  # $2 shipping fee for total price above $50

    return shipping_fee

def process_payment(amount, card_token):
    # Set your secret API key
    stripe.api_key = 'your_stripe_secret_key'

    try:
        # Create a charge
        charge = stripe.Charge.create(
            amount=amount * 100,  # Amount in cents
            currency='usd',  # Currency (change as needed)
            source=card_token,  # Stripe token representing the payment source (e.g., card details)
            description='Payment for products'
        )
        return 'success'  # Payment successful if no exceptions are raised
    except stripe.error.CardError as e:
        # Payment is declined (card is invalid)
        return 'failure'  # Payment failed

# Assuming you already have a db instance created with SQLAlchemy
class Transaction(db.Model):
    __tablename__ = 'transactions'
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    total_price = db.Column(db.Float)
    discount = db.Column(db.Float)
    shipping_fee = db.Column(db.Float)
    grand_total = db.Column(db.Float)

    # Other fields as needed, linking with Users or Products, for instance

def save_transaction(cart_items, total_price, discount, shipping_fee, grand_total):
    try:
        transaction = Transaction(
            total_price=total_price,
            discount=discount,
            shipping_fee=shipping_fee,
            grand_total=grand_total
        )

        # Save the transaction details to the database
        db.session.add(transaction)
        db.session.commit()
        # Optional print for verification
        print("Transaction details saved successfully.")
    except Exception as e:
        print(f"An error occurred while saving transaction details: {e}")
        db.session.rollback()


# Other functions for session management, encryption, and more

# Routes
@app.route('/', methods=['GET'])
def home():
    products = Product.query.all()
    return render_template('home.html', products=products)

# Add routes for adding to cart, viewing cart, checkout, etc.

# Routes

@app.route('/add_to_cart/<product_id>', methods=['POST'])
def add_to_cart(product_id):
    # Retrieve the product from the database
    product = get_product_by_id(product_id)

    if product:
        # Add the product to the cart
        if 'cart' not in session:
            session['cart'] = []
        session['cart'].append(product)
        flash('Product added to cart successfully', 'success')
    else:
        flash('Product not found', 'error')

    return redirect(url_for('home'))

@app.route('/cart', methods=['GET'])
def view_cart():
    if 'cart' in session:
        cart_items = session['cart']
        total_price = calculate_total_price(cart_items)
        discount = calculate_discount(total_price)
        shipping_fee = calculate_shipping_fee(total_price)
        grand_total = total_price - discount + shipping_fee
    else:
        cart_items = []
        total_price = 0
        discount = 0
        shipping_fee = 0
        grand_total = 0

    return render_template('cart.html', cart_items=cart_items, total_price=total_price,
                           discount=discount, shipping_fee=shipping_fee, grand_total=grand_total)

@app.route('/checkout', methods=['POST'])
def checkout():
    if 'cart' in session:
        cart_items = session['cart']
        total_price = calculate_total_price(cart_items)
        discount = calculate_discount(total_price)
        shipping_fee = calculate_shipping_fee(total_price)
        grand_total = total_price - discount + shipping_fee

        # Process secure payment using a payment gateway API
        payment_status = process_payment(grand_total)

        if payment_status == 'success':
            # Save transaction details in the database
            save_transaction(cart_items, total_price, discount, shipping_fee, grand_total)

            # Clear the cart
            session.pop('cart', None)

            flash('Payment successful. Your order has been placed.', 'success')
        else:
            flash('Payment failed. Please try again.', 'error')

    return redirect(url_for('home'))

# Other routes and functions...

if __name__ == '__main__':
    app.run()
