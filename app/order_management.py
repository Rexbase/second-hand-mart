import psycopg2

# Function to create a new order in PostgreSQL
def create_new_order(customer_id, product_id, quantity):
    try:
        # Connect to the PostgreSQL database
        conn = psycopg2.connect(
            dbname='shm',
            user='mac',
            password='Mart7990',
            host='localhost',
            port='5433'
        )
        
        cursor = conn.cursor()

        # Insert a new order into the database
        cursor.execute("INSERT INTO orders (customer_id, product_id, quantity, status) VALUES (%s, %s, %s, 'Pending')",
                       (customer_id, product_id, quantity))
        conn.commit()

        print("New order created successfully.")
        return True

    except Exception as e:
        print("An error occurred while creating a new order:", str(e))
        return False

    finally:
        if conn:
            cursor.close()
            conn.close()

# Function to update order status in PostgreSQL
def update_order_status(order_id, status):
    try:
        # Connect to the PostgreSQL database
        conn = psycopg2.connect(
            dbname='shm',
            user='mac',
            password='Mart7990',
            host='localhost',
            port='5433'
        )
        
        cursor = conn.cursor()

        # Update the order status in the database
        cursor.execute("UPDATE orders SET status = %s WHERE order_id = %s", (status, order_id))
        conn.commit()

        print("Order status updated successfully.")
        return True

    except Exception as e:
        print("An error occurred while updating order status:", str(e))
        return False

    finally:
        if conn:
            cursor.close()
            conn.close()
