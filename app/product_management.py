import sqlite3
import logging
from flask import Flask, render_template, request, redirect, url_for, session

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

def create_product_table():
    try:
        # Create the products table if it doesn't exist
        cursor.execute('''CREATE TABLE IF NOT EXISTS products (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            seller_id INTEGER,
                            title TEXT,
                            description TEXT,
                            price REAL,
                            FOREIGN KEY (seller_id) REFERENCES sellers(id)
                        )''')
        conn.commit()

    except Exception as e:
        logger.error("An error occurred while creating the products table: %s", str(e))

def store_product(seller_id, title, description, price):
    try:
        # Store the product information in the database
        cursor.execute("INSERT INTO products (seller_id, title, description, price) VALUES (?, ?, ?, ?)",
                       (seller_id, title, description, price))
        conn.commit()

        logger.info("Product listing successful.")
        return True

    except Exception as e:
        logger.error("An error occurred during product listing: %s", str(e))
        return False

def retrieve_product(product_id):
    try:
        # Retrieve a product from the database by its ID
        cursor.execute("SELECT * FROM products WHERE id = ?", (product_id,))
        result = cursor.fetchone()
        return result

    except Exception as e:
        logger.error("An error occurred during product retrieval: %s", str(e))

    return None

def update_product(product_id, title, description, price):
    try:
        # Update the product information in the database
        cursor.execute("UPDATE products SET title = ?, description = ?, price = ? WHERE id = ?",
                       (title, description, price, product_id))
        conn.commit()

        logger.info("Product update successful.")
        return True

    except Exception as e:
        logger.error("An error occurred during product update: %s", str(e))
        return False

def delete_product(product_id):
    try:
        # Delete a product from the database by its ID
        cursor.execute("DELETE FROM products WHERE id = ?", (product_id,))
        conn.commit()

        logger.info("Product deletion successful.")
        return True

    except Exception as e:
        logger.error("An error occurred during product deletion: %s", str(e))
        return False

def retrieve_products():
    try:
        # Retrieve all products from the database
        cursor.execute("SELECT * FROM products")
        results = cursor.fetchall()
        return results

    except Exception as e:
        logger.error("An error occurred during product retrieval: %s", str(e))

    return []

# Routes

@app.route('/list-product', methods=['GET', 'POST'])
def list_product():
    if request.method == 'POST':
        seller_id = session['seller_id']
        title = request.form['title']
        description = request.form['description']
        price = request.form['price']

        try:
            # Store the product information in the database
            if store_product(seller_id, title, description, price):
                logger.info("Product listing successful.")
                return redirect(url_for('dashboard'))
            else:
                logger.error("An error occurred during product listing.")
                return redirect(url_for('list_product'))

        except Exception as e:
            logger.error("An error occurred during product listing: %s", str(e))
            return redirect(url_for('list_product'))

    return render_template('list_product.html')

@app.route('/product/<product_id>', methods=['GET'])
def view_product(product_id):
    product = retrieve_product(product_id)
    if product:
        return render_template('view_product.html', product=product)
    else:
        logger.error("Product not found.")
        return redirect(url_for('dashboard'))

@app.route('/product/<product_id>/edit', methods=['GET', 'POST'])
def edit_product(product_id):
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        price = request.form['price']

        try:
            # Update the product information in the database
            if update_product(product_id, title, description, price):
                logger.info("Product update successful.")
                return redirect(url_for('view_product', product_id=product_id))
            else:
                logger.error("An error occurred during product update.")
                return redirect(url_for('edit_product', product_id=product_id))

        except Exception as e:
            logger.error("An error occurred during product update: %s", str(e))
            return redirect(url_for('edit_product', product_id=product_id))

    product = retrieve_product(product_id)
    if product:
        return render_template('edit_product.html', product=product)
    else:
        logger.error("Product not found.")
        return redirect(url_for('dashboard'))

@app.route('/product/<product_id>/delete', methods=['POST'])
def delete_product(product_id):
    try:
        # Delete the product from the database
        if delete_product(product_id):
            logger.info("Product deletion successful.")
        else:
            logger.error("An error occurred during product deletion.")

    except Exception as e:
        logger.error("An error occurred during product deletion: %s", str(e))

    return redirect(url_for('dashboard'))

# ...

if __name__ == '__main__':
    # Create the products table if it doesn't exist
    create_product_table()

    app.run()
