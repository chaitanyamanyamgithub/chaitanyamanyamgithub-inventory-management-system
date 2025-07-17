import pymysql
from config import Config
from app.utils.auth_helpers import safe_check_password_hash, safe_generate_password_hash

def test_login():
    try:
        # Connect to the database
        print("Connecting to MySQL database...")
        conn = pymysql.connect(
            host=Config.MYSQL_HOST,
            user=Config.MYSQL_USER,
            password=Config.MYSQL_PASSWORD,
            database=Config.MYSQL_DB,
            cursorclass=pymysql.cursors.DictCursor
        )
        
        cursor = conn.cursor()
        
        # Get admin user
        cursor.execute('SELECT id, username, password FROM users WHERE username = %s', ('admin',))
        admin = cursor.fetchone()
        
        if not admin:
            print("Admin user not found. Creating one...")
            # Create a new admin user
            admin_password_hash = safe_generate_password_hash('admin123')
            cursor.execute(
                'INSERT INTO users (username, password, full_name, role) VALUES (%s, %s, %s, %s)',
                ('admin', admin_password_hash, 'Admin User', 'admin')
            )
            conn.commit()
            print("Admin user created successfully.")
            
            # Get the newly created admin
            cursor.execute('SELECT id, username, password FROM users WHERE username = %s', ('admin',))
            admin = cursor.fetchone()
        
        print(f"Admin user found: ID: {admin['id']}, Username: {admin['username']}")
        print(f"Password hash: {admin['password']}")
        
        # Test password check
        test_password = 'admin123'
        result = safe_check_password_hash(admin['password'], test_password)
        print(f"Password check result for '{test_password}': {result}")
        
        if not result:
            # Try to update the password
            print("Updating admin password...")
            new_password_hash = safe_generate_password_hash('admin123')
            cursor.execute(
                'UPDATE users SET password = %s WHERE username = %s',
                (new_password_hash, 'admin')
            )
            conn.commit()
            print(f"Password updated to: {new_password_hash}")
            
            # Verify the new password works
            cursor.execute('SELECT password FROM users WHERE username = %s', ('admin',))
            updated_admin = cursor.fetchone()
            result = safe_check_password_hash(updated_admin['password'], test_password)
            print(f"Password check result after update: {result}")
        
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_login() 