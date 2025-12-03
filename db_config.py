# Database Configuration for Kedai Hauna POS
# Konfigurasi untuk koneksi ke MySQL (XAMPP)

import mysql.connector
from mysql.connector import Error

class Database:
    def __init__(self):
        """Initialize database connection"""
        self.host = "localhost"
        self.user = "root"
        self.password = ""  # Default XAMPP password kosong
        self.database = "kedai_hauna"
        self.connection = None
    
    def connect(self):
        """Create database connection"""
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database
            )
            if self.connection.is_connected():
                return True
        except Error as e:
            print(f"Error connecting to MySQL: {e}")
            return False
    
    def disconnect(self):
        """Close database connection"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
    
    def execute_query(self, query, params=None):
        """Execute INSERT, UPDATE, DELETE queries"""
        try:
            cursor = self.connection.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            self.connection.commit()
            return cursor.lastrowid
        except Error as e:
            print(f"Error executing query: {e}")
            self.connection.rollback()
            return None
    
    def fetch_all(self, query, params=None):
        """Execute SELECT query and return all results"""
        try:
            cursor = self.connection.cursor(dictionary=True)
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            return cursor.fetchall()
        except Error as e:
            print(f"Error fetching data: {e}")
            return []
    
    def fetch_one(self, query, params=None):
        """Execute SELECT query and return one result"""
        try:
            cursor = self.connection.cursor(dictionary=True)
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            return cursor.fetchone()
        except Error as e:
            print(f"Error fetching data: {e}")
            return None

# Database helper functions
def save_transaction(db, transaction_id, customer_name, payment_method, items, total):
    """Save transaction to database"""
    try:
        # Calculate subtotal and tax
        subtotal = total / 1.1
        tax = total - subtotal
        
        # Insert transaction
        query = """
        INSERT INTO transactions (transaction_id, customer_name, payment_method, subtotal, tax, total)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        db.execute_query(query, (transaction_id, customer_name, payment_method, subtotal, tax, total))
        
        # Insert transaction items
        for item in items:
            query = """
            INSERT INTO transaction_items (transaction_id, item_id, item_name, variant, price, quantity, subtotal)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            item_subtotal = item['price'] * item['quantity']
            variant = item.get('variant', None)
            db.execute_query(query, (
                transaction_id,
                item['id'],
                item['name'],
                variant,
                item['price'],
                item['quantity'],
                item_subtotal
            ))
        
        return True
    except Exception as e:
        print(f"Error saving transaction: {e}")
        return False

def get_all_transactions(db):
    """Get all transactions from database"""
    query = """
    SELECT 
        t.transaction_id as id,
        t.customer_name,
        t.payment_method,
        t.total,
        DATE_FORMAT(t.created_at, '%Y-%m-%d %H:%i:%s') as date
    FROM transactions t
    ORDER BY t.created_at DESC
    """
    transactions = db.fetch_all(query)
    
    # Get items for each transaction
    for trans in transactions:
        query = """
        SELECT item_id as id, item_name as name, variant, price, quantity
        FROM transaction_items
        WHERE transaction_id = %s
        """
        items = db.fetch_all(query, (trans['id'],))
        trans['items'] = items
    
    return transactions

def get_transaction_stats(db):
    """Get transaction statistics"""
    query = """
    SELECT 
        COUNT(*) as total_transactions,
        COALESCE(SUM(total), 0) as total_income,
        COALESCE(AVG(total), 0) as avg_transaction
    FROM transactions
    """
    return db.fetch_one(query)
