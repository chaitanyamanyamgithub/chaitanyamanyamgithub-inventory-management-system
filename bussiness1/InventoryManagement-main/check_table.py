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
    cursor.execute("DESCRIBE users")
    columns = cursor.fetchall()
    
    print("Current users table structure:")
    for column in columns:
        print(f"  {column[0]} - {column[1]}")
        
    # Check if business_id column exists
    business_id_exists = any(column[0] == 'business_id' for column in columns)
    print(f"\nbusiness_id column exists: {business_id_exists}")
    
    if not business_id_exists:
        print("Adding business_id column...")
        cursor.execute("ALTER TABLE users ADD COLUMN business_id INT NULL")
        cursor.execute("ALTER TABLE users ADD FOREIGN KEY (business_id) REFERENCES businesses(id)")
        conn.commit()
        print("✅ business_id column added successfully!")
    
except Exception as e:
    print(f"❌ Error: {e}")
finally:
    if 'conn' in locals():
        conn.close()
