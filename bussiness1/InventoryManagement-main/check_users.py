import pymysql
from config import Config

def check_users():
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
        cursor.execute('SELECT id, username, password FROM users')
        users = cursor.fetchall()
        
        if not users:
            print("No users found in the database.")
        else:
            print(f"Found {len(users)} users:")
            for user in users:
                print(f"ID: {user['id']}, Username: {user['username']}")
                print(f"Password hash: {user['password'][:30]}...")
        
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_users() 