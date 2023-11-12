from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Configure SQLAlchemy for a PostgreSQL database
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://mac:Mart7990@localhost/shm'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    # ... Define other category fields

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    description = db.Column(db.Text)
    price = db.Column(db.Float)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    category = db.relationship('Category', backref=db.backref('products', lazy='dynamic'))
    # ... Define other product fields

# Error handling decorator
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

# Routes
@app.route('/', methods=['GET'])
def home():
    categories = Category.query.all()
    return render_template('home.html', categories=categories)

@app.route('/category/<category_id>', methods=['GET'])
def view_category(category_id):
    category = Category.query.get(category_id)

    if category:
        products = Product.query.filter_by(category_id=category_id).all()
        return render_template('category.html', category=category, products=products)
    else:
        return page_not_found(404)

# Search route with form submission handling
@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        keyword = request.form['keyword']
        category_id = request.form['category']
        min_price = request.form['min_price']
        max_price = request.form['max_price']

        # Build the SQL query based on the provided search parameters using SQLAlchemy

        # Execute the query and retrieve the search results

        return render_template('search_results.html', keyword=keyword, products=products)

    categories = Category.query.all()
    return render_template('search.html', categories=categories)
