from flask import Flask, render_template, request
from payment_gateway import make_payment
from order_management import update_order_status

app = Flask(__name__)

@app.route('/checkout', methods=['POST'])
def checkout():
    # Retrieve order details from the form
    order_id = request.form['order_id']
    total_amount = request.form['total_amount']
    payment_method = request.form['payment_method']

    # Make payment using the payment gateway
    payment_status = make_payment(order_id, total_amount, payment_method)

    # Handle payment success or failure
    if payment_status == 'success':
        # Update order status and show success message
        update_order_status(order_id, 'paid')
        return render_template('payment_success.html')
    else:
        # Show payment failure message
        return render_template('payment_failure.html')

if __name__ == '__main__':
    app.run(debug=True)
