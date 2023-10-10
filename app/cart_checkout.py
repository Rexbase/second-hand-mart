from flask import Flask, render_template, request, session, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Routes

@app.route('/', methods=['GET'])
def home():
    # Retrieve products from the database
    products = get_products()

    return render_template('home.html', products=products)

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
