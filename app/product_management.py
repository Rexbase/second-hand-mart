import psycopg2
import logging
from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Connect to the PostgreSQL database
conn = psycopg2.connect(
    dbname='shm',
    user='mac',
    password='Mart7990',
    host='localhost',
    port='5433'
)
cursor = conn.cursor()

# Helper functions

def create_product_table():
    try:
        cursor.execute('''CREATE TABLE IF NOT EXISTS products (
                            id SERIAL PRIMARY KEY,
                            seller_id INTEGER,
                            title TEXT,
                            description TEXT,
                            price REAL,
                            FOREIGN KEY (seller_id) REFERENCES sellers(id)
                        )''')
        conn.commit()
        logger.info("Product table creation successful.")

    except Exception as e:
        logger.error(f"An error occurred while creating the products table: {e}")

# Other helper functions (store_product, retrieve_product, update_product, delete_product) as they were

# Routes

@app.route('/list-product', methods=['GET', 'POST'])
def list_product():
    if request.method == 'POST':
        seller_id = session['seller_id']
        title = request.form['title']
        description = request.form['description']
        price = request.form['price']

        try:
            if store_product(seller_id, title, description, price):
                logger.info("Product listing successful.")
                return redirect(url_for('dashboard'))
            else:
                logger.error("An error occurred during product listing.")
                return redirect(url_for('list_product'))

        except Exception as e:
            logger.error(f"An error occurred during product listing: {e}")
            return redirect(url_for('list_product'))

    return render_template('list_product.html')

# Other routes (view_product, edit_product, delete_product) remain as they were

if __name__ == '__main__':
    create_product_table()  # Create the products table if it doesn't exist
    app.run()
