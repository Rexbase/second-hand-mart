import sqlite3

# Establish database connection
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

def update_order_status(order_id, status):
    try:
        # Update the order status in the database
        cursor.execute("UPDATE orders SET status = ? WHERE order_id = ?", (status, order_id))
        conn.commit()

        print("Order status updated successfully.")
        return True

    except Exception as e:
        print("An error occurred while updating order status:", str(e))
        return False
