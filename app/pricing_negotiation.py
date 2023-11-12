import psycopg2
from flask import Flask, render_template, request

app = Flask(__name__)

# Connect to the PostgreSQL database
conn = psycopg2.connect(
    dbname='shm',
    user='mac',
    password='Mart7990',
    host='localhost',
    port='5433'
)

@app.route('/products', methods=['GET'])
def view_products():
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()
    cursor.close()

    return render_template('products.html', products=products)

@app.route('/product/<int:product_id>', methods=['GET', 'POST'])
def view_product(product_id):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products WHERE id = %s", (product_id,))
    product = cursor.fetchone()
    cursor.close()

    if product:
        if request.method == 'POST':
            price = float(request.form['price'])
            offer = float(request.form['offer'])

            # Perform negotiation logic here
            negotiated_price = negotiate_price(product['price'], price, offer)

            return render_template('product_details.html', product=product, negotiated_price=negotiated_price)
        else:
            return render_template('product_details.html', product=product)
    else:
        return "Product not found."

# Negotiation function
def negotiate_price(original_price, proposed_price, offer):
    if proposed_price >= original_price and offer >= original_price * 0.8:
        return proposed_price
    else:
        return original_price

if __name__ == '__main__':
    app.run()