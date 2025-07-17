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
    
    # Tables that need business_id column
    tables_needing_business_id = [
        'products',
        'categories', 
        'customers',
        'suppliers',
        'sales',
        'purchases'
    ]
    
    print("🔧 Adding business_id columns to tables...")
    
    for table in tables_needing_business_id:
        # Check if business_id column exists
        cursor.execute(f"DESCRIBE {table}")
        columns = cursor.fetchall()
        business_id_exists = any(column[0] == 'business_id' for column in columns)
        
        if not business_id_exists:
            print(f"  Adding business_id to {table}...")
            cursor.execute(f"ALTER TABLE {table} ADD COLUMN business_id INT NULL")
            cursor.execute(f"ALTER TABLE {table} ADD FOREIGN KEY (business_id) REFERENCES businesses(id)")
            print(f"  ✅ Added business_id to {table}")
        else:
            print(f"  ✅ business_id already exists in {table}")
    
    # Create a default business if none exists
    cursor.execute("SELECT COUNT(*) as count FROM businesses")
    result = cursor.fetchone()
    business_count = result[0] if result else 0
    
    if business_count == 0:
        print("📝 Creating default business...")
        cursor.execute("""
            INSERT INTO businesses (business_name, email, phone, address, gst_number)
            VALUES ('Default Business', 'admin@business.com', '1234567890', 'Default Address', 'DEFAULT123')
        """)
        default_business_id = cursor.lastrowid
        print(f"✅ Created default business with ID: {default_business_id}")
    else:
        cursor.execute("SELECT id FROM businesses LIMIT 1")
        result = cursor.fetchone()
        default_business_id = result[0] if result else 1
        print(f"📝 Using existing business with ID: {default_business_id}")
    
    # Update all records to have the default business_id
    for table in tables_needing_business_id:
        cursor.execute(f"UPDATE {table} SET business_id = %s WHERE business_id IS NULL", (default_business_id,))
        affected_rows = cursor.rowcount
        print(f"  Updated {affected_rows} records in {table}")
    
    # Also update users table
    cursor.execute("UPDATE users SET business_id = %s WHERE business_id IS NULL", (default_business_id,))
    affected_rows = cursor.rowcount
    print(f"  Updated {affected_rows} records in users")
    
    conn.commit()
    print("\n🎉 All database fixes applied successfully!")
    print("Your application should now work without business_id errors.")
    
except Exception as e:
    print(f"❌ Error: {e}")
    if 'conn' in locals():
        conn.rollback()
finally:
    if 'conn' in locals():
        conn.close()
