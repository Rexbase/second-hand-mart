import sqlite3
from flask import Flask, render_template, request

app = Flask(__name__)

# Establish database connection
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# Routes

@app.route('/', methods=['GET'])
def home():
    # Retrieve all categories from the database
    cursor.execute("SELECT * FROM categories")
    categories = cursor.fetchall()

    return render_template('home.html', categories=categories)

@app.route('/category/<category_id>', methods=['GET'])
def view_category(category_id):
    # Retrieve the category from the database
    cursor.execute("SELECT * FROM categories WHERE id = ?", (category_id,))
    category = cursor.fetchone()

    if category:
        # Retrieve all products in the category from the database
        cursor.execute("SELECT * FROM products WHERE category_id = ?", (category_id,))
        products = cursor.fetchall()

        return render_template('category.html', category=category, products=products)
    else:
        return "Category not found"

@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        keyword = request.form['keyword']
        category_id = request.form['category']
        min_price = request.form['min_price']
        max_price = request.form['max_price']

        # Build the SQL query based on the provided search parameters
        query = "SELECT * FROM products WHERE 1=1"

        if keyword:
            query += " AND (title LIKE ? OR description LIKE ?)"
        if category_id:
            query += " AND category_id = ?"
        if min_price:
            query += " AND price >= ?"
        if max_price:
            query += " AND price <= ?"

        # Prepare the parameters for the SQL query
        params = []

        if keyword:
            params.extend(['%' + keyword + '%', '%' + keyword + '%'])
        if category_id:
            params.append(category_id)
        if min_price:
            params.append(min_price)
        if max_price:
            params.append(max_price)

        # Execute the SQL query with the parameters
        cursor.execute(query, params)
        products = cursor.fetchall()

        return render_template('search_results.html', keyword=keyword, products=products)

    # Retrieve all categories from the database
    cursor.execute("SELECT * FROM categories")
    categories = cursor.fetchall()

    return render_template('search.html', categories=categories)

# Category Management and other routes...

if __name__ == '__main__':
    app.run()
