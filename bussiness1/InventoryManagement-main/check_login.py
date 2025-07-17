import pymysql
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("Clearing any existing user sessions...")

try:
    # Database connection
    conn = pymysql.connect(
        host=os.environ.get('MYSQL_HOST', 'localhost'),
        user=os.environ.get('MYSQL_USER', 'root'),
        password=os.environ.get('MYSQL_PASSWORD', 'root'),
        db=os.environ.get('MYSQL_DB', 'inventory_db')
    )

    cursor = conn.cursor()
    
    # Check current users
    cursor.execute("SELECT username, full_name, role FROM users")
    users = cursor.fetchall()
    
    print("Current users in database:")
    for user in users:
        print(f"  Username: {user[0]}, Name: {user[1]}, Role: {user[2]}")
    
    print("\n💡 To access the application fresh:")
    print("1. Open your web browser")
    print("2. Go to: http://localhost:8000")
    print("3. You should see the login page")
    print("4. If you go directly to dashboard, click logout in the top menu")
    print("5. Use these credentials to login:")
    print("   - Username: admin")
    print("   - Password: admin123")
    print("   OR")
    print("   - Username: staff") 
    print("   - Password: staff123")
    
except Exception as e:
    print(f"❌ Error: {e}")
finally:
    if 'conn' in locals():
        conn.close()

print("\n🚀 Now start the application:")
print("python run.py")
