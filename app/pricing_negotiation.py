from flask import Flask, render_template, request

app = Flask(__name__)

# Sample data
products = [
    {"id": 1, "name": "Product 1", "price": 50.0},
    {"id": 2, "name": "Product 2", "price": 100.0},
    {"id": 3, "name": "Product 3", "price": 75.0}
]

@app.route('/products', methods=['GET'])
def view_products():
    return render_template('products.html', products=products)

@app.route('/product/<int:product_id>', methods=['GET', 'POST'])
def view_product(product_id):
    product = next((p for p in products if p["id"] == product_id), None)

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
    # Implement your negotiation logic here
    # Compare the proposed price with the original price and the buyer's offer
    if proposed_price >= original_price and offer >= original_price * 0.8:
        return proposed_price
    else:
        return original_price

if __name__ == '__main__':
    app.run()
