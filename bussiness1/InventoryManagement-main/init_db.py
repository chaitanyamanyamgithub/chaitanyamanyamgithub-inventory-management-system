import os
import sys
import pymysql
from datetime import datetime, timedelta
import random
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add the parent directory to sys.path to import from app
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Import our compatible password hashing function
from app.utils.auth_helpers import safe_generate_password_hash

# Database configuration - using environment variables
DB_CONFIG = {
    'host': os.environ.get('MYSQL_HOST', 'localhost'),
    'user': os.environ.get('MYSQL_USER', 'root'),
    'password': os.environ.get('MYSQL_PASSWORD', ''),
    'db': os.environ.get('MYSQL_DB', 'inventory_db'),
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor
}

def create_sample_data():
    """
    Creates sample data for the inventory management system.
    
    Before running this script, make sure to:
    1. Create a .env file with your database credentials
    2. Ensure the database exists
    3. Run the database schema first
    
    Example .env file:
    MYSQL_HOST=localhost
    MYSQL_USER=root
    MYSQL_PASSWORD=your_password
    MYSQL_DB=inventory_db
    """
    
    # Check if required environment variables are set
    required_vars = ['MYSQL_USER', 'MYSQL_PASSWORD', 'MYSQL_DB']
    missing_vars = [var for var in required_vars if not os.environ.get(var)]
    
    if missing_vars:
        print("❌ Error: Missing required environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\nPlease create a .env file with your database configuration.")
        print("You can copy .env.template to .env and update the values.")
        return False
    
    print(f"🔗 Connecting to database: {DB_CONFIG['db']} on {DB_CONFIG['host']}")
    print(f"👤 Using user: {DB_CONFIG['user']}")
    
    conn = None
    try:
        # Connect to the database
        print("Connecting to MySQL database...")
        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Disable foreign key checks before truncating
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
        
        # Clear existing data
        tables = [
            'stock_adjustments',
            'sale_items',
            'sales',
            'purchase_items',
            'purchases',
            'products',
            'customers',
            'suppliers',
            'categories',
            'users'
        ]
        
        for table in tables:
            cursor.execute(f"TRUNCATE TABLE {table}")
        
        # Re-enable foreign key checks after truncating
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
        
        # Insert users
        print("Creating users...")
        admin_password = safe_generate_password_hash('admin123')
        staff_password = safe_generate_password_hash('staff123')
        
        cursor.execute('''
            INSERT INTO users (username, password, full_name, email, role)
            VALUES
                ('admin', %s, 'Admin User', 'admin@example.com', 'admin'),
                ('staff', %s, 'Staff User', 'staff@example.com', 'staff')
        ''', (admin_password, staff_password))
        
        # Insert categories
        print("Creating categories...")
        categories = [
            ('Electronics', 'Electronic devices and accessories'),
            ('Clothing', 'Apparel and fashion items'),
            ('Books', 'Books and educational materials'),
            ('Home & Garden', 'Home improvement and gardening supplies'),
            ('Sports', 'Sports and fitness equipment')
        ]
        
        cursor.executemany('''
            INSERT INTO categories (name, description) VALUES (%s, %s)
        ''', categories)
        
        # Get category IDs
        cursor.execute('SELECT id, name FROM categories')
        category_data = cursor.fetchall()
        category_ids = {cat['name']: cat['id'] for cat in category_data}
        
        # Insert products
        print("Creating products...")
        products = [
            ('Laptop Computer', category_ids['Electronics'], 450.00, 580.00, 'piece', 25, 5),
            ('Wireless Mouse', category_ids['Electronics'], 15.00, 25.00, 'piece', 100, 20),
            ('T-Shirt', category_ids['Clothing'], 12.00, 20.00, 'piece', 200, 50),
            ('Jeans', category_ids['Clothing'], 35.00, 55.00, 'piece', 80, 15),
            ('Programming Book', category_ids['Books'], 25.00, 40.00, 'piece', 60, 15),
            ('Garden Hose', category_ids['Home & Garden'], 20.00, 35.00, 'piece', 50, 10),
            ('Basketball', category_ids['Sports'], 18.00, 30.00, 'piece', 40, 10),
            ('Yoga Mat', category_ids['Sports'], 22.00, 38.00, 'piece', 70, 15),
            ('LED Light Bulb', category_ids['Electronics'], 8.00, 15.00, 'piece', 150, 30),
            ('Coffee Mug', category_ids['Home & Garden'], 6.00, 12.00, 'piece', 120, 25)
        ]
        
        for product in products:
            cursor.execute('''
                INSERT INTO products 
                (name, category_id, purchase_price, selling_price, unit, current_stock, min_stock_level)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            ''', product)
        
        # Get product IDs
        cursor.execute('SELECT id, name FROM products')
        product_data = cursor.fetchall()
        product_ids = {prod['name']: prod['id'] for prod in product_data}
        
        # Insert customers
        print("Creating customers...")
        customers = [
            ('Rahul Sharma', '9876543210', 'rahul@example.com', '123 Farmer Colony, Delhi'),
            ('Priya Singh', '8765432109', 'priya@example.com', '456 Green Fields, Mumbai'),
            ('Amit Patel', '7654321098', 'amit@example.com', '789 Harvest Road, Ahmedabad'),
            ('Sunita Verma', '6543210987', 'sunita@example.com', '234 Crop Avenue, Jaipur'),
            ('Rajesh Kumar', '5432109876', 'rajesh@example.com', '567 Soil Street, Chennai')
        ]
        
        cursor.executemany('''
            INSERT INTO customers (name, phone, email, address)
            VALUES (%s, %s, %s, %s)
        ''', customers)
        
        # Get customer IDs
        cursor.execute('SELECT id, name FROM customers')
        customer_data = cursor.fetchall()
        customer_ids = [cust['id'] for cust in customer_data]
        
        # Insert suppliers
        print("Creating suppliers...")
        suppliers = [
            ('Tech Supply Co.', 'John Smith', '9876123450', 'contact@techsupply.com', '123 Tech Street, Tech City'),
            ('Fashion Wholesale Ltd.', 'Sarah Johnson', '8765123450', 'orders@fashionwholesale.com', '456 Fashion Ave, Style Town'),
            ('Book Distributors Inc.', 'Mike Davis', '7654123450', 'sales@bookdist.com', '789 Knowledge Lane, Book City'),
            ('Home & Garden Supplies', 'Lisa Wilson', '6543123450', 'info@homegardens.com', '321 Garden Road, Green Valley'),
            ('Sports Equipment Co.', 'David Brown', '5432123450', 'sales@sportsequip.com', '654 Sports Blvd, Athletic City')
        ]
        
        cursor.executemany('''
            INSERT INTO suppliers (name, contact_person, phone, email, address)
            VALUES (%s, %s, %s, %s, %s)
        ''', suppliers)
        
        # Get supplier IDs
        cursor.execute('SELECT id, name FROM suppliers')
        supplier_data = cursor.fetchall()
        supplier_ids = [sup['id'] for sup in supplier_data]
        
        # Insert purchases
        print("Creating purchases...")
        start_date = datetime.now() - timedelta(days=60)
        
        for i in range(1, 21):
            purchase_date = start_date + timedelta(days=i*3)
            supplier_id = random.choice(supplier_ids)
            ref_number = f"PO-{purchase_date.strftime('%Y%m%d')}-{i:03d}"
            
            # Create purchase header
            cursor.execute('''
                INSERT INTO purchases 
                (supplier_id, reference_number, purchase_date, total_amount, notes, user_id)
                VALUES (%s, %s, %s, %s, %s, %s)
            ''', (supplier_id, ref_number, purchase_date.date(), 0, f"Stock purchase {i}", 1))
            
            purchase_id = cursor.lastrowid
            total_amount = 0
            
            # Add 1-3 products to each purchase
            num_products = random.randint(1, 3)
            selected_products = random.sample(list(product_ids.items()), num_products)
            
            for product_name, product_id in selected_products:
                quantity = random.randint(5, 20)
                product_cursor = conn.cursor()
                product_cursor.execute('SELECT purchase_price FROM products WHERE id = %s', (product_id,))
                product_data = product_cursor.fetchone()
                unit_price = product_data['purchase_price']
                total_price = quantity * unit_price
                total_amount += total_price
                
                cursor.execute('''
                    INSERT INTO purchase_items
                    (purchase_id, product_id, quantity, unit_price, total_price)
                    VALUES (%s, %s, %s, %s, %s)
                ''', (purchase_id, product_id, quantity, unit_price, total_price))
                
                product_cursor.close()
            
            # Update purchase total
            cursor.execute('''
                UPDATE purchases
                SET total_amount = %s
                WHERE id = %s
            ''', (total_amount, purchase_id))
        
        # Insert sales
        print("Creating sales...")
        start_date = datetime.now() - timedelta(days=30)
        
        for i in range(1, 31):
            sale_date = start_date + timedelta(days=i)
            customer_id = random.choice(customer_ids) if random.random() > 0.3 else None
            invoice_number = f"INV-{sale_date.strftime('%Y%m%d')}-{i:03d}"
            
            # Create sale header
            cursor.execute('''
                INSERT INTO sales 
                (customer_id, invoice_number, sale_date, total_amount, notes, user_id)
                VALUES (%s, %s, %s, %s, %s, %s)
            ''', (customer_id, invoice_number, sale_date.date(), 0, f"Sale {i}", 1))
            
            sale_id = cursor.lastrowid
            total_amount = 0
            
            # Add 1-4 products to each sale
            num_products = random.randint(1, 4)
            selected_products = random.sample(list(product_ids.items()), num_products)
            
            for product_name, product_id in selected_products:
                quantity = random.randint(1, 5)
                product_cursor = conn.cursor()
                product_cursor.execute('SELECT selling_price FROM products WHERE id = %s', (product_id,))
                product_data = product_cursor.fetchone()
                unit_price = product_data['selling_price']
                total_price = quantity * unit_price
                total_amount += total_price
                
                cursor.execute('''
                    INSERT INTO sale_items
                    (sale_id, product_id, quantity, unit_price, total_price)
                    VALUES (%s, %s, %s, %s, %s)
                ''', (sale_id, product_id, quantity, unit_price, total_price))
                
                product_cursor.close()
            
            # Update sale total
            cursor.execute('''
                UPDATE sales
                SET total_amount = %s
                WHERE id = %s
            ''', (total_amount, sale_id))
        
        conn.commit()
        print("✅ Sample data created successfully.")
        return True
    
    except pymysql.Error as e:
        print(f"❌ Database Error: {e}")
        if conn:
            conn.rollback()
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        if conn:
            conn.rollback()
        return False
    finally:
        if conn:
            conn.close()
            print("🔌 Database connection closed.")

if __name__ == "__main__":
    success = create_sample_data()
    if not success:
        print("\n📝 Setup Instructions:")
        print("1. Copy .env.template to .env")
        print("2. Update .env with your database credentials")
        print("3. Make sure your MySQL database exists")
        print("4. Run the database schema first: mysql -u root -p inventory_db < database_schema.sql")
        print("5. Then run this script again")
        sys.exit(1)
    else:
        print("\n🎉 Sample data setup completed successfully!")
        print("You can now run the application: python run.py") 