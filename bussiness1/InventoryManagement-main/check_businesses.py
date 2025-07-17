import pymysql
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

try:
    # Database connection
    conn = pymysql.connect(
        host=os.environ.get('MYSQL_HOST', 'localhost'),
        user=os.environ.get('MYSQL_USER', 'root'),
        password=os.environ.get('MYSQL_PASSWORD', 'root'),
        db=os.environ.get('MYSQL_DB', 'inventory_db')
    )

    cursor = conn.cursor()
    
    # Check if businesses table exists
    cursor.execute("SHOW TABLES LIKE 'businesses'")
    businesses_table_exists = cursor.fetchone() is not None
    
    print(f"businesses table exists: {businesses_table_exists}")
    
    if not businesses_table_exists:
        print("Creating businesses table...")
        cursor.execute("""
            CREATE TABLE businesses (
                id INT AUTO_INCREMENT PRIMARY KEY,
                business_name VARCHAR(100) NOT NULL,
                email VARCHAR(100) NOT NULL,
                phone VARCHAR(20) NOT NULL,
                address TEXT NOT NULL,
                gst_number VARCHAR(30) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        print("✅ businesses table created successfully!")
    else:
        print("✅ businesses table already exists!")
    
except Exception as e:
    print(f"❌ Error: {e}")
finally:
    if 'conn' in locals():
        conn.close()
